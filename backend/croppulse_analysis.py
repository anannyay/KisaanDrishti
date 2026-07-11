"""Deterministic RGB crop-health measurements for the CropPulse MVP.

This is a transparent baseline, not a disease diagnostic model. It measures
visible canopy coverage, greenness, yellowing, browning, blur and exposure.
The functions are isolated so a learned segmentation model can replace
``segment_plant`` without changing the mobile API.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from io import BytesIO
from typing import Any

import cv2
import numpy as np
from PIL import Image, ImageOps


@dataclass(frozen=True)
class Quality:
    acceptable: bool
    blur_score: float
    brightness: float
    warnings: list[str]


@dataclass(frozen=True)
class Metrics:
    canopy_coverage_pct: float
    green_pct: float
    yellowing_pct: float
    browning_pct: float
    visual_health_score: int
    confidence: float


def decode_image(payload: bytes, max_side: int = 1600) -> np.ndarray:
    if not payload:
        raise ValueError("Empty image payload")
    try:
        pil = ImageOps.exif_transpose(Image.open(BytesIO(payload))).convert("RGB")
    except Exception as exc:
        raise ValueError("Unsupported or corrupt image") from exc
    pil.thumbnail((max_side, max_side))
    return cv2.cvtColor(np.asarray(pil), cv2.COLOR_RGB2BGR)


def assess_quality(bgr: np.ndarray) -> Quality:
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    blur = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    brightness = float(gray.mean())
    warnings: list[str] = []
    if blur < 55:
        warnings.append("Image is blurred; hold the phone steady and move closer.")
    if brightness < 45:
        warnings.append("Image is too dark; move into even daylight.")
    elif brightness > 225:
        warnings.append("Image is overexposed; avoid glare and direct harsh sunlight.")
    return Quality(not warnings, round(blur, 1), round(brightness, 1), warnings)


def segment_plant(bgr: np.ndarray) -> np.ndarray:
    """Return a conservative visible-vegetation mask.

    Combines HSV vegetation hues with excess-green evidence. Morphology removes
    isolated background pixels while retaining yellow/brown leaf tissue adjacent
    to green canopy regions.
    """
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB).astype(np.int16)
    r, g, b = cv2.split(rgb)
    exg = 2 * g - r - b
    green = ((hsv[..., 0] >= 25) & (hsv[..., 0] <= 100) & (hsv[..., 1] >= 35)) | (exg > 18)
    stressed = (hsv[..., 0] >= 5) & (hsv[..., 0] < 35) & (hsv[..., 1] >= 35) & (hsv[..., 2] >= 35)
    seed = green.astype(np.uint8) * 255
    nearby = cv2.dilate(seed, np.ones((19, 19), np.uint8), iterations=2) > 0
    mask = (green | (stressed & nearby)).astype(np.uint8) * 255
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((11, 11), np.uint8))
    count, labels, stats, _ = cv2.connectedComponentsWithStats(mask)
    if count <= 1:
        return mask.astype(bool)
    min_area = max(80, int(mask.size * 0.0008))
    keep = np.zeros_like(mask)
    for idx in range(1, count):
        if stats[idx, cv2.CC_STAT_AREA] >= min_area:
            keep[labels == idx] = 255
    return keep.astype(bool)


def measure(bgr: np.ndarray, mask: np.ndarray) -> Metrics:
    pixels = int(mask.sum())
    if pixels < max(250, int(mask.size * 0.005)):
        raise ValueError("No sufficiently large plant canopy was found")
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)
    green = mask & (h >= 30) & (h <= 95) & (s >= 30)
    yellow = mask & (h >= 18) & (h < 35) & (s >= 35) & (v >= 55)
    brown = mask & (h >= 3) & (h < 22) & (s >= 45) & (v < 190)
    pct = lambda x: round(float(x.sum()) * 100.0 / pixels, 1)
    green_pct, yellow_pct, brown_pct = pct(green), pct(yellow), pct(brown)
    coverage = round(pixels * 100.0 / mask.size, 1)
    score = int(np.clip(round(35 + 0.65 * green_pct - 0.55 * yellow_pct - 0.75 * brown_pct), 0, 100))
    confidence = round(float(np.clip(0.55 + coverage / 160, 0.55, 0.96)), 2)
    return Metrics(coverage, green_pct, yellow_pct, brown_pct, score, confidence)


def analyze_bytes(payload: bytes) -> dict[str, Any]:
    bgr = decode_image(payload)
    quality = assess_quality(bgr)
    mask = segment_plant(bgr)
    metrics = measure(bgr, mask)
    evidence: list[str] = []
    if metrics.yellowing_pct >= 12:
        evidence.append("Visible yellow tissue is elevated within the detected canopy.")
    if metrics.browning_pct >= 8:
        evidence.append("Visible brown tissue is elevated within the detected canopy.")
    if metrics.green_pct >= 65:
        evidence.append("Most detected canopy tissue is visibly green.")
    if not evidence:
        evidence.append("No dominant colour stress signal was measured in this observation.")
    return {"version": "rgb-baseline-1", "quality": asdict(quality), "metrics": asdict(metrics), "evidence": evidence,
            "disclaimer": "Visual measurements only; not a disease or nutrient diagnosis."}
