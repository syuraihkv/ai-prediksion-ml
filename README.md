# 🤖 AI Prediction ML Trading System

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.0+-red.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Status](https://img.shields.io/badge/Status-Active-success.svg)

**Advanced Machine Learning System for Financial Market Prediction**

Comprehensive trading dashboard with AI-powered predictions, technical analysis, and real-time monitoring

[🚀 Features](#-features) • [📊 Dashboard](#-interactive-dashboard) • [🛠️ Installation](#️-installation) • [📖 Usage](#-usage) • [🎯 Tech Stack](#-tech-stack)

</div>

## 🚀 Features

### 📊 Market Analysis
- **Multi-Instrument Support**: Bitcoin (BTC/USD), Gold (XAU/USD), NASDAQ
- **Multiple Timeframes**: 1H, 4H, Daily analysis
- **Technical Indicators**: RSI, MACD, Moving Averages, ATR, Support/Resistance
- **Volume Analysis**: Volume profile and market depth
- **Multi-Timeframe Analysis**: Trend alignment across timeframes
- **Correlation Analysis**: Asset correlation heatmap for diversification

### 🤖 AI & Prediction
- **Multiple ML Models**: Logistic Regression, Random Forest, XGBoost, LightGBM, CatBoost
- **Advanced Feature Engineering**: 20+ technical indicators
- **Hyperparameter Optimization**: Optuna-based tuning
- **Walk-Forward Validation**: Time-series aware validation
- **Model Comparison**: Compare multiple models side-by-side
- **Probability Calculator**: Expected Value, Kelly Criterion, Monte Carlo Simulation

### 📰 News & Events
- **News Intelligence**: Real-time news sentiment analysis
- **Economic Calendar**: High-impact events with countdown
- **Historical Impact Analysis**: Past event impact on markets
- **Fear/Greed Index**: Market sentiment extremes analysis

### 📈 Performance
- **Historical Accuracy**: Track prediction performance over time
- **Backtesting**: Historical backtesting with real data
- **Performance Metrics**: Sharpe Ratio, Win Rate, Drawdown analysis
- **Equity Curve**: Visual performance tracking

### 🛠️ Tools
- **Personal Notes**: SQLite-based note-taking system
- **Risk Management**: Position sizing and risk analysis
- **Custom Configuration**: Flexible settings and parameters

## 📊 Interactive Dashboard

The system features a modern, glass-morphism styled Streamlit dashboard with:

- **Real-time Price Charts** with technical indicators overlay
- **Volume Analysis** with color-coded volume bars
- **Multi-Timeframe Comparison** charts
- **Correlation Heatmaps** for asset relationships
- **Economic Calendar** with historical impact visualization
- **Fear/Greed Index** with historical trends
- **Monte Carlo Simulation** for probability analysis
- **Backtesting Results** with equity curves

### Dashboard Tabs

1. **Market Analysis** - Technical indicators, volume, multi-timeframe, correlation
2. **News & Events** - News intelligence, economic calendar, fear/greed index
3. **AI & Probability** - AI predictions, model comparison, probability calculator
4. **Performance** - Historical accuracy, backtesting
5. **Tools** - Personal notes

## 🏗️ Project Structure

```
financial_ml_trading/
├── data/
│   └── raw/              # Historical price and macro data
├── database/
│   ├── predictions.db    # Prediction history
│   └── notes.db          # Personal notes
├── src/
│   ├── config.py         # Configuration settings
│   ├── market_api.py     # Market data API
│   ├── news_analyzer.py  # News sentiment analysis
│   ├── economic_api.py   # Economic calendar API
│   ├── database.py       # Database operations
│   ├── predict.py        # ML prediction engine
│   ├── train.py          # Model training
│   ├── feature_engineering_new.py
│   └── utils.py          # Utility functions
├── .streamlit/
│   └── config.toml       # Streamlit configuration
├── streamlit_app.py      # Main dashboard application
├── requirements.txt      # Python dependencies
└── README.md
```

## 🛠️ Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Quick Start

1. **Clone the repository**
```bash
git clone https://github.com/syuraihkv/ai-prediksion-ml.git
cd ai-prediksion-ml
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Run the dashboard**
```bash
streamlit run streamlit_app.py
```

The dashboard will be available at `http://localhost:8501`

### TA-Lib Installation (Optional)

For advanced technical indicators, install TA-Lib:

**Windows:**
```bash
Download from: http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-msvc.zip
```

**macOS:**
```bash
brew install ta-lib
```

**Linux:**
```bash
wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
tar -xzf ta-lib-0.4.0-src.tar.gz
cd ta-lib/
./configure --prefix=/usr
make
sudo make install
```

## 📖 Usage

### Running the Dashboard

```bash
streamlit run streamlit_app.py
```

### Dashboard Navigation

1. **Select Asset** - Choose from BTC/USD, XAU/USD, or NASDAQ
2. **Explore Tabs** - Navigate through Market Analysis, News & Events, AI & Probability, Performance, and Tools
3. **View Predictions** - Get AI-powered trading signals with confidence scores
4. **Analyze Charts** - Interactive charts with technical indicators
5. **Track Performance** - Monitor historical accuracy and backtesting results

### Key Features

- **Real-time Updates**: Automatic data refresh for market prices and news
- **Interactive Charts**: Zoom, pan, and explore detailed visualizations
- **Historical Analysis**: View past performance and trends
- **Probability Tools**: Monte Carlo simulation for risk assessment
- **Personal Notes**: Save your trading ideas and observations

## 🎯 Tech Stack

### Core Technologies
- **Python 3.8+** - Core programming language
- **Streamlit** - Interactive dashboard framework
- **Pandas** - Data manipulation and analysis
- **NumPy** - Numerical computing
- **SQLite** - Database management

### Machine Learning
- **Scikit-learn** - ML algorithms and utilities
- **XGBoost** - Gradient boosting framework
- **LightGBM** - Light gradient boosting
- **CatBoost** - Gradient boosting on decision trees

### Data Visualization
- **Matplotlib** - Plotting library
- **Seaborn** - Statistical data visualization
- **Plotly** - Interactive plots

### APIs & Data Sources
- **Yahoo Finance** - Market data
- **FRED** - Economic indicators
- **News APIs** - Sentiment analysis

### Deployment
- **Docker** - Containerization
- **Streamlit Cloud** - Cloud deployment

## Configuration

Edit `src/config.py` to customize:
- Instruments and timeframes
- Feature engineering parameters
- Model settings
- Trading parameters
- Validation settings

## Data Sources

- **Price Data**: Yahoo Finance (free)
- **Macro Data**: FRED (Federal Reserve Economic Data)
- **Sentiment Data**: Yahoo Finance

## Model Performance Metrics

- Accuracy, Precision, Recall, F1 Score
- ROC AUC, Confusion Matrix
- Win Rate, Profit Factor
- Sharpe Ratio, Sortino Ratio
- Maximum Drawdown, Calmar Ratio

## Risk Management

- No data leakage (strict time-series validation)
- No look-ahead bias
- Walk-forward validation
- Position sizing based on risk
- Stop-loss and take-profit

## Contributing

This is a research/educational project. Use at your own risk for trading.

## Disclaimer

This software is for educational and research purposes only. Past performance does not guarantee future results. Always do your own research and consult with financial advisors before making trading decisions.
