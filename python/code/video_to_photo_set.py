from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import cv2

from photo_metrics import compute_photo_metrics


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extract frames from video and generate photo_set JSON.",
    )
    parser.add_argument(
        "--video-path",
        required=True,
        help="Path to input video file.",
    )
    parser.add_argument(
        "--frames-dir",
        required=True,
        help="Directory to write extracted frames.",
    )
    parser.add_argument(
        "--photo-set-out",
        required=True,
        help="Path to output photo_set JSON.",
    )
    parser.add_argument(
        "--photo-set-id",
        default="cat_video_frames",
        help="photo_set_id value for output JSON.",
    )
    parser.add_argument(
        "--repo-root",
        default="..",
        help="Repository root used to save relative paths in photo_set JSON.",
    )
    parser.add_argument(
        "--max-frames",
        type=int,
        default=60,
        help="Maximum number of frames to sample from the video.",
    )
    return parser.parse_args()


def pick_indices(
    total_frames: int,
    wanted: int,
) -> list[int]:
    if total_frames <= 0:
        return []
    if wanted >= total_frames:
        return list(range(total_frames))
    result: list[int] = []
    for i in range(wanted):
        idx = int(round(i * (total_frames - 1) / float(wanted - 1)))
        result.append(idx)
    return sorted(set(result))


def build_view_type(
    idx: int,
    front_idx: int,
    side_idx: int,
    top_idx: int,
) -> str:
    if idx == front_idx:
        return "front"
    if idx == side_idx:
        return "side"
    if idx == top_idx:
        return "top"
    return "aux"


def main() -> None:
    args = parse_args()
    video_path = Path(args.video_path).resolve()
    frames_dir = Path(args.frames_dir).resolve()
    photo_set_out = Path(args.photo_set_out).resolve()
    repo_root = Path(args.repo_root).resolve()

    if not video_path.exists():
        raise FileNotFoundError(f"Video not found: {video_path}")
    if args.max_frames < 3:
        raise ValueError("--max-frames must be >= 3")

    frames_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise RuntimeError(f"Failed to open video: {video_path}")

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    sample_indices = pick_indices(
        total_frames=total_frames,
        wanted=args.max_frames,
    )
    if len(sample_indices) < 3:
        raise RuntimeError("Not enough frames available to build required views.")

    front_i = sample_indices[0]
    side_i = sample_indices[len(sample_indices) // 2]
    top_i = sample_indices[-1]

    index_set = set(sample_indices)
    frame_id = 0
    written: list[Path] = []
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        if frame_id in index_set:
            out_path = frames_dir / f"frame_{frame_id:05d}.png"
            cv2.imwrite(
                str(out_path),
                frame,
            )
            written.append(out_path)
        frame_id += 1
    cap.release()

    views: list[dict[str, Any]] = []
    for frame_path in written:
        frame_num = int(frame_path.stem.split("_")[-1])
        view_type = build_view_type(
            idx=frame_num,
            front_idx=front_i,
            side_idx=side_i,
            top_idx=top_i,
        )
        metrics = compute_photo_metrics(
            image_path=frame_path,
        )
        rel = frame_path.resolve().relative_to(repo_root).as_posix()
        views.append(
            {
                "view_type": view_type,
                "path": rel,
                "width": metrics.width,
                "height": metrics.height,
                "blur_score": metrics.blur_score,
                "subject_coverage_ratio": metrics.subject_coverage_ratio,
                "background_complexity": metrics.background_complexity,
            },
        )

    photo_set = {
        "photo_set_id": args.photo_set_id,
        "capture_notes": f"Frames sampled from video: {video_path.name}",
        "views": views,
    }

    photo_set_out.parent.mkdir(
        parents=True,
        exist_ok=True,
    )
    with photo_set_out.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            photo_set,
            file,
            indent=2,
        )
        file.write("\n")

    print(
        json.dumps(
            {
                "video_path": str(video_path),
                "total_frames": total_frames,
                "sampled_frames": len(written),
                "frames_dir": str(frames_dir),
                "photo_set_out": str(photo_set_out),
                "required_views": {
                    "front_frame": int(front_i),
                    "side_frame": int(side_i),
                    "top_frame": int(top_i),
                },
            },
            indent=2,
        ),
    )


if __name__ == "__main__":
    main()
