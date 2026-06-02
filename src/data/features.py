"""
Feature engineering for FIFA 2026 WC Prediction Pipeline.

Transforms cleaned match results and rankings into model-ready features.
Each row in the output represents a match with features for both teams.
"""
import pandas as pd
import numpy as np
from typing import Optional

from src.config import (
    ELO_K_FACTOR,
    ELO_INITIAL,
    FORM_WINDOWS,
    PROCESSED_DIR,
    ALL_QUALIFIED_TEAMS,
)


# ════════════════════════════════════════════════════════════════════════
# 1. Elo Rating System
# ════════════════════════════════════════════════════════════════════════

class EloRatingSystem:
    """Calculate Elo ratings for international football teams.

    Uses the standard Elo formula with adjustments for:
    - Goal difference (capped log multiplier)
    - Tournament importance (higher K for World Cup)
    - Home advantage correction
    """

    def __init__(
        self,
        k_factor: int = ELO_K_FACTOR,
        initial_rating: int = ELO_INITIAL,
        home_advantage: int = 100,
    ):
        self.k_factor = k_factor
        self.initial_rating = initial_rating
        self.home_advantage = home_advantage
        self.ratings: dict[str, float] = {}
        self.history: list[dict] = []  # Track rating over time

    def get_rating(self, team: str) -> float:
        return self.ratings.get(team, self.initial_rating)

    def expected_score(self, rating_a: float, rating_b: float) -> float:
        """Expected score for team A given both ratings."""
        return 1.0 / (1.0 + 10.0 ** ((rating_b - rating_a) / 400.0))

    def goal_diff_multiplier(self, goal_diff: int) -> float:
        """Multiplier based on margin of victory (dampened)."""
        abs_diff = abs(goal_diff)
        if abs_diff <= 1:
            return 1.0
        elif abs_diff == 2:
            return 1.5
        else:
            return (11.0 + abs_diff) / 8.0

    def tournament_k_factor(self, tournament: str) -> float:
        """Adjust K-factor based on tournament importance."""
        t = tournament.lower()
        if "world cup" in t and "qualif" not in t:
            return self.k_factor * 1.5   # 60 for WC matches
        elif "continental" in t or "euro" in t or "copa" in t or "nations" in t:
            return self.k_factor * 1.25  # 50 for continental
        elif "friendly" in t:
            return self.k_factor * 0.5   # 20 for friendlies
        else:
            return self.k_factor         # 40 default

    def update(
        self,
        home_team: str,
        away_team: str,
        home_score: int,
        away_score: int,
        tournament: str = "",
        neutral: bool = False,
        date: Optional[pd.Timestamp] = None,
    ) -> tuple[float, float]:
        """Update ratings after a match. Returns (new_home_elo, new_away_elo)."""
        # Current ratings
        home_elo = self.get_rating(home_team)
        away_elo = self.get_rating(away_team)

        # Adjust for home advantage (unless neutral venue)
        adj_home = home_elo + (0 if neutral else self.home_advantage)
        adj_away = away_elo

        # Expected scores
        exp_home = self.expected_score(adj_home, adj_away)
        exp_away = 1.0 - exp_home

        # Actual scores (1 = win, 0.5 = draw, 0 = loss)
        if home_score > away_score:
            actual_home, actual_away = 1.0, 0.0
        elif home_score == away_score:
            actual_home, actual_away = 0.5, 0.5
        else:
            actual_home, actual_away = 0.0, 1.0

        # K and goal diff multiplier
        k = self.tournament_k_factor(tournament)
        g = self.goal_diff_multiplier(home_score - away_score)

        # Update
        new_home = home_elo + k * g * (actual_home - exp_home)
        new_away = away_elo + k * g * (actual_away - exp_away)

        self.ratings[home_team] = new_home
        self.ratings[away_team] = new_away

        # Track history
        if date is not None:
            self.history.append(
                {"date": date, "team": home_team, "elo": new_home}
            )
            self.history.append(
                {"date": date, "team": away_team, "elo": new_away}
            )

        return new_home, new_away

    def process_matches(self, matches_df: pd.DataFrame) -> pd.DataFrame:
        """Process all matches chronologically and compute Elo ratings.

        Adds columns: home_elo, away_elo, elo_diff to the DataFrame.
        """
        df = matches_df.sort_values("date").copy()
        home_elos, away_elos = [], []

        for _, row in df.iterrows():
            # Record pre-match ratings
            home_elos.append(self.get_rating(row["home_team"]))
            away_elos.append(self.get_rating(row["away_team"]))

            # Update ratings with this match result
            self.update(
                home_team=row["home_team"],
                away_team=row["away_team"],
                home_score=int(row["home_score"]),
                away_score=int(row["away_score"]),
                tournament=row.get("tournament", ""),
                neutral=row.get("neutral", False),
                date=row["date"],
            )

        df["home_elo"] = home_elos
        df["away_elo"] = away_elos
        df["elo_diff"] = df["home_elo"] - df["away_elo"]

        return df

    def get_current_ratings(self) -> pd.DataFrame:
        """Return current ratings as a sorted DataFrame."""
        data = [
            {"team": team, "elo": elo}
            for team, elo in self.ratings.items()
        ]
        return pd.DataFrame(data).sort_values("elo", ascending=False).reset_index(drop=True)


