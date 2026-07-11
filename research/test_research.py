import unittest
from pathlib import Path

import numpy as np
import pandas as pd

from train_temporal_baseline import train
from validate_dataset import validate


class ResearchTests(unittest.TestCase):
    def make_data(self, path: Path) -> Path:
        rng = np.random.default_rng(4); rows = []
        for plant in range(10):
            for day in range(7):
                yellow = plant + day * .7
                rows.append({"observation_id":f"{plant}-{day}","plant_id":f"P-{plant}","plot_id":f"plot-{plant%3}","crop":"turmeric","captured_at":f"2026-07-{day+1:02d}T08:00:00Z","image_path":f"x/{plant}-{day}.jpg","canopy_coverage_pct":35+day,"green_pct":75-yellow,"yellowing_pct":yellow,"browning_pct":plant*.2,"expert_health_score":90-yellow+rng.normal(0,.5)})
        target = path / "manifest.csv"; pd.DataFrame(rows).to_csv(target, index=False); return target

    def test_validator_and_grouped_training(self):
        root = Path(__file__).parent
        manifest = self.make_data(root)
        self.assertEqual(validate(manifest, require_images=False), [])
        metrics = train(manifest, root)
        self.assertGreater(metrics["train_plants"], 0)
        self.assertGreater(metrics["test_plants"], 0)
        self.assertTrue((root / "temporal_baseline.joblib").is_file())


if __name__ == "__main__":
    unittest.main()
