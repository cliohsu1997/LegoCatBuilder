# Proposal: initialize_lego_cat_pipeline

## Objective
Implement a practical, reproducible 3D pipeline that converts `front + side + top` cat photos into:
1. a previewable 3D LEGO model,
2. an inventory-constrained buildable decomposition,
3. a BOM and step-by-step instructions.

## Current Phase Status
- Completed: **Phase 0 (Project foundation and data contracts)**.
- Completed: **Phase 1 (Photo acceptability gate)**.
- Current: **Phase 2 (COLMAP reconstruction + visualization helpers)**.
- Next: **Phase 3 (Voxelization)** once reconstruction quality gates are satisfied.
- Phase source of truth: `IMPLEMENTATION_PLAN.md` (root).

## Workflow Governance Decisions (new)
- Root `IMPLEMENTATION_PLAN.md` is now the authoritative high-level phase plan.
- For any phase/subphase change, update `IMPLEMENTATION_PLAN.md` first, then sync task/progress/structure docs.
- Agent is authorized to create/modify/download files up to 200 MB without per-file confirmation.
- For files larger than 200 MB, notify user before proceeding.
- After each completed subtask, update:
  - `conversation_cursor/...`
  - `to-do/...`
  - `task_summary/...`
  - `structure/latest.md`
  - `progress/latest.md`

## Dataset Decision for Phase 1 Bootstrap (new)
- Imported THU-MVS Cat dataset (`cat_images.zip`) for deterministic multi-view validation inputs.
- Curated required views from same subject into:
  - `data/raw/cat_views/thu_mvs_cat/selected_views/front.png`
  - `data/raw/cat_views/thu_mvs_cat/selected_views/side.png`
  - `data/raw/cat_views/thu_mvs_cat/selected_views/top.png`
- Recorded source and verification in:
  - `data/raw/cat_views/thu_mvs_cat/source.md`
  - `data/raw/cat_views/thu_mvs_cat/verification.md`

## Grounded Technical Basis (No speculative-only components)
- **Multi-view reconstruction**: `COLMAP` command-line SfM/MVS pipeline.
- **Voxel-to-brick baseline concepts**: `brickalize`.
- **Inventory-constrained optimization ideas**: `LegoOptimizer` style knapsack/coverage strategy.
- **Stability-analysis direction**: `StableLego`-style support checks.

These are references for implementation strategy, not direct dependencies yet.

## Implementation Plan (Phase-by-Phase)

### Phase 0 - Foundation and contracts (completed)
- Define JSON contracts:
  - `photo_set` (view metadata and quality stats),
  - `brick_inventory` (part dimensions, color, quantity),
  - `build_plan` (placed parts and coordinates).
- Define folder conventions for inputs, artifacts, and outputs.

### Phase 1 - Photo acceptability gate (current)
- Enforce required views: `front`, `side`, `top`.
- Validate:
  - minimum resolution,
  - blur/sharpness threshold,
  - subject coverage ratio,
  - background complexity warning.
- Output a deterministic pass/fail report with recapture suggestions.

### Phase 2 - 3D reconstruction
- Run COLMAP pipeline:
  - feature extraction and matching,
  - sparse reconstruction,
  - dense reconstruction.
- Convert reconstruction output to mesh.
- Normalize to LEGO coordinate conventions (`z` up, base at `z=0`, scaled units).

### Phase 3 - Voxelization
- Generate coarse voxel grid (fast preview) and fine voxel grid (build mode).
- Produce shell-only and thickened variants.
- Persist voxel arrays with metadata for downstream phases.

### Phase 4 - Inventory-constrained decomposition
- Baseline greedy placement in order: `2x4`, `2x2`, `1x2`, `1x1`.
- Optimization pass constrained by:
  - available quantities,
  - color availability,
  - overlap validity,
  - connectivity preference.
- Objective: maximize coverage, minimize part count, reduce unsupported spans.

### Phase 5 - Buildability checks
- Verify each placed part is physically supported.
- Detect fragile segments (isolated chains and long spans).
- Provide `preview_mode` and `build_mode` validation thresholds.

### Phase 6 - Instructions and BOM
- Export:
  - BOM by part and color,
  - missing-parts report,
  - layer-by-layer instructions,
  - top/front/side visual guides.
- Formats: JSON + CSV + image assets (PDF is optional extension).

### Phase 7 - Validation loop
- Evaluate on 3-5 test sets.
- Track reproducible metrics:
  - reconstruction success rate,
  - decomposition validity rate,
  - stability pass rate,
  - brick shortfall rate.
- Tune thresholds and objective weights based on results.

## Immediate Next Implementation Tasks
1. Increase accepted input view count from 3 canonical views to a denser subset for improved Phase 2 completeness.
2. Add mesh export plus coordinate normalization (`z` up, base at `z=0`, LEGO-unit scale).
3. Preserve reconstruction quality diagnostics (registered images, sparse points, dense artifacts) in summary contracts.
4. Use `python/code/visualize_reconstruction.py` to launch COLMAP GUI and export local PLY previews when sparse model files are available.

