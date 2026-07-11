# CropPulse — technical project report

## Problem

Single-image disease classifiers do not describe whether a plant is developing normally or responding to an intervention. CropPulse records repeated plant observations and turns visible canopy signals into a longitudinal health passport.

## Working scope

The delivered system measures visible RGB signals: detected canopy coverage, greenness, yellowing, browning, image sharpness and exposure. It stores observations against a plant, presents trends, records interventions and prompts a follow-up scan.

It deliberately does not infer a disease, nutrient deficiency, water status or yield from colour alone.

## System components

1. Expo/React Native Android application
2. FastAPI image-analysis service
3. OpenCV/Numpy transparent segmentation baseline
4. AsyncStorage observation and intervention persistence
5. Docker deployment configuration
6. Automated synthetic-image regression tests

## Analysis method

The engine corrects EXIF orientation, limits resolution, checks Laplacian sharpness and brightness, then forms a conservative plant mask using HSV vegetation hues and excess-green evidence. Yellow/brown candidate tissue is retained only near green seed regions. Morphological opening, closing and connected-component filtering reduce background contamination.

Measurements are reported as percentages of the detected canopy. A versioned visual-health index is supplied for interface demonstration; individual evidence values must remain visible because the index is not a clinical or agronomic diagnosis.

## Validation already included

- A green synthetic canopy must score above a yellow synthetic canopy.
- A textureless/blurred input must trigger a quality warning.
- An encoded JPEG must complete the full decode-to-measurement pipeline.

## Field-validation protocol

For a formal evaluation, collect repeated images of at least 30 plants under multiple phones and lighting conditions. Photograph a colour card and scale marker in a subset. Compare segmentation with manually traced canopy masks using Dice/IoU; compare yellow/brown fractions with manual pixel annotations using MAE; report repeatability under recapture and performance on an unseen phone/farm.

Interventions should be logged prospectively. CropPulse may describe measured visual change after an intervention, but causality should not be claimed without a controlled experiment.

## Upgrade path

Replace `segment_plant` with a field-trained segmentation model, export it to ONNX/TFLite and preserve the existing versioned response schema. Add thermal and soil-moisture signals only as separately labelled measurements. A temporal model should be trained only after enough same-plant observations exist.
