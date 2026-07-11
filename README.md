# CropPulse

Android-first crop-health monitoring system with real RGB image measurements, longitudinal plant passports, intervention-response tracking and farmer-friendly field insights.

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
