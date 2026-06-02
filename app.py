import streamlit as st
import pandas as pd
import altair as alt
from pathlib import Path
import base64

# --- Page Config ---
st.set_page_config(
    page_title="FIFA 2026 Winner Prediction | Apex Pitch",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- Custom CSS (Apex Pitch Identity) ---
# Deep midnight: #111417
# Electric blue: #00e5ff
# Gold highlight: #FFD700
def inject_custom_css():
    st.markdown("""
        <style>
        /* Import OSWALD */
        @import url('https://fonts.googleapis.com/css2?family=Oswald:wght@400;600;700&family=Inter:wght@400;500;600&display=swap');

        /* Global overrides */
        .stApp {
            background-color: #111417;
            color: #E2E8F0;
            font-family: 'Inter', sans-serif;
        }
        
        /* Typography */
        h1, h2, h3, h4, .stMetric label {
            font-family: 'Oswald', sans-serif !important;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        
        /* Electric Blue Headers */
        h1 { color: #00e5ff !important; font-size: 3rem !important; text-shadow: 0 0 10px rgba(0, 229, 255, 0.3); }
        h2 { color: #E2E8F0 !important; border-bottom: 1px solid rgba(0, 229, 255, 0.2); padding-bottom: 10px; }
        
        /* Glassmorphism Cards */
        .glass-card {
            background: rgba(255, 255, 255, 0.03);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            border-top: 1px solid rgba(255, 255, 255, 0.1);
            border-left: 1px solid rgba(255, 255, 255, 0.1);
            border-bottom: 1px solid rgba(0, 229, 255, 0.2);
            border-right: 1px solid rgba(0, 229, 255, 0.2);
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 24px;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        .glass-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 12px 40px 0 rgba(0, 229, 255, 0.15);
        }
        
        /* Gold text emphasis */
        .gold-text { color: #FFD700; font-weight: 700; }
        .blue-text { color: #00e5ff; font-weight: 700; }
        
        /* Metric values */
        [data-testid="stMetricValue"] {
            font-family: 'Oswald', sans-serif !important;
            color: #FFD700 !important;
            font-size: 3rem !important;
            text-shadow: 0 0 15px rgba(255, 215, 0, 0.4);
        }
        [data-testid="stMetricLabel"] {
            color: #94A3B8 !important;
            font-size: 1.1rem !important;
        }
        
        /* Hero Banner Overlay Text */
        .hero-title {
            font-family: 'Oswald', sans-serif;
            font-size: 4rem;
            font-weight: 700;
            color: white;
            text-transform: uppercase;
            text-shadow: 0px 4px 20px rgba(0, 0, 0, 0.8);
            margin-bottom: 0;
            line-height: 1.1;
        }
        .hero-subtitle {
            font-size: 1.5rem;
            color: #00e5ff;
            text-shadow: 0px 2px 10px rgba(0, 0, 0, 0.8);
            margin-top: 5px;
        }
        
        /* Dataframes */
        .stDataFrame {
            background-color: transparent !important;
        }
        [data-testid="stTable"] {
            background-color: transparent !important;
        }
        
        hr {
            border-color: rgba(0, 229, 255, 0.1) !important;
        }
        </style>
    """, unsafe_allow_html=True)

inject_custom_css()

# --- Data Loading ---
@st.cache_data
def load_predictions():
    pred_path = Path("reports/tournament_predictions.csv")
    if not pred_path.exists():
        return None
    return pd.read_csv(pred_path)

@st.cache_data
def load_squad_values():
    squad_path = Path("data/raw/squad_values.csv")
    if not squad_path.exists():
        return None
    return pd.read_csv(squad_path)

preds = load_predictions()
squads = load_squad_values()

if preds is None:
    st.error("Model prediction data not found. Run pipeline first.")
    st.stop()

# --- Helpers ---
def get_image_base64(image_path):
    import os
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return ""

# --- Command Center (Hero Section) ---
# Locate the generated image path
image_paths = list(Path("/Users/mukilan/.gemini/antigravity-ide/brain/069c6041-4cc3-42fe-b5b7-b45e6f624f8d").glob("spain_captain_hero_*.png"))
hero_img_base64 = get_image_base64(str(image_paths[0])) if image_paths else ""

top_team = preds.iloc[0]

if hero_img_base64:
    st.markdown(f"""
        <div style="
            position: relative;
            width: 100%;
            height: 400px;
            background-image: linear-gradient(rgba(17, 20, 23, 0.3), rgba(17, 20, 23, 0.9)), url('data:image/png;base64,{hero_img_base64}');
            background-size: cover;
            background-position: center;
            border-radius: 12px;
            margin-bottom: 2rem;
            display: flex;
            flex-direction: column;
            justify-content: flex-end;
            padding: 40px;
            border: 1px solid rgba(0, 229, 255, 0.3);
            box-shadow: 0 0 30px rgba(0, 229, 255, 0.1);
        ">
            <div style="font-family: 'Inter'; color: #FFD700; letter-spacing: 2px; text-transform: uppercase; font-size: 0.9rem; font-weight: 600; margin-bottom: 10px;">Model Status v4.2 • Live Simulation</div>
            <div class="hero-title">FIFA 2026 WORLD CUP</div>
            <div class="hero-subtitle">PREDICTED WINNER: <span style="color: white">{top_team['team']}</span></div>
        </div>
    """, unsafe_allow_html=True)
else:
    st.title("FIFA 2026 WORLD CUP")
    st.markdown(f"### Predicted Winner: <span class='blue-text'>{top_team['team']}</span>", unsafe_allow_html=True)


# --- Winner Spotlight Metrics ---
st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="FAVORITE", value=top_team['team'].upper())
with col2:
    st.metric(label="WIN PROBABILITY", value=f"{top_team['win_prob']*100:.1f}%")
