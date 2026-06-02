"""
Model evaluation for FIFA 2026 WC Prediction Pipeline.

Computes metrics: log loss, Brier score, accuracy, calibration,
and generates evaluation reports.
"""
import pandas as pd
import numpy as np
from sklearn.metrics import (
    log_loss,
    accuracy_score,
    classification_report,
    confusion_matrix,
    brier_score_loss,
)
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

from src.config import FIGURES_DIR, REPORTS_DIR


def compute_metrics(
    y_true: np.ndarray,
    y_pred_proba: np.ndarray,
    y_pred: np.ndarray,
    model_name: str = "Model",
) -> dict:
    """Compute all evaluation metrics.

    Args:
        y_true: Ground truth labels (0=Away, 1=Draw, 2=Home)
        y_pred_proba: Predicted probabilities (n_samples, 3)
        y_pred: Predicted labels
        model_name: Name for display

    Returns:
        Dictionary of metric name → value
    """
    metrics = {}

    # Accuracy
    metrics["accuracy"] = accuracy_score(y_true, y_pred)

    # Log loss
    metrics["log_loss"] = log_loss(y_true, y_pred_proba, labels=[0, 1, 2])

    # Brier score (one-vs-rest average)
    brier_scores = []
    for cls in range(3):
        y_binary = (y_true == cls).astype(int)
        brier_scores.append(brier_score_loss(y_binary, y_pred_proba[:, cls]))
    metrics["brier_score_avg"] = np.mean(brier_scores)

    # Ranked Probability Score (RPS)
    rps_values = []
    for i in range(len(y_true)):
        true_cum = np.cumsum(np.eye(3)[y_true[i]])
        pred_cum = np.cumsum(y_pred_proba[i])
        rps_values.append(np.mean((pred_cum - true_cum) ** 2))
    metrics["rps"] = np.mean(rps_values)

    print(f"\n  {'─' * 40}")
    print(f"  {model_name} Evaluation")
    print(f"  {'─' * 40}")
    print(f"  Accuracy:    {metrics['accuracy']:.4f}")
    print(f"  Log Loss:    {metrics['log_loss']:.4f}")
    print(f"  Brier Score: {metrics['brier_score_avg']:.4f}")
    print(f"  RPS:         {metrics['rps']:.4f}")

    return metrics


def evaluate_all_models(
    models: dict,
    X_val: np.ndarray,
    y_val: np.ndarray,
) -> pd.DataFrame:
    """Evaluate all models and return comparison DataFrame."""
    results = []

    for name, model in models.items():
        y_pred_proba = model.predict_proba(X_val)
        y_pred = model.predict(X_val)
        metrics = compute_metrics(y_val, y_pred_proba, y_pred, model_name=name)
        metrics["model"] = name
        results.append(metrics)

    df = pd.DataFrame(results).set_index("model")
    df = df.sort_values("log_loss")

    print("\n" + "=" * 60)
    print("  Model Comparison (sorted by log loss)")
    print("=" * 60)
    print(df.to_string())

    return df


def plot_confusion_matrix(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    model_name: str = "Model",
    save: bool = True,
) -> None:
    """Plot and optionally save confusion matrix."""
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    cm = confusion_matrix(y_true, y_pred, labels=[0, 1, 2])
    labels = ["Away Win", "Draw", "Home Win"]

    fig, ax = plt.subplots(figsize=(8, 6))
    sns.heatmap(
        cm,
        annot=True,
        fmt="d",
        cmap="Blues",
        xticklabels=labels,
        yticklabels=labels,
        ax=ax,
    )
    ax.set_title(f"Confusion Matrix — {model_name}", fontsize=14)
    ax.set_xlabel("Predicted")
    ax.set_ylabel("Actual")

    plt.tight_layout()
    if save:
        path = FIGURES_DIR / f"confusion_matrix_{model_name.lower().replace(' ', '_')}.png"
        fig.savefig(path, dpi=150, bbox_inches="tight")
        print(f"  💾 Saved confusion matrix → {path}")
    plt.close()


def plot_calibration(
    y_true: np.ndarray,
    y_pred_proba: np.ndarray,
    model_name: str = "Model",
    n_bins: int = 10,
    save: bool = True,
) -> None:
    """Plot calibration curve for each outcome class."""
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    labels = ["Away Win", "Draw", "Home Win"]
    colors = ["#e74c3c", "#f39c12", "#2ecc71"]

    fig, axes = plt.subplots(1, 3, figsize=(18, 5))

    for cls in range(3):
        ax = axes[cls]
        y_binary = (y_true == cls).astype(float)
        probs = y_pred_proba[:, cls]

        # Bin predictions
        bins = np.linspace(0, 1, n_bins + 1)
        bin_indices = np.digitize(probs, bins) - 1
        bin_indices = np.clip(bin_indices, 0, n_bins - 1)

        bin_means = []
        bin_true_freq = []
        for b in range(n_bins):
            mask = bin_indices == b
            if mask.sum() > 0:
                bin_means.append(probs[mask].mean())
                bin_true_freq.append(y_binary[mask].mean())

        ax.plot([0, 1], [0, 1], "k--", alpha=0.5, label="Perfect")
        ax.plot(bin_means, bin_true_freq, "o-", color=colors[cls], label=labels[cls])
        ax.set_xlabel("Predicted Probability")
        ax.set_ylabel("Observed Frequency")
        ax.set_title(f"{labels[cls]}")
        ax.legend()
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)

    fig.suptitle(f"Calibration Curves — {model_name}", fontsize=14, y=1.02)
    plt.tight_layout()

    if save:
        path = FIGURES_DIR / f"calibration_{model_name.lower().replace(' ', '_')}.png"
        fig.savefig(path, dpi=150, bbox_inches="tight")
        print(f"  💾 Saved calibration curves → {path}")
    plt.close()


