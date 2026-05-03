# Python Run Guide

Run scripts from `python/` with Poetry.

## Phase 1 Validator

```bash
poetry run python code/phase1_validate_photo_set.py --input ../inputs/photosets/thu_mvs_cat_selected_views.photo_set.json --output ../outputs/reports/thu_mvs_cat_phase1_acceptance_report.json
```

## Phase 2 Reconstruction (COLMAP)

```bash
poetry run python code/phase2_reconstruct_from_photo_set.py --photo-set ../inputs/photosets/thu_mvs_cat_selected_views.photo_set.json --phase1-report ../outputs/reports/thu_mvs_cat_phase1_acceptance_report.json --workspace-dir ../artifacts/reconstruction/thu_mvs_cat_phase2 --summary-out ../outputs/reports/thu_mvs_cat_phase2_reconstruction_summary.json
```

## Video to photo set (for future captures)

Use a **static subject** and stable camera orbit; moving subjects break multi-view SfM.

```bash
poetry run python code/video_to_photo_set.py --video-path ../data/raw/cat_video/your_video.mp4 --frames-dir ../data/raw/cat_video/frames_sampled --photo-set-out ../inputs/photosets/your_video.photo_set.json --photo-set-id your_video --repo-root .. --max-frames 60
```

## Visualization Helpers

Use a workspace that contains a finished sparse model under `workspace/sparse/0/` (for example the 60-image `thu_mvs_cat_full` run). The three-view `thu_mvs_cat_phase2` run often has no `points3D.bin`, so the COLMAP GUI would look empty unless you import a valid model.

Launch COLMAP GUI with automatic model import (`--import_path` + optional database and images):

```bash
poetry run python code/visualize_reconstruction.py --workspace-dir ../artifacts/reconstruction/thu_mvs_cat_full --launch-gui
```

Export sparse model to PLY (if model exists) and open with default viewer:

```bash
poetry run python code/visualize_reconstruction.py --workspace-dir ../artifacts/reconstruction/thu_mvs_cat_full --export-ply --open-ply
```

Launch GUI without loading a model (blank viewer):

```bash
poetry run python code/visualize_reconstruction.py --workspace-dir ../artifacts/reconstruction/thu_mvs_cat_full --launch-gui --no-auto-import
```
