"""
Model training for FIFA 2026 WC Prediction Pipeline.

Trains multiple classifiers to predict match outcomes (Home Win / Draw / Away Win)
from the engineered feature matrix.
"""
import pandas as pd
import numpy as np
import pickle
import warnings
from pathlib import Path
from typing import Optional

from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import log_loss

import optuna
from scipy.optimize import minimize

from src.config import RANDOM_SEED, MODELS_DIR

# Set optuna logging to warning to keep outputs clean
optuna.logging.set_verbosity(optuna.logging.WARNING)

# Leave-One-Tournament-Out (LOTO) World Cup details
LOTO_TOURNAMENTS = {
    "2014": {
        "start": "2014-06-12",
        "end": "2014-07-14",
    },
    "2018": {
        "start": "2018-06-14",
        "end": "2018-07-16",
    },
    "2022": {
        "start": "2022-11-20",
        "end": "2022-12-19",
    },
}

# Optional imports — XGBoost/LightGBM need native libs (libomp on macOS)
try:
    import xgboost as xgb
    HAS_XGBOOST = True
except (ImportError, Exception) as e:
    HAS_XGBOOST = False
    print(f"  ⚠ XGBoost not available ({e}). Using sklearn GradientBoosting fallback.")

try:
    import lightgbm as lgb
    HAS_LIGHTGBM = True
except (ImportError, Exception) as e:
    HAS_LIGHTGBM = False
    print(f"  ⚠ LightGBM not available ({e}). Skipping.")


# ════════════════════════════════════════════════════════════════════════
# Feature columns used by all models
# ════════════════════════════════════════════════════════════════════════

FEATURE_COLUMNS = [
    # Elo
    "home_elo", "away_elo", "elo_diff",
    # FIFA Ranking
    "home_fifa_rank", "away_fifa_rank", "rank_diff",
    "home_fifa_points", "away_fifa_points", "points_diff",
    "home_fifa_rank_delta_6m", "away_fifa_rank_delta_6m",
    "home_fifa_rank_delta_12m", "away_fifa_rank_delta_12m",
    # Form (window=10)
    "home_form_10_win_rate", "away_form_10_win_rate", "form_10_win_rate_diff",
    "home_form_10_goal_diff", "away_form_10_goal_diff", "form_10_goal_diff_diff",
    "home_form_10_goals_scored", "away_form_10_goals_scored",
    "home_form_10_goals_conceded", "away_form_10_goals_conceded",
    # Form (window=30)
    "home_form_30_win_rate", "away_form_30_win_rate", "form_30_win_rate_diff",
    "home_form_30_goal_diff", "away_form_30_goal_diff", "form_30_goal_diff_diff",
    # Head to head
    "h2h_win_rate", "h2h_matches", "h2h_goal_diff",
    # World Cup history
    "home_wc_appearances", "away_wc_appearances", "wc_appearances_diff",
    "home_wc_win_rate", "away_wc_win_rate",
    "home_wc_best_finish", "away_wc_best_finish", "wc_best_finish_diff",
    # Squad Values & Ratings
    "home_squad_value_m", "away_squad_value_m", "squad_value_diff", "squad_value_ratio",
    "home_fifa_rating", "away_fifa_rating", "fifa_rating_diff",
    "home_stars", "away_stars", "stars_diff",
    # Proxy Stats
    "xg_form_diff",
    # Context & Travel
    "neutral", "home_travel_penalty", "away_travel_penalty", "travel_penalty_diff",
]


def prepare_training_data(
    feature_df: pd.DataFrame,
    train_end: str = "2022-11-20",
    val_start: str = "2022-11-20",
    val_end: str = "2023-01-01",
) -> tuple:
    """Split feature matrix into train/validation sets.

    Uses time-based split to prevent data leakage.
    
    Target encoding:
        -1 → Away win (class 0)
         0 → Draw     (class 1)
         1 → Home win (class 2)
    """
    df = feature_df.copy()
    df["date"] = pd.to_datetime(df["date"])

    # Remap target: -1,0,1 → 0,1,2
    df["target"] = df["result"].map({-1: 0, 0: 1, 1: 2})

    # Available feature columns (intersect with what we have)
    available_features = [c for c in FEATURE_COLUMNS if c in df.columns]
    print(f"  Using {len(available_features)} features out of {len(FEATURE_COLUMNS)} defined")

    # Handle boolean → int
    if "neutral" in df.columns:
        df["neutral"] = df["neutral"].astype(int)

    # Split
    train = df[df["date"] < train_end]
    val = df[(df["date"] >= val_start) & (df["date"] < val_end)]
    test = df[df["date"] >= val_end]

    X_train = train[available_features].fillna(0).values
    y_train = train["target"].values
    X_val = val[available_features].fillna(0).values
    y_val = val["target"].values
    X_test = test[available_features].fillna(0).values
    y_test = test["target"].values

    print(f"  Train: {len(X_train):,} matches (up to {train_end})")
    print(f"  Val:   {len(X_val):,} matches ({val_start} to {val_end})")
    print(f"  Test:  {len(X_test):,} matches ({val_end}+)")

    return (
        X_train, y_train,
        X_val, y_val,
        X_test, y_test,
        available_features,
    )


