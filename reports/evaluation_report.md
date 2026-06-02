# FIFA 2026 WC Prediction — Model Evaluation Report

Generated: 2026-06-02 12:40

## Model Comparison

| model               |   accuracy |   log_loss |   brier_score_avg |      rps |
|:--------------------|-----------:|-----------:|------------------:|---------:|
| xgboost             |   0.620155 |   0.872981 |          0.1696   | 0.115465 |
| lightgbm            |   0.617571 |   0.873462 |          0.169692 | 0.115722 |
| random_forest       |   0.608958 |   0.874717 |          0.169939 | 0.115946 |
| logistic_regression |   0.615848 |   0.878674 |          0.17122  | 0.116455 |

**Best model by log loss**: xgboost (log_loss = 0.8730)

## Metrics Explained

| Metric | Description | Ideal |
|--------|-------------|-------|
| Accuracy | % of correct predictions | Higher = better |
| Log Loss | Cross-entropy of probability predictions | Lower = better |
| Brier Score | Mean squared error of probabilities | Lower = better |
| RPS | Ranked Probability Score | Lower = better |
