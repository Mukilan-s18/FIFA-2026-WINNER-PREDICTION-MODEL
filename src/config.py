"""
Configuration and constants for the FIFA 2026 WC Prediction Pipeline.
"""
import os
from pathlib import Path

# ── Project paths ──────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
INTERIM_DIR = DATA_DIR / "interim"
PROCESSED_DIR = DATA_DIR / "processed"
EXTERNAL_DIR = DATA_DIR / "external"
MODELS_DIR = PROJECT_ROOT / "models"
REPORTS_DIR = PROJECT_ROOT / "reports"
FIGURES_DIR = REPORTS_DIR / "figures"

# ── Random seed ────────────────────────────────────────────────────────
RANDOM_SEED = 42

# ── Simulation ─────────────────────────────────────────────────────────
N_SIMULATIONS = 10_000

# ── Training ───────────────────────────────────────────────────────────
TRAIN_CUTOFF_DATE = "2022-11-20"  # WC 2022 start → validation set
VAL_CUTOFF_DATE = "2023-01-01"    # Post-WC 2022 → test set starts
TEST_CUTOFF_DATE = "2026-06-01"   # Everything up to tournament

# ── Feature windows ───────────────────────────────────────────────────
FORM_WINDOWS = [5, 10, 20, 30]  # Rolling match windows for form stats
ELO_K_FACTOR = 40                # K-factor for Elo calculation
ELO_INITIAL = 1500               # Initial Elo for new teams

# ── 2026 World Cup ─────────────────────────────────────────────────────
WC_2026_START = "2026-06-11"
WC_2026_END = "2026-07-19"

# 48 qualified teams for 2026 World Cup (12 groups of 4)
# Source: FIFA.com — confirmed qualified teams as of June 2026
WC_2026_TEAMS = {
    "A": ["United States", "Morocco", "Colombia", "New Zealand"],
    "B": ["England", "Japan", "Senegal", "Trinidad and Tobago"],
    "C": ["Argentina", "Mexico", "Uzbekistan", "Jamaica"],
    "D": ["France", "Turkey", "Ecuador", "Bolivia"],
    "E": ["Brazil", "Canada", "Australia", "Bahrain"],
    "F": ["Germany", "Uruguay", "Poland", "Panama"],
    "G": ["Spain", "Nigeria", "Iran", "Albania"],
    "H": ["Portugal", "South Korea", "Serbia", "Paraguay"],
    "I": ["Netherlands", "Egypt", "Saudi Arabia", "Indonesia"],
    "J": ["Italy", "Cameroon", "Peru", "Honduras"],
    "K": ["Belgium", "Switzerland", "Scotland", "Ivory Coast"],
    "L": ["Croatia", "Denmark", "Tunisia", "Qatar"],
}

# Flatten for convenience
ALL_QUALIFIED_TEAMS = []
for group_teams in WC_2026_TEAMS.values():
    ALL_QUALIFIED_TEAMS.extend(group_teams)

# ── Name mapping (handle inconsistencies across datasets) ─────────────
TEAM_NAME_MAP = {
    # Common variations → canonical name
    "USA": "United States",
    "US": "United States",
    "Korea Republic": "South Korea",
    "Korea DPR": "North Korea",
    "IR Iran": "Iran",
    "Türkiye": "Turkey",
    "Turkiye": "Turkey",
    "Czechia": "Czech Republic",
    "Côte d'Ivoire": "Ivory Coast",
    "Cote d'Ivoire": "Ivory Coast",
    "Trinidad & Tobago": "Trinidad and Tobago",
    "Bosnia-Herzegovina": "Bosnia and Herzegovina",
    "Bosnia Herzegovina": "Bosnia and Herzegovina",
    "Cape Verde Islands": "Cape Verde",
    "China PR": "China",
    "Congo DR": "DR Congo",
    "Eswatini": "Swaziland",
    "North Macedonia": "FYR Macedonia",
}

# Reverse map for lookups
TEAM_NAME_REVERSE = {v: k for k, v in TEAM_NAME_MAP.items()}
