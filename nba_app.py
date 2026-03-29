import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from nba_api.stats.endpoints import (
    TeamGameLogs, LeagueStandings, CommonTeamRoster, PlayerGameLog,
    ScoreboardV3
)
from nba_api.stats.static import teams
import requests
import time
import json
import os
from datetime import datetime, date
import calendar as _cal_lib

# ============================================
# PAGE CONFIG & SESSION STATE
# ============================================
st.set_page_config(page_title="EV Edge", layout="wide", page_icon="⚡")

if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True
if "show_home_team2" not in st.session_state:
    st.session_state.show_home_team2 = False
if "home_analytics" not in st.session_state:
    st.session_state.home_analytics = False
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "user_tier" not in st.session_state:
    st.session_state.user_tier = "free"
if "auth_mode" not in st.session_state:
    st.session_state.auth_mode = "landing"   # "landing" | "login" | "signup"

_d = st.session_state.dark_mode
_bg     = "#080C18" if _d else "#f0f4f8"
_bg2    = "#0D1220" if _d else "#ffffff"
_bg3    = "#141929" if _d else "#e8ecf2"
_txt    = "#e8edf5" if _d else "#1a2030"
_txt2   = "#9AAABB" if _d else "#5a6878"
_txt3   = "#c8d4e0" if _d else "#2a3545"
_bdr    = "#1e2d40" if _d else "#c8d4e0"
_head   = "#f0f6fc" if _d else "#080C18"
_card   = "#0D1525" if _d else "#ffffff"
_card2  = "#121d30" if _d else "#eef2f7"
_accent = "#00C8FF"
_accent2= "#0095CC"
_grey   = "#9AAABB"

st.markdown(f"""
<style>
    .stApp {{ background-color: {_bg}; color: {_txt}; }}
    [data-testid="stHeader"] {{ background-color: {_bg}; }}
    [data-testid="stSidebar"] {{ background-color: {_bg2}; border-right: 1px solid {_bdr}; }}
    .stApp, .stApp p, .stApp li, .stApp span,
    .stApp label, .stApp div {{ color: {_txt}; }}
    .stApp .stCaption, .stApp small {{ color: {_txt2} !important; }}
    .stApp h1, .stApp h2, .stApp h3, .stApp h4 {{ color: {_head}; }}
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] .stMarkdown p,
    [data-testid="stSidebar"] span {{ color: {_txt3} !important; }}
    .app-title {{
        font-size: 2.2rem; font-weight: 800;
        background: linear-gradient(135deg, #00C8FF, #0095CC, #005F99);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        margin-bottom: 0; padding-bottom: 0;
    }}
    .app-subtitle {{ color: {_txt2}; font-size: 0.9rem; margin-top: 0; }}
    .score-card {{
        background: linear-gradient(135deg, {_card}, {_card2});
        border: 1px solid {_bdr}; border-radius: 12px;
        padding: 16px; margin: 6px 0; text-align: center;
    }}
    .score-card .team-name {{ color: {_head}; font-size: 1rem; font-weight: 600; }}
    .score-card .score {{ color: #00C8FF; font-size: 2rem; font-weight: 800; }}
    .score-card .status {{ color: #7ee787; font-size: 0.8rem; font-weight: 600; }}
    .score-card .status-final {{ color: {_txt2}; }}
    .score-card .status-live {{ color: #00C8FF; animation: pulse 1.5s infinite; }}
    @keyframes pulse {{ 0%,100% {{ opacity: 1; }} 50% {{ opacity: 0.5; }} }}
    [data-testid="stMetric"] {{
        background: {_bg2}; border: 1px solid {_bdr};
        border-radius: 8px; padding: 12px;
    }}
    [data-testid="stMetricValue"] {{ color: {_head} !important; font-size: 1.4rem !important; }}
    [data-testid="stMetricLabel"] {{ color: {_txt2} !important; font-weight: 600; }}
    [data-testid="stMetricDelta"] {{ font-weight: 600; }}
    .stTabs [data-baseweb="tab-list"] {{ gap: 4px; background-color: {_bg2}; border-radius: 8px; padding: 4px; }}
    .stTabs [data-baseweb="tab"] {{
        color: {_txt2}; background-color: transparent; border-radius: 6px;
        font-weight: 600; font-size: 0.85rem;
    }}
    .stTabs [aria-selected="true"] {{ background-color: {_bg3}; color: #00C8FF; }}
    [data-testid="stDataFrame"] {{ border: 1px solid {_bdr}; border-radius: 8px; }}
    .stSelectbox label, .stTextInput label,
    .stNumberInput label, .stDateInput label,
    .stSlider label {{ color: {_txt3} !important; font-weight: 500; }}
    .stTextInput input, .stNumberInput input {{
        background-color: {_bg3}; color: {_txt};
        border: 1px solid {_bdr}; border-radius: 6px;
    }}
    .stButton > button {{
        background: linear-gradient(135deg, #00C8FF, #0095CC);
        color: #080C18; border: none; border-radius: 8px;
        font-weight: 700; transition: all 0.2s;
    }}
    .stButton > button:hover {{ transform: translateY(-1px); box-shadow: 0 4px 12px rgba(0,200,255,0.4); }}
    [data-testid="stExpander"] {{ background-color: {_bg2}; border: 1px solid {_bdr}; border-radius: 8px; }}
    [data-testid="stExpander"] summary {{ color: {_txt3} !important; font-weight: 600; }}
    hr {{ border-color: {_bdr}; }}
    [data-testid="stForm"] {{ background-color: {_bg2}; border: 1px solid {_bdr}; border-radius: 8px; padding: 16px; }}
    [data-testid="stNotification"] {{ color: {_txt} !important; }}
    .injury-out {{ color: #f85149; font-weight: 600; }}
    .injury-dtd {{ color: #00C8FF; font-weight: 600; }}
    .injury-probable {{ color: #7ee787; font-weight: 600; }}
    .team-panel {{
        background: {_bg2}; border: 1px solid {_bdr};
        border-radius: 12px; padding: 16px 20px; margin-bottom: 12px;
    }}
</style>
""", unsafe_allow_html=True)

_hdr_l, _hdr_r = st.columns([9, 3])
with _hdr_l:
    st.markdown('<p class="app-title">⚡ EV Edge</p>', unsafe_allow_html=True)
    st.markdown('<p class="app-subtitle">Live 2025-26 season • Scores • Stats • Odds • Sharp Analytics</p>', unsafe_allow_html=True)
with _hdr_r:
    _nav_cols = st.columns([2, 2, 1])
    with _nav_cols[0]:
        if st.session_state.logged_in:
            if st.button(f"👤 {st.session_state.username}", key="btn_profile"):
                pass
        else:
            if st.button("Log In", key="btn_login_nav"):
                st.session_state.auth_mode = "login"
                st.rerun()
    with _nav_cols[1]:
        if not st.session_state.logged_in:
            if st.button("Sign Up", key="btn_signup_nav"):
                st.session_state.auth_mode = "signup"
                st.rerun()
        else:
            if st.button("Log Out", key="btn_logout_nav"):
                st.session_state.logged_in = False
                st.session_state.username = ""
                st.session_state.user_tier = "free"
                st.session_state.auth_mode = "landing"
                st.rerun()
    with _nav_cols[2]:
        st.toggle("🌙", key="dark_mode", help="Dark / Light mode")

# ============================================
# DATA FILES
# ============================================
PREDICTIONS_FILE = "prediction_log.json"
BANKROLL_FILE    = "bankroll_log.json"
CLV_FILE         = "clv_log.json"
USERS_FILE       = "users_ev.json"

def load_json(fp):
    if os.path.exists(fp):
        with open(fp, "r") as f: return json.load(f)
    return []
def save_json(fp, data):
    with open(fp, "w") as f: json.dump(data, f, indent=2)

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f: return json.load(f)
    return {}

def save_users(users):
    with open(USERS_FILE, "w") as f: json.dump(users, f, indent=2)

def auth_login(username, password):
    users = load_users()
    u = users.get(username.lower())
    if u and u["password"] == password:
        return True, u.get("tier", "free")
    return False, None

def auth_signup(username, password, tier="free"):
    users = load_users()
    if username.lower() in users:
        return False, "Username already taken."
    users[username.lower()] = {"password": password, "tier": tier, "created": str(date.today())}
    save_users(users)
    return True, "Account created!"

# ============================================
# API FUNCTIONS
# ============================================
@st.cache_data(ttl=3600)
def get_team_list():
    return teams.get_teams()

@st.cache_data(ttl=3600)
def get_standings():
    return LeagueStandings(season="2025-26").get_data_frames()[0]

@st.cache_data(ttl=3600)
def get_team_games(team_id):
    time.sleep(1.0)
    return TeamGameLogs(team_id_nullable=str(team_id), season_nullable="2025-26", season_type_nullable="Regular Season").get_data_frames()[0]

@st.cache_data(ttl=3600)
def get_roster(team_id):
    time.sleep(0.6)
    return CommonTeamRoster(team_id=str(team_id), season="2025-26").get_data_frames()[0]

@st.cache_data(ttl=3600)
def get_player_game_log(player_id):
    time.sleep(0.6)
    return PlayerGameLog(player_id=str(player_id), season="2025-26").get_data_frames()[0]

@st.cache_data(ttl=120)
def get_todays_scoreboard():
    try:
        today = date.today().strftime("%Y-%m-%d")
        sb = ScoreboardV3(game_date=today, league_id="00")
        return sb.get_dict()
    except:
        return None

@st.cache_data(ttl=120)
def get_live_boxscore(game_id):
    try:
        url = f"https://cdn.nba.com/static/json/liveData/boxscore/boxscore_{game_id}.json"
        resp = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        if resp.status_code == 200:
            return resp.json()
    except:
        pass
    return None

def get_live_odds(api_key):
    if not api_key: return None
    try:
        r = requests.get("https://api.the-odds-api.com/v4/sports/basketball_nba/odds",
            params={"apiKey": api_key, "regions": "us", "markets": "h2h,spreads,totals", "oddsFormat": "american"}, timeout=10)
        return r.json() if r.status_code == 200 else None
    except: return None

