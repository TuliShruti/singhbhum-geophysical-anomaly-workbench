# Data contract

Every source file is a CSV with a header row. Geographic coordinates must use
WGS84 decimal degrees.

| Dataset | Required columns | Notes |
| --- | --- | --- |
| Gravity | latitude, longitude, Bouguer anomaly, elevation | One row per observation. |
| Magnetic | latitude, longitude, magnetic anomaly | One row per observation. |
| Copper occurrences | latitude, longitude | Optional reference-only data; not used for model training. |

The configured coordinate columns must have values in these ranges:

- latitude: -90 to 90
- longitude: -180 to 180

Records at the same coordinates are consolidated using the mean of numeric
measurements. The pipeline records how many source records contributed to each
consolidated location. A reference occurrence is never used as an ML label in
the current unsupervised workflow.