# ════════════════════════════════════════════════════════════════════════
# Model Definitions
# ════════════════════════════════════════════════════════════════════════

def build_logistic_regression() -> Pipeline:
    """Regularized logistic regression with feature scaling."""
    return Pipeline([
        ("scaler", StandardScaler()),
        ("clf", LogisticRegression(
            C=1.0,
            max_iter=1000,
            multi_class="multinomial",
            solver="lbfgs",
            random_state=RANDOM_SEED,
        )),
    ])


def build_random_forest() -> RandomForestClassifier:
    """Random forest classifier."""
    return RandomForestClassifier(
        n_estimators=500,
        max_depth=8,
        min_samples_split=10,
        min_samples_leaf=5,
        random_state=RANDOM_SEED,
        n_jobs=-1,
    )


def build_xgboost():
    """XGBoost classifier tuned for match prediction."""
    if not HAS_XGBOOST:
        # Fallback: sklearn GradientBoosting
        print("  (Using sklearn GradientBoosting as XGBoost fallback)")
        return GradientBoostingClassifier(
            n_estimators=300,
            max_depth=5,
            learning_rate=0.05,
            subsample=0.8,
            min_samples_leaf=10,
            random_state=RANDOM_SEED,
        )
    return xgb.XGBClassifier(
        n_estimators=500,
        max_depth=6,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        min_child_weight=5,
        reg_alpha=0.1,
        reg_lambda=1.0,
        objective="multi:softprob",
        num_class=3,
        eval_metric="mlogloss",
        random_state=RANDOM_SEED,
        use_label_encoder=False,
        verbosity=0,
    )


def build_lightgbm():
    """LightGBM classifier."""
    if not HAS_LIGHTGBM:
        return None
    return lgb.LGBMClassifier(
        n_estimators=500,
        max_depth=6,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        min_child_samples=10,
        reg_alpha=0.1,
        reg_lambda=1.0,
        objective="multiclass",
        num_class=3,
        random_state=RANDOM_SEED,
        verbose=-1,
    )


# ════════════════════════════════════════════════════════════════════════
# Training Pipeline
# ════════════════════════════════════════════════════════════════════════

def run_loto_cv(
    model_builder_fn,
    df: pd.DataFrame,
    feature_names: list[str],
    tournaments: list[str] = ["2014", "2018", "2022"],
) -> float:
    """Run Leave-One-Tournament-Out (LOTO) cross-validation for a model builder.
    
    Returns the average log loss across all folds.
    """
    losses = []
    
    # Ensure date is datetime
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"])
    df["target"] = df["result"].map({-1: 0, 0: 1, 1: 2})
    
    # Handle boolean → int
    if "neutral" in df.columns:
        df["neutral"] = df["neutral"].astype(int)
        
    for year in tournaments:
        info = LOTO_TOURNAMENTS[year]
        start_date = pd.Timestamp(info["start"])
        end_date = pd.Timestamp(info["end"])
        
        # Train on all matches BEFORE the tournament
        train_df = df[df["date"] < start_date]
        
        # Validate ONLY on the World Cup matches of that year
        val_df = df[(df["date"] >= start_date) & (df["date"] <= end_date) & (df["is_world_cup"] == True)]
        
        if len(val_df) == 0:
            continue
            
        X_train = train_df[feature_names].fillna(0).values
        y_train = train_df["target"].values
        X_val = val_df[feature_names].fillna(0).values
        y_val = val_df["target"].values
        
        # Fit model
        model = model_builder_fn()
        model.fit(X_train, y_train)
        
        # Predict probs
        probs = model.predict_proba(X_val)
        loss = log_loss(y_val, probs, labels=[0, 1, 2])
        losses.append(loss)
        
    return np.mean(losses) if losses else 999.0


