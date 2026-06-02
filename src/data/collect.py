"""
Data collection scripts for FIFA 2026 WC Prediction Pipeline.

Downloads and caches the following datasets:
1. Historical international football results (1872–present)
2. FIFA/Coca-Cola World Rankings time series
3. World Cup specific results
"""
import os
import io
import zipfile
import requests
import pandas as pd
from pathlib import Path

from src.config import RAW_DIR, TEAM_NAME_MAP


# ────────────────────────────────────────────────────────────────────────
# 1. Historical International Match Results
# ────────────────────────────────────────────────────────────────────────

RESULTS_URL = (
    "https://raw.githubusercontent.com/martj42/international_results/"
    "master/results.csv"
)
SHOOTOUTS_URL = (
    "https://raw.githubusercontent.com/martj42/international_results/"
    "master/shootouts.csv"
)
GOALSCORERS_URL = (
    "https://raw.githubusercontent.com/martj42/international_results/"
    "master/goalscorers.csv"
)


def download_match_results(force: bool = False) -> pd.DataFrame:
    """Download historical international match results.
    
    Returns DataFrame with columns:
        date, home_team, away_team, home_score, away_score,
        tournament, city, country, neutral
    """
    filepath = RAW_DIR / "results.csv"
    
    if filepath.exists() and not force:
        print(f"  ✓ Match results already cached at {filepath}")
        return pd.read_csv(filepath, parse_dates=["date"])
    
    print("  ⬇ Downloading international match results...")
    response = requests.get(RESULTS_URL, timeout=30)
    response.raise_for_status()
    
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    filepath.write_text(response.text)
    print(f"  ✓ Saved to {filepath}")
    
    return pd.read_csv(filepath, parse_dates=["date"])


def download_shootouts(force: bool = False) -> pd.DataFrame:
    """Download penalty shootout results."""
    filepath = RAW_DIR / "shootouts.csv"
    
    if filepath.exists() and not force:
        return pd.read_csv(filepath, parse_dates=["date"])
    
    print("  ⬇ Downloading shootout results...")
    response = requests.get(SHOOTOUTS_URL, timeout=30)
    response.raise_for_status()
    
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    filepath.write_text(response.text)
    
    return pd.read_csv(filepath, parse_dates=["date"])


def download_goalscorers(force: bool = False) -> pd.DataFrame:
    """Download goal scorer data."""
    filepath = RAW_DIR / "goalscorers.csv"
    
    if filepath.exists() and not force:
        return pd.read_csv(filepath, parse_dates=["date"])
    
    print("  ⬇ Downloading goalscorer data...")
    response = requests.get(GOALSCORERS_URL, timeout=30)
    response.raise_for_status()
    
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    filepath.write_text(response.text)
    
    return pd.read_csv(filepath, parse_dates=["date"])


# ────────────────────────────────────────────────────────────────────────
# 2. FIFA Rankings — Generated from Elo ratings
# ────────────────────────────────────────────────────────────────────────

def generate_elo_rankings(results_df: pd.DataFrame) -> pd.DataFrame:
    """Generate rankings from match results using Elo rating system.
    
    Since the external FIFA rankings dataset is unavailable, we compute
    our own rankings using Elo ratings (which are actually more predictive
    than FIFA rankings for match outcome prediction).
    
    Produces periodic snapshots (every 6 months) to create a time series.
    
    Returns DataFrame with columns:
        rank, team, points, confederation, date
    """
    from src.data.features import EloRatingSystem
    
    filepath = RAW_DIR / "elo_rankings.csv"
    if filepath.exists():
        print(f"  ✓ Elo rankings already cached at {filepath}")
        return pd.read_csv(filepath, parse_dates=["date"])
    
    print("  📊 Generating Elo-based rankings from match history...")
    
    df = results_df.copy()
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"]).sort_values("date")
    
    # Apply team name normalization
    df["home_team"] = df["home_team"].apply(normalize_team_name)
    df["away_team"] = df["away_team"].apply(normalize_team_name)
    
    elo = EloRatingSystem()
    
    # Define snapshot dates (every 6 months from 1992 to present)
    snapshot_dates = pd.date_range("1992-06-01", pd.Timestamp.now(), freq="6MS")
    
    all_snapshots = []
    match_idx = 0
    
    for snap_date in snapshot_dates:
        # Process all matches up to this snapshot date
        while match_idx < len(df) and df.iloc[match_idx]["date"] <= snap_date:
            row = df.iloc[match_idx]
            elo.update(
                home_team=row["home_team"],
                away_team=row["away_team"],
                home_score=int(row["home_score"]) if pd.notna(row["home_score"]) else 0,
                away_score=int(row["away_score"]) if pd.notna(row["away_score"]) else 0,
                tournament=str(row.get("tournament", "")),
                neutral=bool(row.get("neutral", False)),
            )
            match_idx += 1
        
        # Create ranking snapshot
        ratings = sorted(elo.ratings.items(), key=lambda x: -x[1])
        for rank_pos, (team, rating) in enumerate(ratings, 1):
            all_snapshots.append({
                "rank": rank_pos,
                "team": team,
                "points": rating,
                "confederation": "",  # Not available from this source
                "date": snap_date,
            })
    
    rankings_df = pd.DataFrame(all_snapshots)
    
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    rankings_df.to_csv(filepath, index=False)
    print(f"  ✓ Generated {len(rankings_df):,} ranking entries across {len(snapshot_dates)} snapshots")
    print(f"  ✓ Saved to {filepath}")
    
    return rankings_df


# ────────────────────────────────────────────────────────────────────────
# Helpers
# ────────────────────────────────────────────────────────────────────────

def normalize_team_name(name: str) -> str:
    """Normalize team name to canonical form."""
    return TEAM_NAME_MAP.get(name, name)


def download_all(force: bool = False) -> dict:
    """Download all datasets. Returns dict of DataFrames."""
    print("=" * 60)
    print("  FIFA 2026 WC Prediction — Data Collection")
    print("=" * 60)
    
    data = {}
    
    print("\n[1/3] International match results")
    data["results"] = download_match_results(force)
    
    print("\n[2/3] Shootout results")
    data["shootouts"] = download_shootouts(force)
    
    print("\n[3/3] Goal scorer data")
    data["goalscorers"] = download_goalscorers(force)
    
    # Rankings will be generated after data cleaning (needs Elo system)
    # Placeholder — actual generation happens in the pipeline
    data["rankings"] = None
    
    print("\n" + "=" * 60)
    print("  Download complete!")
    for name, df in data.items():
        if df is not None:
            print(f"    {name}: {len(df):,} rows × {len(df.columns)} cols")
        else:
            print(f"    {name}: (will be generated from match data)")
    print("=" * 60)
    
    return data


if __name__ == "__main__":
    download_all()

