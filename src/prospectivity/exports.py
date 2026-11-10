"""Export routines for tabular, GIS, and report artefacts."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


def write_geojson(
    candidates: pd.DataFrame, latitude_column: str, longitude_column: str, output_path: Path
) -> None:
    """Export candidate points as portable GeoJSON without a GIS dependency."""
    features = []
    for _, row in candidates.iterrows():
        properties = {
            key: (value.item() if hasattr(value, "item") else value)
            for key, value in row.items()
            if key not in {latitude_column, longitude_column}
            and pd.notna(value)
            and not isinstance(value, (list, dict))
        }
        features.append(
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [float(row[longitude_column]), float(row[latitude_column])],
                },
                "properties": properties,
            }
        )
    output_path.write_text(
        json.dumps({"type": "FeatureCollection", "features": features}, default=str, indent=2),
        encoding="utf-8",
    )


def write_markdown_report(summary: dict, output_path: Path) -> None:
    """Create a concise report that documents an analysis run."""
    lines = [
        "# Geophysical anomaly analysis report",
        "",
        "## Scope",
        "",
        "This is an unsupervised geophysical anomaly analysis. Detected locations",
        "are priorities for geological investigation, not confirmed mineral deposits.",
        "",
        "## Run summary",
        "",
    ]
    for key, value in summary.items():
        lines.append(f"- **{key.replace('_', ' ').capitalize()}:** {value}")
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
