"""Evaluation helpers for reference occurrence data."""

from __future__ import annotations

import pandas as pd


def summarize_reference_proximity(
    candidates: pd.DataFrame, reference_distance_km: float
) -> dict[str, int | float]:
    """Report proximity of ranked anomalies to known occurrences without training on them."""
    if "nearest_copper_occurrence_km" not in candidates:
        return {"reference_data_available": False}

    close = candidates["nearest_copper_occurrence_km"] <= reference_distance_km
    anomaly_mask = candidates["is_anomaly"]
    return {
        "reference_data_available": True,
        "reference_distance_km": reference_distance_km,
        "records_within_reference_distance": int(close.sum()),
        "anomalies_within_reference_distance": int((close & anomaly_mask).sum()),
        "anomaly_reference_proximity_rate": (
            float((close & anomaly_mask).sum() / anomaly_mask.sum()) if anomaly_mask.any() else 0.0
        ),
    }