def tune_logistic_regression(df: pd.DataFrame, feature_names: list[str], n_trials: int = 15) -> dict:
    """Tune Logistic Regression C hyperparameter using Optuna."""
    def objective(trial):
        c = trial.suggest_float("C", 1e-4, 1e2, log=True)
        
        def builder():
            return Pipeline([
                ("scaler", StandardScaler()),
                ("clf", LogisticRegression(
                    C=c,
                    penalty="l2",
                    max_iter=1000,
                    multi_class="multinomial",
                    solver="lbfgs",
                    random_state=RANDOM_SEED,
                )),
            ])
            
        return run_loto_cv(builder, df, feature_names)
        
    study = optuna.create_study(direction="minimize")
    study.optimize(objective, n_trials=n_trials)
    return study.best_params


def tune_random_forest(df: pd.DataFrame, feature_names: list[str], n_trials: int = 15) -> dict:
    """Tune Random Forest hyperparameters using Optuna."""
    def objective(trial):
        n_estimators = trial.suggest_int("n_estimators", 100, 300, step=100)
        max_depth = trial.suggest_int("max_depth", 4, 10)
        min_samples_split = trial.suggest_int("min_samples_split", 5, 20)
        min_samples_leaf = trial.suggest_int("min_samples_leaf", 2, 10)
        
        def builder():
            return RandomForestClassifier(
                n_estimators=n_estimators,
                max_depth=max_depth,
                min_samples_split=min_samples_split,
                min_samples_leaf=min_samples_leaf,
                random_state=RANDOM_SEED,
                n_jobs=-1,
            )
            
        return run_loto_cv(builder, df, feature_names)
        
    study = optuna.create_study(direction="minimize")
    study.optimize(objective, n_trials=n_trials)
    return study.best_params


def tune_xgboost(df: pd.DataFrame, feature_names: list[str], n_trials: int = 15) -> dict:
    """Tune XGBoost hyperparameters using Optuna."""
    def objective(trial):
        n_estimators = trial.suggest_int("n_estimators", 100, 300, step=100)
        max_depth = trial.suggest_int("max_depth", 3, 6)
        learning_rate = trial.suggest_float("learning_rate", 0.01, 0.1, log=True)
        subsample = trial.suggest_float("subsample", 0.7, 1.0)
        colsample_bytree = trial.suggest_float("colsample_bytree", 0.7, 1.0)
        
        def builder():
            if not HAS_XGBOOST:
                return GradientBoostingClassifier(
                    n_estimators=n_estimators,
                    max_depth=max_depth,
                    learning_rate=learning_rate,
                    subsample=subsample,
                    random_state=RANDOM_SEED,
                )
            return xgb.XGBClassifier(
                n_estimators=n_estimators,
                max_depth=max_depth,
                learning_rate=learning_rate,
                subsample=subsample,
                colsample_bytree=colsample_bytree,
                objective="multi:softprob",
                num_class=3,
                eval_metric="mlogloss",
                random_state=RANDOM_SEED,
                use_label_encoder=False,
                verbosity=0,
            )
            
        return run_loto_cv(builder, df, feature_names)
        
    study = optuna.create_study(direction="minimize")
    study.optimize(objective, n_trials=n_trials)
    return study.best_params


def tune_lightgbm(df: pd.DataFrame, feature_names: list[str], n_trials: int = 15) -> dict:
    """Tune LightGBM hyperparameters using Optuna."""
    if not HAS_LIGHTGBM:
        return {}
        
    def objective(trial):
        n_estimators = trial.suggest_int("n_estimators", 100, 300, step=100)
        max_depth = trial.suggest_int("max_depth", 3, 6)
        learning_rate = trial.suggest_float("learning_rate", 0.01, 0.1, log=True)
        subsample = trial.suggest_float("subsample", 0.7, 1.0)
        colsample_bytree = trial.suggest_float("colsample_bytree", 0.7, 1.0)
        
        def builder():
            return lgb.LGBMClassifier(
                n_estimators=n_estimators,
                max_depth=max_depth,
                learning_rate=learning_rate,
                subsample=subsample,
                colsample_bytree=colsample_bytree,
                objective="multiclass",
                num_class=3,
                random_state=RANDOM_SEED,
                verbose=-1,
            )
            
        return run_loto_cv(builder, df, feature_names)
        
    study = optuna.create_study(direction="minimize")
    study.optimize(objective, n_trials=n_trials)
    return study.best_params


