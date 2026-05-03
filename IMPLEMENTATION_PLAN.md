# LEGO Cat Builder Implementation Plan (Single Source of Truth)

This file is the authoritative high-level implementation plan for the project.
All phase references in `conversation_cursor/`, `to-do/`, `task_summary/`, `progress/latest.md`, and `structure/latest.md` must remain consistent with this plan.

## Execution Policy

- The agent is authorized to download files, create files, and modify project files without per-file confirmation when file size is <= 200 MB.
- For any single file expected to exceed 200 MB, the agent must inform the user before downloading or creating it.
- After each completed subtask, update workflow tracking files (`conversation_cursor`, `to-do`, `task_summary`, `structure/latest.md`, and `progress/latest.md`) so status remains synchronized.
- When a new phase or subphase is added or changed, update this file first, then propagate that change into tracking files.

## Phase Roadmap

### Phase 0 - Foundation and Data Contracts (completed)
- Define schemas and example contracts for `photo_set`, `brick_inventory`, and `build_plan`.
- Establish baseline folder conventions for inputs, artifacts, and outputs.

### Phase 1 - Photo Acceptability Gate (in progress)
- Require `front`, `side`, and `top` views.
- Validate each required view against quality thresholds:
  - resolution,
  - blur/sharpness,
  - subject coverage ratio,
  - background complexity.
- Emit deterministic pass/fail outputs with actionable recapture recommendations.

### Phase 2 - Multi-View 3D Reconstruction (pending)
- Run COLMAP-based feature extraction, matching, sparse reconstruction, and dense reconstruction.
- Save reconstruction quality metrics and normalize mesh orientation/scale for downstream LEGO steps.

### Phase 3 - Voxelization and Canonical Model (pending)
- Produce coarse and fine voxel grids.
- Generate shell and thickened variants suitable for visual preview and build mode.

### Phase 4 - Inventory-Constrained Brick Decomposition (pending)
- Run greedy baseline placement (`2x4`, `2x2`, `1x2`, `1x1`).
- Apply constrained optimization with inventory, color, overlap, and connectivity constraints.

### Phase 5 - Buildability and Stability Validation (pending)
- Verify physical support and detect fragile structures.
- Support both `preview_mode` and `build_mode` criteria.

### Phase 6 - BOM and Build Instructions (pending)
- Generate bill of materials, missing-part report, and layer-by-layer instructions.
- Export machine-readable and human-readable outputs.

### Phase 7 - Benchmarking and Iterative Tuning (pending)
- Evaluate 3-5 datasets.
- Track success/failure metrics and tune thresholds/objective weights.

## Current Focus

- Finish Phase 1 validator implementation and produce a report for the imported `thu_mvs_cat` dataset.
