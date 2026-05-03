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
        description="Run COLMAP automatic_reconstructor on an image folder.",
    )
    parser.add_argument(
        "--colmap-bat",
        default=os.environ.get(
            "COLMAP_BAT",
            r"C:\Tools\COLMAP\COLMAP.bat",
        ),
        help="Path to COLMAP.bat (Windows). Override with COLMAP_BAT env var.",
    )
    parser.add_argument(
        "--image-dir",
        required=True,
        help="Folder containing input images.",
    )
    parser.add_argument(
        "--workspace-dir",
        required=True,
        help="COLMAP workspace output folder (will be created).",
    )
    parser.add_argument(
        "--quality",
        default="medium",
        help="COLMAP automatic_reconstructor quality preset.",
    )
    parser.add_argument(
        "--gpu",
        default="0",
        help="COLMAP --gpu flag (0 disables GPU path in many builds).",
    )
    parser.add_argument(
        "--summary-out",
        required=True,
        help="Path to write a JSON summary of the run.",
    )
    return parser.parse_args()


def run_cmd(
    argv: list[str],
    cwd: Path,
    log_path: Path,
) -> None:
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
            cwd=str(cwd),
            stdout=log_file,
            stderr=subprocess.STDOUT,
            text=True,
        )
    elapsed_s = time.time() - started
    if proc.returncode != 0:
        raise RuntimeError(
            f"Command failed (exit={proc.returncode}) after {elapsed_s:.1f}s. See log: {log_path}",
        )


def main() -> None:
    args = parse_args()
    colmap_bat = Path(
        args.colmap_bat,
    )
    image_dir = Path(
        args.image_dir,
    ).resolve()
    workspace_dir = Path(
        args.workspace_dir,
    ).resolve()
    summary_out = Path(
        args.summary_out,
    ).resolve()

    if not colmap_bat.exists():
        raise FileNotFoundError(
            f"COLMAP.bat not found at: {colmap_bat}",
        )
    if not image_dir.exists():
        raise FileNotFoundError(
            f"image-dir not found: {image_dir}",
        )

    if workspace_dir.exists():
        shutil.rmtree(
            workspace_dir,
        )
    workspace_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    argv = [
        str(colmap_bat),
        "automatic_reconstructor",
        "--workspace_path",
        str(workspace_dir),
        "--image_path",
        str(image_dir),
        "--quality",
        str(args.quality),
        "--gpu",
        str(args.gpu),
    ]

    log_path = workspace_dir / "logs" / "colmap_automatic_reconstructor.log"
    started = time.time()
    run_cmd(
        argv=argv,
        cwd=workspace_dir.parent,
        log_path=log_path,
    )
    elapsed_s = time.time() - started

    summary: dict[str, Any] = {
        "colmap_bat": str(colmap_bat),
        "image_dir": str(image_dir),
        "workspace_dir": str(workspace_dir),
        "argv": argv,
        "elapsed_s": float(elapsed_s),
        "log_path": str(log_path),
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


if __name__ == "__main__":
    main()
