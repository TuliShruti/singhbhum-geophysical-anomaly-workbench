"""Core routines for spatial matching and geophysical anomaly analysis."""

from __future__ import annotations

from pathlib import Path
import json

import numpy as np
import pandas as pd
from scipy.spatial import cKDTree
from sklearn.decomposition import PCA
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

EARTH_RADIUS_KM = 6371.0088


def read_survey(path: str | Path, required_columns: list[str]) -> pd.DataFrame:
    """Read a survey CSV and keep rows with valid required numeric values."""
    data = pd.read_csv(path)
    missing = sorted(set(required_columns).difference(data.columns))
    if missing:
        raise ValueError(f"{path} is missing required columns: {', '.join(missing)}")

    result = data.copy()
    for column in required_columns:
        result[column] = pd.to_numeric(result[column], errors="coerce")
    return result.dropna(subset=required_columns).reset_index(drop=True)


def _unit_sphere_coordinates(latitude: pd.Series, longitude: pd.Series) -> np.ndarray:
    lat_rad = np.deg2rad(latitude.to_numpy())
    lon_rad = np.deg2rad(longitude.to_numpy())
    return np.column_stack(
        (
            np.cos(lat_rad) * np.cos(lon_rad),
            np.cos(lat_rad) * np.sin(lon_rad),
            np.sin(lat_rad),
        )
    )


def _great_circle_distance_km(
    lat1: np.ndarray, lon1: np.ndarray, lat2: np.ndarray, lon2: np.ndarray
) -> np.ndarray:
    """Calculate great-circle distance with the haversine formula."""
    lat1, lon1, lat2, lon2 = map(np.deg2rad, (lat1, lon1, lat2, lon2))
    delta_lat = lat2 - lat1
    delta_lon = lon2 - lon1
    haversine = (
        np.sin(delta_lat / 2) ** 2
        + np.cos(lat1) * np.cos(lat2) * np.sin(delta_lon / 2) ** 2
    )
    return 2 * EARTH_RADIUS_KM * np.arcsin(np.sqrt(haversine))


def match_nearest_gravity(
    magnetic: pd.DataFrame,
    gravity: pd.DataFrame,
    latitude_column: str,
    longitude_column: str,
    matching_radius_km: float,
) -> pd.DataFrame:
    """Attach nearest gravity measurements to each magnetic-survey record."""
    if matching_radius_km <= 0:
        raise ValueError("matching_radius_km must be positive.")

    tree = cKDTree(_unit_sphere_coordinates(gravity[latitude_column], gravity[longitude_column]))
    _, gravity_index = tree.query(
        _unit_sphere_coordinates(magnetic[latitude_column], magnetic[longitude_column]), k=1
    )

    nearest = gravity.iloc[gravity_index].reset_index(drop=True)
    result = magnetic.reset_index(drop=True).copy()
    result["matched_gravity_latitude"] = nearest[latitude_column].to_numpy()
    result["matched_gravity_longitude"] = nearest[longitude_column].to_numpy()
    result["gravity_match_distance_km"] = _great_circle_distance_km(
        result[latitude_column].to_numpy(),
        result[longitude_column].to_numpy(),
        nearest[latitude_column].to_numpy(),
        nearest[longitude_column].to_numpy(),
    )

    for column in gravity.columns:
        if column not in {latitude_column, longitude_column}:
            target = column if column not in result.columns else f"gravity_{column}"
            result[target] = nearest[column].to_numpy()

    return result.loc[result["gravity_match_distance_km"] <= matching_radius_km].reset_index(
        drop=True
    )


def distance_to_nearest_occurrence(
    observations: pd.DataFrame,
    occurrences: pd.DataFrame,
    latitude_column: str,
    longitude_column: str,
) -> np.ndarray:
    """Return nearest-occurrence great-circle distances for all observations."""
    tree = cKDTree(
        _unit_sphere_coordinates(occurrences[latitude_column], occurrences[longitude_column])
    )
    _, occurrence_index = tree.query(
        _unit_sphere_coordinates(observations[latitude_column], observations[longitude_column]),
        k=1,
    )
    nearest = occurrences.iloc[occurrence_index].reset_index(drop=True)
    return _great_circle_distance_km(
        observations[latitude_column].to_numpy(),
        observations[longitude_column].to_numpy(),
        nearest[latitude_column].to_numpy(),
        nearest[longitude_column].to_numpy(),
    )


def analyze_features(
    data: pd.DataFrame, feature_columns: list[str], contamination: float, random_state: int
) -> tuple[pd.DataFrame, PCA]:
    """Run standardized Isolation Forest and PCA on selected feature columns."""
    missing = sorted(set(feature_columns).difference(data.columns))
    if missing:
        raise ValueError(f"Merged data is missing feature columns: {', '.join(missing)}")
    if not 0 < contamination <= 0.5:
        raise ValueError("contamination must be greater than 0 and no greater than 0.5.")

    features = data[feature_columns].apply(pd.to_numeric, errors="coerce")
    features = features.fillna(features.median(numeric_only=True))
    if features.isna().any().any():
        raise ValueError("A feature column contains no valid numeric values.")

    standardized = StandardScaler().fit_transform(features)
    isolation_forest = IsolationForest(
        contamination=contamination, random_state=random_state, n_estimators=300
    )
    labels = isolation_forest.fit_predict(standardized)
    scores = isolation_forest.decision_function(standardized)

    pca = PCA(n_components=min(2, standardized.shape[1]), random_state=random_state)
    principal_components = pca.fit_transform(standardized)

    result = data.copy()
    result["is_anomaly"] = labels == -1
    result["isolation_forest_score"] = scores
    result["PC1"] = principal_components[:, 0]
    result["PC2"] = principal_components[:, 1] if principal_components.shape[1] > 1 else 0.0
    return result, pca


def write_summary(path: str | Path, summary: dict) -> None:
    """Write a human-readable JSON summary."""
    Path(path).write_text(json.dumps(summary, indent=2), encoding="utf-8")
