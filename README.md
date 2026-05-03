# LEGO Cat Builder

This project converts cat photos into a 3D LEGO build plan that is both visually faithful and physically buildable with an available brick inventory.

## Core Targets
- Reconstruct a canonical 3D model from `front + side + top` photos.
- Decompose that model into available LEGO bricks.
- Produce complete build instructions and bill of materials (BOM).

## 3D Pipeline Phases
1. Photo acceptability gate (quality and view completeness).
2. Multi-view 3D reconstruction.
3. Voxelization and canonical model generation.
4. Inventory-constrained brick decomposition.
5. Buildability and stability validation.
6. BOM and instruction generation.
7. Benchmarking and iterative tuning.

## Reference Implementations
- [COLMAP](https://github.com/colmap/colmap) for multi-view reconstruction.
- [brickalize](https://github.com/CreativeMindstorms/brickalize) for voxel-to-brick concepts.
- [LegoOptimizer](https://github.com/Chipdelmal/LegoOptimizer) for constrained optimization ideas.
- [StableLego](https://github.com/intelligent-control-lab/StableLego) for stability-analysis concepts.

## Workflow Tracking
High-level implementation phases are defined in:
- `IMPLEMENTATION_PLAN.md` (single source of truth for phase definitions and status)

This repository uses synchronized task files:
- `conversation_cursor/YYYYMM/YYYYMMDD/task_name.md` for technical decisions.
- `to-do/YYYYMM/YYYYMMDD/task_name.md` for remaining actionable work.
- `task_summary/YYYYMM/YYYYMMDD/task_name.md` for completed work and findings.

Core status files:
- `structure/latest.md`
- `progress/latest.md`