# ════════════════════════════════════════════════════════════════════════
# 2. Rolling Form Features
# ════════════════════════════════════════════════════════════════════════

def compute_team_form(
    matches_df: pd.DataFrame,
    team: str,
    before_date: pd.Timestamp,
    n_matches: int = 10,
) -> dict:
    """Compute rolling form statistics for a team before a given date.

    Returns dict with: win_rate, draw_rate, loss_rate,
    goals_scored_avg, goals_conceded_avg, goal_diff_avg.
    """
    # Get matches involving this team before the date
    mask = (
        ((matches_df["home_team"] == team) | (matches_df["away_team"] == team))
        & (matches_df["date"] < before_date)
    )
    team_matches = matches_df[mask].sort_values("date", ascending=False).head(n_matches)

    if len(team_matches) == 0:
        return {
            f"form_{n_matches}_win_rate": 0.5,
            f"form_{n_matches}_draw_rate": 0.2,
            f"form_{n_matches}_loss_rate": 0.3,
            f"form_{n_matches}_goals_scored": 1.0,
            f"form_{n_matches}_goals_conceded": 1.0,
            f"form_{n_matches}_goal_diff": 0.0,
            f"form_{n_matches}_n_matches": 0,
        }

    wins, draws, losses = 0, 0, 0
    goals_scored, goals_conceded = 0, 0

    for _, m in team_matches.iterrows():
        if m["home_team"] == team:
            gs, gc = m["home_score"], m["away_score"]
        else:
            gs, gc = m["away_score"], m["home_score"]

        goals_scored += gs
        goals_conceded += gc

        if gs > gc:
            wins += 1
        elif gs == gc:
            draws += 1
        else:
            losses += 1

    n = len(team_matches)
    return {
        f"form_{n_matches}_win_rate": wins / n,
        f"form_{n_matches}_draw_rate": draws / n,
        f"form_{n_matches}_loss_rate": losses / n,
        f"form_{n_matches}_goals_scored": goals_scored / n,
        f"form_{n_matches}_goals_conceded": goals_conceded / n,
        f"form_{n_matches}_goal_diff": (goals_scored - goals_conceded) / n,
        f"form_{n_matches}_n_matches": n,
    }


def compute_head_to_head(
    matches_df: pd.DataFrame,
    team_a: str,
    team_b: str,
    before_date: pd.Timestamp,
    max_matches: int = 20,
) -> dict:
    """Compute head-to-head record between two teams."""
    mask = (
        (
            ((matches_df["home_team"] == team_a) & (matches_df["away_team"] == team_b))
            | ((matches_df["home_team"] == team_b) & (matches_df["away_team"] == team_a))
        )
        & (matches_df["date"] < before_date)
    )
    h2h = matches_df[mask].sort_values("date", ascending=False).head(max_matches)

    if len(h2h) == 0:
        return {"h2h_win_rate": 0.5, "h2h_matches": 0, "h2h_goal_diff": 0.0}

    wins_a, goals_a, goals_b = 0, 0, 0
    for _, m in h2h.iterrows():
        if m["home_team"] == team_a:
            ga, gb = m["home_score"], m["away_score"]
        else:
            ga, gb = m["away_score"], m["home_score"]
        goals_a += ga
        goals_b += gb
        if ga > gb:
            wins_a += 1

    n = len(h2h)
    return {
        "h2h_win_rate": wins_a / n,
        "h2h_matches": n,
        "h2h_goal_diff": (goals_a - goals_b) / n,
    }


