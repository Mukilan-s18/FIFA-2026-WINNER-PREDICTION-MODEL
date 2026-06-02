# 🏆 FIFA 2026 World Cup Winner Prediction Model

A machine learning pipeline that predicts the winner of the 2026 FIFA World Cup using historical match data, Elo ratings, FIFA rankings, and Monte Carlo tournament simulation.

## Architecture

```
Historical Data → Feature Engineering → ML Models → Ensemble → Monte Carlo Simulation
                                                                        ↓
                                                            Win Probabilities (48 teams)
```

### Match-Level Prediction
- **Models**: Logistic Regression, Random Forest, XGBoost, LightGBM
- **Target**: P(Home Win), P(Draw), P(Away Win) for each match
- **Features**: Elo ratings, FIFA rankings, recent form, head-to-head, World Cup history

### Tournament Simulation
- **Method**: Monte Carlo simulation (10,000 iterations)
- **Format**: 48 teams, 12 groups of 4, knockout rounds
- **Output**: Win probability for each team

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the full pipeline
python scripts/run_pipeline.py
```

## Project Structure

```
├── data/               # Raw, interim, and processed datasets
├── src/
│   ├── config.py       # Configuration and constants
│   ├── data/
│   │   ├── collect.py  # Data download scripts
│   │   ├── clean.py    # Data cleaning
│   │   └── features.py # Feature engineering + Elo system
│   └── models/
│       ├── train.py    # Model training + ensemble
│       ├── evaluate.py # Metrics, plots, reports
│       └── simulate.py # Monte Carlo tournament simulator
├── models/             # Saved trained models
├── reports/            # Evaluation reports + predictions
├── scripts/
│   └── run_pipeline.py # End-to-end pipeline runner
└── requirements.txt
```

## Features Used

| Feature Domain | Examples |
|---|---|
| Elo Ratings | Current Elo, Elo difference |
| FIFA Rankings | Rank, points, 6/12-month trajectory |
| Recent Form | Win rate, goals scored/conceded (10/30-game windows) |
| Head-to-Head | Historical record between opponents |
| World Cup History | Appearances, best finish, WC win rate |

## Evaluation

- **Primary metric**: Log Loss
- **Cross-validation**: Time-series split + Leave-One-Tournament-Out
- **Backtest**: 2022 World Cup predictions using only pre-2022 data

## License

MIT