with col3:
    st.metric(label="REACH FINAL", value=f"{top_team['final_prob']*100:.1f}%")
st.markdown("</div>", unsafe_allow_html=True)


# --- Power Rankings ---
st.markdown("<h2>POWER RANKINGS</h2>", unsafe_allow_html=True)
st.markdown("<p style='color: #94A3B8; margin-bottom: 20px;'>Top 20 Teams by simulated probability of lifting the trophy.</p>", unsafe_allow_html=True)

top_20 = preds.head(20).copy()
top_20['Win Prob (%)'] = top_20['win_prob'] * 100

# Altair Chart heavily customized for Apex Pitch theme
chart = alt.Chart(top_20).mark_bar(
    cornerRadiusTopRight=3,
    cornerRadiusBottomRight=3,
).encode(
    x=alt.X('Win Prob (%):Q', title='Win Probability (%)', axis=alt.Axis(grid=False, domainColor='rgba(255,255,255,0.2)', tickColor='rgba(255,255,255,0.2)', labelColor='#E2E8F0', titleColor='#00e5ff', titleFont='Oswald')),
    y=alt.Y('team:N', sort='-x', title='', axis=alt.Axis(grid=False, domainColor='rgba(255,255,255,0.2)', tickColor='rgba(255,255,255,0.2)', labelColor='#FFD700', labelFont='Oswald', labelFontSize=13)),
    color=alt.Color('Win Prob (%):Q', scale=alt.Scale(range=['#005f73', '#00e5ff']), legend=None),
    tooltip=[
        alt.Tooltip('team:N', title='Team'),
        alt.Tooltip('Win Prob (%):Q', title='Win %', format='.1f'),
        alt.Tooltip('final_prob:Q', title='Final %', format='.1%')
    ]
).properties(
    height=550,
    background='transparent'
).configure_view(
    strokeWidth=0
).configure_axis(
    labelFont='Inter',
    titleFont='Oswald'
)

st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
st.altair_chart(chart, use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)


# --- Team Spotlight ---
st.markdown("<h2>TEAM SPOTLIGHT</h2>", unsafe_allow_html=True)

if squads is not None:
    merged = pd.merge(preds, squads, left_on='team', right_on='team_name', how='left')
    
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    
    selected_team = st.selectbox("Select a National Team to analyze", options=merged['team'].tolist())
    team_data = merged[merged['team'] == selected_team].iloc[0]
    
    colA, colB = st.columns([1, 1.5])
    
    with colA:
        st.markdown(f"<h3 style='color: #FFD700; font-size: 2rem;'>{selected_team.upper()}</h3>", unsafe_allow_html=True)
        
        rating = team_data.get('fifa_rating', 'N/A')
        val = team_data.get('squad_value_m', 'N/A')
        stars = int(team_data.get('star_player_count', 0))
        inj = int(team_data.get('key_injuries', 0))
        cont = team_data.get('home_continent', 'Unknown')
        
        st.markdown(f"""
        <table style="width:100%; font-size: 1.1rem; border-collapse: separate; border-spacing: 0 10px;">
            <tr><td style="color:#94A3B8;">FIFA Rating:</td><td class="blue-text" style="text-align:right; font-size: 1.3rem;">{rating}</td></tr>
            <tr><td style="color:#94A3B8;">Squad Value:</td><td class="blue-text" style="text-align:right; font-size: 1.3rem;">€{val}M</td></tr>
            <tr><td style="color:#94A3B8;">Continent:</td><td style="text-align:right;">{cont}</td></tr>
            <tr><td style="color:#94A3B8;">Star Players:</td><td style="text-align:right; color: #FFD700;">{'⭐'*stars if stars > 0 else 'None'}</td></tr>
            <tr><td style="color:#94A3B8;">Key Injuries:</td><td style="text-align:right; color: #ef4444;">{inj}</td></tr>
        </table>
        """, unsafe_allow_html=True)
            
    with colB:
        st.markdown("<h4 style='color: #00e5ff; margin-bottom: 15px;'>TOURNAMENT PROGRESSION</h4>", unsafe_allow_html=True)
        
        # Display progression as a styled table
        st.markdown(f"""
        <style>
        .prog-table {{ width: 100%; border-collapse: collapse; }}
        .prog-table th {{ text-align: left; padding: 12px; border-bottom: 1px solid rgba(0,229,255,0.3); color: #94A3B8; font-family: 'Oswald'; }}
        .prog-table td {{ padding: 12px; border-bottom: 1px solid rgba(255,255,255,0.05); font-weight: 600; }}
        </style>
        <table class="prog-table">
            <tr><th>STAGE</th><th style="text-align:right;">PROBABILITY</th></tr>
            <tr><td>Reach Semi-Final</td><td style="text-align:right; color: #E2E8F0;">{team_data['semi_prob']*100:.1f}%</td></tr>
            <tr><td>Reach Final</td><td style="text-align:right; color: #E2E8F0;">{team_data['final_prob']*100:.1f}%</td></tr>
            <tr><td style="color: #FFD700;">WIN WORLD CUP</td><td style="text-align:right; color: #FFD700; font-size: 1.2rem;">{team_data['win_prob']*100:.1f}%</td></tr>
        </table>
        """, unsafe_allow_html=True)
        
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("""
<div style="text-align: center; margin-top: 50px; color: #94A3B8; font-size: 0.9rem;">
    Powered by Advanced Machine Learning & 10,000 Monte Carlo Simulations.<br>
    <span style="color: #00e5ff;">Apex Pitch Design System</span>
</div>
""", unsafe_allow_html=True)
