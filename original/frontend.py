"""
Pest Advisory System - Streamlit Frontend
BUG FREE: Exact state/district/crop/season from pkl files
"""

import streamlit as st
import requests
import plotly.graph_objects as go
from datetime import datetime

API_URL = "http://localhost:8000"

# ============================================================================
# EXACT VALUES FROM YOUR PKL FILES (verified from feature_encoders.pkl)
# state, district, crop → lowercase
# season                → Title Case (Monsoon, Post-monsoon, Summer, Winter)
# ============================================================================

STATE_DISTRICT_MAP = {
    "andhra pradesh":   ["bapatla","guntur","kakinada","krishna","nandyal","ntr","prakasam","sri sathya sai","tirupati","west godavari"],
    "assam":            ["dibrugarh","goalpara","golaghat","hojai","jorhat","kamrup","lakhimpur","nagaon","sonitpur","udalguri"],
    "bihar":            ["araria","bhagalpur","darbhanga","gaya","muzaffarpur","patna","purnia","rohtas","saran","supaul"],
    "chhattisgarh":     ["raipur","rajnandgaon"],
    "goa":              ["north goa","south goa"],
    "gujarat":          ["amreli","anand","bhavnagar","gandhinagar","gir somnath","kachchh","surendranagar","vadodara"],
    "haryana":          ["ambala","hisar","karnal","mahendragarh","rohtak"],
    "himachal pradesh": ["bilaspur","kangra","kullu","mandi","shimla","solan","una"],
    "jammu and kashmir":["anantnag","baramulla","jammu","srinagar"],
    "karnataka":        ["bagalkote","ballari","belagavi","bengaluru rural","bengaluru urban","chikkaballapura","chikkamagaluru","chitradurga","dharwad","gadag","hassan","haveri","koppal","mandya","mysuru","raichur","shivamogga","uttara kannada"],
    "kerala":           ["alappuzha","ernakulam","kannur","kollam","kottayam","kozhikode","malappuram","palakkad","thiruvananthapuram","thrissur"],
    "madhya pradesh":   ["balaghat","betul","chhatarpur","chhindwara","damoh","datia","dhar","guna","gwalior","indore","jabalpur","mandla","raisen","ratlam","rewa","sagar","satna","shajapur","sheopur","shivpuri","sidhi","tikamgarh","ujjain","vidisha"],
    "maharashtra":      ["ahmednagar","amravati","gondia","jalgaon","kolhapur","nagpur","nashik","palghar","parbhani","pune","raigad","ratnagiri","sangli","satara","sindhudurg","solapur","wardha","yavatmal"],
    "manipur":          ["imphal west"],
    "meghalaya":        ["east khasi hills"],
    "mizoram":          ["aizawl"],
    "nagaland":         ["kohima"],
    "odisha":           ["bhadrak","cuttack","ganjam","jharsuguda","kalahandi","khordha","koraput","mayurbhanj","puri","sambalpur","sundargarh"],
    "punjab":           ["amritsar","bathinda","ludhiana","patiala"],
    "rajasthan":        ["ajmer","alwar","barmer","bhilwara","bikaner","bundi","chittorgarh","ganganagar","jaipur","kota","sikar","sirohi"],
    "sikkim":           ["gangtok"],
    "tamil nadu":       ["coimbatore","cuddalore","dharmapuri","dindigul","karur","madurai","salem","thanjavur","tiruchirappalli","tirunelveli","vellore","virudhunagar"],
    "tripura":          ["west tripura"],
    "uttar pradesh":    ["agra","aligarh","bahraich","bareilly","bijnor","ghazipur","gorakhpur","hamirpur","hardoi","jalaun","jhansi","kanpur nagar","lucknow","meerut","moradabad","prayagraj","rae bareli","rampur","shahjahanpur","varanasi"],
    "west bengal":      ["bankura","birbhum","cooch behar","dakshin dinajpur","darjeeling","hooghly","howrah","jalpaiguri","murshidabad","nadia","paschim bardhaman","paschim medinipur","purba bardhaman","purba medinipur","purulia","south 24 parganas"],
}

