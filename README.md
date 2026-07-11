# CropPulse

Android-first crop-health monitoring system with real RGB image measurements, longitudinal plant passports, intervention-response tracking and farmer-friendly field insights.

> **Status:** verified functional MVP and transparent RGB baseline. Field dataset collection and agronomic validation are the next research phase; CropPulse is not a disease diagnostic system.

## Run

### 1. Start the real image-analysis API

```bash
cd backend
python -m pip install -r requirements.txt
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

Alternatively: `docker compose up --build`.

### 2. Start the mobile app

```bash
copy .env.example .env
npm install
npm start
```

Scan the Expo QR code with Expo Go, or press `a` to open an Android emulator. Use `npm run typecheck` before committing.

Scan the Expo QR code with Expo Go, or press `a` for an Android emulator. For a physical phone, change `EXPO_PUBLIC_API_URL` to the computer's LAN IP and keep both devices on the same network.

## Implemented

- Native camera/gallery capture
- Actual RGB analysis: canopy coverage, visible greenness, yellowing, browning, blur and exposure
- Persistent observations and interventions with AsyncStorage
- Plant health passports and longitudinal charts
- Intervention-response views and field anomaly summaries
- English/Hindi/Marathi translation foundation
- FastAPI health-analysis service, Docker deployment and automated analysis tests
- Trained Indian wheat model for healthy, nitrogen-deficient and leaf-rust imagery

## Trained Indian wheat baseline

The bundled `iari-wheat-cnn-v1` model was trained on the public IARI Wheat Nitrogen Deficiency and Leaf Rust dataset (DOI `10.17632/th422bg4yd.1`). The preparation pipeline streamed nested archives, resized images to 224 px, removed 70 exact duplicates across splits and found no corrupt images.

- Unique images: 1,389
- Untouched test accuracy: **90.32%**
- Macro-F1: **0.8839**
- Classes: healthy, leaf rust, nitrogen deficiency

Nitrogen deficiency is the weakest class and must not be treated as a reliable agronomic diagnosis. See `research/IARI_WHEAT_REPORT.md` and `MODEL_CARD.md`.

## Scientific boundary

The RGB engine returns transparent visible-colour measurements. It does **not** diagnose diseases, nutrient deficiencies, water stress or yield. Historical demo cards are labelled sample data; newly scanned measurements are stored separately as real scans.

The segmentation baseline lives in `backend/croppulse_analysis.py`. A trained segmentation model can replace `segment_plant` without changing the mobile API.

## Verification

```bash
cd backend
python -m unittest -v test_analysis.py
cd ..
npm run typecheck
npx expo export --platform android --output-dir dist --max-workers 1
```

The verified Android production export is available in `dist/`. See `BUILD_VERIFICATION.md` for recorded results.

## Architecture

```text
Expo Android app
  ├─ camera/gallery capture
  ├─ plant passports + interventions
  ├─ AsyncStorage persistence
  └─ analysis client
            ↓ JSON/base64
FastAPI analysis service
  ├─ image quality checks
  ├─ plant segmentation baseline
  ├─ colour/coverage measurements
  └─ versioned, non-diagnostic result
```

## Research pipeline

The `research/` directory contains a field manifest, collection protocol, dataset validator and leakage-safe temporal baseline. Training splits are grouped by plant ID so repeated images of the same plant never appear in both train and test sets.

```bash
python research/validate_dataset.py research/manifest.csv
python research/train_temporal_baseline.py research/manifest.csv --output artifacts
python -m unittest discover -s research -p "test_*.py"
```

See [`research/FIELD_PROTOCOL.md`](research/FIELD_PROTOCOL.md) before collecting data.
