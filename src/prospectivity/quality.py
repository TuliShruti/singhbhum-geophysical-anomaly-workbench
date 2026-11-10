"""Data validation and location-level consolidation."""

from __future__ import annotations

import pandas as pd


def validate_coordinate_ranges(
    data: pd.DataFrame, latitude_column: str, longitude_column: str, dataset_name: str
) -> pd.DataFrame:
    """Reject coordinates outside the WGS84 latitude/longitude ranges."""
    valid = data[latitude_column].between(-90, 90) & data[longitude_column].between(-180, 180)
    if not valid.all():
        invalid_count = int((~valid).sum())
        raise ValueError(f"{dataset_name} has {invalid_count} invalid coordinate records.")
    return data


def consolidate_locations(
    data: pd.DataFrame, latitude_column: str, longitude_column: str, precision: int
) -> pd.DataFrame:
    """Aggregate repeated survey observations at a rounded coordinate location."""
    working = data.copy()
    working["_latitude_key"] = working[latitude_column].round(precision)
    working["_longitude_key"] = working[longitude_column].round(precision)
    numeric_columns = working.select_dtypes(include="number").columns.tolist()
    numeric_columns = [
        column
        for column in numeric_columns
        if not column.startswith("_") and column not in {latitude_column, longitude_column}
    ]

    consolidated = (
        working.groupby(["_latitude_key", "_longitude_key"], as_index=False)[numeric_columns]
        .mean()
        .rename(columns={"_latitude_key": latitude_column, "_longitude_key": longitude_column})
    )
    counts = (
        working.groupby(["_latitude_key", "_longitude_key"], as_index=False)
        .size()
        .rename(
            columns={
                "_latitude_key": latitude_column,
                "_longitude_key": longitude_column,
                "size": "source_record_count",
            }
        )
    )
    return consolidated.merge(counts, on=[latitude_column, longitude_column], validate="one_to_one")


def quality_summary(data: pd.DataFrame, dataset_name: str) -> dict:
    """Summarize a dataset after input conversion and before analysis."""
    return {
        "dataset": dataset_name,
        "records": len(data),
        "columns": len(data.columns),
        "missing_cells": int(data.isna().sum().sum()),
        "duplicate_rows": int(data.duplicated().sum()),
    }
