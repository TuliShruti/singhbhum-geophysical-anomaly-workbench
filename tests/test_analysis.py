import pandas as pd

from src.analysis import analyze_features, match_nearest_gravity
from src.prospectivity.quality import consolidate_locations


def test_nearest_gravity_match_respects_radius():
    gravity = pd.DataFrame(
        {
            "latitude": [22.0, 23.0],
            "longitude": [86.0, 87.0],
            "bouguer_anomaly": [10.0, 20.0],
            "elevation": [100.0, 200.0],
        }
    )
    magnetic = pd.DataFrame(
        {
            "latitude": [22.001, 25.0],
            "longitude": [86.001, 90.0],
            "magnetic_anomaly": [5.0, 6.0],
        }
    )

    matched = match_nearest_gravity(magnetic, gravity, "latitude", "longitude", 1.0)

    assert len(matched) == 1
    assert matched.loc[0, "bouguer_anomaly"] == 10.0


def test_analysis_adds_anomaly_and_pca_columns():
    data = pd.DataFrame(
        {
            "magnetic_anomaly": [1.0, 2.0, 3.0, 100.0],
            "bouguer_anomaly": [2.0, 3.0, 4.0, 100.0],
            "elevation": [10.0, 20.0, 30.0, 1000.0],
        }
    )

    results, pca = analyze_features(
        data,
        ["magnetic_anomaly", "bouguer_anomaly", "elevation"],
        contamination=0.25,
        random_state=42,
    )

    assert {"is_anomaly", "isolation_forest_score", "PC1", "PC2"}.issubset(results.columns)
    assert len(pca.explained_variance_ratio_) == 2


def test_consolidation_averages_duplicate_locations():
    data = pd.DataFrame(
        {
            "latitude": [22.0, 22.0, 22.1],
            "longitude": [86.0, 86.0, 86.1],
            "magnetic_anomaly": [10.0, 14.0, 20.0],
        }
    )

    consolidated = consolidate_locations(data, "latitude", "longitude", precision=5)

    assert len(consolidated) == 2
    assert consolidated.loc[consolidated["latitude"] == 22.0, "magnetic_anomaly"].iloc[0] == 12.0
    assert consolidated.loc[consolidated["latitude"] == 22.0, "source_record_count"].iloc[0] == 2
