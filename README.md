# Singhbhum Geophysical Anomaly Analysis

This modular Python research workbench combines gravity and magnetic survey
records, validates and consolidates spatial observations, identifies unusual
geophysical signatures with Isolation Forest, and summarizes variation with
Principal Component Analysis (PCA). It ranks field-investigation candidates; it
does not identify confirmed deposits.

## Setup

Use Python 3.10 or later.

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
```

## Input files

Place survey data in `data/raw/`. CSV files need latitude and longitude columns,
plus the named measurement columns configured below.

Copy and edit the example configuration:

```powershell
Copy-Item config\example_config.json config\analysis_config.json
```

The default column names are:

| File | Required columns |
| --- | --- |
| Gravity | `latitude`, `longitude`, `bouguer_anomaly`, `elevation` |
| Magnetic | `latitude`, `longitude`, `magnetic_anomaly` |
| Copper occurrences (optional) | `latitude`, `longitude` |

Column names can be changed in `analysis_config.json`.

## Run

```powershell
python -m src.run_analysis --config config/analysis_config.json
```

Results are written to `data/processed/` and figures to `outputs/figures/`.
The key outputs are:

- `merged_geophysics.csv` — magnetic records matched to nearby gravity records.
- `anomaly_results.csv` — anomaly label, Isolation Forest score, PCA scores,
  and optional distance to the closest copper occurrence.
- `analysis_summary.json` — row counts, PCA variance, and anomaly count.
- `priority_candidates.csv` — ranked locations for field-review prioritization.
- `anomaly_results.geojson` — point data ready for QGIS or other GIS tools.
- `analysis_report.md` — a self-documenting, human-readable run report.

## Optional dashboard

```powershell
pip install -e ".[dashboard]"
streamlit run app/dashboard.py
```

## Architecture

See [the project architecture](docs/architecture.md) and the
[data contract](docs/data_contract.md) before adding data sources or models.

## Notes

- Spatial matching uses great-circle distance, not a direct latitude/longitude
  join.
- A magnetic point is retained only when its nearest gravity point is within
  `matching_radius_km`.
- Measurements are standardized before anomaly detection and PCA.
- Edit the configuration rather than modifying source code for a new dataset.

## Test

```powershell
pytest
```
