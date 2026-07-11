# CropPulse RGB baseline model card

## Trained classifier: `iari-wheat-cnn-v1`

This compact CNN distinguishes healthy, leaf-rust and nitrogen-deficient wheat imagery from the IARI field dataset. It achieved 90.32% accuracy and 0.8839 macro-F1 on the retained test split after exact-duplicate removal. The confusion matrix was `[[116,0,2],[3,51,0],[16,0,29]]` in alphabetical class order: healthy, leaf_rust, nitrogen_deficient.

The model is scoped to wheat leaves captured at the booting stage. Nitrogen deficiency had the lowest recall and may be confused with healthy leaves. Predictions on other crops, stages, farms or phone conditions are out of distribution.

## Version

`rgb-baseline-1`

## Intended use

Measure visible plant-colour and image-quality signals for longitudinal monitoring and prototype evaluation.

## Not intended for

- Disease diagnosis
- Fertilizer or pesticide recommendation
- Nutrient-deficiency diagnosis
- Irrigation prescription
- Yield prediction
- Autonomous farm decisions

## Inputs and outputs

Input: JPEG/PNG RGB plant image. Output: image quality, canopy coverage, green/yellow/brown fractions, a versioned visual score, confidence proxy and evidence text.

## Known limitations

Background vegetation, coloured soil, mulch, flowers, strong colour casts and mixed plants can affect the mask. The confidence value reflects visible mask coverage, not medical-style diagnostic certainty. RGB colour cannot reliably determine the underlying cause of stress.

## Human oversight

The interface must show measurements and the non-diagnostic disclaimer. Agronomic decisions require field inspection or expert advice. Low-quality images should be recaptured.