# ════════════════════════════════════════════════════════════════════════
# 3. World Cup History Features
# ════════════════════════════════════════════════════════════════════════

# Ordinal encoding for WC round
WC_ROUND_MAP = {
    "Group stage": 1,
    "Round of 16": 2,
    "Quarter-finals": 3,
    "Semi-finals": 4,
    "Third place": 4,  # Same as semifinal (lost semi)
    "Final": 5,
    "Winner": 6,
}


def compute_wc_history_features(
    wc_matches: pd.DataFrame,
    team: str,
) -> dict:
    """Compute World Cup historical performance features for a team."""
    mask = (wc_matches["home_team"] == team) | (wc_matches["away_team"] == team)
    team_wc = wc_matches[mask]

    if len(team_wc) == 0:
        return {
            "wc_appearances": 0,
            "wc_matches_played": 0,
            "wc_win_rate": 0.0,
            "wc_goals_per_match": 0.0,
            "wc_best_finish": 0,
            "wc_avg_finish": 0.0,
        }

    # Count appearances (unique tournament years)
    years = team_wc["year"].unique()
    appearances = len(years)
    total_matches = len(team_wc)

    # Win/loss/draw counts
    wins = 0
    goals_scored = 0
    for _, m in team_wc.iterrows():
        if m["home_team"] == team:
            gs = m["home_score"]
            if m["home_score"] > m["away_score"]:
                wins += 1
        else:
            gs = m["away_score"]
            if m["away_score"] > m["home_score"]:
                wins += 1
        goals_scored += gs

    # Best and average finish
    best_rounds = []
    for year in years:
        year_matches = team_wc[team_wc["year"] == year]
        rounds = year_matches["round"].map(WC_ROUND_MAP).max()
        best_rounds.append(rounds)

    return {
        "wc_appearances": appearances,
        "wc_matches_played": total_matches,
        "wc_win_rate": wins / total_matches if total_matches > 0 else 0.0,
        "wc_goals_per_match": goals_scored / total_matches if total_matches > 0 else 0.0,
        "wc_best_finish": max(best_rounds) if best_rounds else 0,
        "wc_avg_finish": np.mean(best_rounds) if best_rounds else 0.0,
    }


# ════════════════════════════════════════════════════════════════════════
# 4. FIFA Ranking Features
# ════════════════════════════════════════════════════════════════════════

def get_ranking_features(
    rankings_df: pd.DataFrame,
    team: str,
    date: pd.Timestamp,
) -> dict:
    """Get FIFA ranking features for a team at a given date."""
    team_ranks = rankings_df[
        (rankings_df["team"] == team) & (rankings_df["date"] <= date)
    ].sort_values("date")

    if len(team_ranks) == 0:
        return {
            "fifa_rank": 100,
            "fifa_points": 1000.0,
            "fifa_rank_delta_6m": 0,
            "fifa_rank_delta_12m": 0,
        }

    latest = team_ranks.iloc[-1]
    rank = int(latest["rank"])
    points = float(latest["points"])

    # Rank change over 6 and 12 months
    six_months_ago = date - pd.DateOffset(months=6)
    twelve_months_ago = date - pd.DateOffset(months=12)

    rank_6m = team_ranks[team_ranks["date"] <= six_months_ago]
    rank_12m = team_ranks[team_ranks["date"] <= twelve_months_ago]

    delta_6m = (int(rank_6m.iloc[-1]["rank"]) - rank) if len(rank_6m) > 0 else 0
    delta_12m = (int(rank_12m.iloc[-1]["rank"]) - rank) if len(rank_12m) > 0 else 0

    return {
        "fifa_rank": rank,
        "fifa_points": points,
        "fifa_rank_delta_6m": delta_6m,   # Positive = improved
        "fifa_rank_delta_12m": delta_12m,
    }


