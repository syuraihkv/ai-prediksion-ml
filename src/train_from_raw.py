"""
End-to-end training entry point that actually produces a trained model file.

Why this script exists
-----------------------
`src/train.py` defines the ModelTrainer class (splitting, training, evaluating,
saving) but nothing in the repo actually calls it against the historical price
data in `data/raw/`. As shipped, `data/models/` is empty, which means
`src/predict.py` always falls back to a "no trained model" state.

This script closes that gap:
1. Loads a raw OHLCV CSV for one instrument/timeframe from `data/raw/`.
2. Builds technical features with the existing feature engineering module.
3. Builds a BUY/SELL target label from *future* returns (shifted forward,
   so the label for day T only uses prices strictly after T - no look-ahead).
4. Splits chronologically into train/val/test (no shuffling).
5. Trains all available models and evaluates them on the validation split.
6. Saves the best model to `data/models/<ASSET>_<model_name>.joblib`.

Usage
-----
    python -m src.train_from_raw --asset XAU --timeframe 1d
    python -m src.train_from_raw --asset BTC --timeframe 1d
    python -m src.train_from_raw --all
"""

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from src.config import RAW_DATA_DIR, MODELS_DIR
from src.feature_engineering_new import NewsImpactFeatureEngineer
from src.train import ModelTrainer
from src.utils import setup_logger

logger = setup_logger("TrainFromRaw")

# How many periods ahead the target looks, and the minimum move (as a
# fraction of price) required to count as a BUY signal rather than SELL.
LOOKAHEAD_PERIODS = 1
TARGET_THRESHOLD = 0.0  # BUY if the next period's close is higher, else SELL


def load_raw_price_csv(asset: str, timeframe: str) -> pd.DataFrame:
    """Load a single OHLCV CSV from data/raw/, e.g. XAU_1d.csv."""
    path = RAW_DATA_DIR / f"{asset}_{timeframe}.csv"
    if not path.exists():
        raise FileNotFoundError(f"No raw data file found at {path}")

    df = pd.read_csv(path, parse_dates=["Date"])
    df = df.sort_values("Date").reset_index(drop=True)
    return df


def build_feature_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """
    Build technical features + a leak-free target column.

    The target for row T is derived from price data at T + LOOKAHEAD_PERIODS
    (via pandas .shift(-LOOKAHEAD_PERIODS)), so it is only known in hindsight
    -- this is standard for supervised training, NOT look-ahead bias, because
    at prediction time we only ever feed the model features from the current
    and past rows, never the label itself.
    """
    engineer = NewsImpactFeatureEngineer(logger=logger)
    features = engineer.create_technical_features(df)

    if features.empty:
        raise ValueError("Feature engineering returned an empty DataFrame - check input columns")

    # Leak-free target: did price go up over the next LOOKAHEAD_PERIODS?
    target = engineer.create_target_labels(
        features, lookahead=LOOKAHEAD_PERIODS, threshold=TARGET_THRESHOLD
    )
    features["Target"] = target

    # Drop rows with NaNs introduced by indicator warm-up windows (start of
    # series) and by the forward-shifted target (end of series).
    features = features.dropna().reset_index(drop=True)

    return features


def train_one(asset: str, timeframe: str = "1d") -> str:
    logger.info(f"=== Training on {asset} ({timeframe}) ===")

    raw_df = load_raw_price_csv(asset, timeframe)
    logger.info(f"Loaded {len(raw_df)} rows from data/raw/{asset}_{timeframe}.csv")

    feature_df = build_feature_matrix(raw_df)
    logger.info(f"Built feature matrix: {feature_df.shape}")

    trainer = ModelTrainer(logger=logger)

    train_df, val_df, test_df = trainer.split_time_series_data(feature_df, date_column="Date")
    if len(train_df) < 50 or len(val_df) < 10:
        raise ValueError(
            f"Not enough data after the chronological split "
            f"(train={len(train_df)}, val={len(val_df)}, test={len(test_df)}) "
            f"to train reliably for {asset}."
        )

    X_train, y_train = trainer.prepare_features(train_df, target_column="Target")
    X_val, y_val = trainer.prepare_features(val_df, target_column="Target")
    X_test, y_test = trainer.prepare_features(test_df, target_column="Target")

    logger.info(
        f"Split sizes - train: {len(X_train)}, val: {len(X_val)}, test: {len(X_test)}"
    )
    logger.info(f"Train target balance - BUY: {y_train.mean():.1%}")

    results = trainer.train_all_models(X_train, y_train, X_val, y_val)

    if not results:
        raise RuntimeError(f"No models trained successfully for {asset}")

    comparison = trainer.compare_models(results)
    logger.info("Validation comparison:\n" + comparison.to_string(index=False))

    # Final honest check on the held-out test split (never used for model
    # selection) so we know how the *chosen* model performs out-of-sample.
    test_metrics = trainer.evaluate_model(trainer.best_model, X_test, y_test)
    logger.info(
        f"Best model ({trainer.best_model_name}) on held-out TEST split: "
        f"accuracy={test_metrics['accuracy']:.3f}, "
        f"f1={test_metrics['f1_score']:.3f}, "
        f"roc_auc={test_metrics['roc_auc']}"
    )

    save_dir = Path(MODELS_DIR)
    model_filename = f"{asset}_{trainer.best_model_name}"
    trainer.save_model(trainer.best_model, model_filename, save_dir)

    return str(save_dir / f"{model_filename}.joblib")


def main():
    parser = argparse.ArgumentParser(description="Train real ML models from data/raw CSVs")
    parser.add_argument("--asset", type=str, help="Asset to train on, e.g. XAU, BTC, NASDAQ")
    parser.add_argument("--timeframe", type=str, default="1d", help="Timeframe, e.g. 1d, 1h, 4h")
    parser.add_argument("--all", action="store_true", help="Train on all default assets (XAU, BTC)")
    args = parser.parse_args()

    if args.all:
        assets = ["XAU", "BTC"]
    elif args.asset:
        assets = [args.asset]
    else:
        parser.error("Provide --asset <NAME> or --all")
        return

    saved_paths = []
    for asset in assets:
        try:
            path = train_one(asset, args.timeframe)
            saved_paths.append(path)
        except Exception as e:
            logger.error(f"Failed to train model for {asset}: {e}")

    if saved_paths:
        logger.info("Saved trained model(s):")
        for p in saved_paths:
            logger.info(f"  - {p}")
    else:
        logger.error("No models were successfully trained/saved.")


if __name__ == "__main__":
    main()
