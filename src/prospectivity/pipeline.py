"""Orchestration layer for a complete prospectivity-analysis run."""

from __future__ import annotations

from pathlib import Path

from src.analysis import (
    analyze_features,
    distance_to_nearest_occurrence,
    match_nearest_gravity,
    read_survey,
    write_summary,
)
from src.prospectivity.contracts import AnalysisConfig
from src.prospectivity.evaluation import summarize_reference_proximity
from src.prospectivity.exports import write_geojson, write_markdown_report
from src.prospectivity.quality import (
    consolidate_locations,
    quality_summary,
    validate_coordinate_ranges,
)
from src.prospectivity.visualization import write_static_figures


def run_pipeline(config: AnalysisConfig) -> dict:
    """Validate, fuse, analyse, evaluate, and export a complete research run."""
    lat, lon = config.latitude_column, config.longitude_column
    gravity = read_survey(config.gravity_file, [lat, lon, *config.gravity_features])
    magnetic = read_survey(config.magnetic_file, [lat, lon, config.magnetic_feature])
    gravity = validate_coordinate_ranges(gravity, lat, lon, "Gravity survey")
    magnetic = validate_coordinate_ranges(magnetic, lat, lon, "Magnetic survey")
    raw_quality = [quality_summary(gravity, "gravity"), quality_summary(magnetic, "magnetic")]

    gravity = consolidate_locations(gravity, lat, lon, config.coordinate_precision)
    magnetic = consolidate_locations(magnetic, lat, lon, config.coordinate_precision)
    merged = match_nearest_gravity(magnetic, gravity, lat, lon, config.matching_radius_km)
    if merged.empty:
        raise ValueError("No magnetic records matched gravity records within the configured radius.")

    results, pca = analyze_features(
        merged,
        [config.magnetic_feature, *config.gravity_features],
        config.contamination,
        config.random_state,
    )
    results["candidate_rank"] = (
        results["isolation_forest_score"].rank(method="first", ascending=True).astype(int)
    )
    candidates = results.sort_values("candidate_rank").reset_index(drop=True)

    if config.copper_occurrences_file and config.copper_occurrences_file.is_file():
        occurrences = read_survey(config.copper_occurrences_file, [lat, lon])
        occurrences = validate_coordinate_ranges(occurrences, lat, lon, "Copper occurrences")
        candidates["nearest_copper_occurrence_km"] = distance_to_nearest_occurrence(
            candidates, occurrences, lat, lon
        )

    data_dir = Path(config.output_data_dir)
    data_dir.mkdir(parents=True, exist_ok=True)
    candidates.to_csv(data_dir / "anomaly_results.csv", index=False)
    merged.to_csv(data_dir / "merged_geophysics.csv", index=False)
    candidates.head(config.top_candidate_count).to_csv(data_dir / "priority_candidates.csv", index=False)
    write_geojson(candidates, lat, lon, data_dir / "anomaly_results.geojson")
    write_static_figures(candidates, lat, lon, Path(config.output_figure_dir))

    summary = {
        "gravity_records_after_validation": len(gravity),
        "magnetic_records_after_validation": len(magnetic),
        "matched_records": len(merged),
        "anomalies": int(candidates["is_anomaly"].sum()),
        "pca_explained_variance_ratio": pca.explained_variance_ratio_.round(6).tolist(),
        "data_quality": raw_quality,
        **summarize_reference_proximity(candidates, config.reference_distance_km),
    }
    write_summary(data_dir / "analysis_summary.json", summary)
    write_markdown_report(summary, data_dir / "analysis_report.md")
    return summary