STATE_CROPS_MAP = {
    "andhra pradesh":   ["banana","brinjal","chilli","cotton","maize","pigeonpea (red gram)","rice","sugarcane","tomato","urad bean (black gram)"],
    "assam":            ["banana","brinjal","chilli","maize","rice","sugarcane"],
    "bihar":            ["brinjal","chilli","maize","pigeonpea (red gram)","rice","soybean","tomato","wheat"],
    "chhattisgarh":     ["chilli","maize","rice","tomato"],
    "goa":              ["brinjal","rice"],
    "gujarat":          ["banana","brinjal","chilli","cotton","grapes","maize","mango","pigeonpea (red gram)","pomegranate","rice","soybean","sugarcane","tomato","wheat"],
    "haryana":          ["brinjal","chilli","cotton","maize","rice","sugarcane","tomato","wheat"],
    "himachal pradesh": ["apple","brinjal","maize","rice","soybean","tomato"],
    "jammu and kashmir":["apple","brinjal","chilli","maize","rice","tomato","urad bean (black gram)","wheat"],
    "karnataka":        ["banana","brinjal","chilli","cotton","grapes","maize","mango","pigeonpea (red gram)","pomegranate","rice","sugarcane","tomato"],
    "kerala":           ["banana","brinjal","chilli","maize","rice","tomato"],
    "madhya pradesh":   ["brinjal","chilli","cotton","maize","pigeonpea (red gram)","rice","soybean","tomato","urad bean (black gram)"],
    "maharashtra":      ["brinjal","chilli","cotton","grapes","maize","mango","pigeonpea (red gram)","pomegranate","rice","soybean","sugarcane","tomato","wheat"],
    "manipur":          ["banana","brinjal","chilli","maize","rice","tomato"],
    "meghalaya":        ["banana","maize","rice","tomato"],
    "mizoram":          ["banana","brinjal","chilli","maize","rice"],
    "nagaland":         ["banana","chilli","rice"],
    "odisha":           ["banana","brinjal","chilli","cotton","maize","mango","pigeonpea (red gram)","rice","sugarcane","tomato","urad bean (black gram)"],
    "punjab":           ["cotton","maize","rice","sugarcane","wheat"],
    "rajasthan":        ["brinjal","chilli","cotton","grapes","maize","pomegranate","rice","soybean","sugarcane","tomato","wheat"],
    "sikkim":           ["banana","chilli","maize","rice","sugarcane","tomato"],
    "tamil nadu":       ["banana","brinjal","chilli","cotton","maize","mango","pigeonpea (red gram)","rice","sugarcane","tomato","urad bean (black gram)"],
    "tripura":          ["brinjal","chilli","rice","tomato"],
    "uttar pradesh":    ["banana","brinjal","chilli","cotton","grapes","maize","mango","pigeonpea (red gram)","pomegranate","rice","soybean","sugarcane","tomato","urad bean (black gram)","wheat"],
    "west bengal":      ["banana","brinjal","chilli","maize","mango","rice","sugarcane","tomato"],
}

# EXACT seasons from feature_encoders.pkl (Title Case!)
ALL_SEASONS = ["Monsoon", "Post-monsoon", "Summer", "Winter"]
ALL_STATES  = sorted(STATE_DISTRICT_MAP.keys())
MONTH_NAMES = {1:"January",2:"February",3:"March",4:"April",5:"May",6:"June",
               7:"July",8:"August",9:"September",10:"October",11:"November",12:"December"}

# ============================================================================
# PAGE CONFIG
# ============================================================================

