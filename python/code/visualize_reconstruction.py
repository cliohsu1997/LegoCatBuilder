from __future__ import annotations

import argparse
import os
import subprocess
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Visualize COLMAP reconstruction by launching GUI and exporting PLY.",
    )
    parser.add_argument(
        "--workspace-dir",
        required=True,
        help="Reconstruction workspace root (contains workspace/sparse).",
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
        "--launch-gui",
        action="store_true",
        help="Launch COLMAP GUI.",
    )
    parser.add_argument(
        "--import-path",
        default="",
        help="COLMAP --import_path (sparse model folder, usually workspace/sparse/0).",
    )
    parser.add_argument(
        "--no-auto-import",
        action="store_true",
        help="Launch GUI without --import_path even if a sparse model exists.",
    )
    parser.add_argument(
        "--export-ply",
        action="store_true",
        help="Export sparse model to PLY if model files exist.",
    )
    parser.add_argument(
        "--open-ply",
        action="store_true",
        help="Open exported PLY with default OS application (Windows).",
    )
    parser.add_argument(
        "--ply-out",
        default="",
        help="Optional output PLY path. Default: <workspace-dir>/preview/sparse_points.ply",
    )
    return parser.parse_args()


def find_sparse_model_dir(
    workspace_dir: Path,
) -> Path:
    sparse_root = workspace_dir / "workspace" / "sparse"
    if not sparse_root.exists():
        raise FileNotFoundError(f"sparse folder not found: {sparse_root}")

    candidate_0 = sparse_root / "0"
    if candidate_0.exists():
        return candidate_0
    return sparse_root


def has_model_files(
    model_dir: Path,
) -> bool:
    return any(
        [
            (model_dir / "points3D.bin").exists(),
            (model_dir / "points3D.txt").exists(),
            (model_dir / "points3D.ply").exists(),
        ],
    )


def run_cmd(
    argv: list[str],
) -> None:
    proc = subprocess.run(
        argv,
        text=True,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"Command failed (exit={proc.returncode}): {' '.join(argv)}")


def main() -> None:
    args = parse_args()
    workspace_dir = Path(args.workspace_dir).resolve()
    colmap_bat = Path(args.colmap_bat)

    if not colmap_bat.exists():
        raise FileNotFoundError(f"COLMAP.bat not found: {colmap_bat}")
    if not workspace_dir.exists():
        raise FileNotFoundError(f"workspace-dir not found: {workspace_dir}")

    if not args.launch_gui and not args.export_ply and not args.open_ply:
        raise ValueError("Select at least one action: --launch-gui and/or --export-ply and/or --open-ply")

    if args.launch_gui:
        gui_argv: list[str] = [
            str(colmap_bat),
            "gui",
        ]
        import_path_str = str(args.import_path).strip()
        if import_path_str != "":
            gui_argv.extend(
                [
                    "--import_path",
                    str(Path(import_path_str).resolve()),
                ],
            )
        elif not args.no_auto_import:
            try:
                model_dir = find_sparse_model_dir(
                    workspace_dir=workspace_dir,
                )
            except FileNotFoundError:
                model_dir = None
            if (
                model_dir is not None
                and has_model_files(
                    model_dir=model_dir,
                )
            ):
                gui_argv.extend(
                    [
                        "--import_path",
                        str(model_dir),
                    ],
                )
                database_path = workspace_dir / "workspace" / "database.db"
                if database_path.exists():
                    gui_argv.extend(
                        [
                            "--database_path",
                            str(database_path.resolve()),
                        ],
                    )
                image_path = workspace_dir / "images"
                if image_path.exists():
                    gui_argv.extend(
                        [
                            "--image_path",
                            str(image_path.resolve()),
                        ],
                    )
                print(f"COLMAP GUI will import model: {model_dir}")
            else:
                print(
                    "No sparse model found for auto-import. "
                    "Use a full reconstruction workspace (e.g. thu_mvs_cat_full), "
                    "or pass --import-path explicitly, "
                    "or run dense multi-view reconstruction first.",
                )
        run_cmd(
            argv=gui_argv,
        )

    export_target: Path | None = None
    if args.export_ply or args.open_ply:
        model_dir = find_sparse_model_dir(
            workspace_dir=workspace_dir,
        )
        if not has_model_files(
            model_dir=model_dir,
        ):
            print("No sparse model files found yet. Need points3D.* in sparse model folder.")
            print(f"Checked: {model_dir}")
            return

        if str(args.ply_out).strip() != "":
            export_target = Path(args.ply_out).resolve()
        else:
            export_target = workspace_dir / "preview" / "sparse_points.ply"
        export_target.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        if args.export_ply:
            run_cmd(
                [
                    str(colmap_bat),
                    "model_converter",
                    "--input_path",
                    str(model_dir),
                    "--output_path",
                    str(export_target),
                    "--output_type",
                    "PLY",
                ],
            )
            print(f"Exported PLY: {export_target}")

    if args.open_ply:
        if export_target is None:
            if str(args.ply_out).strip() != "":
                export_target = Path(args.ply_out).resolve()
            else:
                export_target = workspace_dir / "preview" / "sparse_points.ply"
        if not export_target.exists():
            raise FileNotFoundError(
                f"PLY file not found to open: {export_target}. Run with --export-ply first.",
            )
        os.startfile(
            str(export_target),
        )
        print(f"Opened PLY with default app: {export_target}")


if __name__ == "__main__":
    main()
