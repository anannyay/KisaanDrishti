"""Validate a CropPulse longitudinal image manifest before training."""
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

REQUIRED = {
    "observation_id", "plant_id", "plot_id", "crop", "captured_at", "image_path",
    "canopy_coverage_pct", "green_pct", "yellowing_pct", "browning_pct",
}
PERCENT_COLUMNS = ["canopy_coverage_pct", "green_pct", "yellowing_pct", "browning_pct"]


def validate(path: Path, require_images: bool = True) -> list[str]:
    frame = pd.read_csv(path)
    errors: list[str] = []
    missing = sorted(REQUIRED - set(frame.columns))
    if missing:
        return [f"Missing columns: {', '.join(missing)}"]
    if frame["observation_id"].duplicated().any():
        errors.append("observation_id values must be unique")
    parsed = pd.to_datetime(frame["captured_at"], errors="coerce", utc=True)
    if parsed.isna().any():
        errors.append(f"Invalid captured_at values: {int(parsed.isna().sum())}")
    for column in PERCENT_COLUMNS:
        numeric = pd.to_numeric(frame[column], errors="coerce")
        invalid = numeric.notna() & ~numeric.between(0, 100)
        if invalid.any():
            errors.append(f"{column} has {int(invalid.sum())} values outside 0..100")
    counts = frame.groupby("plant_id").size()
    if (counts < 3).any():
        errors.append(f"{int((counts < 3).sum())} plants have fewer than 3 observations")
    if require_images:
        root = path.parent
        absent = [item for item in frame["image_path"].dropna() if not (root / str(item)).is_file()]
        if absent:
            errors.append(f"Missing image files: {len(absent)}")
    ordered = frame.assign(_time=parsed).sort_values(["plant_id", "_time"])
    if ordered.duplicated(["plant_id", "_time"]).any():
        errors.append("A plant cannot have two observations at the same timestamp")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--skip-images", action="store_true")
    args = parser.parse_args()
    errors = validate(args.manifest, not args.skip_images)
    if errors:
        print("Dataset invalid:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Dataset valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