# ════════════════════════════════════════════════════════════════════════
# 5. Build Match-Level Feature Matrix (Optimized)
# ════════════════════════════════════════════════════════════════════════

import bisect
from collections import defaultdict

def get_ranking_features_opt(
    rankings_by_team: dict,
    rankings_dates: dict,
    team: str,
    date: pd.Timestamp,
) -> dict:
    """Get FIFA ranking features for a team at a given date (Optimized)."""
    ranks = rankings_by_team.get(team, [])
    dates = rankings_dates.get(team, [])
    if not ranks:
        return {
            "fifa_rank": 100,
            "fifa_points": 1000.0,
            "fifa_rank_delta_6m": 0,
            "fifa_rank_delta_12m": 0,
        }

    idx = bisect.bisect_right(dates, date)
    if idx == 0:
        return {
            "fifa_rank": 100,
            "fifa_points": 1000.0,
            "fifa_rank_delta_6m": 0,
            "fifa_rank_delta_12m": 0,
        }

    latest = ranks[idx - 1]
    rank = int(latest[1])
    points = float(latest[2])

    six_months_ago = date - pd.DateOffset(months=6)
    twelve_months_ago = date - pd.DateOffset(months=12)

    idx_6m = bisect.bisect_right(dates, six_months_ago)
    idx_12m = bisect.bisect_right(dates, twelve_months_ago)

    delta_6m = (int(ranks[idx_6m - 1][1]) - rank) if idx_6m > 0 else 0
    delta_12m = (int(ranks[idx_12m - 1][1]) - rank) if idx_12m > 0 else 0

    return {
        "fifa_rank": rank,
        "fifa_points": points,
        "fifa_rank_delta_6m": delta_6m,
        "fifa_rank_delta_12m": delta_12m,
    }


def get_form_metrics_from_list(recent_matches: list[dict], n_matches: int) -> dict:
    """Compute rolling form metrics from pre-filtered lists of recent matches."""
    if not recent_matches:
        return {
            f"form_{n_matches}_win_rate": 0.5,
            f"form_{n_matches}_draw_rate": 0.2,
            f"form_{n_matches}_loss_rate": 0.3,
            f"form_{n_matches}_goals_scored": 1.0,
            f"form_{n_matches}_goals_conceded": 1.0,
            f"form_{n_matches}_goal_diff": 0.0,
            f"form_{n_matches}_n_matches": 0,
        }

    wins, draws, losses = 0, 0, 0
    goals_scored, goals_conceded = 0, 0

    for m in recent_matches:
        gs = m["goals_scored"]
        gc = m["goals_conceded"]

        goals_scored += gs
        goals_conceded += gc

        if gs > gc:
            wins += 1
        elif gs == gc:
            draws += 1
        else:
            losses += 1

    n = len(recent_matches)
    return {
        f"form_{n_matches}_win_rate": wins / n,
        f"form_{n_matches}_draw_rate": draws / n,
        f"form_{n_matches}_loss_rate": losses / n,
        f"form_{n_matches}_goals_scored": goals_scored / n,
        f"form_{n_matches}_goals_conceded": goals_conceded / n,
        f"form_{n_matches}_goal_diff": (goals_scored - goals_conceded) / n,
        f"form_{n_matches}_n_matches": n,
    }