@st.cache_data(ttl=900)
def get_injuries():
    try:
        r = requests.get("https://www.basketball-reference.com/friv/injuries.fcgi",
            timeout=10, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"})
        if r.status_code == 200:
            dfs = pd.read_html(r.text)
            if len(dfs) > 0: return dfs[0]
    except: pass
    return None

def american_to_implied(odds):
    if odds < 0: return round(abs(odds) / (abs(odds) + 100) * 100, 1)
    return round(100 / (odds + 100) * 100, 1)

# ── Model helpers ─────────────────────────────────────────────────────────────

def calc_elo_ratings(standings_df):
    """Estimate Elo from season win% + point differential (no per-game API needed)."""
    df = standings_df.copy()
    df["WinPCT"]      = pd.to_numeric(df["WinPCT"],      errors="coerce").fillna(0.5)
    df["DiffPointsPG"]= pd.to_numeric(df["DiffPointsPG"],errors="coerce").fillna(0)
    df["elo"] = 1500 + (df["WinPCT"] - 0.5)*800 + df["DiffPointsPG"]*12
    df["elo"] = df["elo"].round(0).astype(int)
    return df[["TeamCity","TeamName","Conference","Record","WinPCT","DiffPointsPG","elo"]]\
              .sort_values("elo", ascending=False).reset_index(drop=True)

def elo_win_prob(elo_team, elo_opp, home=True):
    """Win probability from Elo difference; home court worth ~65 Elo points."""
    adj = 65 if home else 0
    return round(1 / (1 + 10 ** ((elo_opp - elo_team - adj) / 400)) * 100, 1)

def calc_four_factors(games_df):
    """Offensive Four Factors from a TeamGameLog dataframe."""
    g = games_df
    fga  = g["FGA"].sum();  fgm  = g["FGM"].sum()
    fg3m = g["FG3M"].sum(); fta  = g["FTA"].sum()
    oreb = g["OREB"].sum(); dreb = g["DREB"].sum(); tov = g["TOV"].sum()
    efg      = (fgm + 0.5*fg3m) / fga                         if fga > 0 else 0
    tov_rate = tov / (fga + 0.44*fta + tov)                   if (fga+0.44*fta+tov)>0 else 0
    oreb_pct = oreb / (oreb + dreb)                            if (oreb+dreb) > 0 else 0
    ftr      = fta / fga                                       if fga > 0 else 0
    return {"eFG%": round(efg*100,1), "TOV%": round(tov_rate*100,1),
            "OREB%": round(oreb_pct*100,1), "FTR": round(ftr,3)}

def ff_win_prob(ff1, ff2):
    """Win probability for team1 using Four Factors composite (logistic)."""
    efg_edge  = (ff1["eFG%"]  - ff2["eFG%"])  / 5.0
    tov_edge  = (ff2["TOV%"]  - ff1["TOV%"])  / 3.0   # lower TOV is better
    oreb_edge = (ff1["OREB%"] - ff2["OREB%"]) / 5.0
    ftr_edge  = (ff1["FTR"]   - ff2["FTR"])   / 0.05
    composite = efg_edge*0.40 + tov_edge*0.25 + oreb_edge*0.20 + ftr_edge*0.15
    prob = 1 / (1 + 2.71828**(-composite * 2.5))
    return round(prob * 100, 1)

def calc_market_factors(games_df):
    """Rest days, back-to-back flag, and home/road splits from a game log."""
    if len(games_df) < 2:
        return {"rest_days": "N/A", "b2b": False, "home_record": "N/A", "away_record": "N/A",
                "home_wpct": 0, "away_wpct": 0, "last_b2b_loss": False}
    gf = games_df.copy()
    gf["GAME_DATE"] = pd.to_datetime(gf["GAME_DATE"])
    gf = gf.sort_values("GAME_DATE", ascending=False)
    last  = gf.iloc[0]; prev = gf.iloc[1]
    rest_days = (date.today() - last["GAME_DATE"].date()).days
    b2b = int((last["GAME_DATE"].date() - prev["GAME_DATE"].date()).days) == 1
    hg = gf[gf["MATCHUP"].str.contains("vs\.", na=False)]
    ag = gf[gf["MATCHUP"].str.contains("@",    na=False)]
    hw = int((hg["WL"]=="W").sum()); hl = int((hg["WL"]=="L").sum())
    aw = int((ag["WL"]=="W").sum()); al = int((ag["WL"]=="L").sum())
    return {"rest_days": rest_days, "b2b": b2b,
            "home_record": f"{hw}-{hl}", "away_record": f"{aw}-{al}",
            "home_wpct": round(hw/(hw+hl)*100,1) if hw+hl>0 else 0,
            "away_wpct": round(aw/(aw+al)*100,1) if aw+al>0 else 0}

def clv_calc(bet_odds, closing_odds):
    """CLV% = implied_prob(closing) – implied_prob(bet). Positive = beating the market."""
    def _imp(o):
        o = int(o)
        return abs(o)/(abs(o)+100) if o<0 else 100/(o+100)
    return round((_imp(closing_odds) - _imp(bet_odds)) * 100, 2)

PLOTLY_THEME = dict(
    template="plotly_dark" if _d else "plotly_white",
    paper_bgcolor=_bg, plot_bgcolor=_bg,
    font=dict(color=_txt2),
    xaxis=dict(gridcolor=_bdr), yaxis=dict(gridcolor=_bdr)
)

# ============================================
# SIDEBAR
# ============================================
nba_teams = get_team_list()
team_names = sorted([t["full_name"] for t in nba_teams])

# Default team — used as starting index for in-tab selectors
team1_name = "Oklahoma City Thunder"
team1 = next(t for t in nba_teams if t["full_name"] == team1_name)
team2_name = team_names[0]
team2 = nba_teams[0]

st.sidebar.markdown("### ⚙️ Settings")
st.sidebar.divider()
st.sidebar.markdown("### 🔑 Odds API")
odds_api_key = st.sidebar.text_input("API Key", type="password", help="Free at the-odds-api.com")

# ============================================
# LANDING / AUTH GATE
# ============================================
if not st.session_state.logged_in:
    _am = st.session_state.auth_mode

    # ── Shared page CSS ────────────────────────────────────────────────────
    st.markdown(f"""
    <style>
    .lp-hero {{ text-align:center; padding: 60px 20px 30px; }}
    .lp-logo {{ font-size:4rem; font-weight:900;
        background: linear-gradient(135deg,#00C8FF,#0095CC,#005F99);
        -webkit-background-clip:text; -webkit-text-fill-color:transparent; }}
    .lp-tagline {{ color:{_txt2}; font-size:1.15rem; margin-top:8px; }}
    .tier-card {{
        background: linear-gradient(160deg,{_card},{_card2});
        border:1px solid {_bdr}; border-radius:16px;
        padding:28px 20px; text-align:center; position:relative;
        transition: transform .2s;
    }}
    .tier-card:hover {{ transform: translateY(-4px); }}
    .tier-card.popular {{ border-color:#00C8FF; box-shadow:0 0 24px rgba(0,200,255,.25); }}
    .tier-badge {{
        position:absolute; top:-12px; left:50%; transform:translateX(-50%);
        background:#00C8FF; color:#080C18; font-size:.7rem; font-weight:800;
        padding:3px 12px; border-radius:999px; letter-spacing:.08em;
    }}
    .tier-name {{ color:{_head}; font-size:1.3rem; font-weight:800; margin-bottom:6px; }}
    .tier-price {{ color:#00C8FF; font-size:2.4rem; font-weight:900; line-height:1; }}
    .tier-period {{ color:{_txt2}; font-size:.85rem; }}
    .tier-feat {{ color:{_txt3}; font-size:.88rem; text-align:left; margin:14px 0; line-height:1.8; }}
    .feat-check {{ color:#00C8FF; }}
    .feat-x {{ color:#555e6e; }}
    .auth-form {{ max-width:420px; margin:0 auto; padding:32px;
        background:{_card}; border:1px solid {_bdr}; border-radius:16px; }}
    .auth-title {{ color:{_head}; font-size:1.6rem; font-weight:800; margin-bottom:4px; }}
    .auth-sub {{ color:{_txt2}; font-size:.9rem; margin-bottom:20px; }}
    </style>
    """, unsafe_allow_html=True)

    if _am == "landing":
        # ── Hero ───────────────────────────────────────────────────────────
        st.markdown("""
        <div class="lp-hero">
            <div class="lp-logo">⚡ EV Edge</div>
            <div class="lp-tagline">Sharp NBA analytics. Beat the closing line. Edge the market.</div>
        </div>
        """, unsafe_allow_html=True)

        # ── Feature highlights ─────────────────────────────────────────────
        _f1, _f2, _f3, _f4 = st.columns(4)
        for _col, _icon, _label in [
            (_f1, "🔴", "Live Scores & Box Scores"),
            (_f2, "🧠", "Elo + Four Factors Models"),
            (_f3, "⚡", "EV Calculator & CLV Tracker"),
            (_f4, "💵", "Bankroll & P&L Calendar"),
        ]:
            with _col:
                st.markdown(f"""
                <div style="background:{_card};border:1px solid {_bdr};border-radius:12px;
                     padding:18px;text-align:center;margin-bottom:8px;">
                    <div style="font-size:2rem;">{_icon}</div>
                    <div style="color:{_txt3};font-size:.85rem;margin-top:6px;">{_label}</div>
                </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Pricing cards ──────────────────────────────────────────────────
        st.markdown(f"<h2 style='text-align:center;color:{_head};'>Choose Your Plan</h2>", unsafe_allow_html=True)
        _pc1, _pc2, _pc3 = st.columns(3)

        with _pc1:
            st.markdown(f"""
            <div class="tier-card">
                <div class="tier-name">Free</div>
                <div class="tier-price">$0</div>
                <div class="tier-period">forever</div>
                <div class="tier-feat">
                    <span class="feat-check">✓</span> Live Scores & Standings<br>
                    <span class="feat-check">✓</span> Team Stats & Compare<br>
                    <span class="feat-check">✓</span> Injury Reports<br>
                    <span class="feat-x">✗</span> EV Calculator<br>
                    <span class="feat-x">✗</span> Models (Elo, FF, CLV)<br>
                    <span class="feat-x">✗</span> Bankroll Tracker<br>
                    <span class="feat-x">✗</span> Odds Feed<br>
                </div>
            </div>""", unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Get Started Free", key="cta_free"):
                st.session_state.auth_mode = "signup"
                st.rerun()

        with _pc2:
            st.markdown(f"""
            <div class="tier-card popular">
                <div class="tier-badge">MOST POPULAR</div>
                <div class="tier-name">Pro</div>
                <div class="tier-price">$19.99</div>
                <div class="tier-period">per month</div>
                <div class="tier-feat">
                    <span class="feat-check">✓</span> Everything in Free<br>
                    <span class="feat-check">✓</span> EV Calculator<br>
                    <span class="feat-check">✓</span> Elo & Four Factors Models<br>
                    <span class="feat-check">✓</span> Market Factors Analysis<br>
                    <span class="feat-check">✓</span> Bankroll Tracker & Calendar<br>
                    <span class="feat-check">✓</span> Live Odds Feed<br>
                    <span class="feat-x">✗</span> CLV Tracker<br>
                </div>
            </div>""", unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Start Pro — $19.99/mo", key="cta_pro"):
                st.session_state.auth_mode = "signup"
                st.rerun()

        with _pc3:
            st.markdown(f"""
            <div class="tier-card">
                <div class="tier-name">Elite</div>
                <div class="tier-price">$49.99</div>
                <div class="tier-period">per month</div>
                <div class="tier-feat">
                    <span class="feat-check">✓</span> Everything in Pro<br>
                    <span class="feat-check">✓</span> CLV Tracker (full history)<br>
                    <span class="feat-check">✓</span> Player-Level Model<br>
                    <span class="feat-check">✓</span> Prediction Log & Analytics<br>
                    <span class="feat-check">✓</span> Priority Data Refresh<br>
                    <span class="feat-check">✓</span> Early Access to New Features<br>
                    <span class="feat-check">✓</span> Discord Community Access<br>
                </div>
            </div>""", unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Go Elite — $49.99/mo", key="cta_elite"):
                st.session_state.auth_mode = "signup"
                st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        _lp_c1, _lp_c2, _lp_c3 = st.columns([3, 2, 3])
        with _lp_c2:
            if st.button("Already have an account? Log In →", key="cta_login"):
                st.session_state.auth_mode = "login"
                st.rerun()

    elif _am == "login":
        _ac, _bc = st.columns([1, 1])
        with _ac:
            st.markdown(f"""
            <div class="auth-form">
                <div class="auth-title">⚡ Welcome back</div>
                <div class="auth-sub">Log in to your EV Edge account</div>
            </div>""", unsafe_allow_html=True)
        with _bc:
            st.markdown("<br>", unsafe_allow_html=True)
            with st.form("login_form"):
                _li_user = st.text_input("Username")
                _li_pass = st.text_input("Password", type="password")
                _li_sub  = st.form_submit_button("Log In")
                if _li_sub:
                    _ok, _tier = auth_login(_li_user, _li_pass)
                    if _ok:
                        st.session_state.logged_in = True
                        st.session_state.username  = _li_user
                        st.session_state.user_tier = _tier
                        st.session_state.auth_mode = "app"
                        st.rerun()
                    else:
                        st.error("Invalid username or password.")
            if st.button("← Back to Home", key="login_back"):
                st.session_state.auth_mode = "landing"
                st.rerun()
            if st.button("Create an account →", key="login_to_signup"):
                st.session_state.auth_mode = "signup"
                st.rerun()

    elif _am == "signup":
        _ac, _bc = st.columns([1, 1])
        with _ac:
            st.markdown(f"""
            <div class="auth-form">
                <div class="auth-title">⚡ Join EV Edge</div>
                <div class="auth-sub">Create your free account — upgrade anytime</div>
            </div>""", unsafe_allow_html=True)
        with _bc:
            st.markdown("<br>", unsafe_allow_html=True)
            with st.form("signup_form"):
                _su_user = st.text_input("Choose a username")
                _su_pass = st.text_input("Password", type="password")
                _su_pass2= st.text_input("Confirm password", type="password")
                _su_tier = st.selectbox("Plan", ["free", "pro", "elite"],
                    format_func=lambda x: {"free":"Free","pro":"Pro — $19.99/mo","elite":"Elite — $49.99/mo"}[x])
                _su_sub  = st.form_submit_button("Create Account")
                if _su_sub:
                    if not _su_user.strip():
                        st.error("Username is required.")
                    elif _su_pass != _su_pass2:
                        st.error("Passwords do not match.")
                    elif len(_su_pass) < 6:
                        st.error("Password must be at least 6 characters.")
                    else:
                        _ok2, _msg = auth_signup(_su_user.strip(), _su_pass, _su_tier)
                        if _ok2:
                            st.success(_msg)
                            st.session_state.logged_in = True
                            st.session_state.username  = _su_user.strip()
                            st.session_state.user_tier = _su_tier
                            st.session_state.auth_mode = "app"
                            st.rerun()
                        else:
                            st.error(_msg)
            if st.button("← Back to Home", key="signup_back"):
                st.session_state.auth_mode = "landing"
                st.rerun()
            if st.button("Already have an account? Log In →", key="signup_to_login"):
                st.session_state.auth_mode = "login"
                st.rerun()

    st.stop()

# ============================================
# TABS
# ============================================
tab_live, tab_comp, tab_trends, tab_players, tab_odds, tab_predict, tab_injuries, tab_record, tab_ev, tab_models, tab_bank, tab_stand = st.tabs([
    "🔴 Live", "📊 Compare", "📈 Trends", "🏀 Players", "💰 Odds",
    "🎯 Predict", "🏥 Injuries", "📉 Record", "⚡ EV", "🧠 Models", "💵 Bankroll", "📋 Standings"
])

# ============================================
# TAB: LIVE SCOREBOARD
# ============================================
with tab_live:
    # ── Team selector panel ──────────────────────────────────────────────
    st.markdown('<div class="team-panel">', unsafe_allow_html=True)
    _lc1, _lc2, _lc3 = st.columns([4, 4, 2])
    with _lc1:
        live_t1 = st.selectbox("🏀 Team", team_names,
            index=team_names.index(team1_name), key="live_t1")
    with _lc2:
        if st.session_state.show_home_team2:
            live_t2 = st.selectbox("vs Team", team_names, key="live_t2",
                index=(team_names.index("Cleveland Cavaliers") if "Cleveland Cavaliers" in team_names else 0))
            live_t2_obj = next(t for t in nba_teams if t["full_name"] == live_t2)
            if st.button("✕ Remove", key="rm_live_t2"):
                st.session_state.show_home_team2 = False
                st.rerun()
        else:
            st.markdown(f"<div style='padding-top:28px'>", unsafe_allow_html=True)
            if st.button("➕ Add team", key="add_live_t2"):
                st.session_state.show_home_team2 = True
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
            live_t2 = None; live_t2_obj = None
    with _lc3:
        st.markdown("<div style='padding-top:28px'>", unsafe_allow_html=True)
        if st.button("🔍 View Analytics", type="primary", use_container_width=True, key="live_analytics_btn"):
            st.session_state.home_analytics = not st.session_state.home_analytics
        st.markdown("</div>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Inline team analytics ────────────────────────────────────────────
    if st.session_state.home_analytics:
        _at = next(t for t in nba_teams if t["full_name"] == live_t1)
        st.markdown(f"#### 📊 {live_t1} Analytics")
        try:
            _ag = get_team_games(_at["id"])
            if len(_ag) > 0:
                _aw=len(_ag[_ag["WL"]=="W"]); _al=len(_ag[_ag["WL"]=="L"])
                _ac1,_ac2,_ac3,_ac4=st.columns(4)
                _ac1.metric("Record",f"{_aw}-{_al}")
                _ac2.metric("PPG",round(_ag["PTS"].mean(),1))
                _ac3.metric("FG%",f"{round(_ag['FG_PCT'].mean()*100,1)}%")
                _ac4.metric("3PT%",f"{round(_ag['FG3_PCT'].mean()*100,1)}%")
                _ar=_ag.head(15).iloc[::-1].reset_index(drop=True)
                _ar["GN"]=range(1,len(_ar)+1); _ar["OPP"]=_ar["PTS"]-_ar["PLUS_MINUS"]
                _afig=go.Figure()
                _afig.add_trace(go.Scatter(x=_ar["GN"],y=_ar["PTS"],mode="lines+markers",name="Scored",line=dict(color="#00C8FF",width=2)))
                _afig.add_trace(go.Scatter(x=_ar["GN"],y=_ar["OPP"],mode="lines+markers",name="Allowed",line=dict(color="#f85149",width=2)))
                _afig.update_layout(title=f"{live_t1} — Last 15 Games",height=320,**PLOTLY_THEME)
                st.plotly_chart(_afig, use_container_width=True)
                st.dataframe(_ag.head(10)[["GAME_DATE","MATCHUP","WL","PTS","REB","AST","PLUS_MINUS"]].reset_index(drop=True),use_container_width=True,hide_index=True)
                if live_t2_obj:
                    st.markdown(f"#### 📊 {live_t2} Analytics")
                    _bg2g = get_team_games(live_t2_obj["id"])
                    if len(_bg2g) > 0:
                        _bw=len(_bg2g[_bg2g["WL"]=="W"]); _bl=len(_bg2g[_bg2g["WL"]=="L"])
                        _bc1,_bc2,_bc3,_bc4=st.columns(4)
                        _bc1.metric("Record",f"{_bw}-{_bl}")
                        _bc2.metric("PPG",round(_bg2g["PTS"].mean(),1))
                        _bc3.metric("FG%",f"{round(_bg2g['FG_PCT'].mean()*100,1)}%")
                        _bc4.metric("3PT%",f"{round(_bg2g['FG3_PCT'].mean()*100,1)}%")
                        st.dataframe(_bg2g.head(10)[["GAME_DATE","MATCHUP","WL","PTS","REB","AST","PLUS_MINUS"]].reset_index(drop=True),use_container_width=True,hide_index=True)
        except Exception as e:
            st.error(f"Error loading analytics: {e}")
        st.divider()

    # ── Scoreboard ───────────────────────────────────────────────────────
    st.markdown("### 🔴 Today's Games")
    _today_str = date.today().strftime("%Y-%m-%d")

    if st.button("🔄 Refresh Scores"):
        get_todays_scoreboard.clear()

    # Fetch fresh data
    _fresh_sb = get_todays_scoreboard()
    _fresh_games = (_fresh_sb["scoreboard"].get("games", [])
                    if _fresh_sb and "scoreboard" in _fresh_sb else [])

    # Merge fresh data into the stored game list (keyed by gameId).
    # This ensures finished games are never dropped when the API only
    # returns the currently-live game.
    _stored = {g["gameId"]: g for g in st.session_state.get("sb_games", [])}
    for g in _fresh_games:
        _stored[g["gameId"]] = g          # update score / status in place
    if _stored and st.session_state.get("sb_games_date") == _today_str or _fresh_games:
        if _fresh_games:                  # only commit when we got something new
            st.session_state["sb_games"] = list(_stored.values())
            st.session_state["sb_games_date"] = _today_str

    games_today = st.session_state.get("sb_games", []) if st.session_state.get("sb_games_date") == _today_str else []
    if not games_today and not _fresh_games:
        pass  # will hit the else branch below

    if games_today:
            cols = st.columns(min(len(games_today), 3))
            for i, game in enumerate(games_today):
                with cols[i % 3]:
                    home = game.get("homeTeam", {})
                    away = game.get("awayTeam", {})
                    status = game.get("gameStatusText", "")
                    game_id = game.get("gameId", "")

                    is_live = game.get("gameStatus", 1) == 2
                    is_final = game.get("gameStatus", 1) == 3
                    status_class = "status-live" if is_live else "status-final" if is_final else "status"
                    live_dot = "🔴 " if is_live else ""

                    st.markdown(f"""
                    <div class="score-card">
                        <div class="team-name">{away.get('teamCity','')} {away.get('teamName','')}</div>
                        <div class="score">{away.get('score', 0)}</div>
                        <div style="color:#8c959f; margin: 4px 0;">@</div>
                        <div class="team-name">{home.get('teamCity','')} {home.get('teamName','')}</div>
                        <div class="score">{home.get('score', 0)}</div>
                        <div class="{status_class}">{live_dot}{status}</div>
                    </div>
                    """, unsafe_allow_html=True)

                    if (is_live or is_final) and game_id:
                        with st.expander("📊 Box Score"):
                            box = get_live_boxscore(game_id)
                            if box and "game" in box:
                                for team_key in ["homeTeam", "awayTeam"]:
                                    t = box["game"].get(team_key, {})
                                    st.write(f"**{t.get('teamCity','')} {t.get('teamName','')}** — {t.get('score','')} pts")
                                    players = t.get("players", [])
                                    if players:
                                        pdata = []
                                        for p in players:
                                            s = p.get("statistics", {})
                                            if s.get("minutesCalculated", "PT00M") not in ("PT00M", "PT00M00.00S", ""):
                                                _raw_min = s.get("minutesCalculated","").replace("PT","").replace("S","")
                                                _mparts = _raw_min.split("M")
                                                _fmt_min = f"{int(_mparts[0])}:{int(float(_mparts[1] or 0)):02d}" if len(_mparts)==2 else _raw_min
                                                _fgm = s.get("fieldGoalsMade",0); _fga = s.get("fieldGoalsAttempted",0)
                                                _2pm = s.get("twoPointersMade",0); _2pa = s.get("twoPointersAttempted",0)
                                                _3pm = s.get("threePointersMade",0); _3pa = s.get("threePointersAttempted",0)
                                                _ftm = s.get("freeThrowsMade",0); _fta = s.get("freeThrowsAttempted",0)
                                                pdata.append({
                                                    "Player": p.get("name",""),
                                                    "MIN": _fmt_min,
                                                    "PTS": s.get("points",0),
                                                    "FGM-A": f"{_fgm}/{_fga}",
                                                    "FG%": f"{round(s.get('fieldGoalsPercentage',0)*100,0):.0f}%",
                                                    "2PM-A": f"{_2pm}/{_2pa}",
                                                    "3PM-A": f"{_3pm}/{_3pa}",
                                                    "3P%": f"{round(s.get('threePointersPercentage',0)*100,0):.0f}%",
                                                    "FTM-A": f"{_ftm}/{_fta}",
                                                    "REB": s.get("reboundsTotal",0),
                                                    "OREB": s.get("reboundsOffensive",0),
                                                    "AST": s.get("assists",0),
                                                    "STL": s.get("steals",0),
                                                    "BLK": s.get("blocks",0),
                                                    "TO": s.get("turnovers",0),
                                                    "+/-": s.get("plusMinusPoints",0),
                                                })
                                        if pdata:
                                            st.dataframe(pd.DataFrame(pdata), use_container_width=True, hide_index=True)
    else:
        st.info("No games scheduled today.")

# ============================================
# TAB: TEAM COMPARISON
# ============================================
with tab_comp:
    # Inline team selectors
    _csc1, _csc2 = st.columns(2)
    with _csc1:
        comp_t1_name = st.selectbox("Team 1", team_names, index=team_names.index(team1_name), key="comp_t1")
    with _csc2:
        _comp_t2_default = team_names.index("Cleveland Cavaliers") if "Cleveland Cavaliers" in team_names else 0
        comp_t2_name = st.selectbox("Team 2", team_names, index=_comp_t2_default, key="comp_t2")
    comp_t1 = next(t for t in nba_teams if t["full_name"] == comp_t1_name)
    comp_t2 = next(t for t in nba_teams if t["full_name"] == comp_t2_name)
    st.markdown(f"### {comp_t1_name} vs {comp_t2_name}")

    col1, col2 = st.columns(2)
    team_data = {}
    for col, team, name in [(col1, comp_t1, comp_t1_name), (col2, comp_t2, comp_t2_name)]:
        with col:
            st.markdown(f"**{name}**")
            try:
                g = get_team_games(team["id"])
                if len(g) > 0:
                    w=len(g[g["WL"]=="W"]); l=len(g[g["WL"]=="L"]); ppg=round(g["PTS"].mean(),1)
                    opp=round((g["PTS"]-g["PLUS_MINUS"]).mean(),1); pm=round(g["PLUS_MINUS"].mean(),1)
                    team_data[name] = {"wins":w,"losses":l,"ppg":ppg,"opp_ppg":opp,"games":g,"win_pct":w/(w+l)}
                    m1,m2=st.columns(2); m1.metric("Record",f"{w}-{l}"); m2.metric("+/-",f"{'+' if pm>0 else ''}{pm}")
                    m3,m4=st.columns(2); m3.metric("PPG",ppg); m4.metric("Opp PPG",opp)
                    m5,m6=st.columns(2); m5.metric("FG%",f"{round(g['FG_PCT'].mean()*100,1)}%"); m6.metric("3PT%",f"{round(g['FG3_PCT'].mean()*100,1)}%")
                    m7,m8=st.columns(2); m7.metric("REB",round(g["REB"].mean(),1)); m8.metric("AST",round(g["AST"].mean(),1))
                    st.write("**Last 5:**")
                    st.dataframe(g.head(5)[["GAME_DATE","MATCHUP","WL","PTS","PLUS_MINUS"]].reset_index(drop=True), use_container_width=True)
            except Exception as e: st.error(f"Error: {e}")
    if len(team_data)==2:
        st.divider(); st.markdown("#### ⚔️ Head-to-Head")
        try:
            h2h=team_data[comp_t1_name]["games"]; h2h=h2h[h2h["MATCHUP"].str.contains(comp_t2["abbreviation"])]
            if len(h2h)>0:
                st.write(f"**Series:** {comp_t1_name} {len(h2h[h2h['WL']=='W'])} - {len(h2h[h2h['WL']=='L'])} {comp_t2_name}")
                st.dataframe(h2h[["GAME_DATE","MATCHUP","WL","PTS","REB","AST","PLUS_MINUS"]].reset_index(drop=True), use_container_width=True)
            else: st.info("Haven't played each other yet.")
        except: pass

# ============================================
# TAB: TRENDS
# ============================================
with tab_trends:
    st.markdown("### 📈 Trend Charts")
    tt=st.selectbox("Team",team_names,key="tt"); tn=next(t for t in nba_teams if t["full_name"]==tt); ng=st.slider("Games",5,30,10)
    try:
        tg=get_team_games(tn["id"])
        if len(tg)>0:
            r=tg.head(ng).iloc[::-1].reset_index(drop=True); r["GN"]=range(1,len(r)+1); r["OPP"]=r["PTS"]-r["PLUS_MINUS"]
            fig=go.Figure()
            fig.add_trace(go.Scatter(x=r["GN"],y=r["PTS"],mode="lines+markers",name="Scored",line=dict(color="#00C8FF",width=3)))
            fig.add_trace(go.Scatter(x=r["GN"],y=r["OPP"],mode="lines+markers",name="Allowed",line=dict(color="#f85149",width=3)))
            fig.update_layout(title=f"Scoring (Last {ng})",height=400,**PLOTLY_THEME)
            st.plotly_chart(fig, use_container_width=True)
            fig2=go.Figure()
            fig2.add_trace(go.Bar(x=r["GN"],y=r["PLUS_MINUS"],marker_color=["#7ee787" if x>0 else "#f85149" for x in r["PLUS_MINUS"]]))
            fig2.add_hline(y=0,line_color="#484f58"); fig2.update_layout(title="+/- Margin",height=300,**PLOTLY_THEME)
            st.plotly_chart(fig2, use_container_width=True)
    except Exception as e: st.error(f"Error: {e}")

# ============================================
# TAB: PLAYERS
# ============================================
with tab_players:
    st.markdown("### 🏀 Player Stats")
    ptn=st.selectbox("Team",team_names,key="pt"); pt=next(t for t in nba_teams if t["full_name"]==ptn)
    try:
        ros=get_roster(pt["id"]); sel=st.selectbox("Player",ros["PLAYER"].tolist())
        pr=ros[ros["PLAYER"]==sel].iloc[0]
        st.write(f"**{pr['POSITION']}** | #{pr['NUM']} | {pr['EXP']} yrs exp")
        try:
            gl=get_player_game_log(pr["PLAYER_ID"])
            if len(gl)>0:
                a1,a2,a3,a4,a5=st.columns(5)
                a1.metric("PPG",round(gl["PTS"].mean(),1)); a2.metric("RPG",round(gl["REB"].mean(),1)); a3.metric("APG",round(gl["AST"].mean(),1))
                a4.metric("FG%",f"{round(gl['FG_PCT'].mean()*100,1)}%"); a5.metric("3P%",f"{round(gl['FG3_PCT'].mean()*100,1)}%")
                st.divider(); st.markdown("#### 🎲 Prop Projections")
                l10=gl.head(10); l5=gl.head(5); pd_list=[]
                for p,c in [("Points","PTS"),("Rebounds","REB"),("Assists","AST"),("Threes","FG3M")]:
                    s=gl[c].mean(); t10=l10[c].mean(); t5=l5[c].mean(); proj=s*0.4+t10*0.35+t5*0.25
                    trend="🔥" if t5>s*1.1 else "🥶" if t5<s*0.9 else "➡️"
                    pd_list.append({"Prop":p,"Season":round(s,1),"L10":round(t10,1),"L5":round(t5,1),"Proj":round(proj,1),"":trend})
                st.dataframe(pd.DataFrame(pd_list),use_container_width=True,hide_index=True)
                cg=gl.head(20).iloc[::-1].reset_index(drop=True); cg["GN"]=range(1,len(cg)+1)
                fp=go.Figure(); fp.add_trace(go.Bar(x=cg["GN"],y=cg["PTS"],marker_color=["#7ee787" if w=="W" else "#f85149" for w in cg["WL"]]))
                fp.add_hline(y=gl["PTS"].mean(),line_dash="dash",line_color="#00C8FF",annotation_text=f"Avg: {round(gl['PTS'].mean(),1)}")
                fp.update_layout(title=f"{sel} - Scoring",height=350,**PLOTLY_THEME)
                st.plotly_chart(fp, use_container_width=True)
                st.markdown("#### Recent Games")
                st.dataframe(gl.head(10)[["GAME_DATE","MATCHUP","WL","MIN","PTS","REB","AST","STL","BLK","PLUS_MINUS"]].reset_index(drop=True),use_container_width=True)
        except Exception as e: st.error(f"Error: {e}")
    except Exception as e: st.error(f"Error: {e}")

# ============================================
# TAB: ODDS & LINE SHOPPING
# ============================================
with tab_odds:
    st.markdown("### 💰 Live Odds & Line Shopping")
    st.caption("🟢 Green = best available line")
    if not odds_api_key:
        st.warning("Enter your API key in the sidebar → [Get free key](https://the-odds-api.com)")
    else:
        if st.button("🔄 Fetch Odds"):
            od=get_live_odds(odds_api_key)
            if od and len(od)>0:
                for game in od:
                    with st.expander(f"🏀 {game['away_team']} @ {game['home_team']}",expanded=True):
                        if game.get("bookmakers"):
                            rows=[]
                            for book in game["bookmakers"]:
                                row={"Book":book["title"]}
                                for m in book.get("markets",[]):
                                    if m["key"]=="h2h":
                                        for o in m["outcomes"]:
                                            if o["name"]==game["home_team"]: row["Home"]=o["price"]
                                            else: row["Away"]=o["price"]
                                    elif m["key"]=="spreads":
                                        for o in m["outcomes"]:
                                            if o["name"]==game["home_team"]: row["Spread"]=o.get("point",""); row["Sprd Odds"]=o["price"]
                                    elif m["key"]=="totals":
                                        for o in m["outcomes"]:
                                            if o["name"]=="Over": row["O/U"]=o.get("point",""); row["Over"]=o["price"]
                                            else: row["Under"]=o["price"]
                                rows.append(row)
                            if rows:
                                odf=pd.DataFrame(rows)
                                def hl(df):
                                    s=pd.DataFrame("",index=df.index,columns=df.columns)
                                    for c in ["Home","Away","Sprd Odds","Over","Under"]:
                                        if c in df.columns:
                                            try: n=pd.to_numeric(df[c],errors="coerce"); s.loc[n.idxmax(),c]="background-color: #238636; color: white; font-weight: bold"
                                            except: pass
                                    return s
                                st.dataframe(odf.style.apply(hl,axis=None),use_container_width=True,hide_index=True)
            elif od is not None: st.info("No games with odds right now.")
            else: st.error("Check your API key.")

# ============================================
# TAB: PREDICTION
# ============================================
with tab_predict:
    st.markdown("### 🎯 Matchup Predictor")
    _pc1, _pc2 = st.columns(2)
    with _pc1:
        pred_t1_name = st.selectbox("Team 1", team_names, index=team_names.index(team1_name), key="pred_t1")
    with _pc2:
        _pred_t2_default = team_names.index("Cleveland Cavaliers") if "Cleveland Cavaliers" in team_names else 0
        pred_t2_name = st.selectbox("Team 2", team_names, index=_pred_t2_default, key="pred_t2")
    pred_t1 = next(t for t in nba_teams if t["full_name"] == pred_t1_name)
    pred_t2 = next(t for t in nba_teams if t["full_name"] == pred_t2_name)
    st.caption(f"{pred_t1_name} vs {pred_t2_name}")
    if st.button("Run Prediction",type="primary"):
        try:
            g1=get_team_games(pred_t1["id"]); g2=get_team_games(pred_t2["id"])
            if len(g1)>0 and len(g2)>0:
                t1p=g1["PTS"].mean(); t1o=(g1["PTS"]-g1["PLUS_MINUS"]).mean(); t1w=len(g1[g1["WL"]=="W"])/len(g1); t1r=len(g1.head(10)[g1.head(10)["WL"]=="W"])/10
                t2p=g2["PTS"].mean(); t2o=(g2["PTS"]-g2["PLUS_MINUS"]).mean(); t2w=len(g2[g2["WL"]=="W"])/len(g2); t2r=len(g2.head(10)[g2.head(10)["WL"]=="W"])/10
                t1e=(t1p+t2o)/2; t2e=(t2p+t1o)/2
                t1s=(t1w*0.35)+(t1r*0.25)+((t1p-t1o)/20*0.4); t2s=(t2w*0.35)+(t2r*0.25)+((t2p-t2o)/20*0.4)
                ts=t1s+t2s; t1pr=t1s/ts*100 if ts>0 else 50; t2pr=t2s/ts*100 if ts>0 else 50
                winner=pred_t1_name if t1pr>t2pr else pred_t2_name
                p1,pm,p2=st.columns([2,1,2])
                with p1: st.metric(pred_t1_name,f"{round(t1pr,1)}%"); st.metric("Exp Score",round(t1e,1))
                with pm: st.markdown(f"<div style='text-align:center;padding-top:20px;color:{_txt2};font-size:1.5rem;font-weight:800;'>VS</div>",unsafe_allow_html=True); st.metric("Total",round(t1e+t2e,1))
                with p2: st.metric(pred_t2_name,f"{round(t2pr,1)}%"); st.metric("Exp Score",round(t2e,1))
                st.success(f"**{winner}** wins by ~{round(abs(t1e-t2e),1)}")
                with st.form("log_pred"):
                    gd=st.date_input("Game Date")
                    if st.form_submit_button("💾 Save Prediction"):
                        preds=load_json(PREDICTIONS_FILE)
                        preds.append({"date":str(gd),"team1":pred_t1_name,"team2":pred_t2_name,"predicted_winner":winner,"t1_prob":round(t1pr,1),"t2_prob":round(t2pr,1),"t1_expected":round(t1e,1),"t2_expected":round(t2e,1),"result":"pending","actual_winner":""})
                        save_json(PREDICTIONS_FILE,preds); st.success("Saved!")
                if odds_api_key:
                    st.divider(); st.markdown("#### 💰 Value Analysis")
                    od=get_live_odds(odds_api_key)
                    if od:
                        for g in od:
                            if pred_t1["full_name"] in [g.get("home_team"),g.get("away_team")] and pred_t2["full_name"] in [g.get("home_team"),g.get("away_team")]:
                                for b in g.get("bookmakers",[])[:1]:
                                    for m in b.get("markets",[]):
                                        if m["key"]=="h2h":
                                            for o in m["outcomes"]:
                                                imp=american_to_implied(o["price"]); mp=t1pr if o["name"]==pred_t1_name else t2pr; edge=round(mp-imp,1)
                                                st.write(f"{'✅' if edge>0 else '❌'} **{o['name']}** | Book: {imp}% | Model: {round(mp,1)}% | Edge: {'+' if edge>0 else ''}{edge}%")
        except Exception as e: st.error(f"Error: {e}")

# ============================================
# TAB: INJURIES
# ============================================
with tab_injuries:
    st.markdown("### 🏥 Injury Report")
    if st.button("🔄 Load Injuries"):
        st.session_state["inj_data"] = get_injuries()
    inj = st.session_state.get("inj_data")
    if inj is not None:
        if isinstance(inj, pd.DataFrame) and len(inj) > 0:
            search = st.text_input("🔍 Search player or team")
            filtered = inj[inj.apply(lambda r: r.astype(str).str.contains(search, case=False).any(), axis=1)] if search else inj
            st.dataframe(filtered, use_container_width=True, hide_index=True)
            st.caption(f"{len(filtered)} injuries listed")
        else:
            st.warning("Injury data unavailable right now. Basketball Reference may be down.")

# ============================================
# TAB: MODEL RECORD
# ============================================
with tab_record:
    st.markdown("### 📉 Prediction Record")
    preds=load_json(PREDICTIONS_FILE)
    if not preds: st.info("No predictions yet. Save from Predict tab.")
    else:
        pending=[p for p in preds if p["result"]=="pending"]
        if pending:
            st.markdown("#### Update Results")
            for i,p in enumerate(pending):
                with st.expander(f"{p['date']}: {p['team1']} vs {p['team2']} → {p['predicted_winner']}"):
                    c1,c2=st.columns(2)
                    if c1.button(f"✅ Correct",key=f"w{i}"):
                        for x in preds:
                            if x["date"]==p["date"] and x["team1"]==p["team1"]: x["result"]="correct"; x["actual_winner"]=p["predicted_winner"]
                        save_json(PREDICTIONS_FILE,preds); st.rerun()
                    loser=p["team2"] if p["predicted_winner"]==p["team1"] else p["team1"]
                    if c2.button(f"❌ Wrong",key=f"l{i}"):
                        for x in preds:
                            if x["date"]==p["date"] and x["team1"]==p["team1"]: x["result"]="incorrect"; x["actual_winner"]=loser
                        save_json(PREDICTIONS_FILE,preds); st.rerun()
        cor=len([p for p in preds if p["result"]=="correct"]); inc=len([p for p in preds if p["result"]=="incorrect"]); td=cor+inc
        s1,s2,s3=st.columns(3)
        s1.metric("Record",f"{cor}-{inc}" if td>0 else "0-0"); s2.metric("Win%",f"{round(cor/td*100,1)}%" if td>0 else "—"); s3.metric("Pending",len(pending))
        if td>0:
            rt=[]; rc=0; rn=0
            for p in preds:
                if p["result"] in ["correct","incorrect"]:
                    rn+=1; rc+=1 if p["result"]=="correct" else 0; rt.append({"#":rn,"Win%":round(rc/rn*100,1)})
            if rt:
                rtdf=pd.DataFrame(rt); fig=go.Figure()
                fig.add_trace(go.Scatter(x=rtdf["#"],y=rtdf["Win%"],mode="lines+markers",line=dict(color="#00C8FF",width=3),fill="tozeroy",fillcolor="rgba(0,200,255,0.1)"))
                fig.add_hline(y=50,line_dash="dash",line_color="#f85149",annotation_text="50%")
                fig.update_layout(title="Win Rate Over Time",height=350,**PLOTLY_THEME)
                st.plotly_chart(fig,use_container_width=True)
        st.dataframe(pd.DataFrame(preds),use_container_width=True,hide_index=True)
        if st.button("🗑️ Clear"): save_json(PREDICTIONS_FILE,[]); st.rerun()

# ============================================
# TAB: EV CALCULATOR
# ============================================
with tab_ev:
    st.markdown("### ⚡ Expected Value Calculator")
    st.caption("Enter your model's win probability and the sportsbook odds to see if a bet has positive EV.")

    ev_c1, ev_c2 = st.columns(2)
    with ev_c1:
        st.markdown("#### Bet Details")
        ev_odds = st.number_input("American Odds", value=-110, step=1,
                                  help="e.g. -110, +150, -220")
        ev_model_pct = st.slider("Your Model Win %", min_value=0.0, max_value=100.0,
                                 value=55.0, step=0.5)
        ev_stake = st.number_input("Stake ($)", min_value=1.0, value=100.0, step=10.0)

    with ev_c2:
        st.markdown("#### Results")
        # Implied probability from odds
        if ev_odds < 0:
            implied = abs(ev_odds) / (abs(ev_odds) + 100)
            profit_if_win = ev_stake * (100 / abs(ev_odds))
        else:
            implied = 100 / (ev_odds + 100)
            profit_if_win = ev_stake * (ev_odds / 100)

        model_prob = ev_model_pct / 100
        ev_dollar = (model_prob * profit_if_win) - ((1 - model_prob) * ev_stake)
        edge_pct = (model_prob - implied) * 100
        roi_pct = (ev_dollar / ev_stake) * 100

        # Kelly criterion (full Kelly)
        if ev_odds < 0:
            b = 100 / abs(ev_odds)
        else:
            b = ev_odds / 100
        kelly_pct = max(0.0, (b * model_prob - (1 - model_prob)) / b) * 100
        kelly_quarter = kelly_pct / 4  # quarter-Kelly is more practical

        ev_color = "#7ee787" if ev_dollar > 0 else "#f85149"
        edge_color = "#7ee787" if edge_pct > 0 else "#f85149"

        r1c1, r1c2 = st.columns(2)
        r1c1.metric("Implied Prob", f"{implied*100:.1f}%")
        r1c2.metric("Your Model Prob", f"{ev_model_pct:.1f}%")
        r2c1, r2c2 = st.columns(2)
        r2c1.metric("Edge", f"{edge_pct:+.1f}%", delta_color="normal" if edge_pct >= 0 else "inverse")
        r2c2.metric("EV per Bet", f"${ev_dollar:+.2f}", delta_color="normal" if ev_dollar >= 0 else "inverse")
        r3c1, r3c2 = st.columns(2)
        r3c1.metric("ROI", f"{roi_pct:+.1f}%")
        r3c2.metric("¼ Kelly Stake", f"{kelly_quarter:.1f}%")

        verdict = "✅ Positive EV — this bet has value." if ev_dollar > 0 else "❌ Negative EV — skip this bet."
        st.markdown(f"<div style='margin-top:12px;padding:10px 14px;border-radius:8px;"
                    f"background:{ev_color}22;border:1px solid {ev_color};color:{ev_color};"
                    f"font-weight:700;'>{verdict}</div>", unsafe_allow_html=True)

    st.divider()
    st.markdown("#### 📖 How it works")
    st.markdown(f"""
| Term | Formula |
|---|---|
| **Implied Prob** | Sportsbook's break-even % derived from the odds |
| **Edge** | Your Model % − Implied % |
| **EV** | (Model % × Profit if Win) − (Model % × Stake) |
| **ROI** | EV ÷ Stake × 100 |
| **¼ Kelly** | Conservative fraction of bankroll to wager |
""")

# ============================================
# TAB: MODELS
# ============================================
with tab_models:
    st.markdown("### 🧠 Betting Models")
    st.caption("Win probabilities from each model feed directly into the ⚡ EV tab.")
    m_elo, m_ff, m_mkt, m_clv = st.tabs(["📊 Elo Ratings", "🏀 Four Factors", "📈 Market Factors", "💰 CLV Tracker"])

    # ── Elo ───────────────────────────────────────────────────────────────
    with m_elo:
        st.markdown("#### 📊 Elo Power Ratings")
        st.caption("Estimated from season win% + point differential. Updated every hour.")
        try:
            _stnd = get_standings()
            _elo_df = calc_elo_ratings(_stnd)
            _elo_df.index = _elo_df.index + 1
            _elo_df.columns = ["City","Team","Conf","Record","Win%","Diff/G","Elo"]

            _ec1, _ec2 = st.columns([3, 2])
            with _ec1:
                st.markdown("**League Rankings**")
                st.dataframe(_elo_df, use_container_width=True)
            with _ec2:
                st.markdown("**Matchup Win Probability**")
                _et1 = st.selectbox("Team 1", team_names, index=team_names.index(team1_name), key="elo_t1")
                _et2 = st.selectbox("Team 2", team_names, key="elo_t2",
                    index=(team_names.index("Cleveland Cavaliers") if "Cleveland Cavaliers" in team_names else 0))
                _home = st.radio("Home team", [_et1, _et2], horizontal=True, key="elo_home")

                _stnd2 = get_standings()
                _elo_full = calc_elo_ratings(_stnd2)
                def _get_elo(name):
                    _row = _elo_full[(_elo_full["TeamCity"]+" "+_elo_full["TeamName"]) == name]
                    return int(_row["elo"].iloc[0]) if len(_row) > 0 else 1500
                _e1 = _get_elo(_et1); _e2 = _get_elo(_et2)
                _is_home = _home == _et1
                _wp1 = elo_win_prob(_e1, _e2, home=_is_home)
                _wp2 = round(100 - _wp1, 1)

                st.metric(f"{_et1} Elo", _e1)
                st.metric(f"{_et2} Elo", _e2)
                _p1c, _p2c = st.columns(2)
                _p1c.metric(f"{_et1} Win%", f"{_wp1}%")
                _p2c.metric(f"{_et2} Win%", f"{_wp2}%")
                st.info(f"Copy **{_wp1}%** into the ⚡ EV tab as your Model Win % to calculate edge.")
        except Exception as e:
            st.error(f"Error loading standings: {e}")

    # ── Four Factors ──────────────────────────────────────────────────────
    with m_ff:
        st.markdown("#### 🏀 Four Factors Model")
        st.caption("Dean Oliver's framework — explains ~90% of NBA performance variance.")
        _fc1, _fc2 = st.columns(2)
        _ff_t1 = _fc1.selectbox("Team 1", team_names, index=team_names.index(team1_name), key="ff_t1")
        _ff_t2 = _fc2.selectbox("Team 2", team_names, key="ff_t2",
            index=(team_names.index("Cleveland Cavaliers") if "Cleveland Cavaliers" in team_names else 0))
        _ff_obj1 = next(t for t in nba_teams if t["full_name"] == _ff_t1)
        _ff_obj2 = next(t for t in nba_teams if t["full_name"] == _ff_t2)
        try:
            _g1 = get_team_games(_ff_obj1["id"]); _g2 = get_team_games(_ff_obj2["id"])
            _f1 = calc_four_factors(_g1);          _f2 = calc_four_factors(_g2)
            _ff_prob1 = ff_win_prob(_f1, _f2);     _ff_prob2 = round(100 - _ff_prob1, 1)

            # Comparison table
            _ff_rows = []
            _weights = {"eFG%": "40%", "TOV%": "25%", "OREB%": "20%", "FTR": "15%"}
            _better_higher = {"eFG%", "OREB%", "FTR"}
            for _fk, _wt in _weights.items():
                _v1 = _f1[_fk]; _v2 = _f2[_fk]
                if _fk in _better_higher:
                    _edge = "✅" if _v1 > _v2 else ("🔴" if _v1 < _v2 else "—")
                else:
                    _edge = "✅" if _v1 < _v2 else ("🔴" if _v1 > _v2 else "—")
                _ff_rows.append({"Factor": _fk, "Weight": _wt,
                                 _ff_t1: _v1, _ff_t2: _v2, "Edge": _edge})
            st.dataframe(pd.DataFrame(_ff_rows), use_container_width=True, hide_index=True)

            # Radar chart
            _cats = ["eFG%", "TOV% (inv)", "OREB%", "FTR×100"]
            _v1r = [_f1["eFG%"], 100-_f1["TOV%"], _f1["OREB%"], _f1["FTR"]*100]
            _v2r = [_f2["eFG%"], 100-_f2["TOV%"], _f2["OREB%"], _f2["FTR"]*100]
            _fig_r = go.Figure()
            _fig_r.add_trace(go.Scatterpolar(r=_v1r+[_v1r[0]], theta=_cats+[_cats[0]],
                fill="toself", name=_ff_t1, line_color="#00C8FF"))
            _fig_r.add_trace(go.Scatterpolar(r=_v2r+[_v2r[0]], theta=_cats+[_cats[0]],
                fill="toself", name=_ff_t2, line_color="#8b5cf6"))
            _fig_r.update_layout(polar=dict(
                bgcolor=_bg2,
                radialaxis=dict(gridcolor=_bdr, color=_txt2),
                angularaxis=dict(gridcolor=_bdr, color=_txt2)),
                paper_bgcolor=_bg, font_color=_txt2, height=380,
                legend=dict(bgcolor=_bg2, bordercolor=_bdr))
            st.plotly_chart(_fig_r, use_container_width=True)

            _fp1c, _fp2c = st.columns(2)
            _fp1c.metric(f"{_ff_t1} Win%", f"{_ff_prob1}%")
            _fp2c.metric(f"{_ff_t2} Win%", f"{_ff_prob2}%")
            st.info(f"Copy **{_ff_prob1}%** into the ⚡ EV tab as your Model Win % to calculate edge.")
        except Exception as e:
            st.error(f"Error: {e}")

    # ── Market Factors ────────────────────────────────────────────────────
    with m_mkt:
        st.markdown("#### 📈 Market Factors")
        st.caption("Rest, back-to-backs, and home/road splits — spots where the market often misprices.")
        _mc1, _mc2 = st.columns(2)
        _mf_t1 = _mc1.selectbox("Team 1", team_names, index=team_names.index(team1_name), key="mf_t1")
        _mf_t2 = _mc2.selectbox("Team 2", team_names, key="mf_t2",
            index=(team_names.index("Cleveland Cavaliers") if "Cleveland Cavaliers" in team_names else 0))
        _mf_obj1 = next(t for t in nba_teams if t["full_name"] == _mf_t1)
        _mf_obj2 = next(t for t in nba_teams if t["full_name"] == _mf_t2)
        _mf_home = st.radio("Home team", [_mf_t1, _mf_t2], horizontal=True, key="mf_home")

        try:
            _mg1 = get_team_games(_mf_obj1["id"]); _mg2 = get_team_games(_mf_obj2["id"])
            _mf1 = calc_market_factors(_mg1);       _mf2 = calc_market_factors(_mg2)

            st.divider()
            _mrc1, _mrc2 = st.columns(2)
            for _mcol, _mfdata, _mname in [(_mrc1, _mf1, _mf_t1), (_mrc2, _mf2, _mf_t2)]:
                with _mcol:
                    st.markdown(f"**{_mname}**")
                    _b2b_flag = "⚠️ Back-to-Back" if _mfdata["b2b"] else "✅ Rested"
                    st.markdown(f"- Days since last game: **{_mfdata['rest_days']}**")
                    st.markdown(f"- Schedule: **{_b2b_flag}**")
                    st.markdown(f"- Home record: **{_mfdata['home_record']}** ({_mfdata['home_wpct']}%)")
                    st.markdown(f"- Road record: **{_mfdata['away_record']}** ({_mfdata['away_wpct']}%)")

            # Market-adjusted win probability
            st.divider(); st.markdown("#### Market-Adjusted Win Probability")
            _t1_home = _mf_home == _mf_t1
            # Base: use home/road win% weighted vs opponent home/road win%
            _t1_base = (_mf1["home_wpct"] if _t1_home else _mf1["away_wpct"]) / 100
            _t2_base = (_mf2["away_wpct"] if _t1_home else _mf2["home_wpct"]) / 100
            _total   = _t1_base + _t2_base
            _mkt_p1  = round(_t1_base / _total * 100, 1) if _total > 0 else 50
            _mkt_p2  = round(100 - _mkt_p1, 1)
            # B2B penalty: -5% win prob
            if _mf1["b2b"]: _mkt_p1 = round(max(0, _mkt_p1 - 5), 1); _mkt_p2 = round(100 - _mkt_p1, 1)
            if _mf2["b2b"]: _mkt_p2 = round(max(0, _mkt_p2 - 5), 1); _mkt_p1 = round(100 - _mkt_p2, 1)

            _ma1, _ma2 = st.columns(2)
            _ma1.metric(f"{_mf_t1} Win%", f"{_mkt_p1}%",
                        delta="B2B penalty applied" if _mf1["b2b"] else None)
            _ma2.metric(f"{_mf_t2} Win%", f"{_mkt_p2}%",
                        delta="B2B penalty applied" if _mf2["b2b"] else None)
            st.info(f"Copy **{_mkt_p1}%** into the ⚡ EV tab as your Model Win % to calculate edge.")
        except Exception as e:
            st.error(f"Error: {e}")

    # ── CLV Tracker ───────────────────────────────────────────────────────
    with m_clv:
        st.markdown("#### 💰 Closing Line Value (CLV) Tracker")
        st.caption("Log the closing odds for your settled bets. Consistently positive CLV = you're beating the market long-term.")

        _clv_data = load_json(CLV_FILE)   # list of {key, game, bet_odds, closing_odds, clv}

        with st.form("clv_form"):
            st.markdown("**Log a Closing Line**")
            _cf1, _cf2 = st.columns(2)
            _clv_game   = _cf1.text_input("Game", placeholder="OKC vs CLE")
            _clv_pick   = _cf2.text_input("Pick", placeholder="OKC -3.5")
            _cf3, _cf4, _cf5 = st.columns(3)
            _clv_date   = _cf3.date_input("Date", value=date.today(), key="clv_date")
            _clv_bet_o  = _cf4.number_input("Your Odds",     value=-110, step=1, key="clv_bet_o")
            _clv_cls_o  = _cf5.number_input("Closing Odds",  value=-110, step=1, key="clv_cls_o")
            if st.form_submit_button("💾 Save CLV"):
                _clv_val = clv_calc(_clv_bet_o, _clv_cls_o)
                _clv_data.append({"date": str(_clv_date), "game": _clv_game, "pick": _clv_pick,
                                  "bet_odds": _clv_bet_o, "closing_odds": _clv_cls_o, "clv": _clv_val})
                save_json(CLV_FILE, _clv_data); st.rerun()

        if _clv_data:
            _clv_df = pd.DataFrame(_clv_data)
            _avg_clv = round(_clv_df["clv"].mean(), 2)
            _pos_clv = len(_clv_df[_clv_df["clv"] > 0])
            _neg_clv = len(_clv_df[_clv_df["clv"] < 0])
            _clv_c1, _clv_c2, _clv_c3 = st.columns(3)
            _clv_c1.metric("Avg CLV",         f"{_avg_clv:+.2f}%",
                           delta="Beating the market" if _avg_clv > 0 else "Losing to the market")
            _clv_c2.metric("Positive CLV bets", str(_pos_clv))
            _clv_c3.metric("Negative CLV bets", str(_neg_clv))

            _clv_df["clv_fmt"] = _clv_df["clv"].apply(lambda x: f"{x:+.2f}%")
            st.dataframe(_clv_df[["date","game","pick","bet_odds","closing_odds","clv_fmt"]]
                         .rename(columns={"clv_fmt":"CLV"}),
                         use_container_width=True, hide_index=True)

            # CLV over time chart
            _clv_sorted = _clv_df.sort_values("date").copy()
            _clv_sorted["cum_clv"] = _clv_sorted["clv"].cumsum()
            _clv_sorted["n"] = range(1, len(_clv_sorted)+1)
            _fc = go.Figure()
            _fc.add_trace(go.Scatter(x=_clv_sorted["n"], y=_clv_sorted["cum_clv"],
                mode="lines+markers", fill="tozeroy",
                line=dict(color="#7ee787" if _avg_clv>=0 else "#f85149", width=2),
                fillcolor="rgba(126,231,135,0.08)" if _avg_clv>=0 else "rgba(248,81,73,0.08)",
                hovertemplate="Bet %{x}<br>Cumulative CLV: %{y:+.2f}%<extra></extra>"))
            _fc.add_hline(y=0, line_color=_bdr)
            _fc.update_layout(title="Cumulative CLV", height=300, **PLOTLY_THEME)
            st.plotly_chart(_fc, use_container_width=True)
            if st.button("🗑️ Clear CLV Log"): save_json(CLV_FILE, []); st.rerun()
        else:
            st.info("No CLV entries yet. Log your first closing line above.")
        st.divider()
        st.markdown("""
**How to use CLV:**
- After a game tips off, note the final odds (closing line) for your bet
- If the line moved in your direction (e.g. you bet -3, it closed -5), that's **positive CLV**
- Sportsbooks move lines based on sharp money — positive CLV means you're on the same side as the sharps
- Aim for **+1% to +3% average CLV** over a large sample — that's a sustainable edge
""")

# ============================================
# TAB: BANKROLL
# ============================================
with tab_bank:
    st.markdown("### 💵 Bankroll Tracker")

    # ── Log new bet ───────────────────────────────────────────────────────
    with st.expander("➕ Log New Bet", expanded=False):
        with st.form("nb"):
            r1,r2=st.columns(2); bd=r1.date_input("Date"); bg=r2.text_input("Game")
            r3,r4,r5=st.columns(3)
            bt=r3.selectbox("Type",["ML","Spread","O/U","Prop","Parlay","Other"])
            bp=r4.text_input("Pick"); bo=r5.number_input("Odds",value=-110)
            r6,r7=st.columns(2)
            ba=r6.number_input("Amount",min_value=1.0,value=20.0,step=5.0)
            br=r7.selectbox("Result",["Pending","Win","Loss","Push"])
            if st.form_submit_button("💾 Save Bet"):
                if br=="Win": net=round(ba*(100/abs(bo)) if bo<0 else ba*(bo/100),2)
                elif br=="Loss": net=-ba
                else: net=0
                _tmp=load_json(BANKROLL_FILE)
                _tmp.append({"date":str(bd),"game":bg,"type":bt,"pick":bp,"odds":bo,"amount":ba,"result":br,"net":net})
                save_json(BANKROLL_FILE,_tmp); st.rerun()

    bets = load_json(BANKROLL_FILE)

    if not bets:
        st.info("No bets logged yet. Use the form above to get started.")
    else:
        bdf = pd.DataFrame(bets)
        bdf["date"]   = pd.to_datetime(bdf["date"])
        bdf["net"]    = pd.to_numeric(bdf["net"],    errors="coerce").fillna(0)
        bdf["amount"] = pd.to_numeric(bdf["amount"], errors="coerce").fillna(0)
        bdf["odds"]   = pd.to_numeric(bdf["odds"],   errors="coerce").fillna(0)
        dec = bdf[bdf["result"].isin(["Win","Loss","Push"])].copy()

        today_dt = date.today()

        # ── Helpers ───────────────────────────────────────────────────────
        def _pstats(df):
            if len(df) == 0:
                return {"w":0,"l":0,"p":0,"net":0.0,"wagered":0.0,"roi":0.0,"n":0}
            w=len(df[df["result"]=="Win"]); l=len(df[df["result"]=="Loss"]); p=len(df[df["result"]=="Push"])
            net=df["net"].sum(); wag=df["amount"].sum()
            return {"w":w,"l":l,"p":p,"net":float(net),"wagered":float(wag),
                    "roi":round(float(net)/float(wag)*100,1) if wag>0 else 0.0,"n":len(df)}

        def _streak(df):
            rs = df[df["result"].isin(["Win","Loss"])].sort_values("date")["result"].tolist()
            if not rs: return 0, "–"
            cur=rs[-1]; cnt=1
            for r in reversed(rs[:-1]):
                if r==cur: cnt+=1
                else: break
            return cnt, cur

        # ── Daily aggregation for calendar ───────────────────────────────
        _daily = (dec.groupby(dec["date"].dt.strftime("%Y-%m-%d"))
                     .agg(net=("net","sum"), n=("net","count"),
                          w=("result",lambda x:(x=="Win").sum()),
                          l=("result",lambda x:(x=="Loss").sum()),
                          p=("result",lambda x:(x=="Push").sum()))
                     .reset_index())
        _daily_dict = {row["date"]: row.to_dict() for _,row in _daily.iterrows()}

        # ── Period stats ──────────────────────────────────────────────────
        _today_dec = dec[dec["date"].dt.date == today_dt]
        _month_dec = dec[(dec["date"].dt.year==today_dt.year)&(dec["date"].dt.month==today_dt.month)]
        _ts = _pstats(_today_dec); _ms = _pstats(_month_dec); _as = _pstats(dec)
        _sn, _sr = _streak(dec)

        st.markdown("#### 📊 Performance Overview")
        for _lbl, _s in [("Today",_ts),("This Month",_ms),("All Time",_as)]:
            _nc = "#7ee787" if _s["net"] >= 0 else "#f85149"
            st.markdown(
                f"<div style='display:inline-block;background:{_bg2};border:1px solid {_bdr};"
                f"border-radius:10px;padding:14px 20px;margin:0 8px 8px 0;min-width:180px;vertical-align:top;'>"
                f"<div style='color:{_txt2};font-size:0.75rem;font-weight:600;text-transform:uppercase;"
                f"letter-spacing:.05em;margin-bottom:4px;'>{_lbl}</div>"
                f"<div style='color:{_nc};font-size:1.7rem;font-weight:800;line-height:1;'>${_s['net']:+.2f}</div>"
                f"<div style='color:{_txt};font-size:0.85rem;margin-top:6px;'>"
                f"{_s['w']}W – {_s['l']}L – {_s['p']}P</div>"
                f"<div style='color:{_txt2};font-size:0.78rem;'>ROI {_s['roi']:+.1f}% &nbsp;•&nbsp; {_s['n']} bets</div>"
                f"</div>", unsafe_allow_html=True)
        st.markdown("")

        # Streak + highlights row
        _best_row  = _daily.loc[_daily["net"].idxmax()] if len(_daily)>0 else None
        _worst_row = _daily.loc[_daily["net"].idxmin()] if len(_daily)>0 else None
        _avg_odds  = float(dec["odds"].mean()) if len(dec)>0 else 0
        _hc1,_hc2,_hc3,_hc4 = st.columns(4)
        _hc1.metric("Current Streak", f"{_sn}{'W' if _sr=='Win' else 'L' if _sr=='Loss' else ''}" if _sr!="–" else "–")
        _hc2.metric("Best Day",  f"${_best_row['net']:+.2f}"  if _best_row  is not None else "–", _best_row['date']  if _best_row  is not None else "")
        _hc3.metric("Worst Day", f"${_worst_row['net']:+.2f}" if _worst_row is not None else "–", _worst_row['date'] if _worst_row is not None else "")
        _hc4.metric("Avg Odds",  f"{_avg_odds:+.0f}" if len(dec)>0 else "–")

        # ── Custom date range ─────────────────────────────────────────────
        st.divider(); st.markdown("#### 🔎 Date Range Filter")
        _dr1,_dr2 = st.columns(2)
        _rstart = _dr1.date_input("From", value=today_dt.replace(day=1), key="bank_from")
        _rend   = _dr2.date_input("To",   value=today_dt,               key="bank_to")
        _rdec = dec[(dec["date"].dt.date>=_rstart)&(dec["date"].dt.date<=_rend)]
        _rs = _pstats(_rdec); _rsn,_rsr = _streak(_rdec)
        _rc1,_rc2,_rc3,_rc4,_rc5,_rc6 = st.columns(6)
        _rc1.metric("Record",  f"{_rs['w']}-{_rs['l']}-{_rs['p']}")
        _rc2.metric("P/L",     f"${_rs['net']:+.2f}")
        _rc3.metric("ROI",     f"{_rs['roi']:+.1f}%")
        _rc4.metric("Wagered", f"${_rs['wagered']:,.0f}")
        _rc5.metric("Bets",    str(_rs["n"]))
        _rc6.metric("Streak",  f"{_rsn}{'W' if _rsr=='Win' else 'L' if _rsr=='Loss' else ''}" if _rsr!="–" else "–")

        # ── Calendar ──────────────────────────────────────────────────────
        st.divider(); st.markdown("#### 📅 Bet Calendar")
        if "cal_y" not in st.session_state: st.session_state.cal_y = today_dt.year
        if "cal_m" not in st.session_state: st.session_state.cal_m = today_dt.month
        _cv1,_cv2,_cv3 = st.columns([1,4,1])
        with _cv1:
            if st.button("◀", key="cal_prev"):
                _pm = st.session_state.cal_m - 1
                if _pm < 1: _pm=12; st.session_state.cal_y -= 1
                st.session_state.cal_m = _pm; st.rerun()
        with _cv3:
            if st.button("▶", key="cal_next"):
                _nm = st.session_state.cal_m + 1
                if _nm > 12: _nm=1; st.session_state.cal_y += 1
                st.session_state.cal_m = _nm; st.rerun()
        with _cv2:
            st.markdown(f"<div style='text-align:center;font-weight:700;color:{_head};font-size:1.1rem;padding:4px 0;'>"
                        f"{_cal_lib.month_name[st.session_state.cal_m]} {st.session_state.cal_y}</div>",
                        unsafe_allow_html=True)

        _cal_weeks = _cal_lib.monthcalendar(st.session_state.cal_y, st.session_state.cal_m)
        _th = f"text-align:center;color:{_txt2};font-size:0.75rem;padding:4px;font-weight:600;"
        _td_base = f"border-radius:8px;padding:8px 4px;text-align:center;vertical-align:top;"
        _cal_html = (f"<table style='width:100%;border-collapse:separate;border-spacing:5px;margin-top:6px;'><tr>"
                     + "".join(f"<th style='{_th}'>{d}</th>" for d in ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"])
                     + "</tr>")
        for _wk in _cal_weeks:
            _cal_html += "<tr>"
            for _dy in _wk:
                if _dy == 0:
                    _cal_html += f"<td style='background:transparent;{_td_base}'></td>"
                else:
                    _dstr = f"{st.session_state.cal_y}-{st.session_state.cal_m:02d}-{_dy:02d}"
                    _ds   = _daily_dict.get(_dstr)
                    _today_ring = "outline:2px solid #00C8FF;outline-offset:2px;" if _dstr==str(today_dt) else ""
                    if _ds:
                        _dn = _ds["net"]
                        if   _dn > 0: _cbg,_cbdr,_cnc = "rgba(126,231,135,0.18)","#7ee787","#7ee787"
                        elif _dn < 0: _cbg,_cbdr,_cnc = "rgba(248,81,73,0.18)",  "#f85149","#f85149"
                        else:         _cbg,_cbdr,_cnc = "rgba(0,200,255,0.12)", "#00C8FF","#00C8FF"
                        _cal_html += (
                            f"<td style='background:{_cbg};border:1px solid {_cbdr};{_td_base}{_today_ring}'>"
                            f"<div style='font-weight:700;color:{_head};font-size:0.85rem;'>{_dy}</div>"
                            f"<div style='color:{_cnc};font-weight:800;font-size:1rem;line-height:1.3;'>${_dn:+.0f}</div>"
                            f"<div style='color:{_txt2};font-size:0.68rem;'>{int(_ds['w'])}W {int(_ds['l'])}L</div>"
                            f"<div style='color:{_txt2};font-size:0.65rem;'>{int(_ds['n'])} bet{'s' if _ds['n']!=1 else ''}</div>"
                            f"</td>")
                    else:
                        _ebg = f"rgba(249,115,22,0.06)" if _dstr==str(today_dt) else _bg2
                        _ebdr = "#00C8FF" if _dstr==str(today_dt) else _bdr
                        _cal_html += (
                            f"<td style='background:{_ebg};border:1px solid {_ebdr};{_td_base}'>"
                            f"<div style='font-weight:700;color:{_txt2};font-size:0.85rem;'>{_dy}</div>"
                            f"</td>")
            _cal_html += "</tr>"
        _cal_html += "</table>"
        st.markdown(_cal_html, unsafe_allow_html=True)

        # ── Charts ────────────────────────────────────────────────────────
        st.divider()
        _cha, _chb = st.columns(2)
        with _cha:
            _cd = dec.sort_values("date").copy()
            _cd["Cum"] = _cd["net"].cumsum(); _cd["BN"] = range(1,len(_cd)+1)
            _tn = float(_cd["net"].sum())
            _fc = go.Figure()
            _fc.add_trace(go.Scatter(x=_cd["BN"],y=_cd["Cum"],mode="lines+markers",fill="tozeroy",
                line=dict(color="#7ee787" if _tn>=0 else "#f85149",width=2),
                fillcolor="rgba(126,231,135,0.08)" if _tn>=0 else "rgba(248,81,73,0.08)",
                hovertemplate="Bet %{x}<br>P/L: $%{y:+.2f}<extra></extra>"))
            _fc.add_hline(y=0,line_color=_bdr)
            _fc.update_layout(title="Cumulative P/L",height=320,**PLOTLY_THEME)
            st.plotly_chart(_fc,use_container_width=True)
        with _chb:
            _md = dec.copy(); _md["mo"] = _md["date"].dt.strftime("%b %Y")
            _mg = _md.groupby("mo")["net"].sum().reset_index()
            _fm = go.Figure()
            _fm.add_trace(go.Bar(x=_mg["mo"],y=_mg["net"],
                marker_color=["#7ee787" if v>=0 else "#f85149" for v in _mg["net"]],
                hovertemplate="%{x}: $%{y:+.2f}<extra></extra>"))
            _fm.add_hline(y=0,line_color=_bdr)
            _fm.update_layout(title="Monthly P/L",height=320,**PLOTLY_THEME)
            st.plotly_chart(_fm,use_container_width=True)

        # ── By bet type ───────────────────────────────────────────────────
        st.divider(); st.markdown("#### 📂 By Bet Type")
        _tg = (dec.groupby("type")
                  .agg(Bets=("net","count"),
                       W=("result",lambda x:(x=="Win").sum()),
                       L=("result",lambda x:(x=="Loss").sum()),
                       P=("result",lambda x:(x=="Push").sum()),
                       Net=("net","sum"),
                       Wagered=("amount","sum"))
                  .reset_index())
        _tg["ROI%"]   = (_tg["Net"]/_tg["Wagered"]*100).round(1)
        _tg["Net"]    = _tg["Net"].apply(lambda x:f"${x:+.2f}")
        _tg["Wagered"]= _tg["Wagered"].apply(lambda x:f"${x:,.0f}")
        st.dataframe(_tg.rename(columns={"type":"Type"}),use_container_width=True,hide_index=True)

        # ── Pending bets ──────────────────────────────────────────────────
        _pend = bdf[bdf["result"]=="Pending"]
        if len(_pend) > 0:
            st.divider(); st.markdown("#### ⏳ Pending Bets")
            for _idx,_bet in _pend.iterrows():
                with st.expander(f"{_bet['date'].strftime('%Y-%m-%d')}: {_bet['game']} — {_bet['pick']}"):
                    _u1,_u2,_u3 = st.columns(3)
                    if _u1.button("✅ Win",  key=f"bw{_idx}"):
                        bets[_idx]["result"]="Win"
                        bets[_idx]["net"]=round(bets[_idx]["amount"]*(100/abs(bets[_idx]["odds"])) if bets[_idx]["odds"]<0 else bets[_idx]["amount"]*(bets[_idx]["odds"]/100),2)
                        save_json(BANKROLL_FILE,bets); st.rerun()
                    if _u2.button("❌ Loss", key=f"bl{_idx}"):
                        bets[_idx]["result"]="Loss"; bets[_idx]["net"]=-bets[_idx]["amount"]
                        save_json(BANKROLL_FILE,bets); st.rerun()
                    if _u3.button("↩️ Push", key=f"bp{_idx}"):
                        bets[_idx]["result"]="Push"; bets[_idx]["net"]=0
                        save_json(BANKROLL_FILE,bets); st.rerun()

        # ── Full bet log ──────────────────────────────────────────────────
        st.divider(); st.markdown("#### 📋 Full Bet Log")
        _show = bdf.copy()
        _show["date"] = _show["date"].dt.strftime("%Y-%m-%d")
        _show["net"]  = _show["net"].apply(lambda x:f"${x:+.2f}")
        st.dataframe(_show[["date","game","type","pick","odds","amount","result","net"]],
                     use_container_width=True, hide_index=True)
        if st.button("🗑️ Clear All Bets"): save_json(BANKROLL_FILE,[]); st.rerun()

# ============================================
# TAB: STANDINGS
# ============================================
with tab_stand:
    st.markdown("### 📋 2025-26 Standings")
    try:
        stnd=get_standings()
        e,w=st.columns(2)
        with e:
            st.markdown("**Eastern Conference**")
            east=stnd[stnd["Conference"]=="East"][["TeamCity","TeamName","Record","WinPCT","PointsPG","OppPointsPG","DiffPointsPG"]].reset_index(drop=True)
            east.index=east.index+1; east.columns=["City","Team","Record","Win%","PPG","Opp","Diff"]
            st.dataframe(east,use_container_width=True)
        with w:
            st.markdown("**Western Conference**")
            west=stnd[stnd["Conference"]=="West"][["TeamCity","TeamName","Record","WinPCT","PointsPG","OppPointsPG","DiffPointsPG"]].reset_index(drop=True)
            west.index=west.index+1; west.columns=["City","Team","Record","Win%","PPG","Opp","Diff"]
            st.dataframe(west,use_container_width=True)
    except Exception as e: st.error(f"Error: {e}")

st.divider()
st.markdown('<p style="color:#484f58;text-align:center;font-size:0.8rem;">Built with Python • Streamlit • NBA API • The Odds API</p>',unsafe_allow_html=True)