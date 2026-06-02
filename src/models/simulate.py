"""
Monte Carlo Tournament Simulator for FIFA 2026 World Cup.

Simulates the entire tournament structure:
  - 12 groups of 4 teams (group stage)
  - Top 2 from each group advance (24 teams)
  - 8 best third-placed teams advance (total 32 in knockouts)
  - Round of 32 → Round of 16 → QF → SF → Final

Each match outcome is sampled from the model's predicted probability
distribution, and the full tournament is simulated N times (default 10,000)
to produce win-probability estimates for each team.
"""
import numpy as np
import pandas as pd
from typing import Optional
from collections import Counter

from src.config import (
    WC_2026_TEAMS,
    ALL_QUALIFIED_TEAMS,
    N_SIMULATIONS,
    RANDOM_SEED,
    REPORTS_DIR,
)


class TournamentSimulator:
    """Monte Carlo simulator for the 2026 FIFA World Cup.

    The 2026 format:
      - 48 teams in 12 groups of 4
      - Group stage: each team plays 3 matches
      - Top 2 per group (24) + 8 best 3rd-place teams = 32 advance
      - Single-elimination knockouts: R32 → R16 → QF → SF → Final
    """

    def __init__(
        self,
        predict_fn,
        team_snapshots: dict[str, dict],
        feature_builder_fn,
        feature_columns: list[str],
        groups: dict[str, list[str]] = None,
        n_simulations: int = N_SIMULATIONS,
        random_seed: int = RANDOM_SEED,
    ):
        """
        Args:
            predict_fn: Callable that takes (n_samples, n_features) array
                        and returns (n_samples, 3) probability array
                        [P(Away Win), P(Draw), P(Home Win)].
            team_snapshots: Dict mapping team name → feature snapshot dict.
            feature_builder_fn: Callable(home_snap, away_snap, neutral) → feature dict.
            feature_columns: List of feature column names in correct order.
            groups: Dict mapping group letter → list of 4 team names.
            n_simulations: Number of tournament simulations.
            random_seed: Random seed for reproducibility.
        """
        self.predict_fn = predict_fn
        self.team_snapshots = team_snapshots
        self.feature_builder_fn = feature_builder_fn
        self.feature_columns = feature_columns
        self.groups = groups or WC_2026_TEAMS
        self.n_simulations = n_simulations
        self.rng = np.random.RandomState(random_seed)
        self.matchup_cache = {}

        # Validate all teams have snapshots
        for group, teams in self.groups.items():
            for team in teams:
                if team not in self.team_snapshots:
                    raise ValueError(
                        f"Team '{team}' (Group {group}) not found in snapshots"
                    )

    def predict_match(
        self,
        team_a: str,
        team_b: str,
        knockout: bool = False,
    ) -> dict:
        """Predict a single match outcome.

        In group stage: returns Win/Draw/Loss.
        In knockout: no draw allowed — resample until decisive result,
        simulating extra time / penalties.
        """
        # Check cache to avoid redundant predictions
        cache_key = (team_a, team_b, knockout)
        if cache_key in self.matchup_cache:
            probs = self.matchup_cache[cache_key]
        else:
            snap_a = self.team_snapshots[team_a]
            snap_b = self.team_snapshots[team_b]

            # Build features (team_a = "home" in the feature structure)
            features = self.feature_builder_fn(snap_a, snap_b, neutral=True)
            X = np.array([[features.get(col, 0) for col in self.feature_columns]])

            # Predict: [P(Away=B wins), P(Draw), P(Home=A wins)]
            probs = self.predict_fn(X)[0]

            # Ensure probabilities sum exactly to 1.0 (avoids float precision errors in np.random.choice)
            probs = np.nan_to_num(probs, nan=0.33)
            if probs.sum() > 0:
                probs = probs / probs.sum()
            else:
                probs = np.array([0.33, 0.34, 0.33])

            if knockout:
                # In knockouts, redistribute draw probability
                # proportional to win probabilities
                p_away, p_draw, p_home = probs
                p_home_adj = p_home + p_draw * (p_home / (p_home + p_away + 1e-10))
                p_away_adj = p_away + p_draw * (p_away / (p_home + p_away + 1e-10))
                probs = np.array([p_away_adj, 0.0, p_home_adj])
                probs = probs / probs.sum()  # Renormalize
                
            self.matchup_cache[cache_key] = probs

        # Sample outcome
        outcome = self.rng.choice([0, 1, 2], p=probs)

        if outcome == 2:  # Home/A win
            return {"winner": team_a, "loser": team_b, "draw": False}
        elif outcome == 0:  # Away/B win
            return {"winner": team_b, "loser": team_a, "draw": False}
        else:  # Draw
            return {"winner": None, "loser": None, "draw": True}

    def simulate_group(self, group_name: str) -> list[str]:
        """Simulate all group stage matches and return ranked teams.

        Returns list of 4 teams sorted by: points, goal difference (random tiebreak).
        """
        teams = self.groups[group_name]
        standings = {t: {"pts": 0, "gd": 0, "gf": 0} for t in teams}

        # Round-robin: 6 matches per group (each pair plays once)
        for i in range(len(teams)):
            for j in range(i + 1, len(teams)):
                result = self.predict_match(teams[i], teams[j], knockout=False)

                if result["draw"]:
                    standings[teams[i]]["pts"] += 1
                    standings[teams[j]]["pts"] += 1
                elif result["winner"] == teams[i]:
                    standings[teams[i]]["pts"] += 3
                else:
                    standings[teams[j]]["pts"] += 3

        # Sort by points, then goal difference (randomized tiebreak)
        ranked = sorted(
            teams,
            key=lambda t: (
                standings[t]["pts"],
                self.rng.random(),  # Random tiebreak for simplicity
            ),
            reverse=True,
        )
        return ranked

    def simulate_tournament(self) -> dict:
        """Simulate the full tournament once.

        Returns dict with:
            - winner: tournament winner
            - finalist: runner-up
            - semifinalists: list of 2 losing semifinalists
            - group_results: dict of group → ranked team list
        """
        # ── Group Stage ──
        group_results = {}
        group_winners = []
        group_runners_up = []
        third_place_teams = []

        for group_name in sorted(self.groups.keys()):
            ranked = self.simulate_group(group_name)
            group_results[group_name] = ranked
            group_winners.append(ranked[0])
            group_runners_up.append(ranked[1])
            third_place_teams.append(ranked[2])

        # 8 best third-place teams advance
        # Shuffle and take 8 (simplified — in reality based on points)
        self.rng.shuffle(third_place_teams)
        best_thirds = third_place_teams[:8]

        # 32 teams advance to knockouts
        advancing = group_winners + group_runners_up + best_thirds
        self.rng.shuffle(advancing)  # Simplified bracket seeding

        # ── Knockout Rounds ──
        current_round = advancing

        round_names = ["Round of 32", "Round of 16", "Quarter-finals",
                       "Semi-finals", "Final"]

        for round_name in round_names:
            next_round = []
            for i in range(0, len(current_round), 2):
                if i + 1 < len(current_round):
                    result = self.predict_match(
                        current_round[i],
                        current_round[i + 1],
                        knockout=True,
                    )
                    next_round.append(result["winner"])
                else:
                    # Bye (odd number)
                    next_round.append(current_round[i])

            if round_name == "Semi-finals":
                semifinalists = [
                    t for t in current_round if t not in next_round
                ]

            if round_name == "Final":
                finalist = [
                    t for t in current_round if t not in next_round
                ][0] if len(current_round) > 1 else None

            current_round = next_round

        winner = current_round[0] if current_round else None

        return {
            "winner": winner,
            "finalist": finalist,
            "semifinalists": semifinalists if 'semifinalists' in dir() else [],
            "group_results": group_results,
        }

    def run_simulations(self) -> pd.DataFrame:
        """Run N tournament simulations and aggregate results.

        Returns DataFrame with columns:
            team, win_count, win_prob, final_count, final_prob,
            semi_count, semi_prob, group_advance_count, group_advance_prob
        """
        print(f"\n{'=' * 60}")
        print(f"  Monte Carlo Tournament Simulation")
        print(f"  Running {self.n_simulations:,} simulations...")
        print(f"{'=' * 60}")

        win_counts = Counter()
        final_counts = Counter()
        semi_counts = Counter()
        advance_counts = Counter()

        for sim in range(self.n_simulations):
            if (sim + 1) % 1000 == 0:
                print(f"    Simulation {sim + 1:,}/{self.n_simulations:,}...")

            result = self.simulate_tournament()

            # Winner
            if result["winner"]:
                win_counts[result["winner"]] += 1
                final_counts[result["winner"]] += 1

            # Finalist
            if result.get("finalist"):
                final_counts[result["finalist"]] += 1

            # Semifinalists
            for team in result.get("semifinalists", []):
                semi_counts[team] += 1
                final_counts.get(team, 0)  # Already counted if finalist

            # Group advancement
            for group, ranked in result["group_results"].items():
                for team in ranked[:3]:  # Top 3 might advance
                    advance_counts[team] += 1

        # Build results DataFrame
        results = []
        for team in ALL_QUALIFIED_TEAMS:
            results.append({
                "team": team,
                "win_count": win_counts.get(team, 0),
                "win_prob": win_counts.get(team, 0) / self.n_simulations,
                "final_count": final_counts.get(team, 0),
                "final_prob": final_counts.get(team, 0) / self.n_simulations,
                "semi_count": semi_counts.get(team, 0),
                "semi_prob": semi_counts.get(team, 0) / self.n_simulations,
            })

        df = pd.DataFrame(results).sort_values("win_prob", ascending=False)
        df = df.reset_index(drop=True)
        df.index += 1  # 1-indexed ranking

        print(f"\n{'=' * 60}")
        print("  TOP 15 TEAMS BY WIN PROBABILITY")
        print(f"{'=' * 60}")
        print(df.head(15)[["team", "win_prob", "final_prob", "semi_prob"]].to_string())
        print(f"{'=' * 60}\n")

        return df

    def save_predictions(self, results_df: pd.DataFrame) -> None:
        """Save prediction results to reports directory."""
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)

        # CSV
        csv_path = REPORTS_DIR / "tournament_predictions.csv"
        results_df.to_csv(csv_path)
        print(f"  💾 Saved predictions CSV → {csv_path}")

        # Markdown report
        md = "# FIFA 2026 World Cup — Tournament Predictions\n\n"
        md += f"Based on {self.n_simulations:,} Monte Carlo simulations\n\n"
        md += "## Win Probabilities\n\n"
        md += "| Rank | Team | Win % | Final % | Semi % |\n"
        md += "|------|------|-------|---------|--------|\n"

        for idx, row in results_df.head(48).iterrows():
            md += (
                f"| {idx} | {row['team']} | "
                f"{row['win_prob']*100:.1f}% | "
                f"{row['final_prob']*100:.1f}% | "
                f"{row['semi_prob']*100:.1f}% |\n"
            )

        md_path = REPORTS_DIR / "tournament_predictions.md"
        md_path.write_text(md)
        print(f"  💾 Saved predictions report → {md_path}")
