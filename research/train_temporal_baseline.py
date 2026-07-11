"""Train an honest same-plant next-observation baseline from measured features.

The split is grouped by plant_id, preventing observations from the same plant
from leaking into both train and test sets.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import GroupShuffleSplit

FEATURES = ["canopy_coverage_pct", "green_pct", "yellowing_pct", "browning_pct", "days_since_previous"]


def sequences(frame: pd.DataFrame) -> pd.DataFrame:
    frame = frame.copy()
    frame["captured_at"] = pd.to_datetime(frame["captured_at"], utc=True)
    frame = frame.sort_values(["plant_id", "captured_at"])
    frame["days_since_previous"] = frame.groupby("plant_id")["captured_at"].diff().dt.total_seconds().div(86400)
    frame["target_next_health"] = frame.groupby("plant_id")["expert_health_score"].shift(-1)
    return frame.dropna(subset=FEATURES + ["target_next_health"])


def train(manifest: Path, output: Path) -> dict[str, float | int]:
    data = sequences(pd.read_csv(manifest))
    if len(data) < 20 or data["plant_id"].nunique() < 5:
        raise ValueError("Need at least 20 usable transitions from at least 5 plants")
    split = GroupShuffleSplit(n_splits=1, test_size=.25, random_state=42)
    train_idx, test_idx = next(split.split(data, groups=data["plant_id"]))
    train_set, test_set = data.iloc[train_idx], data.iloc[test_idx]
    model = RandomForestRegressor(n_estimators=250, min_samples_leaf=2, random_state=42, n_jobs=1)
    model.fit(train_set[FEATURES], train_set["target_next_health"])
    prediction = model.predict(test_set[FEATURES])
    metrics = {"test_mae": round(float(mean_absolute_error(test_set["target_next_health"], prediction)), 3),
               "test_r2": round(float(r2_score(test_set["target_next_health"], prediction)), 3),
               "train_rows": int(len(train_set)), "test_rows": int(len(test_set)),
               "train_plants": int(train_set["plant_id"].nunique()), "test_plants": int(test_set["plant_id"].nunique())}
    output.mkdir(parents=True, exist_ok=True)
    joblib.dump({"model": model, "features": FEATURES}, output / "temporal_baseline.joblib")
    (output / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    return metrics


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--output", type=Path, default=Path("artifacts"))
    args = parser.parse_args()
    print(json.dumps(train(args.manifest, args.output), indent=2))


if __name__ == "__main__":
    main()
