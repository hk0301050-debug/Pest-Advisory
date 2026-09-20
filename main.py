"""
Pest Advisory System - FastAPI app.
Serves the JSON API (/api/...) and the HTML/CSS/JS frontend (/) from one service.
Run locally:  uvicorn main:app --reload
"""
import json
from pathlib import Path

import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from predictor import CompactForest

BASE = Path(__file__).parent
META = json.loads((BASE / "model" / "meta.json").read_text(encoding="utf-8"))
FOREST = CompactForest(BASE / "model" / "forest.npz")

# label -> index, identical to sklearn LabelEncoder (classes are stored sorted)
INDEX = {k: {v: i for i, v in enumerate(vals)} for k, vals in META["classes"].items()}
PESTS, REMEDIES = META["pests"], META["remedies"]

SEASONS = {"monsoon": "Monsoon", "post-monsoon": "Post-monsoon", "post monsoon": "Post-monsoon",
           "postmonsoon": "Post-monsoon", "summer": "Summer", "winter": "Winter",
           "kharif": "Monsoon", "rabi": "Winter"}

app = FastAPI(title="Pest Advisory System API", version="2.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


class PredictRequest(BaseModel):
    state: str
    district: str
    crop: str
    season: str
    month: int = Field(ge=1, le=12)
    avg_temp: float = Field(ge=-30, le=60)
    min_temp: float = Field(ge=-30, le=60)
    max_temp: float = Field(ge=-30, le=60)
    wind_speed: float = Field(ge=0, le=200)
    rainfall: float = Field(ge=0, le=5000)
    avg_temp_lag1: float; avg_temp_lag2: float; avg_temp_lag3: float
    rainfall_lag1: float; rainfall_lag2: float; rainfall_lag3: float
    wind_speed_lag1: float; wind_speed_lag2: float; wind_speed_lag3: float


def band(p: float) -> str:
    return "HIGH" if p >= 0.5 else "MEDIUM" if p >= 0.3 else "LOW"


ADVICE = {
    "HIGH": ["Scout the field every 2-3 days, checking the underside of leaves and growing tips.",
             "Start preventive measures now: traps, clean bunds and removal of affected plants.",
             "Contact your local agricultural extension officer before spraying."],
    "MEDIUM": ["Scout the field at least once a week.",
               "Keep traps and monitoring in place and act at the first sign of damage."],
    "LOW": ["Continue routine weekly monitoring.",
            "The weather signal for this pest is weak this month, so no special action is needed."],
}


BENEFICIAL_ADVICE = ["The most likely species here is a beneficial insect, which usually points to a healthy field.",
                     "No control action is needed. Avoid broad-spectrum sprays that would harm it."]


def lookup(kind: str, value: str, label: str) -> int:
    v = value.strip()
    key = SEASONS.get(v.lower(), v) if kind == "season" else v.lower()
    if key not in INDEX[kind]:
        raise HTTPException(400, f"Unknown {label} '{value}'. It was not in the training data.")
    return INDEX[kind][key]


@app.get("/api/health")
def health():
    return {"status": "ok", "model_loaded": True}


@app.get("/api/meta")
def meta():
    return {"states": sorted(META["state_districts"]), "state_districts": META["state_districts"],
            "state_crops": META["state_crops"], "seasons": META["classes"]["season"]}


@app.post("/api/predict")
def predict(r: PredictRequest):
    row = [lookup("state", r.state, "state"), lookup("district", r.district, "district"),
           lookup("crop", r.crop, "crop"), lookup("season", r.season, "season"), r.month,
           r.avg_temp, r.min_temp, r.max_temp, r.wind_speed, r.rainfall,
           r.avg_temp_lag1, r.avg_temp_lag2, r.avg_temp_lag3,
           r.rainfall_lag1, r.rainfall_lag2, r.rainfall_lag3,
           r.wind_speed_lag1, r.wind_speed_lag2, r.wind_speed_lag3]
    probs = FOREST.predict_proba(row)
    top = probs.argsort()[-3:][::-1]
    preds = []
    for i in top:
        pest, p = PESTS[i], float(probs[i])
        remedy = REMEDIES.get(pest.lower(), f"Consult your local agricultural extension officer about {pest} management.")
        preds.append({"pest": pest, "probability": round(p, 4), "percent": f"{p * 100:.1f}%",
                      "severity": band(p), "remedy": remedy,
                      "beneficial": remedy.lower().startswith("beneficial")})
    return {"state": r.state, "district": r.district, "crop": r.crop, "month": r.month,
            "predictions": preds, "top_pest": preds[0]["pest"], "top_confidence": preds[0]["percent"],
            "advisory": BENEFICIAL_ADVICE if preds[0]["beneficial"] else ADVICE[preds[0]["severity"]]}


app.mount("/static", StaticFiles(directory=BASE / "static"), name="static")


@app.get("/")
def index():
    return FileResponse(BASE / "static" / "index.html")
