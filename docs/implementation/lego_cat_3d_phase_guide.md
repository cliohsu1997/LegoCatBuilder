# LEGO Cat 3D Phase Guide

This document defines concrete implementation behavior for each pipeline phase.

## Phase 0: Data Contracts and Folder Conventions

### Data contracts
- `photo_set`: required metadata and quality annotations for each view.
- `brick_inventory`: available parts with dimensions, colors, and counts.
- `build_plan`: deterministic list of placed bricks with coordinates.

Schemas are stored in:
- `contracts/schemas/photo_set.schema.json`
- `contracts/schemas/brick_inventory.schema.json`
- `contracts/schemas/build_plan.schema.json`

### Folder conventions
- `inputs/photos/` raw and curated image sets.
- `artifacts/reconstruction/` sparse and dense reconstruction outputs.
- `artifacts/voxel/` canonical voxel grids.
- `artifacts/decomposition/` placement outputs and solver traces.
- `outputs/instructions/` final instruction pages and manifests.
- `outputs/reports/` validation and benchmark reports.

## Phase 1: Photo Acceptability Gate
- Required views: `front`, `side`, `top`.
- Quality checks:
  - minimum image resolution (`min_width`, `min_height`),
  - blur score threshold,
  - subject coverage ratio threshold,
  - background complexity warning threshold.
- Output:
  - `accepted: true/false`,
  - per-view reasons,
  - recapture recommendations.

## Phase 2: Multi-View 3D Reconstruction
- Use COLMAP steps:
  - feature extraction and matching,
  - sparse reconstruction,
  - dense reconstruction.
- Normalize mesh orientation:
  - `z` axis as height,
  - base plane at `z = 0`,
  - scale to desired LEGO stud dimensions.
- Save quality metrics:
  - matched feature count,
  - reprojection error,
  - dense point count.

## Phase 3: Voxelization Strategy
- Build two voxel resolutions:
  - coarse for quick preview,
  - fine for build mode.
- Produce:
  - shell model for visual fidelity,
  - thickened model variant for structural robustness.
- Persist as 3D arrays and metadata sidecars.

## Phase 4: Brick Decomposition
- Greedy baseline order:
  - `2x4`, `2x2`, `1x2`, `1x1`.
- Constrained optimization:
  - enforce inventory counts and allowed colors,
  - avoid overlap collisions,
  - maximize support continuity.
- Weighted objective:
  - maximize voxel coverage,
  - minimize total brick count,
  - maximize connectivity,
  - penalize unsupported overhangs.

## Phase 5: Buildability and Stability
- Validate support:
  - each brick requires direct support beneath or approved support structure.
- Detect fragile elements:
  - isolated chains,
  - long unsupported spans.
- Provide two operational modes:
  - `preview_mode`: appearance-first.
  - `build_mode`: buildability-first.

## Phase 6: Instructions and Reports
- Generate:
  - BOM by part and color,
  - missing inventory list,
  - layer-by-layer placement instructions,
  - top/front/side visualization aids.
- Export targets:
  - machine-readable JSON,
  - CSV summaries,
  - printable guide assets.

## Phase 7: Validation Loop
- Evaluate with 3-5 samples.
- Track:
  - reconstruction success rate,
  - decomposition validity rate,
  - stability pass rate,
  - brick shortfall rate.
- Feed back into:
  - photo acceptance thresholds,
  - decomposition objective weights,
  - stability heuristics.

