import re

with open("src/models/train.py", "r") as f:
    content = f.read()

# LR Builder
content = content.replace(
    'solver="lbfgs",\n            random_state=RANDOM_SEED,',
    'solver="lbfgs",\n            random_state=RANDOM_SEED,\n            class_weight="balanced",'
)

# RF Builder
content = content.replace(
    'n_jobs=-1,\n    )',
    'n_jobs=-1,\n        class_weight="balanced",\n    )'
)

# LGBM Builder
content = content.replace(
    'objective="multiclass",\n        num_class=3,\n        random_state=RANDOM_SEED,',
    'class_weight="balanced",\n        objective="multiclass",\n        num_class=3,\n        random_state=RANDOM_SEED,'
)

# n_trials 15 -> 50
content = content.replace('n_trials: int = 15', 'n_trials: int = 50')

# XGBoost objective bounds
xgb_old = """        n_estimators = trial.suggest_int("n_estimators", 100, 300, step=100)
        max_depth = trial.suggest_int("max_depth", 3, 6)
        learning_rate = trial.suggest_float("learning_rate", 0.01, 0.1, log=True)
        subsample = trial.suggest_float("subsample", 0.7, 1.0)
        colsample_bytree = trial.suggest_float("colsample_bytree", 0.7, 1.0)"""

xgb_new = """        n_estimators = trial.suggest_int("n_estimators", 100, 500, step=100)
        max_depth = trial.suggest_int("max_depth", 3, 9)
        learning_rate = trial.suggest_float("learning_rate", 0.005, 0.2, log=True)
        subsample = trial.suggest_float("subsample", 0.6, 1.0)
        colsample_bytree = trial.suggest_float("colsample_bytree", 0.6, 1.0)
        min_child_weight = trial.suggest_int("min_child_weight", 1, 7)
        gamma = trial.suggest_float("gamma", 0.0, 0.5)"""
content = content.replace(xgb_old, xgb_new)

# XGBoost tuned builder params
xgb_builder_old = """                colsample_bytree=colsample_bytree,
                objective="multi:softprob",
                num_class=3,"""
xgb_builder_new = """                colsample_bytree=colsample_bytree,
                min_child_weight=min_child_weight,
                gamma=gamma,
                objective="multi:softprob",
                num_class=3,"""
content = content.replace(xgb_builder_old, xgb_builder_new)

# XGBoost tuned instantiator params in train_all_models
xgb_tune_old = """                colsample_bytree=best_params["colsample_bytree"],
                objective="multi:softprob","""
xgb_tune_new = """                colsample_bytree=best_params["colsample_bytree"],
                min_child_weight=best_params.get("min_child_weight", 5),
                gamma=best_params.get("gamma", 0.0),
                objective="multi:softprob","""
content = content.replace(xgb_tune_old, xgb_tune_new)

with open("src/models/train.py", "w") as f:
    f.write(content)
print("Patched successfully")
