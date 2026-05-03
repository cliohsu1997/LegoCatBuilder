from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import time
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run Phase 2 COLMAP reconstruction from accepted photo_set.",
    )
    parser.add_argument(
        "--photo-set",
        required=True,
        help="Path to photo_set JSON.",
    )
    parser.add_argument(
        "--phase1-report",
        required=True,
        help="Path to Phase 1 acceptance report JSON.",
    )
    parser.add_argument(
        "--workspace-dir",
        required=True,
        help="Workspace root for this reconstruction run.",
    )
    parser.add_argument(
        "--summary-out",
        required=True,
        help="Path to write reconstruction summary JSON.",
    )
    parser.add_argument(
        "--repo-root",
        default="..",
        help="Repository root used to resolve relative image paths.",
    )
    parser.add_argument(
        "--colmap-bat",
        default=os.environ.get(
            "COLMAP_BAT",
            r"C:\Tools\COLMAP\COLMAP.bat",
        ),
        help="Path to COLMAP.bat.",
    )
    parser.add_argument(
        "--quality",
        default="medium",
        help="COLMAP automatic_reconstructor quality preset.",
    )
    parser.add_argument(
        "--gpu",
        default="0",
        help="COLMAP --gpu value.",
    )
    return parser.parse_args()


def load_json(
    path: Path,
) -> dict[str, Any]:
    with path.open(
        "r",
        encoding="utf-8",
    ) as file:
        data = json.load(
            file,
        )
    if not isinstance(
        data,
        dict,
    ):
        raise ValueError(f"JSON must be object: {path}")
    return data


def stage_images(
    photo_set: dict[str, Any],
    repo_root: Path,
    image_dir: Path,
) -> list[dict[str, str]]:
    views = photo_set.get(
        "views",
        [],
    )
    if not isinstance(
        views,
        list,
    ):
        raise ValueError("'views' must be an array in photo_set.")

    image_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    staged: list[dict[str, str]] = []
    for idx, view in enumerate(views):
        view_type = str(
            view.get(
                "view_type",
                f"view_{idx}",
            ),
        )
        rel_path = str(
            view.get(
                "path",
                "",
            ),
        ).strip()
        if rel_path == "":
            raise ValueError(f"Missing view path for {view_type}.")

        src = (repo_root / rel_path).resolve()
        if not src.exists():
            raise FileNotFoundError(f"Source image not found: {src}")

        suffix = src.suffix.lower()
        if suffix == "":
            suffix = ".png"
        dst_name = f"{idx:02d}_{view_type}{suffix}"
        dst = image_dir / dst_name
        shutil.copy2(
            src,
            dst,
        )
        staged.append(
            {
                "view_type": view_type,
                "source_path": str(src),
                "staged_path": str(dst),
            },
        )
    return staged


def run_colmap(
    colmap_bat: Path,
    image_dir: Path,
    workspace_colmap: Path,
    quality: str,
    gpu: str,
    log_path: Path,
) -> tuple[list[str], float]:
    argv = [
        str(colmap_bat),
        "automatic_reconstructor",
        "--workspace_path",
        str(workspace_colmap),
        "--image_path",
        str(image_dir),
        "--quality",
        quality,
        "--gpu",
        gpu,
    ]

    log_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )
    started = time.time()
    with log_path.open(
        "w",
        encoding="utf-8",
    ) as log_file:
        log_file.write("COMMAND:\n")
        log_file.write(" ".join(argv))
        log_file.write("\n\n")
        proc = subprocess.run(
            argv,
            stdout=log_file,
            stderr=subprocess.STDOUT,
            text=True,
        )
    elapsed_s = time.time() - started
    if proc.returncode != 0:
        raise RuntimeError(
            f"COLMAP failed (exit={proc.returncode}). See log: {log_path}",
        )
    return argv, elapsed_s


def main() -> None:
    args = parse_args()

    photo_set_path = Path(
        args.photo_set,
    )
    phase1_report_path = Path(
        args.phase1_report,
    )
    workspace_dir = Path(
        args.workspace_dir,
    ).resolve()
    summary_out = Path(
        args.summary_out,
    ).resolve()
    repo_root = Path(
        args.repo_root,
    ).resolve()
    colmap_bat = Path(
        args.colmap_bat,
    )

    if not colmap_bat.exists():
        raise FileNotFoundError(f"COLMAP.bat not found: {colmap_bat}")

    photo_set = load_json(
        photo_set_path,
    )
    phase1 = load_json(
        phase1_report_path,
    )
    if not bool(
        phase1.get(
            "accepted",
            False,
        ),
    ):
        raise RuntimeError(
            "Phase 1 report is not accepted. Stop before reconstruction.",
        )

    if workspace_dir.exists():
        shutil.rmtree(
            workspace_dir,
        )
    image_dir = workspace_dir / "images"
    workspace_colmap = workspace_dir / "workspace"
    log_path = workspace_colmap / "logs" / "colmap_automatic_reconstructor.log"

    staged_views = stage_images(
        photo_set=photo_set,
        repo_root=repo_root,
        image_dir=image_dir,
    )

    argv, elapsed_s = run_colmap(
        colmap_bat=colmap_bat,
        image_dir=image_dir,
        workspace_colmap=workspace_colmap,
        quality=str(args.quality),
        gpu=str(args.gpu),
        log_path=log_path,
    )

    summary: dict[str, Any] = {
        "photo_set_id": str(
            photo_set.get(
                "photo_set_id",
                "",
            ),
        ),
        "phase1_accepted": True,
        "staged_image_count": len(staged_views),
        "staged_views": staged_views,
        "colmap_bat": str(colmap_bat),
        "workspace_dir": str(workspace_dir),
        "image_dir": str(image_dir),
        "colmap_workspace_dir": str(workspace_colmap),
        "argv": argv,
        "elapsed_s": float(elapsed_s),
        "log_path": str(log_path),
        "sparse_exists": (workspace_colmap / "sparse").exists(),
        "dense_exists": (workspace_colmap / "dense").exists(),
    }

    summary_out.parent.mkdir(
        parents=True,
        exist_ok=True,
    )
    with summary_out.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            summary,
            file,
            indent=2,
        )
        file.write("\n")

    print(
        json.dumps(
            summary,
            indent=2,
        ),
    )


if __name__ == "__main__":
    main()
