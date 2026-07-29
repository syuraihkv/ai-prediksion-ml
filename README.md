# Financial ML Trading System

A comprehensive Machine Learning system for financial market prediction with historical backtesting and real-time paper trading capabilities.

## Features

- **Multi-Instrument Support**: Bitcoin, Gold, NASDAQ
- **Multiple Timeframes**: 5-minute, 1-hour, 4-hour
- **Advanced Feature Engineering**: 20+ technical indicators
- **Multiple ML Models**: Logistic Regression, Random Forest, XGBoost, LightGBM, CatBoost
- **Hyperparameter Optimization**: Optuna-based tuning
- **Walk-Forward Validation**: Time-series aware validation
- **Comprehensive Backtesting**: 15+ performance metrics
- **Real-Time Paper Trading**: Live prediction and tracking
- **Interactive Dashboard**: Streamlit-based visualization

## Project Structure

```
financial_ml_trading/
├── data/
│   ├── raw/              # Raw downloaded data
│   ├── processed/        # Processed feature data
│   └── models/           # Saved model files
├── database/
│   └── trading.db        # SQLite database
├── notebooks/
│   └── exploration.ipynb # EDA notebooks
├── src/
│   ├── __init__.py
│   ├── config.py         # Configuration settings
│   ├── data_collector.py # Data fetching
│   ├── feature_engineering.py
│   ├── preprocessing.py
│   ├── model_training.py
│   ├── hyperparameter_tuning.py
│   ├── evaluation.py
│   ├── backtest.py
│   ├── realtime_trading.py
│   └── utils.py
├── streamlit_app.py
├── requirements.txt
└── README.md
```

## Installation

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Install TA-Lib (required for technical indicators):
```bash
# Windows
Download from: http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-msvc.zip

# macOS
brew install ta-lib

# Linux
wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
tar -xzf ta-lib-0.4.0-src.tar.gz
cd ta-lib/
./configure --prefix=/usr
make
sudo make install
```

## Usage

### Data Collection

```python
from src.data_collector import DataCollector

collector = DataCollector()
data = collector.collect_all_data()
```

### Feature Engineering

```python
from src.feature_engineering import FeatureEngineer

engineer = FeatureEngineer()
features = engineer.create_features(price_data)
```

### Model Training

```python
from src.model_training import ModelTrainer

trainer = ModelTrainer()
model = trainer.train_model(X_train, y_train)
```

### Backtesting

```python
from src.backtest import Backtester

backtester = Backtester()
results = backtester.run_backtest(model, test_data)
```

### Real-Time Trading

```python
from src.realtime_trading import RealTimeTrader

trader = RealTimeTrader()
trader.start_trading()
```

### Streamlit Dashboard

```bash
streamlit run streamlit_app.py
```

## Deployment

### Docker Deployment

The application can be deployed using Docker for easy containerization and deployment.

#### Prerequisites
- Docker installed on your system
- Docker Compose (optional, for easier deployment)

#### Build and Run with Docker Compose (Recommended)

```bash
# Build and start the container
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the container
docker-compose down
```

The application will be available at `http://localhost:8501`

#### Build and Run with Docker

```bash
# Build the image
docker build -t financial-ml-trading .

# Run the container
docker run -d \
  -p 8501:8501 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/database:/app/database \
  -v $(pwd)/catboost_info:/app/catboost_info \
  --name financial-ml-trading \
  financial-ml-trading
```

#### Data Persistence

The Docker setup uses volume mounts to persist data outside the container:
- `./data` - Raw and processed data
- `./database` - SQLite database
- `./catboost_info` - CatBoost training info

This ensures your data and models are preserved even when the container is recreated.

#### Environment Variables

You can customize the application by setting environment variables:
- `STREAMLIT_SERVER_PORT` - Port for Streamlit server (default: 8501)
- `STREAMLIT_SERVER_ADDRESS` - Server address (default: 0.0.0.0)

#### Cloud Deployment

For cloud deployment, you can push the Docker image to a container registry and deploy to:
- **AWS ECS/Fargate**
- **Google Cloud Run**
- **Azure Container Instances**
- **Heroku** (using container registry)
- **Railway**
- **Render**

Example for deploying to a cloud platform:
```bash
# Tag and push to registry
docker tag financial-ml-trading your-registry/financial-ml-trading:latest
docker push your-registry/financial-ml-trading:latest

# Deploy using your cloud provider's CLI
```

### Streamlit Cloud Deployment

For easy deployment to Streamlit Cloud, follow these steps:

#### Prerequisites
- GitHub account with the code pushed to a repository
- Streamlit Cloud account (free tier available)

#### Deployment Steps

1. **Push code to GitHub**
```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/yourusername/financial-ml-trading.git
git push -u origin main
```

2. **Deploy to Streamlit Cloud**
- Go to [share.streamlit.io](https://share.streamlit.io)
- Click "New app"
- Connect your GitHub repository
- Select the repository and branch
- Set main file path to `streamlit_app.py`
- Click "Deploy"

#### Streamlit Cloud Configuration Files

The project includes the following files for Streamlit Cloud:
- `requirements.txt` - Python dependencies
- `packages.txt` - System dependencies (TA-Lib)
- `.streamlit/config.toml` - Streamlit configuration

#### Important Notes for Streamlit Cloud

- **TA-Lib Installation**: Streamlit Cloud will automatically install system dependencies from `packages.txt`
- **Data Persistence**: Streamlit Cloud doesn't persist data between deployments. Consider using:
  - External database (PostgreSQL, MongoDB)
  - Cloud storage (AWS S3, Google Cloud Storage)
  - Streamlit's built-in file upload for temporary data
- **Environment Variables**: Set secrets in Streamlit Cloud dashboard for sensitive data
- **Resource Limits**: Free tier has CPU and memory limitations

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
