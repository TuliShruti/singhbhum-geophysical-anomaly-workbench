"""Command-line entry point for the modular prospectivity workbench."""

from __future__ import annotations

import argparse
import os
import webbrowser
from pathlib import Path

from src.prospectivity.contracts import AnalysisConfig
from src.prospectivity.pipeline import run_pipeline


def print_review_prompt(config: AnalysisConfig, summary: dict) -> None:
    """Offer to open a generated figure or result file for review."""
    options = {
        "1": (config.output_figure_dir / "anomaly_locations.png", "Candidate location map"),
        "2": (config.output_figure_dir / "pca_scores.png", "PCA comparison figure"),
        "3": (config.output_data_dir / "priority_candidates.csv", "Top-ranked candidates and measurements"),
        "4": (config.output_data_dir / "analysis_report.md", "Analysis summary report"),
        "5": (config.output_data_dir / "anomaly_results.csv", "All anomaly results"),
    }
    while True:
        print(f"\nAnalysis found {summary['anomalies']} anomalies. What would you like to open?")
        for number, (path, description) in options.items():
            print(f"  {number}. {description} — {path}")
        print("  0. Close menu")
        choice = input("Choose an option: ").strip()
        if choice == "0":
            print("Review menu closed.")
            return
        if choice not in options:
            print("Invalid choice. Select a listed number, or 0 to close the menu.")
            continue

        path, _ = options[choice]
        if not path.is_file():
            print(f"File not found: {path}")
            continue
        if os.name == "nt":
            os.startfile(path)  # type: ignore[attr-defined]
        else:
            webbrowser.open(Path(path).resolve().as_uri())
        print(f"Opened {path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run geophysical anomaly analysis.")
    parser.add_argument("--config", required=True, help="Path to an analysis JSON configuration.")
    args = parser.parse_args()
    config = AnalysisConfig.from_json(args.config)
    summary = run_pipeline(config)
    print(f"Completed analysis: {summary['anomalies']} anomalies identified.")
    print_review_prompt(config, summary)


if __name__ == "__main__":
    main()