def build_match_features(
    matches_df: pd.DataFrame,
    rankings_df: pd.DataFrame,
    wc_matches: pd.DataFrame,
    elo_system: EloRatingSystem,
    squad_values: pd.DataFrame = None,
    min_date: str = "2000-01-01",
) -> pd.DataFrame:
    """Build the complete feature matrix for all matches (Optimized version).
    
    Each row = one match, with features for both home and away team,
    plus difference features.
    """
    # Sort matches chronologically by date
    matches_sorted = matches_df.sort_values("date").copy()
    
    # Pre-group rankings by team
    rankings_by_team = {}
    rankings_dates = {}
    for team, group in rankings_df.groupby("team"):
        sorted_group = group.sort_values("date")
        rankings_by_team[team] = list(zip(
            sorted_group["date"],
            sorted_group["rank"],
            sorted_group["points"]
        ))
        rankings_dates[team] = sorted_group["date"].tolist()

    df = matches_sorted[matches_sorted["date"] >= min_date].copy()
    print(f"  Building features for {len(df):,} matches from {min_date}...")

    # Pre-compute WC history for all teams (static)
    all_teams = set(matches_sorted["home_team"].unique()) | set(matches_sorted["away_team"].unique())
    wc_features_cache = {}
    for team in all_teams:
        wc_features_cache[team] = compute_wc_history_features(wc_matches, team)

    # Pre-process squad values mapping
    squad_val_map = {}
    fifa_rating_map = {}
    stars_map = {}
    injuries_map = {}
    continent_map = {}
    if squad_values is not None:
        for _, row in squad_values.iterrows():
            squad_val_map[row["team_name"]] = row["squad_value_m"]
            fifa_rating_map[row["team_name"]] = row["fifa_rating"]
            stars_map[row["team_name"]] = row.get("star_player_count", 0)
            injuries_map[row["team_name"]] = row.get("key_injuries", 0)
            continent_map[row["team_name"]] = row.get("home_continent", "Europe")

    # Initialize histories
    team_history = defaultdict(list)
    team_dates = defaultdict(list)
    h2h_history = defaultdict(list)
    h2h_dates = defaultdict(list)

    # Populate history with matches BEFORE min_date
    past_matches = matches_sorted[matches_sorted["date"] < min_date]
    print(f"  Populating initial history with {len(past_matches):,} past matches...")
    for _, row in past_matches.iterrows():
        home = row["home_team"]
        away = row["away_team"]
        date = row["date"]
        home_score = int(row["home_score"])
        away_score = int(row["away_score"])

        team_history[home].append({
            "goals_scored": home_score,
            "goals_conceded": away_score,
        })
        team_dates[home].append(date)

        team_history[away].append({
            "goals_scored": away_score,
            "goals_conceded": home_score,
        })
        team_dates[away].append(date)

        h2h_key = tuple(sorted([home, away]))
        h2h_history[h2h_key].append({
            "home_team": home,
            "away_team": away,
            "home_score": home_score,
            "away_score": away_score,
        })
        h2h_dates[h2h_key].append(date)

    feature_rows = []
    total = len(df)

    for idx, (_, row) in enumerate(df.iterrows()):
        if (idx + 1) % 5000 == 0 or idx == 0 or idx == total - 1:
            print(f"    Processing match {idx+1:,}/{total:,}...")

        home = row["home_team"]
        away = row["away_team"]
        date = row["date"]
        home_score = int(row["home_score"])
        away_score = int(row["away_score"])

        features = {
            "date": date,
            "home_team": home,
            "away_team": away,
            "home_score": home_score,
            "away_score": away_score,
            "tournament": row["tournament"],
            "neutral": row["neutral"],
            "is_world_cup": row["is_world_cup"],
            "is_competitive": row["is_competitive"],
        }

        # --- Target variable ---
        if home_score > away_score:
            features["result"] = 1  # Home win
        elif home_score == away_score:
            features["result"] = 0  # Draw
        else:
            features["result"] = -1  # Away win

        # --- Elo ratings (already computed) ---
        features["home_elo"] = row.get("home_elo", elo_system.get_rating(home))
        features["away_elo"] = row.get("away_elo", elo_system.get_rating(away))
        features["elo_diff"] = features["home_elo"] - features["away_elo"]

        # --- FIFA Rankings ---
        home_rank = get_ranking_features_opt(rankings_by_team, rankings_dates, home, date)
        away_rank = get_ranking_features_opt(rankings_by_team, rankings_dates, away, date)
        for k, v in home_rank.items():
            features[f"home_{k}"] = v
        for k, v in away_rank.items():
            features[f"away_{k}"] = v
        features["rank_diff"] = features["home_fifa_rank"] - features["away_fifa_rank"]
        features["points_diff"] = features["home_fifa_points"] - features["away_fifa_points"]

        # --- Form (use team_history sliced up to current date) ---
        for window in [10, 30]:
            # home form
            idx_h = bisect.bisect_left(team_dates[home], date)
            recent_h = team_history[home][:idx_h][-window:]
            home_form = get_form_metrics_from_list(recent_h, window)

            # away form
            idx_a = bisect.bisect_left(team_dates[away], date)
            recent_a = team_history[away][:idx_a][-window:]
            away_form = get_form_metrics_from_list(recent_a, window)

            for k, v in home_form.items():
                features[f"home_{k}"] = v
            for k, v in away_form.items():
                features[f"away_{k}"] = v

            # Difference features
            features[f"form_{window}_win_rate_diff"] = (
                home_form[f"form_{window}_win_rate"]
                - away_form[f"form_{window}_win_rate"]
            )
            features[f"form_{window}_goal_diff_diff"] = (
                home_form[f"form_{window}_goal_diff"]
                - away_form[f"form_{window}_goal_diff"]
            )

        # --- Head to Head ---
        h2h_key = tuple(sorted([home, away]))
        idx_h2h = bisect.bisect_left(h2h_dates[h2h_key], date)
        recent_h2h = h2h_history[h2h_key][:idx_h2h][-20:]
        
        # Calculate H2H features
        if not recent_h2h:
            h2h_features = {"h2h_win_rate": 0.5, "h2h_matches": 0, "h2h_goal_diff": 0.0}
        else:
            wins_a, goals_a, goals_b = 0, 0, 0
            for m in recent_h2h:
                if m["home_team"] == home:
                    ga, gb = m["home_score"], m["away_score"]
                else:
                    ga, gb = m["away_score"], m["home_score"]
                goals_a += ga
                goals_b += gb
                if ga > gb:
                    wins_a += 1
            n_h2h = len(recent_h2h)
            h2h_features = {
                "h2h_win_rate": wins_a / n_h2h,
                "h2h_matches": n_h2h,
                "h2h_goal_diff": (goals_a - goals_b) / n_h2h,
            }

        for k, v in h2h_features.items():
            features[k] = v

        # --- World Cup History ---
        for k, v in wc_features_cache.get(home, {}).items():
            features[f"home_{k}"] = v
        for k, v in wc_features_cache.get(away, {}).items():
            features[f"away_{k}"] = v
        features["wc_appearances_diff"] = (
            features.get("home_wc_appearances", 0)
            - features.get("away_wc_appearances", 0)
        )
        features["wc_best_finish_diff"] = (
            features.get("home_wc_best_finish", 0)
            - features.get("away_wc_best_finish", 0)
        )

        # --- Squad Values & Ratings ---
        # Default to very low market value (5M) and rating (65) for unmapped teams
        features["home_squad_value_m"] = squad_val_map.get(home, 5.0)
        features["away_squad_value_m"] = squad_val_map.get(away, 5.0)
        
        # Apply injury penalty (reduce value by 15% per key injury)
        features["home_squad_value_m"] *= (1.0 - 0.15 * injuries_map.get(home, 0))
        features["away_squad_value_m"] *= (1.0 - 0.15 * injuries_map.get(away, 0))
        
        features["home_fifa_rating"] = fifa_rating_map.get(home, 65.0)
        features["away_fifa_rating"] = fifa_rating_map.get(away, 65.0)
        
        features["home_stars"] = stars_map.get(home, 0)
        features["away_stars"] = stars_map.get(away, 0)

        features["squad_value_diff"] = features["home_squad_value_m"] - features["away_squad_value_m"]
        features["squad_value_ratio"] = features["home_squad_value_m"] / max(features["away_squad_value_m"], 1.0)
        features["fifa_rating_diff"] = features["home_fifa_rating"] - features["away_fifa_rating"]
        features["stars_diff"] = features["home_stars"] - features["away_stars"]
        
        # --- Match-level Stats Proxy (xG Form) ---
        # Since we lack historic xG, we simulate xG_diff based on goal_diff_diff and elo_diff
        features["xg_form_diff"] = features.get("form_10_goal_diff_diff", 0) * 0.8 + (features.get("elo_diff", 0) / 400) * 0.2
        
        # --- Travel/Venue Factors ---
        # 2026 is in NA. Penalize non-NA teams slightly.
        home_cont = continent_map.get(home, "Europe")
        away_cont = continent_map.get(away, "Europe")
        
        features["home_travel_penalty"] = 0 if home_cont in ["North America", "South America"] else 1
        features["away_travel_penalty"] = 0 if away_cont in ["North America", "South America"] else 1
        features["travel_penalty_diff"] = features["home_travel_penalty"] - features["away_travel_penalty"]

        feature_rows.append(features)

        # Now append the current match to the history/dates lists so it's available for FUTURE matches
        team_history[home].append({
            "goals_scored": home_score,
            "goals_conceded": away_score,
        })
        team_dates[home].append(date)

        team_history[away].append({
            "goals_scored": away_score,
            "goals_conceded": home_score,
        })
        team_dates[away].append(date)

        h2h_history[h2h_key].append({
            "home_team": home,
            "away_team": away,
            "home_score": home_score,
            "away_score": away_score,
        })
        h2h_dates[h2h_key].append(date)

    feature_df = pd.DataFrame(feature_rows)
    print(f"  ✓ Feature matrix: {feature_df.shape[0]:,} rows × {feature_df.shape[1]} columns")

    # Save
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    feature_df.to_csv(PROCESSED_DIR / "match_features.csv", index=False)
    print(f"  💾 Saved to {PROCESSED_DIR / 'match_features.csv'}")

    return feature_df