def optimize_ensemble_weights(
    models: dict,
    X_val: np.ndarray,
    y_val: np.ndarray,
) -> dict:
    """Find weights that minimize log loss of ensemble on validation data."""
    model_names = list(models.keys())
    n_models = len(model_names)
    
    # Get predictions for all models
    preds = []
    for name in model_names:
        preds.append(models[name].predict_proba(X_val))
    preds = np.array(preds) # shape: (n_models, n_samples, 3)
    
    # Define objective function
    def objective(weights):
        # Normalize weights to sum to 1
        w = np.abs(weights)
        if w.sum() == 0:
            return 999.0
        w = w / w.sum()
        
        # Weighted average probabilities
        ensemble_probs = np.tensordot(w, preds, axes=(0, 0)) # shape: (n_samples, 3)
        
        # Compute log loss
        return log_loss(y_val, ensemble_probs, labels=[0, 1, 2])
        
    # Initial guess: equal weights
    init_weights = np.ones(n_models) / n_models
    
    # Bounds: all weights >= 0
    bounds = [(0, 1) for _ in range(n_models)]
    
    # Run optimization
    res = minimize(
        objective,
        init_weights,
        method="Nelder-Mead",
        bounds=bounds,
        options={"maxiter": 200},
    )
    
    # Normalize final weights
    best_weights = np.abs(res.x)
    if best_weights.sum() > 0:
        best_weights = best_weights / best_weights.sum()
    else:
        best_weights = init_weights
        
    return {model_names[i]: best_weights[i] for i in range(n_models)}


def train_all_models(
    feature_df: pd.DataFrame,
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_val: np.ndarray,
    y_val: np.ndarray,
    feature_names: list[str],
    tune: bool = True,
) -> dict:
    """Train tuned and calibrated models, returning a dictionary of fitted models."""
    models = {}
    model_num = 0
    total_models = 2 + 1 + (1 if HAS_LIGHTGBM else 0)  # LR + RF + XGB + LGBM (if HAS)

    print("\n" + "=" * 60)
    print("  Model Training & Tuning (Phase 2)")
    print("=" * 60)

    # 1. Logistic Regression
    model_num += 1
    print(f"\n[{model_num}/{total_models}] Tuning & Training Logistic Regression...")
    if tune:
        best_params = tune_logistic_regression(feature_df, feature_names)
        print(f"  Best params: {best_params}")
        base_model = Pipeline([
            ("scaler", StandardScaler()),
            ("clf", LogisticRegression(
                C=best_params["C"],
                penalty="l2",
                max_iter=1000,
                multi_class="multinomial",
                solver="lbfgs",
                random_state=RANDOM_SEED,
            )),
        ])
    else:
        base_model = build_logistic_regression()
    
    # Wrap in CalibratedClassifierCV
    calibrated_model = CalibratedClassifierCV(estimator=base_model, method="sigmoid", cv=3)
    calibrated_model.fit(X_train, y_train)
    models["logistic_regression"] = calibrated_model
    print(f"  ✓ Calibrated Train acc: {calibrated_model.score(X_train, y_train):.4f}")
    print(f"  ✓ Calibrated Val acc:   {calibrated_model.score(X_val, y_val):.4f}")

    # 2. Random Forest
    model_num += 1
    print(f"\n[{model_num}/{total_models}] Tuning & Training Random Forest...")
    if tune:
        best_params = tune_random_forest(feature_df, feature_names)
        print(f"  Best params: {best_params}")
        base_model = RandomForestClassifier(
            n_estimators=best_params["n_estimators"],
            max_depth=best_params["max_depth"],
            min_samples_split=best_params["min_samples_split"],
            min_samples_leaf=best_params["min_samples_leaf"],
            random_state=RANDOM_SEED,
            n_jobs=-1,
        )
    else:
        base_model = build_random_forest()
        
    calibrated_model = CalibratedClassifierCV(estimator=base_model, method="sigmoid", cv=3)
    calibrated_model.fit(X_train, y_train)
    models["random_forest"] = calibrated_model
    print(f"  ✓ Calibrated Train acc: {calibrated_model.score(X_train, y_train):.4f}")
    print(f"  ✓ Calibrated Val acc:   {calibrated_model.score(X_val, y_val):.4f}")

    # 3. XGBoost (or GradientBoosting fallback)
    model_num += 1
    label = "XGBoost" if HAS_XGBOOST else "GradientBoosting (XGBoost fallback)"
    print(f"\n[{model_num}/{total_models}] Tuning & Training {label}...")
    if tune:
        best_params = tune_xgboost(feature_df, feature_names)
        print(f"  Best params: {best_params}")
        if HAS_XGBOOST:
            base_model = xgb.XGBClassifier(
                n_estimators=best_params["n_estimators"],
                max_depth=best_params["max_depth"],
                learning_rate=best_params["learning_rate"],
                subsample=best_params["subsample"],
                colsample_bytree=best_params["colsample_bytree"],
                objective="multi:softprob",
                num_class=3,
                eval_metric="mlogloss",
                random_state=RANDOM_SEED,
                use_label_encoder=False,
                verbosity=0,
            )
        else:
            base_model = GradientBoostingClassifier(
                n_estimators=best_params["n_estimators"],
                max_depth=best_params["max_depth"],
                learning_rate=best_params["learning_rate"],
                subsample=best_params["subsample"],
                random_state=RANDOM_SEED,
            )
    else:
        base_model = build_xgboost()
        
    calibrated_model = CalibratedClassifierCV(estimator=base_model, method="sigmoid", cv=3)
    calibrated_model.fit(X_train, y_train)
    models["xgboost"] = calibrated_model
    print(f"  ✓ Calibrated Train acc: {calibrated_model.score(X_train, y_train):.4f}")
    print(f"  ✓ Calibrated Val acc:   {calibrated_model.score(X_val, y_val):.4f}")

    # 4. LightGBM (optional)
    if HAS_LIGHTGBM:
        model_num += 1
        print(f"\n[{model_num}/{total_models}] Tuning & Training LightGBM...")
        if tune:
            best_params = tune_lightgbm(feature_df, feature_names)
            print(f"  Best params: {best_params}")
            base_model = lgb.LGBMClassifier(
                n_estimators=best_params["n_estimators"],
                max_depth=best_params["max_depth"],
                learning_rate=best_params["learning_rate"],
                subsample=best_params["subsample"],
                colsample_bytree=best_params["colsample_bytree"],
                objective="multiclass",
                num_class=3,
                random_state=RANDOM_SEED,
                verbose=-1,
            )
        else:
            base_model = build_lightgbm()
            
        calibrated_model = CalibratedClassifierCV(estimator=base_model, method="sigmoid", cv=3)
        calibrated_model.fit(X_train, y_train)
        models["lightgbm"] = calibrated_model
        print(f"  ✓ Calibrated Train acc: {calibrated_model.score(X_train, y_train):.4f}")
        print(f"  ✓ Calibrated Val acc:   {calibrated_model.score(X_val, y_val):.4f}")
    else:
        print("\n  ⚠ Skipping LightGBM (not available)")

    # Save models
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    for name, model in models.items():
        path = MODELS_DIR / f"{name}.pkl"
        with open(path, "wb") as f:
            pickle.dump(model, f)
        print(f"  💾 Saved tuned calibrated {name} → {path}")

    return models


