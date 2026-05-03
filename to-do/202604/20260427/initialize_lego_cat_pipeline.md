# To-Do: initialize_lego_cat_pipeline

## Phase 1 - Acceptability gate
- [x] Acquire a same-subject multi-view cat dataset with at least `front`, `side`, `top` views.
- [x] Record data source and verification notes for selected views.
- [ ] Implement required view completeness check (`front`, `side`, `top`).
- [ ] Implement resolution, blur, subject-coverage, and background-complexity checks.
- [ ] Emit pass/fail report with recapture suggestions.
- [ ] Run Phase 1 validator on `thu_mvs_cat` selected views and save the report under `outputs/reports/`.

## Workflow and governance
- [x] Create root `IMPLEMENTATION_PLAN.md` as single source of truth for project phases.
- [x] Update workflow skill/rule to enforce <=200 MB autonomous file operations and synchronized updates.
- [ ] Keep phase names and statuses synchronized across task files, `progress/latest.md`, and `structure/latest.md` after every completed subtask.

## Phase 2 - Reconstruction
- [ ] Implement COLMAP runner integration for accepted photo sets.
- [ ] Export sparse/dense reconstruction metrics for reporting.
- [ ] Normalize mesh orientation and scale to LEGO coordinates.

## Phase 3-4 - Voxel and decomposition
- [ ] Implement coarse and fine voxelization modes.
- [ ] Implement baseline greedy brick placement (`2x4`, `2x2`, `1x2`, `1x1`).
- [ ] Implement constrained optimization pass with inventory limits.

## Phase 5-6 - Buildability and outputs
- [ ] Implement support/stability checks for `build_mode`.
- [ ] Generate BOM and missing-inventory reports.
- [ ] Generate layer-by-layer instructions with top/front/side guides.

## Phase 7 - Validation loop
- [ ] Run 3-5 benchmark photo sets.
- [ ] Record reconstruction/decomposition/stability metrics.
- [ ] Tune thresholds and objective weights from benchmark results.