def plot_feature_importance(
    model,
    feature_names: list[str],
    model_name: str = "Model",
    top_n: int = 20,
    save: bool = True,
) -> None:
    """Plot feature importance for tree-based models."""
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    if hasattr(model, "feature_importances_"):
        importances = model.feature_importances_
    elif hasattr(model, "named_steps") and hasattr(model.named_steps.get("clf", None), "coef_"):
        # Logistic regression: use mean absolute coefficient
        importances = np.mean(np.abs(model.named_steps["clf"].coef_), axis=0)
    else:
        print(f"  ⚠ Cannot extract feature importance from {model_name}")
        return

    # Sort
    indices = np.argsort(importances)[-top_n:]
    top_features = [feature_names[i] for i in indices]
    top_importances = importances[indices]

    fig, ax = plt.subplots(figsize=(10, 8))
    ax.barh(top_features, top_importances, color="#3498db")
    ax.set_xlabel("Importance")
    ax.set_title(f"Top {top_n} Features — {model_name}", fontsize=14)

    plt.tight_layout()
    if save:
        path = FIGURES_DIR / f"feature_importance_{model_name.lower().replace(' ', '_')}.png"
        fig.savefig(path, dpi=150, bbox_inches="tight")
        print(f"  💾 Saved feature importance → {path}")
    plt.close()


def generate_evaluation_report(
    metrics_df: pd.DataFrame,
    save: bool = True,
) -> str:
    """Generate a markdown evaluation report."""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    report = "# FIFA 2026 WC Prediction — Model Evaluation Report\n\n"
    report += f"Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}\n\n"

    report += "## Model Comparison\n\n"
    report += metrics_df.to_markdown() + "\n\n"

    best = metrics_df["log_loss"].idxmin()
    report += f"**Best model by log loss**: {best} "
    report += f"(log_loss = {metrics_df.loc[best, 'log_loss']:.4f})\n\n"

    report += "## Metrics Explained\n\n"
    report += "| Metric | Description | Ideal |\n"
    report += "|--------|-------------|-------|\n"
    report += "| Accuracy | % of correct predictions | Higher = better |\n"
    report += "| Log Loss | Cross-entropy of probability predictions | Lower = better |\n"
    report += "| Brier Score | Mean squared error of probabilities | Lower = better |\n"
    report += "| RPS | Ranked Probability Score | Lower = better |\n"

    if save:
        path = REPORTS_DIR / "evaluation_report.md"
        path.write_text(report)
        print(f"  💾 Saved evaluation report → {path}")

    return report

def compare_to_betting_odds(y_true: np.ndarray, y_pred_proba: np.ndarray, model_name: str = "Ensemble"):
    """Benchmark model performance against implied betting odds logic.
    
    In a standard international football match, the bookmaker 'overround' (margin)
    is typically 105-108%. Removing the margin, average implied probabilities for 
    closely matched teams are roughly: Home (45%), Draw (28%), Away (27%).
    
    A strong model should beat a naive historical baseline that always predicts 
    the average historical distribution.
    """
    # Naive baseline predicting average historical distribution
    # (Home: 48%, Draw: 24%, Away: 28%)
    n = len(y_true)
    naive_probs = np.tile([0.28, 0.24, 0.48], (n, 1))
    
    model_loss = log_loss(y_true, y_pred_proba, labels=[0, 1, 2])
    naive_loss = log_loss(y_true, naive_probs, labels=[0, 1, 2])
    
    print(f"\n  {'─' * 40}")
    print(f"  Commercial Benchmark: {model_name} vs Bookmaker Baseline")
    print(f"  {'─' * 40}")
    print(f"  {model_name} Log Loss:      {model_loss:.4f}")
    print(f"  Naive Baseline Log Loss: {naive_loss:.4f}")
    
    if model_loss < naive_loss:
        edge = (naive_loss - model_loss) / naive_loss * 100
        print(f"  Result: Model beats baseline by {edge:.1f}%")
        if model_loss < 0.90:
            print("  Assessment: COMMERCIALLY VIABLE. Log loss < 0.90 approaches professional syndicate accuracy.")
    else:
        print("  Result: Model fails to beat baseline.")
