"""Static visualizations produced as reproducible pipeline artefacts."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def write_static_figures(
    candidates: pd.DataFrame, latitude_column: str, longitude_column: str, output_dir: Path
) -> None:
    """Save location and PCA figures for reports and presentations."""
    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    normal = candidates.loc[~candidates["is_anomaly"]]
    anomalous = candidates.loc[candidates["is_anomaly"]]

    figure, axis = plt.subplots(figsize=(8, 6))
    axis.scatter(normal[longitude_column], normal[latitude_column], s=18, alpha=0.65, label="Other")
    axis.scatter(
        anomalous[longitude_column],
        anomalous[latitude_column],
        color="crimson",
        marker="x",
        s=42,
        label="Anomaly",
    )
    axis.set(xlabel="Longitude", ylabel="Latitude", title="Geophysical anomaly candidates")
    axis.legend()
    figure.tight_layout()
    figure.savefig(output_dir / "anomaly_locations.png", dpi=180)
    plt.close(figure)

    figure, axis = plt.subplots(figsize=(8, 6))
    scatter = axis.scatter(
        candidates["PC1"],
        candidates["PC2"],
        c=candidates["isolation_forest_score"],
        cmap="viridis",
        s=26,
    )
    axis.set(xlabel="Principal component 1", ylabel="Principal component 2", title="PCA feature space")
    figure.colorbar(scatter, ax=axis, label="Isolation Forest score")
    figure.tight_layout()
    figure.savefig(output_dir / "pca_scores.png", dpi=180)
    plt.close(figure)
