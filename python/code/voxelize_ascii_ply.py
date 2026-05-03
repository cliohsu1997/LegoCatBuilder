from __future__ import annotations

import argparse
import json
import struct
from dataclasses import dataclass
from pathlib import Path

import numpy as np


@dataclass(frozen=True)
class PlyPoints:
    vertices: np.ndarray


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Voxelize a PLY point cloud into coarse/fine occupancy grids.",
    )
    parser.add_argument(
        "--ply",
        required=True,
        help="Path to ASCII PLY with vertex x y z fields.",
    )
    parser.add_argument(
        "--coarse",
        type=int,
        default=64,
        help="Coarse voxel grid resolution (per axis).",
    )
    parser.add_argument(
        "--fine",
        type=int,
        default=128,
        help="Fine voxel grid resolution (per axis).",
    )
    parser.add_argument(
        "--out-dir",
        required=True,
        help="Directory to write .npy grids + metadata JSON.",
    )
    return parser.parse_args()


def _ply_dtype_and_skip(
    properties: list[tuple[str, str]],
) -> tuple[str, int, int, int]:
    # Returns struct format string for one vertex, byte size, and x/y/z indexes in fields list.
    fmt_parts: list[str] = []
    names: list[str] = []
    for dtype, name in properties:
        if dtype == "float":
            fmt_parts.append("f")
        elif dtype == "double":
            fmt_parts.append("d")
        elif dtype == "uchar" or dtype == "uint8":
            fmt_parts.append("B")
        elif dtype == "int" or dtype == "int32":
            fmt_parts.append("i")
        elif dtype == "uint" or dtype == "uint32":
            fmt_parts.append("I")
        else:
            raise ValueError(
                f"Unsupported PLY property type: {dtype} ({name})",
            )
        names.append(name)

    if "x" not in names or "y" not in names or "z" not in names:
        raise ValueError("PLY must include x,y,z vertex properties.")

    struct_fmt = "<" + "".join(fmt_parts)
    size = struct.calcsize(struct_fmt)
    xi = names.index("x")
    yi = names.index("y")
    zi = names.index("z")
    return struct_fmt, size, xi, yi, zi


def _read_ply_xyz(
    ply_path: Path,
) -> PlyPoints:
    data = ply_path.read_bytes()
    if not data.startswith(b"ply"):
        raise ValueError("Not a PLY file (missing 'ply' header).")

    end_token = b"end_header"
    header_end = data.find(end_token)
    if header_end < 0:
        raise ValueError("PLY missing end_header marker.")

    cursor = header_end + len(end_token)
    if cursor < len(data) and data[cursor : cursor + 1] == b"\r":
        cursor += 1
    if cursor < len(data) and data[cursor : cursor + 1] == b"\n":
        cursor += 1

    header = data[:header_end].decode(
        "utf-8",
        errors="replace",
    )
    body = data[cursor:]

    fmt_line = ""
    vertex_count = 0
    props: list[tuple[str, str]] = []
    for raw_line in header.splitlines():
        line = raw_line.strip()
        if line.startswith("format "):
            fmt_line = line
        elif line.startswith("element vertex "):
            vertex_count = int(line.split()[-1])
        elif line.startswith("property "):
            parts = line.split()
            if len(parts) < 3:
                continue
            dtype = parts[1]
            name = parts[2]
            props.append(
                (
                    dtype,
                    name,
                ),
            )

    if vertex_count <= 0:
        raise ValueError("Invalid vertex count in PLY header.")

    struct_fmt, vsize, xi, yi, zi = _ply_dtype_and_skip(
        properties=props,
    )

    if "binary_little_endian" in fmt_line:
        expected = vertex_count * vsize
        if len(body) < expected:
            raise ValueError("PLY body too small for declared vertices.")
        buf = body[:expected]
        verts = np.zeros(
            (vertex_count, 3),
            dtype=np.float32,
        )
        for i in range(vertex_count):
            off = i * vsize
            chunk = buf[off : off + vsize]
            fields = struct.unpack(
                struct_fmt,
                chunk,
            )
            verts[i, 0] = float(fields[xi])
            verts[i, 1] = float(fields[yi])
            verts[i, 2] = float(fields[zi])
        return PlyPoints(
            vertices=verts,
        )

    if "ascii" in fmt_line:
        text = body.decode(
            "utf-8",
            errors="replace",
        )
        lines = text.splitlines()
        names = [n for _, n in props]
        xi = names.index("x")
        yi = names.index("y")
        zi = names.index("z")
        verts_list: list[list[float]] = []
        for j in range(min(vertex_count, len(lines))):
            parts = lines[j].split()
            if len(parts) < len(names):
                continue
            verts_list.append(
                [
                    float(parts[xi]),
                    float(parts[yi]),
                    float(parts[zi]),
                ],
            )
        arr = np.array(
            verts_list,
            dtype=np.float32,
        )
        if arr.shape[0] == 0:
            raise ValueError("No vertices parsed from ASCII PLY body.")
        return PlyPoints(
            vertices=arr,
        )

    raise ValueError(
        f"Unsupported PLY format line: {fmt_line}",
    )


def _voxelize(
    points_xyz: np.ndarray,
    grid: int,
) -> tuple[np.ndarray, dict[str, float]]:
    mins = points_xyz.min(axis=0)
    maxs = points_xyz.max(axis=0)
    spans = np.maximum(
        maxs - mins,
        1e-6,
    )

    idx = np.floor(
        (points_xyz - mins)
        / spans
        * (grid - 1),
    ).astype(np.int32)
    idx = np.clip(
        idx,
        0,
        grid - 1,
    )

    occ = np.zeros(
        (
            grid,
            grid,
            grid,
        ),
        dtype=np.bool_,
    )
    occ[
        idx[:, 0],
        idx[:, 1],
        idx[:, 2],
    ] = True

    meta = {
        "min_x": float(mins[0]),
        "min_y": float(mins[1]),
        "min_z": float(mins[2]),
        "max_x": float(maxs[0]),
        "max_y": float(maxs[1]),
        "max_z": float(maxs[2]),
        "grid": int(grid),
        "occupied_voxels": int(np.count_nonzero(occ)),
    }
    return occ, meta


def main() -> None:
    args = parse_args()
    ply_path = Path(
        args.ply,
    )
    out_dir = Path(
        args.out_dir,
    )
    out_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    ply = _read_ply_xyz(
        ply_path=ply_path,
    )
    pts = ply.vertices

    coarse, coarse_meta = _voxelize(
        points_xyz=pts,
        grid=int(args.coarse),
    )
    fine, fine_meta = _voxelize(
        points_xyz=pts,
        grid=int(args.fine),
    )

    coarse_path = out_dir / "voxel_occ_coarse.npy"
    fine_path = out_dir / "voxel_occ_fine.npy"
    meta_path = out_dir / "voxel_meta.json"

    np.save(
        coarse_path,
        coarse,
        allow_pickle=False,
    )
    np.save(
        fine_path,
        fine,
        allow_pickle=False,
    )

    payload = {
        "source_ply": str(ply_path.resolve()),
        "coarse": coarse_meta,
        "fine": fine_meta,
        "arrays": {
            "coarse": str(coarse_path.resolve()),
            "fine": str(fine_path.resolve()),
        },
    }
    meta_path.write_text(
        json.dumps(
            payload,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