st.set_page_config(page_title="Pest Advisory System", page_icon="🌾", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&family=Inter:wght@400;500&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.block-container { max-width: 900px !important; padding: 2rem 2rem 4rem 2rem !important; margin: 0 auto; }
#MainMenu, footer { visibility: hidden; }
.app-header { text-align:center; padding:2rem 0 1.5rem 0; border-bottom:2px solid #e8f5e9; margin-bottom:2rem; }
.app-header h1 { font-family:'Poppins',sans-serif; font-size:2.4rem; font-weight:700; color:#1b5e20; margin:0; }
.app-header p  { color:#555; font-size:1rem; margin:0.3rem 0 0 0; }
.section-card  { background:#fff; border:1px solid #e0e0e0; border-radius:12px; padding:1.5rem; margin-bottom:1.2rem; box-shadow:0 2px 8px rgba(0,0,0,0.05); }
.section-title { font-family:'Poppins',sans-serif; font-weight:600; font-size:1rem; color:#2e7d32; margin-bottom:1rem; padding-bottom:0.4rem; border-bottom:1px solid #e8f5e9; }
.result-header { background:linear-gradient(135deg,#1b5e20,#388e3c); color:white; border-radius:12px; padding:1.5rem; margin-bottom:1.2rem; text-align:center; }
.result-header h2 { margin:0; font-family:'Poppins',sans-serif; font-size:1.4rem; }
.result-header p  { margin:0.3rem 0 0 0; opacity:0.85; font-size:0.9rem; }
.pest-card         { border-radius:10px; padding:1rem 1.2rem; margin-bottom:0.8rem; border-left:5px solid; }
.pest-card.high    { background:#fff5f5; border-color:#e53935; }
.pest-card.medium  { background:#fffde7; border-color:#f9a825; }
.pest-card.low     { background:#f1f8e9; border-color:#7cb342; }
.pest-name  { font-family:'Poppins',sans-serif; font-weight:600; font-size:1.05rem; }
.pest-prob  { font-size:0.85rem; color:#666; margin:0.2rem 0 0.5rem 0; }
.pest-remedy{ font-size:0.88rem; color:#333; }
.step-badge { display:inline-block; background:#e8f5e9; color:#2e7d32; border-radius:50%; width:26px; height:26px; text-align:center; line-height:26px; font-weight:700; font-size:0.85rem; margin-right:8px; }
.stButton > button { background:linear-gradient(135deg,#2e7d32,#43a047) !important; color:white !important; border:none !important; border-radius:8px !important; padding:0.65rem 2rem !important; font-family:'Poppins',sans-serif !important; font-weight:600 !important; font-size:1rem !important; width:100% !important; }
.stButton > button:hover { background:linear-gradient(135deg,#1b5e20,#2e7d32) !important; box-shadow:0 4px 12px rgba(46,125,50,0.3) !important; }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# HEADER
# ============================================================================

st.markdown("""
<div class="app-header">
    <h1>🌾 Pest Advisory System</h1>
    <p>AI-powered pest outbreak prediction for Indian farmers · MoAFW AI Hackathon</p>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# API CHECK
# ============================================================================

try:
    h = requests.get(f"{API_URL}/health", timeout=3).json()
    api_ok = h.get("models_loaded", False)
except Exception:
    api_ok = False

if not api_ok:
    st.error("❌ FastAPI backend not running. Open a new terminal and run: `python app.py`")
    st.stop()

st.success("✅ API Connected & Model Loaded")

# ============================================================================
# STEP 1 — LOCATION
# ============================================================================

st.markdown('<div class="section-card"><div class="section-title"><span class="step-badge">1</span>Select Location</div>', unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)
with c1:
    # Show Title Case in UI, send lowercase to API
    state_display = st.selectbox("State", [s.title() for s in ALL_STATES])
    state = state_display.lower()

with c2:
    districts_raw = STATE_DISTRICT_MAP.get(state, [])
    district_display = st.selectbox("District", [d.title() for d in districts_raw])
    district = district_display.lower()

with c3:
    crops_raw = STATE_CROPS_MAP.get(state, [])
    crop_display = st.selectbox("Crop", [c.title() for c in crops_raw])
    crop = crop_display.lower()

st.markdown('</div>', unsafe_allow_html=True)

# ============================================================================
# STEP 2 — SEASON & MONTH
# ============================================================================

st.markdown('<div class="section-card"><div class="section-title"><span class="step-badge">2</span>Season & Month</div>', unsafe_allow_html=True)

c1, c2 = st.columns(2)
with c1:
    # Exact Title Case values from pkl
    season = st.selectbox("Season", ALL_SEASONS)
with c2:
    month = st.selectbox("Month", list(range(1, 13)),
                         format_func=lambda x: MONTH_NAMES[x], index=5)

st.markdown('</div>', unsafe_allow_html=True)

# ============================================================================
# STEP 3 — CURRENT WEATHER
# ============================================================================

st.markdown('<div class="section-card"><div class="section-title"><span class="step-badge">3</span>Current Month Weather</div>', unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)
with c1:
    avg_temp   = st.number_input("Avg Temp (°C)",     value=28.0, step=0.5)
    min_temp   = st.number_input("Min Temp (°C)",     value=22.0, step=0.5)
with c2:
    max_temp   = st.number_input("Max Temp (°C)",     value=34.0, step=0.5)
    wind_speed = st.number_input("Wind Speed (km/h)", value=8.5,  step=0.5)
with c3:
    rainfall   = st.number_input("Rainfall (mm)",     value=45.0, step=1.0)

st.markdown('</div>', unsafe_allow_html=True)

# ============================================================================
# STEP 4 — LAGGED WEATHER
# ============================================================================

st.markdown('<div class="section-card"><div class="section-title"><span class="step-badge">4</span>Previous 3 Months Weather <span style="font-weight:400;color:#888;font-size:0.85rem">(improves accuracy)</span></div>', unsafe_allow_html=True)

with st.expander("Enter last 3 months weather data (click to expand)", expanded=False):
    st.caption("Lag-1 = last month · Lag-2 = 2 months ago · Lag-3 = 3 months ago")
    r1, r2, r3 = st.columns(3)
    with r1:
        st.markdown("**Avg Temperature (°C)**")
        t_l1 = st.number_input("Avg Temp Lag-1", value=float(avg_temp - 1),  key="tl1")
        t_l2 = st.number_input("Avg Temp Lag-2", value=float(avg_temp - 2),  key="tl2")
        t_l3 = st.number_input("Avg Temp Lag-3", value=float(avg_temp - 3),  key="tl3")
    with r2:
        st.markdown("**Rainfall (mm)**")
        r_l1 = st.number_input("Rainfall Lag-1", value=float(rainfall + 5),  key="rl1")
        r_l2 = st.number_input("Rainfall Lag-2", value=float(rainfall - 10), key="rl2")
        r_l3 = st.number_input("Rainfall Lag-3", value=float(rainfall - 20), key="rl3")
    with r3:
        st.markdown("**Wind Speed (km/h)**")
        w_l1 = st.number_input("Wind Lag-1", value=float(wind_speed - 0.5), key="wl1")
        w_l2 = st.number_input("Wind Lag-2", value=float(wind_speed - 1.0), key="wl2")
        w_l3 = st.number_input("Wind Lag-3", value=float(wind_speed - 1.5), key="wl3")

st.markdown('</div>', unsafe_allow_html=True)

# ============================================================================
# PREDICT BUTTON
# ============================================================================

_, col_btn, _ = st.columns([1, 2, 1])
with col_btn:
    predict_btn = st.button("🔍 Predict Pest Risk", type="primary")

# ============================================================================
# RESULTS
# ============================================================================

REMEDIES = {
    'fall armyworm': 'Spray neem oil every 7-10 days or use Spinosad/Emamectin benzoate',
    'leaf curl': 'Manage whitefly vectors, use yellow sticky traps',
    'thrips': 'Spray neem oil, use blue sticky traps',
    'yellow stem borer': 'Use pheromone traps, apply Emamectin benzoate',
    'aphid': 'Spray neem oil or systemic insecticide early morning',
    'leaf folder': 'Use approved insecticide, monitor weekly',
    'shoot and fruit borer': 'Apply Chlorpyrifos or neem-based spray',
    'whitefly': 'Use yellow sticky traps, neem oil spray',
    'white fly': 'Use yellow sticky traps, neem oil spray',
    'brown spot': 'Apply Mancozeb or Propiconazole fungicide',
    'red rot': 'Remove infected plants, apply fungicide',
    'stem borer': 'Use pheromone traps, apply Chlorpyrifos',
    'sheath blight': 'Apply Hexaconazole or Validamycin',
    'rice blast': 'Apply Tricyclazole or Isoprothiolane fungicide',
    'late blight': 'Apply Metalaxyl + Mancozeb, destroy infected plants',
    'early blight': 'Apply Mancozeb or Chlorothalonil fungicide',
    'powdery mildew': 'Apply Sulphur-based fungicide or Triadimefon',
    'bacterial blight': 'Use copper-based bactericide, remove infected leaves',
    'pink bollworm': 'Use pheromone traps, Spinosad spray',
    'mango hopper': 'Spray imidacloprid or lambda-cyhalothrin',
}

def get_remedy_local(pest: str) -> str:
    return REMEDIES.get(pest.lower().strip(),
           f'Consult local agricultural extension officer for {pest} management')

if predict_btn:
    payload = {
        "state": state, "district": district, "crop": crop,
        "season": season,           # Exact: Monsoon / Post-monsoon / Summer / Winter
        "month": month,
        "avg_temp": avg_temp, "min_temp": min_temp, "max_temp": max_temp,
        "wind_speed": wind_speed, "rainfall": rainfall,
        "avg_temp_lag1": t_l1, "avg_temp_lag2": t_l2, "avg_temp_lag3": t_l3,
        "rainfall_lag1": r_l1, "rainfall_lag2": r_l2, "rainfall_lag3": r_l3,
        "wind_speed_lag1": w_l1, "wind_speed_lag2": w_l2, "wind_speed_lag3": w_l3,
    }

    with st.spinner("Analyzing weather conditions and predicting pests..."):
        try:
            resp   = requests.post(f"{API_URL}/predict", json=payload, timeout=15)
            result = resp.json()
        except Exception as e:
            st.error(f"❌ API request failed: {e}")
            st.stop()

    if "detail" in result:
        st.error(f"❌ {result['detail']}")
        st.stop()

    preds = result.get("predictions", [])
    if not preds:
        st.warning("No predictions returned.")
        st.stop()

    # Result header
    st.markdown(f"""
    <div class="result-header">
        <h2>🎯 {crop_display} in {district_display}, {state_display}</h2>
        <p>{season} · {MONTH_NAMES[month]} · {avg_temp}°C · {rainfall} mm rain</p>
    </div>
    """, unsafe_allow_html=True)

    # Metrics
    sev0  = preds[0].get("severity", "")
    icon  = "🔴" if sev0 == "HIGH" else "🟡" if sev0 == "MEDIUM" else "🟢"
    m1, m2, m3 = st.columns(3)
    m1.metric("🚨 Top Pest",   preds[0]["pest"].title())
    m2.metric("📊 Confidence", preds[0]["percent"])
    m3.metric("⚠️ Risk Level", f"{icon} {sev0}")

    # Action
    action = get_remedy_local(preds[0]["pest"])
    if sev0 == "HIGH":
        st.error(f"**Immediate Action:** {action}")
    elif sev0 == "MEDIUM":
        st.warning(f"**Recommended Action:** {action}")
    else:
        st.success(f"**Precautionary Action:** {action}")

    # Chart + cards
    st.markdown("#### 📊 Pest Risk Breakdown")
    col_chart, col_cards = st.columns([3, 2])

    with col_chart:
        names  = [p["pest"].title() for p in preds]
        probs  = [round(p["probability"] * 100, 1) for p in preds]
        colors = ["#e53935" if p >= 50 else "#f9a825" if p >= 30 else "#7cb342" for p in probs]
        fig = go.Figure(go.Bar(
            x=probs, y=names, orientation='h',
            marker_color=colors,
            text=[f"{p}%" for p in probs], textposition='auto',
        ))
        fig.update_layout(
            xaxis=dict(title="Risk (%)", range=[0, 100]),
            yaxis=dict(autorange="reversed"),
            height=200, margin=dict(l=0, r=10, t=10, b=30),
            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_cards:
        for i, p in enumerate(preds, 1):
            sev  = p.get("severity", "LOW")
            cls  = sev.lower()
            icon = "🔴" if sev == "HIGH" else "🟡" if sev == "MEDIUM" else "🟢"
            remedy = get_remedy_local(p["pest"])
            st.markdown(f"""
            <div class="pest-card {cls}">
                <div class="pest-name">{i}. {p['pest'].title()}</div>
                <div class="pest-prob">{icon} {sev} · {p['percent']}</div>
                <div class="pest-remedy">💊 {remedy}</div>
            </div>
            """, unsafe_allow_html=True)

    # Export
    import pandas as pd
    df_out = pd.DataFrame([{
        "Pest": p["pest"].title(), "Probability": p["percent"],
        "Severity": p.get("severity", ""), "Remedy": get_remedy_local(p["pest"])
    } for p in preds])
    st.download_button("📥 Download Results as CSV", data=df_out.to_csv(index=False),
        file_name=f"pest_advisory_{district}_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
        mime="text/csv")

# Footer
st.markdown("""
<div style="text-align:center;color:#aaa;font-size:0.8rem;margin-top:3rem;padding-top:1rem;border-top:1px solid #eee;">
    🌾 Pest Advisory System &nbsp;·&nbsp; MoAFW AI Hackathon &nbsp;·&nbsp; Powered by Random Forest + FastAPI + Streamlit
</div>
""", unsafe_allow_html=True)