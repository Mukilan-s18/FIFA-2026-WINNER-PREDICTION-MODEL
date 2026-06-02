"""
Data cleaning and preprocessing for FIFA 2026 WC Prediction Pipeline.

Takes raw downloaded data and produces clean, consistent interim datasets.
"""
import pandas as pd
import numpy as np
from typing import Optional

from src.config import (
    TEAM_NAME_MAP,
    INTERIM_DIR,
    ALL_QUALIFIED_TEAMS,
)


def normalize_team_name(name: str) -> str:
    """Map variant team names to a single canonical form."""
    return TEAM_NAME_MAP.get(name, name)


def clean_match_results(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and validate the international match results dataset.

    Steps:
        1. Parse dates, drop rows with missing scores.
        2. Normalize team names.
        3. Add derived columns: result, goal_difference, is_world_cup.
        4. Filter to a useful date range (1990+).
    """
    df = df.copy()

    # -- 1. Basic validation --
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date", "home_score", "away_score"])
    df["home_score"] = df["home_score"].astype(int)
    df["away_score"] = df["away_score"].astype(int)

    # -- 2. Normalize team names --
    df["home_team"] = df["home_team"].apply(normalize_team_name)
    df["away_team"] = df["away_team"].apply(normalize_team_name)

    # -- 3. Derived columns --
    # Result from home team's perspective: W / D / L
    conditions = [
        df["home_score"] > df["away_score"],
        df["home_score"] == df["away_score"],
        df["home_score"] < df["away_score"],
    ]
    df["home_result"] = np.select(conditions, ["W", "D", "L"], default="D")

    # Goal difference (home perspective)
    df["goal_diff"] = df["home_score"] - df["away_score"]

    # Tournament flags
    df["is_world_cup"] = df["tournament"].str.contains(
        "FIFA World Cup", case=False, na=False
    ) & ~df["tournament"].str.contains("qualification", case=False, na=False)

    df["is_competitive"] = ~df["tournament"].str.contains(
        "Friendly", case=False, na=False
    )

    # Neutral venue flag (fill missing as False)
    df["neutral"] = df["neutral"].fillna(False).astype(bool)

    # -- 4. Filter to modern era (1990+) --
    df = df[df["date"] >= "1990-01-01"].reset_index(drop=True)

    # -- 5. Sort by date --
    df = df.sort_values("date").reset_index(drop=True)

    print(f"  ✓ Cleaned match results: {len(df):,} matches (1990–present)")
    return df


def clean_fifa_rankings(df: pd.DataFrame) -> pd.DataFrame:
    """Clean rankings time series.

    Handles both formats:
    - Old FIFA format: rank_date, country_full, total_points
    - Elo-generated format: date, team, points, rank
    """
    df = df.copy()

    # Detect format
    if "rank_date" in df.columns:
        # Old FIFA format
        df["date"] = pd.to_datetime(df["rank_date"], errors="coerce")
        df = df.dropna(subset=["date", "total_points"])
        df["team"] = df["country_full"].apply(normalize_team_name)
        df["points"] = df["total_points"]
        if "confederation" not in df.columns:
            df["confederation"] = ""
    else:
        # Elo-generated format (already has correct columns)
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df = df.dropna(subset=["date", "points"])
        df["team"] = df["team"].apply(normalize_team_name)
        if "confederation" not in df.columns:
            df["confederation"] = ""

    # Keep relevant columns
    df = df[["rank", "team", "points", "confederation", "date"]]

    # Sort
    df = df.sort_values(["date", "rank"]).reset_index(drop=True)

    print(f"  ✓ Cleaned rankings: {len(df):,} entries")
    return df


def get_latest_rankings(rankings_df: pd.DataFrame) -> pd.DataFrame:
    """Get the most recent ranking for each team."""
    latest_date = rankings_df["date"].max()
    latest = rankings_df[rankings_df["date"] == latest_date].copy()
    latest = latest.sort_values("rank").reset_index(drop=True)
    print(f"  ✓ Latest rankings as of {latest_date.date()}: {len(latest)} teams")
    return latest


def get_team_ranking_at_date(
    rankings_df: pd.DataFrame,
    team: str,
    date: pd.Timestamp,
) -> Optional[dict]:
    """Get a team's ranking closest to (but not after) a given date."""
    team_data = rankings_df[
        (rankings_df["team"] == team) & (rankings_df["date"] <= date)
    ]
    if team_data.empty:
        return None
    latest = team_data.sort_values("date").iloc[-1]
    return {
        "rank": int(latest["rank"]),
        "points": float(latest["points"]),
        "confederation": latest["confederation"],
    }


def build_world_cup_history(matches_df: pd.DataFrame) -> pd.DataFrame:
    """Extract World Cup match history with tournament metadata.
    
    Returns a DataFrame with WC matches and the year/tournament round.
    """
    wc = matches_df[matches_df["is_world_cup"]].copy()

    # Extract year
    wc["year"] = wc["date"].dt.year

    # Identify tournament rounds from the tournament name
    # e.g., "FIFA World Cup" → group stage, "FIFA World Cup Quarter-finals" etc.
    wc["round"] = "Group stage"
    for rnd in [
        "Round of 16", "Quarter-finals", "Semi-finals",
        "Third place", "Final", "Play-off",
    ]:
        mask = wc["tournament"].str.contains(rnd, case=False, na=False)
        wc.loc[mask, "round"] = rnd

    print(f"  ✓ World Cup history: {len(wc):,} matches across {wc['year'].nunique()} tournaments")
    return wc


def clean_squad_values(df: pd.DataFrame) -> pd.DataFrame:
    """Standardize squad values dataset."""
    df = df.copy()
    df["team_name"] = df["team_name"].apply(normalize_team_name)
    print(f"  ✓ Cleaned squad values: {len(df):,} teams")
    return df



def clean_all(raw_data: dict) -> dict:
    """Run full cleaning pipeline on all raw datasets."""
    print("\n" + "=" * 60)
    print("  Data Cleaning Pipeline")
    print("=" * 60)

    cleaned = {}

    print("\n[1/3] Cleaning match results...")
    cleaned["matches"] = clean_match_results(raw_data["results"])

    print("\n[2/4] Cleaning FIFA rankings...")
    cleaned["rankings"] = clean_fifa_rankings(raw_data["rankings"])

    print("\n[3/4] Extracting World Cup history...")
    cleaned["wc_history"] = build_world_cup_history(cleaned["matches"])

    if "squad_values" in raw_data:
        print("\n[4/4] Cleaning squad values...")
        cleaned["squad_values"] = clean_squad_values(raw_data["squad_values"])

    # Save interim datasets
    INTERIM_DIR.mkdir(parents=True, exist_ok=True)
    for name, df in cleaned.items():
        path = INTERIM_DIR / f"{name}.csv"
        df.to_csv(path, index=False)
        print(f"  💾 Saved {name} → {path}")

    # Coverage check for 2026 teams
    all_teams_in_data = set(
        cleaned["matches"]["home_team"].unique()
    ) | set(cleaned["matches"]["away_team"].unique())
    
    qualified = set(ALL_QUALIFIED_TEAMS)
    missing = qualified - all_teams_in_data
    if missing:
        print(f"\n  ⚠ Teams not found in match data: {missing}")
    else:
        print(f"\n  ✓ All 48 qualified teams found in match data")

    print("\n" + "=" * 60)
    return cleaned
