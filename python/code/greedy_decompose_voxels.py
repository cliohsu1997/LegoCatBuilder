from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np


BRICKS = (
    ("3001", 2, 4),
    ("3003", 2, 2),
    ("3004", 1, 2),
    ("3005", 1, 1),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Greedy brick decomposition over a boolean voxel occupancy grid.",
    )
    parser.add_argument(
        "--occupancy-npy",
        required=True,
        help="Path to voxel occupancy .npy (bool).",
    )
    parser.add_argument(
        "--out",
        required=True,
        help="Output build_plan JSON path.",
    )
    parser.add_argument(
        "--mode",
        default="preview_mode",
        choices=("preview_mode", "build_mode"),
        help="Build plan mode.",
    )
    parser.add_argument(
        "--color",
        default="Tan",
        help="Brick color string for prototype output.",
    )
    return parser.parse_args()


def try_place_brick(
    occ: np.ndarray,
    x: int,
    y: int,
    z: int,
    sx: int,
    sy: int,
) -> bool:
    if (
        x + sx > occ.shape[0]
        or y + sy > occ.shape[1]
        or z + 1 > occ.shape[2]
    ):
        return False
    sub = occ[
        x : x + sx,
        y : y + sy,
        z : z + 1,
    ]
    return bool(np.all(sub))


def clear_brick(
    occ: np.ndarray,
    x: int,
    y: int,
    z: int,
    sx: int,
    sy: int,
) -> None:
    occ[
        x : x + sx,
        y : y + sy,
        z : z + 1,
    ] = False


def main() -> None:
    args = parse_args()
    occ = np.load(
        args.occupancy_npy,
        allow_pickle=False,
    )
    if occ.dtype != np.bool_:
        occ = occ.astype(np.bool_)

    remaining = int(np.count_nonzero(occ))
    placements: list[dict[str, Any]] = []

    layer = 0
    while remaining > 0:
        placed_this_pass = 0
        for z in range(occ.shape[2]):
            for x in range(occ.shape[0]):
                for y in range(occ.shape[1]):
                    if not occ[x, y, z]:
                        continue

                    for part_id, sx, sy in BRICKS:
                        if try_place_brick(
                            occ=occ,
                            x=x,
                            y=y,
                            z=z,
                            sx=sx,
                            sy=sy,
                        ):
                            orientation = (
                                "x_aligned"
                                if sx >= sy
                                else "y_aligned"
                            )
                            placements.append(
                                {
                                    "part_id": part_id,
                                    "color": str(args.color),
                                    "x": int(x),
                                    "y": int(y),
                                    "z": int(z),
                                    "orientation": orientation,
                                    "layer": int(layer),
                                },
                            )
                            clear_brick(
                                occ=occ,
                                x=x,
                                y=y,
                                z=z,
                                sx=sx,
                                sy=sy,
                            )
                            placed_this_pass += 1
                            break

        new_remaining = int(np.count_nonzero(occ))
        if placed_this_pass == 0:
            break
        remaining = new_remaining
        layer += 1

    build_plan = {
        "build_plan_id": "prototype_from_voxels",
        "mode": str(args.mode),
        "placements": placements,
    }

    out_path = Path(
        args.out,
    )
    out_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )
    out_path.write_text(
        json.dumps(
            build_plan,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
