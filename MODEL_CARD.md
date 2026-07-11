# CropPulse RGB baseline model card

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
