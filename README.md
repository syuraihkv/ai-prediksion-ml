# 🤖 AI Market Prediction System

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Next.js](https://img.shields.io/badge/Next.js-14.0+-black.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Status](https://img.shields.io/badge/Status-Active-success.svg)

**Professional AI-Powered Market Prediction Platform**

Modern web application with machine learning predictions, real-time market data, and advanced analytics

[🚀 Features](#-features) • [🏗️ Architecture](#-architecture) • [🛠️ Installation](#️-installation) • [📖 Usage](#-usage) • [🎯 Tech Stack](#-tech-stack)

</div>

## 🚀 Features

### 📊 Market Analysis
- **Multi-Instrument Support**: Bitcoin (BTC), Ethereum (ETH), Gold (XAU)
- **Real-time Data**: Live market prices from yfinance
- **Historical Charts**: Interactive price history with multiple timeframes
- **Volume Analysis**: Volume profiles and market depth indicators
- **Correlation Analysis**: Asset correlation heatmaps for diversification

### 🤖 AI & Prediction
- **Multiple ML Models**: Logistic Regression, Random Forest, XGBoost, LightGBM, CatBoost
- **Ensemble Predictions**: Combines multiple models for better accuracy
- **Probability Scores**: Confidence scores with up/down probabilities
- **Feature Analysis**: Real-time feature importance display
- **Model Comparison**: Compare performance across all models

### 📈 Performance Tracking
- **Accuracy Metrics**: Track model performance over time
- **Performance Charts**: Visual accuracy trends
- **Model Selection**: Automatic best model selection
- **Historical Data**: Prediction history and results

## 🏗️ Architecture

The project now features a modern **Next.js + FastAPI** architecture:

```
Frontend (Next.js + Tailwind CSS)
    ↓ HTTP/REST API
Backend (FastAPI + Python)
    ↓
ML Models (scikit-learn, XGBoost, LightGBM, CatBoost)
    ↓
Data Sources (yfinance, APIs)
```

### Project Structure

```
financial_ml_trading/
├── frontend/              # Next.js frontend application
│   ├── app/
│   │   ├── layout.tsx    # Root layout with navigation
│   │   ├── page.tsx      # Home page
│   │   ├── market/       # Live market data
│   │   ├── prediction/   # AI predictions
│   │   ├── models/       # Model comparison
│   │   └── performance/  # Performance metrics
│   ├── package.json      # Frontend dependencies
│   ├── tailwind.config.js
│   └── tsconfig.json
├── backend/              # FastAPI backend application
│   ├── main.py          # FastAPI application entry
│   ├── src/
│   │   ├── config.py    # Configuration settings
│   │   ├── database.py  # Database models
│   │   ├── schemas.py   # Pydantic schemas
│   │   └── api/         # API endpoints
│   │       ├── health.py
│   │       ├── market.py
│   │       ├── prediction.py
│   │       └── models.py
│   └── requirements.txt # Backend dependencies
├── data/
│   └── models/          # Trained ML models
├── src/                 # Legacy Streamlit code
│   ├── config.py
│   ├── market_api.py
│   ├── predict.py
│   ├── train.py
│   └── ...
├── streamlit_app.py     # Legacy Streamlit dashboard
└── requirements.txt     # Legacy dependencies
```

## 🛠️ Installation

### Prerequisites

- **Frontend**: Node.js 18+ and npm/yarn
- **Backend**: Python 3.8+ and pip
- **Database**: PostgreSQL (optional, for production)

### Quick Start

#### 1. Clone the repository

```bash
git clone https://github.com/syuraihkv/ai-prediksion-ml.git
cd ai-prediksion-ml
```

#### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp ../.env.example .env
# Edit .env with your API keys

# Run backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The backend API will be available at `http://localhost:8000`

#### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Set environment variable
echo NEXT_PUBLIC_API_URL=http://localhost:8000 > .env.local

# Run development server
npm run dev
```

The frontend will be available at `http://localhost:3000`

### API Endpoints

#### Health Check
- `GET /api/health` - Check API status

#### Market Data
- `GET /api/market/price/{asset}` - Get current price
- `GET /api/market/history/{asset}` - Get historical data
- `GET /api/market/assets` - List supported assets

#### Predictions
- `POST /api/prediction/predict` - Get AI prediction

#### Models
- `GET /api/models/compare/{asset}` - Compare models
- `GET /api/models/list` - List all models
- `GET /api/models/performance/{asset}/{model_name}` - Get model performance

## 📖 Usage

### Running the Application

1. **Start the backend** (in `backend/` directory):
```bash
uvicorn main:app --reload
```

2. **Start the frontend** (in `frontend/` directory):
```bash
npm run dev
```

3. **Open browser**:
Navigate to `http://localhost:3000`

### Using the Dashboard

1. **Home Page** - Overview of features and supported assets
2. **Live Market** - Real-time market data and prices
3. **AI Prediction** - Get AI-powered predictions with confidence scores
4. **Compare Models** - Compare performance across different ML models
5. **Performance** - Track model accuracy over time

### Training New Models

```bash
# From project root
python train_all_models.py
```

This will train all ML models (Logistic Regression, Random Forest, XGBoost, LightGBM, CatBoost) for BTC and XAU assets.

## 🎯 Tech Stack

### Frontend
- **Next.js 14** - React framework with App Router
- **TypeScript** - Type-safe JavaScript
- **Tailwind CSS** - Utility-first CSS framework
- **Lucide React** - Icon library
- **Recharts** - Chart library
- **Axios** - HTTP client

### Backend
- **FastAPI** - Modern Python web framework
- **Pydantic** - Data validation
- **SQLAlchemy** - ORM for database
- **Uvicorn** - ASGI server

### Machine Learning
- **Scikit-learn** - ML algorithms
- **XGBoost** - Gradient boosting
- **LightGBM** - Light gradient boosting
- **CatBoost** - Gradient boosting on decision trees
- **Joblib** - Model serialization

### Data Sources
- **yfinance** - Market data
- **Yahoo Finance** - Additional market data

### Deployment

#### Frontend (Vercel)
```bash
cd frontend
vercel deploy
```

#### Backend (Render/Railway)
```bash
cd backend
# Deploy to Render or Railway
```

## Configuration

### Backend Configuration

Edit `backend/src/config.py`:
- API keys for data sources
- Database connection strings
- Model directory paths
- CORS settings

### Frontend Configuration

Edit `frontend/.env.local`:
- `NEXT_PUBLIC_API_URL` - Backend API URL

## Legacy Streamlit Version

The original Streamlit dashboard is still available:

```bash
# Install legacy dependencies
pip install -r requirements.txt

# Run Streamlit dashboard
streamlit run streamlit_app.py
```

## Contributing

This is a research/educational project. Contributions are welcome!

## Disclaimer

This software is for educational and research purposes only. Past performance does not guarantee future results. Always do your own research and consult with financial advisors before making trading decisions.