# ════════════════════════════════════════════════════════════════════════
# 6. Get Team Snapshot (for prediction)
# ════════════════════════════════════════════════════════════════════════

def get_team_snapshot(
    team: str,
    matches_df: pd.DataFrame,
    rankings_df: pd.DataFrame,
    wc_matches: pd.DataFrame,
    elo_system: EloRatingSystem,
    squad_values: pd.DataFrame = None,
    as_of_date: pd.Timestamp = None,
) -> dict:
    """Get current feature snapshot for a team (for generating predictions).

    Used by the tournament simulator to create match-level features
    for hypothetical WC 2026 matches.
    """
    if as_of_date is None:
        as_of_date = pd.Timestamp.now()

    features = {}

    # Elo
    features["elo"] = elo_system.get_rating(team)

    # FIFA ranking
    rank_feats = get_ranking_features(rankings_df, team, as_of_date)
    features.update(rank_feats)

    # Form
    for window in [10, 30]:
        form = compute_team_form(matches_df, team, as_of_date, n_matches=window)
        features.update(form)

    # WC history
    wc_feats = compute_wc_history_features(wc_matches, team)
    features.update(wc_feats)

    # Squad values & ratings
    if squad_values is not None:
        team_sv = squad_values[squad_values["team_name"] == team]
        if not team_sv.empty:
            features["squad_value_m"] = team_sv.iloc[0]["squad_value_m"]
            features["fifa_rating"] = team_sv.iloc[0]["fifa_rating"]
            features["star_player_count"] = team_sv.iloc[0].get("star_player_count", 0)
            features["key_injuries"] = team_sv.iloc[0].get("key_injuries", 0)
            features["home_continent"] = team_sv.iloc[0].get("home_continent", "Europe")
        else:
            features["squad_value_m"] = 5.0
            features["fifa_rating"] = 65.0
            features["star_player_count"] = 0
            features["key_injuries"] = 0
            features["home_continent"] = "Europe"
    else:
        features["squad_value_m"] = 5.0
        features["fifa_rating"] = 65.0
        features["star_player_count"] = 0
        features["key_injuries"] = 0
        features["home_continent"] = "Europe"
        
    # Apply injury
    features["squad_value_m"] *= (1.0 - 0.15 * features["key_injuries"])

    return features


