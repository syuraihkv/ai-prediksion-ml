# Setup Guide for AI Economic News Impact Predictor

## 🚨 CRITICAL: API Key Rotation Required

The following API keys were previously exposed in the git repository and must be revoked/rotated immediately:

- **CoinMarketCap API Key** - Revoke at https://coinmarketcap.com/api/
- **CoinGecko API Key** - Revoke at https://www.coingecko.com/en/api
- **FRED API Key** - Revoke at https://fred.stlouisfed.org/docs/api/api_key.html
- **TwelveData API Key** - Revoke at https://twelvedata.com/docs#authentication
- **NewsData API Key** - Revoke at https://newsdata.io/docs

## Step 1: Create .env File

Copy the example file and add your new API keys:

```bash
cp .env.example .env
```

Edit `.env` and add your new API keys:

```env
# Crypto API Keys
COINMARKETCAP_API_KEY=your_new_coinmarketcap_api_key_here
COINGECKO_API_KEY=your_new_coingecko_api_key_here

# Economic Data API Keys
FRED_API_KEY=your_new_fred_api_key_here
TWELVEDATA_API_KEY=your_new_twelvedata_api_key_here
NEWS_DATA_API_KEY=your_new_newsdata_api_key_here
FINHUB_API_KEY=your_finhub_api_key_here
TRADING_ECONOMICS_API_KEY=your_trading_economics_api_key_here

# GitHub API (optional)
GITHUB_TOKEN=your_github_token_here
GITHUB_REPO=username/repo
```

## Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 3: Train ML Models (Optional but Recommended)

Train models using historical data:

```bash
# Train for XAU (Gold)
python -m src.train_from_raw --asset XAU --timeframe 1d

# Train for BTC (Bitcoin)
python -m src.train_from_raw --asset BTC --timeframe 1d

# Train for both
python -m src.train_from_raw --all
```

**Note:** This requires historical data files in `data/raw/` directory (e.g., `XAU_1d.csv`, `BTC_1d.csv`).

## Step 4: Run the Application

```bash
streamlit run streamlit_app.py
```

## Step 5: Streamlit Cloud Deployment

For deployment on Streamlit Cloud:

1. Go to your app's workspace on Streamlit Cloud
2. Navigate to Settings → Secrets
3. Add your API keys in the format:
   ```
   COINMARKETCAP_API_KEY=your_new_coinmarketcap_api_key_here
   COINGECKO_API_KEY=your_new_coingecko_api_key_here
   FRED_API_KEY=your_new_fred_api_key_here
   TWELVEDATA_API_KEY=your_new_twelvedata_api_key_here
   NEWS_DATA_API_KEY=your_new_newsdata_api_key_here
   ```

## Security Best Practices

- ✅ Never commit `.env` file to version control
- ✅ Use different API keys for development and production
- ✅ Rotate API keys regularly
- ✅ Monitor API usage for unusual activity
- ✅ Use environment variables for all sensitive data

## Troubleshooting

### "No trained models found" warning

This is expected if you haven't trained models yet. The app will use sentiment-based heuristics instead. To train models:

```bash
python -m src.train_from_raw --all
```

### API connection errors

- Verify your API keys are correct in `.env`
- Check if you have reached API rate limits
- Ensure internet connection is stable

### Database errors

The app will automatically create the SQLite database on first run. Ensure you have write permissions in the project directory.

## Model Performance Notes

- **XAU Model**: Shows promise but trained on limited data (~160 rows). Use with caution.
- **BTC Model**: Currently shows no predictive edge (ROC AUC ≈ 0.50). Needs more features or data.

Both models should be considered as examples of the pipeline, not as trading recommendations.