class EnsemblePredictor:
    """Weighted ensemble of multiple classifiers.

    Predicts P(Away Win), P(Draw), P(Home Win) for a match.
    Classes: 0=Away Win, 1=Draw, 2=Home Win
    """

    def __init__(
        self,
        models: dict,
        weights: Optional[dict] = None,
    ):
        self.models = models
        if weights is None:
            # Default: equal weights
            n = len(models)
            self.weights = {name: 1.0 / n for name in models}
        else:
            self.weights = weights

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Weighted average of model probability predictions.

        Returns array of shape (n_samples, 3):
            col 0 = P(Away Win)
            col 1 = P(Draw)
            col 2 = P(Home Win)
        """
        weighted_probs = np.zeros((X.shape[0], 3))
        total_weight = sum(self.weights.values())

        for name, model in self.models.items():
            w = self.weights.get(name, 0) / total_weight
            probs = model.predict_proba(X)
            weighted_probs += w * probs

        return weighted_probs

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Return predicted class (argmax of probabilities)."""
        probs = self.predict_proba(X)
        return np.argmax(probs, axis=1)

class StackingEnsemblePredictor:
    """Meta-learner that stacks predictions of base models."""
    def __init__(self, models: dict):
        self.models = models
        self.meta_learner = LogisticRegression(multi_class="multinomial", solver="lbfgs", C=1.0)
        self.is_fitted = False
        
    def _get_meta_features(self, X: np.ndarray) -> np.ndarray:
        # Concatenate probability outputs of all base models
        preds = []
        for name, model in self.models.items():
            preds.append(model.predict_proba(X))
        return np.hstack(preds)
        
    def fit(self, X_val: np.ndarray, y_val: np.ndarray):
        meta_X = self._get_meta_features(X_val)
        self.meta_learner.fit(meta_X, y_val)
        self.is_fitted = True
        return self
        
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        if not self.is_fitted:
            raise ValueError("Stacking ensemble not fitted.")
        meta_X = self._get_meta_features(X)
        return self.meta_learner.predict_proba(meta_X)
        
    def predict(self, X: np.ndarray) -> np.ndarray:
        probs = self.predict_proba(X)
        return np.argmax(probs, axis=1)
