"""
Pest Advisory System - FastAPI Backend
BUG FREE VERSION - matches exact pkl encoder classes
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator
import joblib
import numpy as np
import os

app = FastAPI(title="Pest Advisory System API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"],
                   allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

# ============================================================================
# LOAD MODELS (exact filenames from your folder)
# ============================================================================

model = None
location_encoders = None
pest_encoder = None
MODELS_LOADED = False

try:
    model             = joblib.load('pest_prediction_model.pkl')
    location_encoders = joblib.load('feature_encoders.pkl')
    pest_encoder      = joblib.load('target_encoder.pkl')
    MODELS_LOADED     = True
    print("✅ All models loaded!")
    print("\n=== ENCODER CLASSES ===")
    for key in location_encoders:
        print(f"  {key}: {list(location_encoders[key].classes_)}")
    print("=======================\n")
except Exception as e:
    print(f"❌ Model loading error: {e}")

# ============================================================================
# KNOWN VALID VALUES (from your actual pkl files)
# ============================================================================

# state, district, crop → LOWERCASE in encoder
# season               → Title Case in encoder: Monsoon, Post-monsoon, Summer, Winter

VALID_SEASONS = ['Monsoon', 'Post-monsoon', 'Summer', 'Winter']

# ============================================================================
# SCHEMA
# ============================================================================

class PredictRequest(BaseModel):
    state:           str
    district:        str
    crop:            str
    season:          str   # Must be: Monsoon / Post-monsoon / Summer / Winter
    month:           int
    avg_temp:        float
    min_temp:        float
    max_temp:        float
    wind_speed:      float
    rainfall:        float
    avg_temp_lag1:   float
    avg_temp_lag2:   float
    avg_temp_lag3:   float
    rainfall_lag1:   float
    rainfall_lag2:   float
    rainfall_lag3:   float
    wind_speed_lag1: float
    wind_speed_lag2: float
    wind_speed_lag3: float

    @field_validator('state', 'district', 'crop', mode='before')
    @classmethod
    def lowercase_location(cls, v):
        # state, district, crop are lowercase in encoder
        return str(v).strip().lower()

    @field_validator('season', mode='before')
    @classmethod
    def fix_season(cls, v):
        # season is Title Case in encoder — normalize carefully
        v = str(v).strip()
        # Map common variants to exact encoder values
        mapping = {
            'monsoon':      'Monsoon',
            'post-monsoon': 'Post-monsoon',
            'postmonsoon':  'Post-monsoon',
            'post monsoon': 'Post-monsoon',
            'summer':       'Summer',
            'winter':       'Winter',
            'rabi':         'Winter',
            'kharif':       'Monsoon',
        }
        normalized = mapping.get(v.lower(), v)
        return normalized

# ============================================================================
# REMEDIES (all lowercase keys)
# ============================================================================

REMEDIES = {
    'fall armyworm':                        'Spray neem oil every 7-10 days or use Spinosad/Emamectin benzoate',
    'leaf curl':                            'Manage whitefly vectors, use yellow sticky traps',
    'thrips':                               'Spray neem oil, use blue sticky traps',
    'yellow stem borer':                    'Use pheromone traps, apply Emamectin benzoate',
    'aphid':                                'Spray neem oil or systemic insecticide early morning',
    'leaf folder':                          'Use approved insecticide, monitor weekly',
    'shoot and fruit borer':               'Apply Chlorpyrifos or neem-based spray',
    'whitefly':                             'Use yellow sticky traps, neem oil spray',
    'white fly':                            'Use yellow sticky traps, neem oil spray',
    'whiteflies':                           'Use yellow sticky traps, neem oil spray',
    'brown spot':                           'Apply Mancozeb or Propiconazole fungicide',
    'red rot':                              'Remove infected plants, apply fungicide',
    'gram pod borer':                       'Spray Quinalphos or neem oil at flowering',
    'hadda beetle':                         'Apply approved insecticide, remove egg masses',
    'black thrips':                         'Use systemic insecticide, blue sticky traps',
    'rice blast':                           'Apply Tricyclazole or Isoprothiolane fungicide',
    'gundhi bug':                           'Spray Malathion at milky grain stage',
    'false smut':                           'Apply Propiconazole at boot leaf stage',
    'stem borer':                           'Use pheromone traps, apply Chlorpyrifos',
    'pink stem borer':                      'Use pheromone traps, recommended insecticide',
    'stem rot':                             'Improve drainage, apply Carbendazim',
    'sheath blight':                        'Apply Hexaconazole or Validamycin',
    'bacterial blight':                     'Use copper-based bactericide, remove infected leaves',
    'bacterial leaf blight':               'Use copper-based bactericide, avoid overhead irrigation',
    'early blight':                         'Apply Mancozeb or Chlorothalonil fungicide',
    'late blight':                          'Apply Metalaxyl + Mancozeb, destroy infected plants',
    'powdery mildew':                       'Apply Sulphur-based fungicide or Triadimefon',
    'downy mildew':                         'Apply Metalaxyl or Fosetyl-aluminium',
    'anthracnose':                          'Apply Carbendazim or Mancozeb fungicide',
    'rust':                                 'Apply Propiconazole or Mancozeb fungicide',
    'yellow rust or stripe rust':          'Apply Propiconazole at first sign of disease',
    'fusarium wilt':                        'Remove infected plants, apply Carbendazim drench',
    'panama wilt':                          'Remove infected plants, use resistant varieties',
    'bacterial wilt':                       'Remove infected plants, practice crop rotation',
    'leaf hopper/jassids':                 'Spray imidacloprid or neem oil',
    'jassid':                               'Spray imidacloprid or neem oil',
    'brown plant hopper':                  'Use pheromone traps, recommended insecticide',
    'green leaf hopper':                   'Use recommended systemic insecticide',
    'pink bollworm':                        'Use pheromone traps, Spinosad spray',
    'red cotton bug':                       'Spray approved insecticide at boll opening stage',
    'mango hopper':                         'Spray imidacloprid or lambda-cyhalothrin',
    'mango mealybug':                      'Use sticky bands on trunk, spray neem oil',
    'maydis leaf blight':                  'Apply Mancozeb, use resistant hybrids',
    'turcicum leaf  blight':               'Apply Mancozeb, use resistant varieties',
    'cercospora leaf spot':                'Apply Copper oxychloride or Mancozeb',
    'alternaria leaf spot':                'Apply Mancozeb or Iprodione fungicide',
    'alternaria leaf spot/blight':         'Apply Mancozeb or Iprodione fungicide',
    'angular leaf spot/ black arm/ bacterial blight': 'Apply copper bactericide, avoid wet conditions',
    'hispa':                                'Clip and destroy affected leaves, use recommended insecticide',
    'shoot fly':                            'Use carbofuran granules at sowing, early planting',
    'leaf miner':                           'Spray spinosad or neem oil, remove mined leaves',
    'serpentine leaf miner':               'Apply neem oil, remove affected leaves',
    'spotted pod borer':                   'Spray chlorpyrifos or neem oil at pod formation',
    'pod fly':                              'Spray dimethoate at flowering stage',
    'pod bug':                              'Spray approved insecticide at pod formation',
    'girdle beetle':                        'Remove and destroy affected stems, spray insecticide',
    'internode borer':                      'Apply Chlorpyrifos, remove infected plant parts',
    'pyrilla':                              'Use pheromone traps, spray recommended insecticide',
    'swarming caterpillar':               'Spray chlorpyrifos or emamectin benzoate',
    'tobacco caterpillar':                'Spray chlorpyrifos or spinosad',
    'bihar hairy caterpillar':            'Collect and destroy egg masses, spray insecticide',
    'helicoverpa catterpillar':           'Spray Bt (Bacillus thuringiensis) or spinosad',
    'gram caterpillar/fruit borer':       'Spray chlorpyrifos or neem oil at flowering',
    'ear borer/corn borer':              'Apply Chlorpyrifos granules into whorls',
    'cut worm':                             'Apply Chlorpyrifos or carbofuran at soil level',
    'yellow mite':                          'Spray acaricide, increase humidity',
    'spider':                               'Spray acaricide (Dicofol), increase humidity',
    'spiders':                              'Spray acaricide (Dicofol), increase humidity',
    'case worm':                            'Drain water, apply recommended insecticide',
    'leaf webber':                          'Remove webbed leaves, spray Chlorpyrifos',
    'rugose spiralling whitefly':          'Spray buprofezin or spiromesifen',
    'banana skippers':                     'Spray Chlorpyrifos or remove affected leaves',
    'anar butterfly':                       'Use pheromone traps, spray recommended insecticide',
    'fruit scarring beetle':              'Use light traps, bag fruits before ripening',
    'die back and fruit rot (anthracnose)': 'Prune infected parts, apply Carbendazim',
    'phomopsis blight and fruit rot':     'Apply Mancozeb, remove infected fruits',
    'little leaf':                          'Control leafhopper vector, remove infected plants',
    'yellow mosaic':                        'Control whitefly vector, use resistant varieties',
    'red striped disease':                 'Use certified disease-free seed, remove infected plants',
    'woolly aphid':                         'Apply dimethoate or neem-based spray',
    'yellow sigatoka & black sigatoka':  'Apply approved systemic fungicide, remove infected leaves',
    'dragon fly':                           'Beneficial insect — no action needed',
    'dragonfly':                            'Beneficial insect — no action needed',
    'green lacewing':                       'Beneficial insect — no action needed',
    'lady bird beetle':                    'Beneficial insect — no action needed',
    'ladybird beetle':                     'Beneficial insect — no action needed',
    'ground beetle':                        'Beneficial insect — no action needed',
    'wolf spider':                          'Beneficial predator — no action needed',
}

def get_remedy(pest: str) -> str:
    return REMEDIES.get(pest.lower().strip(),
           f'Consult local agricultural extension officer for {pest} management')

# ============================================================================
# ENDPOINTS
# ============================================================================

@app.get("/")
def root():
    return {"status": "running", "models_loaded": MODELS_LOADED}

@app.get("/health")
def health():
    return {"status": "ok", "models_loaded": MODELS_LOADED}

@app.get("/options")
def get_options():
    if not MODELS_LOADED:
        raise HTTPException(status_code=503, detail="Models not loaded")
    return {
        "states":   sorted(list(location_encoders['state'].classes_)),
        "districts": sorted(list(location_encoders['district'].classes_)),
        "crops":    sorted(list(location_encoders['crop'].classes_)),
        "seasons":  list(location_encoders['season'].classes_),
    }

@app.post("/predict")
def predict(req: PredictRequest):
    if not MODELS_LOADED:
        raise HTTPException(status_code=503, detail="Models not loaded")

    try:
        # Validate season explicitly (most common source of errors)
        if req.season not in VALID_SEASONS:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid season: '{req.season}'. Must be one of: {VALID_SEASONS}"
            )

        # Encode
        state_enc    = location_encoders['state'].transform([req.state])[0]
        district_enc = location_encoders['district'].transform([req.district])[0]
        crop_enc     = location_encoders['crop'].transform([req.crop])[0]
        season_enc   = location_encoders['season'].transform([req.season])[0]

        features = np.array([[
            state_enc, district_enc, crop_enc, season_enc,
            req.month,
            req.avg_temp, req.min_temp, req.max_temp,
            req.wind_speed, req.rainfall,
            req.avg_temp_lag1, req.avg_temp_lag2, req.avg_temp_lag3,
            req.rainfall_lag1, req.rainfall_lag2, req.rainfall_lag3,
            req.wind_speed_lag1, req.wind_speed_lag2, req.wind_speed_lag3
        ]])

        probs    = model.predict_proba(features)[0]
        top3_idx = probs.argsort()[-3:][::-1]

        predictions = []
        for idx in top3_idx:
            pest = pest_encoder.classes_[idx]
            prob = float(probs[idx])
            predictions.append({
                "pest":        pest,
                "probability": round(prob, 3),
                "percent":     f"{prob*100:.1f}%",
                "remedy":      get_remedy(pest),
                "severity":    "HIGH" if prob >= 0.5 else "MEDIUM" if prob >= 0.3 else "LOW"
            })

        return {
            "state":          req.state,
            "district":       req.district,
            "crop":           req.crop,
            "predictions":    predictions,
            "top_pest":       predictions[0]["pest"],
            "top_confidence": predictions[0]["percent"],
            "action":         predictions[0]["remedy"]
        }

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400,
            detail=f"Encoding error: {str(e)}. Value not seen during training.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    print("\n🌾 Starting Pest Advisory API → http://localhost:8000")
    print("📚 Docs → http://localhost:8000/docs\n")
    uvicorn.run(app, host="0.0.0.0", port=8000)