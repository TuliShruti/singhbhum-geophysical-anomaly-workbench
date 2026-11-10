"""Typed configuration contract for a prospectivity-analysis run."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path


@dataclass(frozen=True)
class AnalysisConfig:
    gravity_file: Path
    magnetic_file: Path
    copper_occurrences_file: Path | None
    output_data_dir: Path
    output_figure_dir: Path
    latitude_column: str
    longitude_column: str
    gravity_features: tuple[str, ...]
    magnetic_feature: str
    matching_radius_km: float
    contamination: float
    random_state: int
    coordinate_precision: int = 5
    reference_distance_km: float = 1.0
    top_candidate_count: int = 25

    @classmethod
    def from_json(cls, path: str | Path) -> "AnalysisConfig":
        source = Path(path)
        values = json.loads(source.read_text(encoding="utf-8"))
        root = source.parent.parent

        def resolve(value: str | None) -> Path | None:
            if value is None:
                return None
            candidate = Path(value)
            return candidate if candidate.is_absolute() else root / candidate

        config = cls(
            gravity_file=resolve(values["gravity_file"]),
            magnetic_file=resolve(values["magnetic_file"]),
            copper_occurrences_file=resolve(values.get("copper_occurrences_file")),
            output_data_dir=resolve(values["output_data_dir"]),
            output_figure_dir=resolve(values["output_figure_dir"]),
            latitude_column=values["latitude_column"],
            longitude_column=values["longitude_column"],
            gravity_features=tuple(values["gravity_features"]),
            magnetic_feature=values["magnetic_feature"],
            matching_radius_km=float(values["matching_radius_km"]),
            contamination=float(values["contamination"]),
            random_state=int(values["random_state"]),
            coordinate_precision=int(values.get("coordinate_precision", 5)),
            reference_distance_km=float(values.get("reference_distance_km", 1.0)),
            top_candidate_count=int(values.get("top_candidate_count", 25)),
        )
        config.validate()
        return config

    def validate(self) -> None:
        if not self.gravity_features:
            raise ValueError("At least one gravity feature is required.")
        if self.matching_radius_km <= 0 or self.reference_distance_km <= 0:
            raise ValueError("Distance thresholds must be positive.")
        if not 0 < self.contamination <= 0.5:
            raise ValueError("contamination must be in the interval (0, 0.5].")
        if not 0 <= self.coordinate_precision <= 10:
            raise ValueError("coordinate_precision must be between 0 and 10.")
        if self.top_candidate_count <= 0:
            raise ValueError("top_candidate_count must be positive.")
