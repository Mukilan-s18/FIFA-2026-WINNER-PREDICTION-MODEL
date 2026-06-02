#!/usr/bin/env python3
"""
FIFA 2026 World Cup Winner Prediction Pipeline — End-to-End Runner.

Usage:
    python scripts/run_pipeline.py

Executes the full pipeline:
    1. Download data
    2. Clean data
    3. Compute Elo ratings + engineer features
    4. Train models
    5. Evaluate models
    6. Simulate tournament
    7. Generate predictions
"""
import sys
import os
import time
import warnings
warnings.filterwarnings("ignore")

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pandas as pd

from src.config import (
    ALL_QUALIFIED_TEAMS,
    WC_2026_TEAMS,
    RANDOM_SEED,
    N_SIMULATIONS,
    PROCESSED_DIR,
    FIGURES_DIR,
    REPORTS_DIR,
)
from src.data.collect import download_all
from src.data.clean import clean_all
from src.data.features import (
    EloRatingSystem,
    build_match_features,
    get_team_snapshot,
    build_matchup_features,
)
from src.models.train import (
    prepare_training_data,
    train_all_models,
    EnsemblePredictor,
    StackingEnsemblePredictor,
    FEATURE_COLUMNS,
)
from src.models.evaluate import (
    evaluate_all_models,
    plot_confusion_matrix,
    plot_calibration,
    plot_feature_importance,
    generate_evaluation_report,
)
from src.models.simulate import TournamentSimulator


