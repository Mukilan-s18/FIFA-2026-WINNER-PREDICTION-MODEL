<div align="center">
  <img src="banner.png" alt="FIFA 2026 Prediction Model Banner" width="100%" />

  <h1>🏆 FIFA 2026 World Cup Predictor & Simulator</h1>
  
  <p><strong>A state-of-the-art Machine Learning pipeline and stunning interactive web application predicting the winner of the 2026 FIFA World Cup.</strong></p>

  <p>
    <a href="https://fifa-wc-26-predictor-mukil.web.app" target="_blank">
      <img src="https://img.shields.io/badge/Live_Demo-fifa--wc--26--predictor--mukil.web.app-2ea44f?style=for-the-badge&logo=firebase" alt="Live Demo" />
    </a>
  </p>

  <p>
    <img src="https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python" />
    <img src="https://img.shields.io/badge/scikit--learn-%23F7931E.svg?style=flat-square&logo=scikit-learn&logoColor=white" alt="scikit-learn" />
    <img src="https://img.shields.io/badge/React-20232A?style=flat-square&logo=react&logoColor=61DAFB" alt="React" />
    <img src="https://img.shields.io/badge/Vite-B73BFE?style=flat-square&logo=vite&logoColor=FFD62E" alt="Vite" />
    <img src="https://img.shields.io/badge/Firebase-ffca28?style=flat-square&logo=firebase&logoColor=black" alt="Firebase" />
  </p>
</div>

---

## ✨ Overview

This project bridges the gap between **Advanced Data Science** and **Premium UI Design**. It leverages historical international football match data dating back decades, Elo ratings, and FIFA rankings to train an ensemble of Machine Learning models (Logistic Regression, Random Forest, XGBoost). These models power a massive Monte Carlo simulation engine that plays out the 2026 World Cup 10,000 times to calculate exact win probabilities.

The result is visualized in a breathtaking, cinematic web application featuring a stunning Glassmorphism design system, smooth cross-fading animations, and interactive data representations.

### 🌟 Key Features

*   🧠 **Ensemble ML Engine**: Predictive models trained on thousands of historical matches.
*   🎲 **Monte Carlo Simulations**: Runs 10,000 parallel tournament brackets based on the new 48-team format.
*   💎 **Cinematic Web Application**: A beautiful React frontend using Glassmorphism, smooth animations, and high-fidelity player cutouts.
*   📊 **Deep Feature Engineering**: Analyzes Elo differences, team momentum, recent form, and World Cup historical pedigree.
*   ⚡ **Lightning Fast**: Powered by Vite and globally distributed via Firebase Hosting.

---

## 🏗️ Architecture & Pipeline

```mermaid
graph LR
  A[Historical Match Data] --> B(Feature Engineering);
  A2[FIFA Rankings / Elo] --> B;
  B --> C{ML Ensemble Model};
  C -->|P(Win), P(Draw), P(Loss)| D[Monte Carlo Simulator];
  D -->|10,000 Iterations| E((Win Probabilities));
  E --> F[React Web Dashboard];
```

## 🚀 Quick Start (Machine Learning Pipeline)

Want to train the models and run your own simulations? It's fully open-sourced.

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/fifa-2026-predictor.git
cd fifa-2026-predictor

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Run the end-to-end data processing and training pipeline
python scripts/run_pipeline.py
```

## 💻 Running the Web App Locally

Want to mess around with the beautiful React frontend?

```bash
# Navigate to the web_app directory
cd web_app

# Install Node dependencies
npm install

# Start the Vite development server
npm run dev
```

---

## 📈 Model Evaluation

The model uses a rigorous Leave-One-Tournament-Out cross-validation strategy, avoiding data leakage from the future to predict the past.

- **Primary metric**: Log Loss
- **Backtesting**: We simulated the 2022 World Cup using only data up until the day before the 2022 opening match. The model heavily favored Argentina and France to reach the final, aligning perfectly with reality.

## 🤝 Contributing

Contributions, issues and feature requests are welcome! Feel free to check the [issues page](https://github.com/yourusername/fifa-2026-predictor/issues). If you like this project, please consider giving it a ⭐️ to help it reach more people!

## 📜 License

This project is [MIT](https://choosealicense.com/licenses/mit/) licensed.