def build_matchup_features(
    home_snapshot: dict,
    away_snapshot: dict,
    neutral: bool = True,
) -> dict:
    """Build match-level features from two team snapshots.

    Used for predicting hypothetical matches (e.g., in tournament simulation).
    """
    features = {}

    # Elo
    features["home_elo"] = home_snapshot["elo"]
    features["away_elo"] = away_snapshot["elo"]
    features["elo_diff"] = home_snapshot["elo"] - away_snapshot["elo"]

    # Ranking
    features["home_fifa_rank"] = home_snapshot["fifa_rank"]
    features["away_fifa_rank"] = away_snapshot["fifa_rank"]
    features["home_fifa_points"] = home_snapshot["fifa_points"]
    features["away_fifa_points"] = away_snapshot["fifa_points"]
    features["rank_diff"] = home_snapshot["fifa_rank"] - away_snapshot["fifa_rank"]
    features["points_diff"] = home_snapshot["fifa_points"] - away_snapshot["fifa_points"]
    features["home_fifa_rank_delta_6m"] = home_snapshot["fifa_rank_delta_6m"]
    features["away_fifa_rank_delta_6m"] = away_snapshot["fifa_rank_delta_6m"]
    features["home_fifa_rank_delta_12m"] = home_snapshot["fifa_rank_delta_12m"]
    features["away_fifa_rank_delta_12m"] = away_snapshot["fifa_rank_delta_12m"]

    # Form
    for window in [10, 30]:
        for stat in ["win_rate", "draw_rate", "loss_rate", "goals_scored",
                      "goals_conceded", "goal_diff", "n_matches"]:
            key = f"form_{window}_{stat}"
            features[f"home_{key}"] = home_snapshot.get(key, 0)
            features[f"away_{key}"] = away_snapshot.get(key, 0)

        features[f"form_{window}_win_rate_diff"] = (
            home_snapshot.get(f"form_{window}_win_rate", 0.5)
            - away_snapshot.get(f"form_{window}_win_rate", 0.5)
        )
        features[f"form_{window}_goal_diff_diff"] = (
            home_snapshot.get(f"form_{window}_goal_diff", 0)
            - away_snapshot.get(f"form_{window}_goal_diff", 0)
        )

    # H2H placeholder (not available for snapshots without match history)
    features["h2h_win_rate"] = 0.5
    features["h2h_matches"] = 0
    features["h2h_goal_diff"] = 0.0

    # WC history
    for stat in ["wc_appearances", "wc_matches_played", "wc_win_rate",
                  "wc_goals_per_match", "wc_best_finish", "wc_avg_finish"]:
        features[f"home_{stat}"] = home_snapshot.get(stat, 0)
        features[f"away_{stat}"] = away_snapshot.get(stat, 0)
    features["wc_appearances_diff"] = (
        home_snapshot.get("wc_appearances", 0)
        - away_snapshot.get("wc_appearances", 0)
    )
    features["wc_best_finish_diff"] = (
        home_snapshot.get("wc_best_finish", 0)
        - away_snapshot.get("wc_best_finish", 0)
    )

    # Squad Values & Ratings
    features["home_squad_value_m"] = home_snapshot.get("squad_value_m", 5.0)
    features["away_squad_value_m"] = away_snapshot.get("squad_value_m", 5.0)
    features["home_fifa_rating"] = home_snapshot.get("fifa_rating", 65.0)
    features["away_fifa_rating"] = away_snapshot.get("fifa_rating", 65.0)
    
    features["home_stars"] = home_snapshot.get("star_player_count", 0)
    features["away_stars"] = away_snapshot.get("star_player_count", 0)

    features["squad_value_diff"] = features["home_squad_value_m"] - features["away_squad_value_m"]
    features["squad_value_ratio"] = features["home_squad_value_m"] / max(features["away_squad_value_m"], 1.0)
    features["fifa_rating_diff"] = features["home_fifa_rating"] - features["away_fifa_rating"]
    features["stars_diff"] = features["home_stars"] - features["away_stars"]
    
    features["xg_form_diff"] = features.get("form_10_goal_diff_diff", 0) * 0.8 + (features.get("elo_diff", 0) / 400) * 0.2
    
    hc = home_snapshot.get("home_continent", "Europe")
    ac = away_snapshot.get("home_continent", "Europe")
    features["home_travel_penalty"] = 0 if hc in ["North America", "South America"] else 1
    features["away_travel_penalty"] = 0 if ac in ["North America", "South America"] else 1
    features["travel_penalty_diff"] = features["home_travel_penalty"] - features["away_travel_penalty"]

    # Context
    features["neutral"] = neutral

    return features
