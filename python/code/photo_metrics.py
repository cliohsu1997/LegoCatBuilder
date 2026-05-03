from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
from PIL import Image


@dataclass(frozen=True)
class PhotoMetrics:
    width: int
    height: int
    blur_score: float
    subject_coverage_ratio: float
    background_complexity: float


def _to_gray_u8(
    rgb: np.ndarray,
) -> np.ndarray:
    # ITU-R BT.601 luma, uint8
    r = rgb[..., 0].astype(np.float32)
    g = rgb[..., 1].astype(np.float32)
    b = rgb[..., 2].astype(np.float32)
    y = (
        0.299 * r
        + 0.587 * g
        + 0.114 * b
    )
    return np.clip(y, 0.0, 255.0).astype(np.uint8)


def _laplacian_variance_u8(
    gray_u8: np.ndarray,
) -> float:
    gray = gray_u8.astype(np.float32)
    lap = (
        -4.0 * gray
        + np.roll(gray, 1, axis=0)
        + np.roll(gray, -1, axis=0)
        + np.roll(gray, 1, axis=1)
        + np.roll(gray, -1, axis=1)
    )
    return float(np.var(lap))


def _otsu_threshold_u8(
    gray_u8: np.ndarray,
) -> int:
    hist = np.bincount(
        gray_u8.reshape(-1),
        minlength=256,
    ).astype(np.float64)
    total = gray_u8.size
    if total <= 0:
        return 0

    omega = np.cumsum(hist)
    mu = np.cumsum(hist * np.arange(256))
    mu_t = mu[-1]
    eps = 1e-12

    best_t = 0
    best_val = -1.0
    for t in range(256):
        w0 = omega[t]
        w1 = omega[-1] - omega[t]
        if w0 <= eps or w1 <= eps:
            continue
        m0 = mu[t] / w0
        m1 = (mu_t - mu[t]) / w1
        diff = m0 - m1
        between = w0 * w1 * (diff * diff)
        if between > best_val:
            best_val = between
            best_t = t

    return int(best_t)


def compute_photo_metrics(
    image_path: Path,
) -> PhotoMetrics:
    with Image.open(image_path) as image:
        rgb = np.array(image.convert("RGB"))

    height, width, _ = rgb.shape
    gray = _to_gray_u8(rgb)

    blur_score = _laplacian_variance_u8(gray)

    # Studio-style captures often have large near-black background regions.
    # Otsu can split *within* the subject (fur texture), producing tiny "subject"
    # masks. For Phase-1 gating, prefer a dark-background separation heuristic.
    bg_level = float(np.quantile(gray.astype(np.float32), 0.05))
    bg_level_u8 = int(np.clip(bg_level, 0.0, 255.0))
    margin = 12
    subject_mask = gray > (bg_level_u8 + margin)
    if float(np.mean(subject_mask)) < 0.03:
        thr = _otsu_threshold_u8(gray)
        subject_mask = gray >= thr

    subject_coverage_ratio = float(np.mean(subject_mask))

    # Heuristic: treat very dark pixels as background for complexity scoring.
    bg_mask = gray <= bg_level_u8 + 2
    if float(np.mean(bg_mask)) < 0.05:
        bg_mask = gray <= int(0.05 * 255)

    bg = gray[bg_mask]
    if bg.size < 32:
        background_complexity = 0.0
    else:
        # Use local edge energy on the full image, evaluated on background pixels.
        lap = np.zeros_like(gray, dtype=np.float32)
        g = gray.astype(np.float32)
        lap[1:-1, 1:-1] = (
            -4.0 * g[1:-1, 1:-1]
            + g[0:-2, 1:-1]
            + g[2:, 1:-1]
            + g[1:-1, 0:-2]
            + g[1:-1, 2:]
        )
        lap_mag = lap * lap
        bg_edges = float(
            np.mean(lap_mag[bg_mask]),
        )
        background_complexity = float(
            np.tanh(bg_edges / 900.0),
        )

    return PhotoMetrics(
        width=int(width),
        height=int(height),
        blur_score=float(blur_score),
        subject_coverage_ratio=float(subject_coverage_ratio),
        background_complexity=float(background_complexity),
    )