def main():
    start_time = time.time()

    print("\n" + "█" * 60)
    print("█  FIFA 2026 WORLD CUP WINNER PREDICTION PIPELINE")
    print("█  " + "─" * 54)
    print("█  48 teams • 12 groups • Monte Carlo simulation")
    print("█" * 60 + "\n")

    # ═══════════════════════════════════════════════════════════════
    # STEP 1: Download Data
    # ═══════════════════════════════════════════════════════════════
    print("\n🔽 STEP 1: Downloading datasets...\n")
    raw_data = download_all()
    from src.data.collect_squads import download_squad_values
    raw_data["squad_values"] = download_squad_values()

    # ═══════════════════════════════════════════════════════════════
    # STEP 2: Generate Elo-based Rankings
    # ═══════════════════════════════════════════════════════════════
    print("\n📊 STEP 2: Generating Elo-based rankings...\n")
    from src.data.collect import generate_elo_rankings
    raw_data["rankings"] = generate_elo_rankings(raw_data["results"])

    # ═══════════════════════════════════════════════════════════════
    # STEP 3: Clean Data
    # ═══════════════════════════════════════════════════════════════
    print("\n🧹 STEP 3: Cleaning data...\n")
    cleaned = clean_all(raw_data)

    # ═══════════════════════════════════════════════════════════════
    # STEP 4: Compute Elo Ratings
    # ═══════════════════════════════════════════════════════════════
    print("\n📊 STEP 4: Computing Elo ratings...\n")
    elo = EloRatingSystem()
    matches_with_elo = elo.process_matches(cleaned["matches"])
    print(f"  ✓ Elo ratings computed for {len(elo.ratings)} teams")

    # Show Elo for qualified teams
    current_elo = elo.get_current_ratings()
    qualified_elo = current_elo[current_elo["team"].isin(ALL_QUALIFIED_TEAMS)]
    print(f"\n  Top 10 qualified teams by Elo:")
    for idx, row in qualified_elo.head(10).iterrows():
        print(f"    {idx+1:2d}. {row['team']:<25s} Elo: {row['elo']:.0f}")

    # ═══════════════════════════════════════════════════════════════
    # STEP 5: Feature Engineering
    # ═══════════════════════════════════════════════════════════════
    print("\n\n🔧 STEP 5: Engineering features...\n")
    feature_df = build_match_features(
        matches_df=matches_with_elo,
        rankings_df=cleaned["rankings"],
        wc_matches=cleaned["wc_history"],
        elo_system=elo,
        squad_values=cleaned.get("squad_values"),
        min_date="2000-01-01",
    )

    # ═══════════════════════════════════════════════════════════════
    # STEP 6: Train Models
    # ═══════════════════════════════════════════════════════════════
    print("\n\n🤖 STEP 6: Training models...\n")
    (
        X_train, y_train,
        X_val, y_val,
        X_test, y_test,
        feature_names,
    ) = prepare_training_data(
        feature_df,
        train_end="2022-11-20",
        val_start="2022-11-20",
        val_end="2024-01-01",
    )

    models = train_all_models(feature_df, X_train, y_train, X_val, y_val, feature_names, tune=True)

    # ═══════════════════════════════════════════════════════════════
    # STEP 7: Evaluate Models
    # ═══════════════════════════════════════════════════════════════
    print("\n\n📈 STEP 7: Evaluating models...\n")
    metrics_df = evaluate_all_models(models, X_val, y_val)

    # Generate plots for best model
    best_model_name = metrics_df["log_loss"].idxmin()
    best_model = models[best_model_name]
    y_val_pred = best_model.predict(X_val)
    y_val_proba = best_model.predict_proba(X_val)

    plot_confusion_matrix(y_val, y_val_pred, model_name=best_model_name)
    plot_calibration(y_val, y_val_proba, model_name=best_model_name)
    plot_feature_importance(best_model, feature_names, model_name=best_model_name)
    generate_evaluation_report(metrics_df)

    # Test set evaluation
    print("\n  Test set evaluation (2024+ matches):")
    if len(X_test) > 0:
        evaluate_all_models(models, X_test, y_test)

    # ═══════════════════════════════════════════════════════════════
    # STEP 8: Build Stacking Ensemble
    # ═══════════════════════════════════════════════════════════════
    print("\n\n🎯 STEP 8: Building stacking ensemble...\n")

    ensemble = StackingEnsemblePredictor(models)
    ensemble.fit(X_val, y_val)

    # Evaluate ensemble on test set
    if len(X_test) > 0:
        ens_proba = ensemble.predict_proba(X_test)
        ens_pred = ensemble.predict(X_test)
        from src.models.evaluate import compute_metrics, compare_to_betting_odds
        ens_metrics = compute_metrics(y_test, ens_proba, ens_pred, model_name="Stacking Ensemble (Test Set)")
        
        # Benchmark against betting odds
        compare_to_betting_odds(y_test, ens_proba, model_name="Stacking Ensemble")
    else:
        ens_proba = ensemble.predict_proba(X_val)
        ens_pred = ensemble.predict(X_val)
        from src.models.evaluate import compute_metrics, compare_to_betting_odds
        ens_metrics = compute_metrics(y_val, ens_proba, ens_pred, model_name="Stacking Ensemble (Val Set)")
        compare_to_betting_odds(y_val, ens_proba, model_name="Stacking Ensemble")

    # ═══════════════════════════════════════════════════════════════
    # STEP 9: Simulate Tournament
    # ═══════════════════════════════════════════════════════════════
    print("\n\n🏆 STEP 9: Simulating FIFA 2026 World Cup...\n")

    # Build team snapshots
    as_of = pd.Timestamp("2026-06-01")
    team_snapshots = {}
    for team in ALL_QUALIFIED_TEAMS:
        team_snapshots[team] = get_team_snapshot(
            team=team,
            matches_df=matches_with_elo,
            rankings_df=cleaned["rankings"],
            wc_matches=cleaned["wc_history"],
            elo_system=elo,
            squad_values=cleaned.get("squad_values"),
            as_of_date=as_of,
        )

    # Determine available feature columns for simulation
    # (intersection of FEATURE_COLUMNS and what build_matchup_features produces)
    sample_features = build_matchup_features(
        team_snapshots[ALL_QUALIFIED_TEAMS[0]],
        team_snapshots[ALL_QUALIFIED_TEAMS[1]],
        neutral=True,
    )
    sim_feature_cols = [c for c in feature_names if c in sample_features]
    print(f"  Using {len(sim_feature_cols)} features for simulation")

    # Run simulation
    simulator = TournamentSimulator(
        predict_fn=ensemble.predict_proba,
        team_snapshots=team_snapshots,
        feature_builder_fn=build_matchup_features,
        feature_columns=sim_feature_cols,
        groups=WC_2026_TEAMS,
        n_simulations=N_SIMULATIONS,
        random_seed=RANDOM_SEED,
    )

    predictions = simulator.run_simulations()
    simulator.save_predictions(predictions)

    # ═══════════════════════════════════════════════════════════════
    # DONE
    # ═══════════════════════════════════════════════════════════════
    elapsed = time.time() - start_time
    print(f"\n{'█' * 60}")
    print(f"█  PIPELINE COMPLETE")
    print(f"█  Time elapsed: {elapsed:.1f}s")
    print(f"█  ")
    print(f"█  PREDICTED WINNER: {predictions.iloc[0]['team']}")
    print(f"█  Win probability:  {predictions.iloc[0]['win_prob']*100:.1f}%")
    print(f"█{'─' * 58}█")
    print(f"█  Top 5:")
    for i in range(5):
        row = predictions.iloc[i]
        bar = "█" * int(row["win_prob"] * 100)
        print(f"█   {i+1}. {row['team']:<20s} {row['win_prob']*100:5.1f}% {bar}")
    print(f"{'█' * 60}\n")

    return predictions


if __name__ == "__main__":
    predictions = main()
