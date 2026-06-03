# FIFA 2026 WC Prediction — Model Evaluation Report

Generated: 2026-06-03 12:45

## Model Comparison

| model               |   accuracy |   log_loss |   brier_score_avg |      rps |
|:--------------------|-----------:|-----------:|------------------:|---------:|
| xgboost             |   0.614987 |   0.871698 |          0.169302 | 0.115255 |
| lightgbm            |   0.61671  |   0.873361 |          0.169679 | 0.115674 |
| random_forest       |   0.607235 |   0.87515  |          0.170064 | 0.116014 |
| logistic_regression |   0.611542 |   0.879313 |          0.171349 | 0.116579 |

**Best model by log loss**: xgboost (log_loss = 0.8717)

## Metrics Explained

| Metric | Description | Ideal |
|--------|-------------|-------|
| Accuracy | % of correct predictions | Higher = better |
| Log Loss | Cross-entropy of probability predictions | Lower = better |
| Brier Score | Mean squared error of probabilities | Lower = better |
| RPS | Ranked Probability Score | Lower = better |
