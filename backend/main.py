from __future__ import annotations

import base64
import binascii

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from croppulse_analysis import analyze_bytes
from wheat_model import predict_wheat


class AnalyzeRequest(BaseModel):
    image_base64: str = Field(min_length=32, max_length=20_000_000)


app = FastAPI(title="CropPulse Analysis API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["GET", "POST"], allow_headers=["*"])


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "engine": "rgb-baseline-1"}


@app.post("/v1/analyze")
def analyze(request: AnalyzeRequest) -> dict:
    encoded = request.image_base64.split(",", 1)[-1]
    try:
        payload = base64.b64decode(encoded, validate=True)
        result = analyze_bytes(payload)
        result["wheat_model"] = predict_wheat(payload)
        return result
    except (binascii.Error, ValueError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
