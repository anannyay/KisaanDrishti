import unittest
from io import BytesIO

import cv2
import numpy as np
from PIL import Image

from croppulse_analysis import analyze_bytes, assess_quality, measure, segment_plant
from wheat_model import predict_wheat


class AnalysisTests(unittest.TestCase):
    def test_green_canopy_scores_higher_than_yellow(self):
        green = np.full((240, 320, 3), 245, np.uint8)
        yellow = green.copy()
        cv2.ellipse(green, (160, 120), (95, 70), 0, 0, 360, (35, 165, 45), -1)
        cv2.ellipse(yellow, (160, 120), (95, 70), 0, 0, 360, (45, 195, 220), -1)
        gm, ym = segment_plant(green), segment_plant(yellow)
        self.assertGreater(measure(green, gm).visual_health_score, measure(yellow, ym).visual_health_score)

    def test_blur_warning(self):
        flat = np.full((200, 200, 3), 120, np.uint8)
        self.assertFalse(assess_quality(flat).acceptable)
        self.assertTrue(any("blurred" in x for x in assess_quality(flat).warnings))

    def test_encoded_image_end_to_end(self):
        bgr = np.full((250, 250, 3), 240, np.uint8)
        cv2.rectangle(bgr, (45, 45), (205, 205), (30, 150, 40), -1)
        rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
        out = BytesIO(); Image.fromarray(rgb).save(out, format="JPEG", quality=95)
        result = analyze_bytes(out.getvalue())
        self.assertEqual(result["version"], "rgb-baseline-1")
        self.assertGreater(result["metrics"]["green_pct"], 50)

    def test_trained_wheat_model_loads(self):
        bgr = np.full((250, 250, 3), 240, np.uint8)
        cv2.rectangle(bgr, (45, 45), (205, 205), (30, 150, 40), -1)
        out = BytesIO(); Image.fromarray(cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)).save(out, format="JPEG")
        result = predict_wheat(out.getvalue())
        self.assertIn(result["label"], {"healthy", "leaf_rust", "nitrogen_deficient"})
        self.assertAlmostEqual(sum(result["probabilities"].values()), 1.0, places=3)


if __name__ == "__main__":
    unittest.main()
