from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from photo_metrics import compute_photo_metrics


REQUIRED_VIEWS = ("front", "side", "top")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate photo-set metadata for Phase 1 acceptability gate.",
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to photo_set JSON file.",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Path to write acceptance report JSON.",
    )
    parser.add_argument(
        "--min-width",
        type=int,
        default=1000,
        help="Minimum acceptable image width.",
    )
    parser.add_argument(
        "--min-height",
        type=int,
        default=800,
        help="Minimum acceptable image height.",
    )
    parser.add_argument(
        "--min-blur-score",
        type=float,
        default=100.0,
        help="Minimum acceptable blur score (higher is sharper).",
    )
    parser.add_argument(
        "--min-subject-coverage",
        type=float,
        default=0.35,
        help="Minimum subject coverage ratio in [0, 1].",
    )
    parser.add_argument(
        "--max-background-complexity",
        type=float,
        default=0.65,
        help="Maximum background complexity ratio in [0, 1].",
    )
    parser.add_argument(
        "--repo-root",
        default="..",
        help="Repository root used to resolve relative image paths in photo_set JSON.",
    )
    parser.add_argument(
        "--recompute-from-images",
        action="store_true",
        help="Recompute width/height/blur/coverage/background metrics from image files.",
    )
    parser.add_argument(
        "--write-photo-set",
        default="",
        help="Optional path to write updated photo_set JSON (only when --recompute-from-images).",
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
        raise ValueError("Input JSON must be an object.")
    return data


def validate_view(
    view: dict[str, Any],
    min_width: int,
    min_height: int,
    min_blur_score: float,
    min_subject_coverage: float,
    max_background_complexity: float,
) -> dict[str, Any]:
    reasons: list[str] = []
    view_type = str(
        view.get(
            "view_type",
            "",
        ),
    )

    width = int(
        view.get(
            "width",
            0,
        ),
    )
    height = int(
        view.get(
            "height",
            0,
        ),
    )
    blur_score = float(
        view.get(
            "blur_score",
            0.0,
        ),
    )
    subject_coverage = float(
        view.get(
            "subject_coverage_ratio",
            0.0,
        ),
    )
    background_complexity = float(
        view.get(
            "background_complexity",
            1.0,
        ),
    )

    if (
        width < min_width
        or height < min_height
    ):
        reasons.append(
            f"resolution_too_low: got {width}x{height}, need >= {min_width}x{min_height}",
        )
    if blur_score < min_blur_score:
        reasons.append(
            f"too_blurry: blur_score {blur_score:.2f} < {min_blur_score:.2f}",
        )
    if subject_coverage < min_subject_coverage:
        reasons.append(
            (
                "insufficient_subject_coverage: "
                f"{subject_coverage:.2f} < {min_subject_coverage:.2f}"
            ),
        )
    if background_complexity > max_background_complexity:
        reasons.append(
            (
                "background_too_complex: "
                f"{background_complexity:.2f} > {max_background_complexity:.2f}"
            ),
        )

    return {
        "view_type": view_type,
        "passed": len(reasons) == 0,
        "reasons": reasons,
    }


def build_recommendations(
    missing_views: list[str],
    per_view: list[dict[str, Any]],
) -> list[str]:
    recommendations: list[str] = []
    for view in missing_views:
        recommendations.append(
            f"Capture missing required view: {view}.",
        )

    for view_result in per_view:
        view_type = view_result["view_type"]
        for reason in view_result["reasons"]:
            if reason.startswith(
                "resolution_too_low",
            ):
                recommendations.append(
                    f"Retake {view_type} view at higher resolution.",
                )
            elif reason.startswith(
                "too_blurry",
            ):
                recommendations.append(
                    f"Retake {view_type} view with improved focus or less motion.",
                )
            elif reason.startswith(
                "insufficient_subject_coverage",
            ):
                recommendations.append(
                    f"Move camera closer or crop so the cat fills more of the {view_type} frame.",
                )
            elif reason.startswith(
                "background_too_complex",
            ):
                recommendations.append(
                    f"Use a simpler backdrop for the {view_type} view.",
                )

    return sorted(
        set(recommendations),
    )


def main() -> None:
    args = parse_args()
    input_path = Path(
        args.input,
    )
    output_path = Path(
        args.output,
    )
    repo_root = Path(
        args.repo_root,
    ).resolve()

    photo_set = load_json(
        input_path,
    )
    views = photo_set.get(
        "views",
        [],
    )
    if not isinstance(
        views,
        list,
    ):
        raise ValueError("'views' must be an array in input JSON.")

    if args.recompute_from_images:
        for item in views:
            rel = str(
                item.get(
                    "path",
                    "",
                ),
            )
            abs_path = (repo_root / rel).resolve()
            metrics = compute_photo_metrics(
                image_path=abs_path,
            )
            item["path"] = rel
            item["width"] = metrics.width
            item["height"] = metrics.height
            item["blur_score"] = metrics.blur_score
            item["subject_coverage_ratio"] = metrics.subject_coverage_ratio
            item["background_complexity"] = metrics.background_complexity

        if str(args.write_photo_set).strip() != "":
            out_photo_set = Path(
                args.write_photo_set,
            )
            out_photo_set.parent.mkdir(
                parents=True,
                exist_ok=True,
            )
            with out_photo_set.open(
                "w",
                encoding="utf-8",
            ) as file:
                json.dump(
                    photo_set,
                    file,
                    indent=2,
                )
                file.write("\n")

    available_views = {
        str(
            item.get(
                "view_type",
                "",
            ),
        )
        for item in views
    }
    missing_views = [
        view
        for view in REQUIRED_VIEWS
        if view not in available_views
    ]

    per_view = []
    for required_view in REQUIRED_VIEWS:
        matching = [
            item
            for item in views
            if item.get("view_type") == required_view
        ]
        if len(matching) == 0:
            continue
        per_view.append(
            validate_view(
                view=matching[0],
                min_width=args.min_width,
                min_height=args.min_height,
                min_blur_score=args.min_blur_score,
                min_subject_coverage=args.min_subject_coverage,
                max_background_complexity=args.max_background_complexity,
            ),
        )

    accepted = (
        len(missing_views) == 0
        and all(
            item["passed"]
            for item in per_view
        )
    )
    recommendations = build_recommendations(
        missing_views=missing_views,
        per_view=per_view,
    )

    report = {
        "photo_set_id": str(
            photo_set.get(
                "photo_set_id",
                "",
            ),
        ),
        "accepted": accepted,
        "missing_views": missing_views,
        "per_view": per_view,
        "recommendations": recommendations,
    }

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )
    with output_path.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            report,
            file,
            indent=2,
        )
        file.write("\n")

    print(
        json.dumps(
            report,
            indent=2,
        ),
    )


if __name__ == "__main__":
    main()
