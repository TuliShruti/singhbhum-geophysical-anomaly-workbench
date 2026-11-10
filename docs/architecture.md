# Project architecture

```text
Raw surveys ──> validation ──> coordinate consolidation ──> spatial fusion
                                                                  │
Copper occurrences ──────────────────────────────────────────────┤
                                                                  v
                                                         feature matrix
                                                                  │
                                             ┌────────────────────┴───────────────────┐
                                             v                                        v
                                    Isolation Forest                               PCA
                                             │                                        │
                                             └──────────> ranked candidates <─────────┘
                                                                  │
                                     ┌────────────────────────────┼──────────────────────────┐
                                     v                            v                          v
                              CSV / GeoJSON                 quality report              dashboard
```

The code is separated by responsibility:

- `src/analysis.py`: reusable numerical and geospatial primitives.
- `src/prospectivity/contracts.py`: configuration and input-schema contracts.
- `src/prospectivity/quality.py`: validation, missing-data metrics, and spatial
  consolidation.
- `src/prospectivity/evaluation.py`: reference-occurrence proximity metrics.
- `src/prospectivity/exports.py`: map-ready and human-readable artefacts.
- `src/prospectivity/pipeline.py`: orchestration only; it does not contain
  statistical implementation details.
- `app/dashboard.py`: optional results viewer, separated from the analysis.

This separation means a future supervised model, a new survey type, or an
alternative spatial-matching method can be added without changing reporting or
visualization code.
