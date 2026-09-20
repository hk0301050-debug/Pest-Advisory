# 🌾 Pest Advisory: AI-based pest risk prediction for Indian crops

Pick a state, district, crop and month, enter the weather, and get the three most likely pests
with a confidence score and crop protection advice.

**Live demo:** _paste your Render URL here_  ·  **API docs:** `<your-url>/docs`

## How it works
- **Data:** NPSS pest occurrence records + India weather and rainfall data, merged by state, district and month
- **Features:** location, crop, season, month, temperature, rainfall, wind speed and 3-month lagged weather
- **Model:** Random Forest classifier (100 trees, 92 pest and disease classes), top-3 predictions
- **Backend:** FastAPI (`main.py`). The forest is exported to plain NumPy arrays (`predictor.py`), which cut
  memory from ~350 MB to ~100 MB so it runs on a free 512 MB instance
- **Frontend:** HTML, CSS and vanilla JavaScript in `static/`, served by the same FastAPI app

## API
| Method | Path | Purpose |
|---|---|---|
| GET | `/api/health` | Health check |
| GET | `/api/meta` | States, districts, crops, seasons |
| POST | `/api/predict` | Returns top-3 pests, confidence, remedies, advisory |

## Run locally
```bash
python -m venv .venv && source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
# open http://localhost:8000
```

## Deploy on Render (free)
1. Push this folder to a GitHub repository.
2. On render.com: **New, then Blueprint**, pick the repo (it reads `render.yaml`). Or **New, then Web Service** with
   Build `pip install -r requirements.txt` and Start `uvicorn main:app --host 0.0.0.0 --port $PORT`.
3. Wait 2 to 3 minutes for the first build, then open the `onrender.com` URL.

## Rebuilding the model files (optional)
`original/` holds the trained scikit-learn artifacts. To regenerate `model/`:
```bash
pip install scikit-learn==1.6.1 joblib numpy
python build_assets.py
```

## Author
Himanshu Kumar
