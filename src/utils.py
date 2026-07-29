"""
Utility functions for the Financial ML Trading System.

This file contains common utility functions used across the system:
- Logging setup
- File I/O operations
- Data validation
- Helper functions
"""

import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional
import pandas as pd
import numpy as np
from datetime import datetime


def setup_logger(
    name: str,
    log_file: Optional[Path] = None,
    level: str = "INFO"
) -> logging.Logger:
    """
    Setup logger with file and console handlers.
    
    Args:
        name: Logger name
        log_file: Optional path to log file
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Remove existing handlers
    logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, level.upper()))
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (optional)
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(getattr(logging, level.upper()))
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def ensure_directory(path: Path) -> Path:
    """
    Ensure directory exists, create if it doesn't.
    
    Args:
        path: Directory path
    
    Returns:
        Path object
    """
    path.mkdir(parents=True, exist_ok=True)
    return path


def save_to_csv(
    data: pd.DataFrame,
    filepath: Path,
    index: bool = True
) -> None:
    """
    Save DataFrame to CSV file.
    
    Args:
        data: DataFrame to save
        filepath: Output file path
        index: Whether to save index
    """
    ensure_directory(filepath.parent)
    data.to_csv(filepath, index=index)
    print(f"Data saved to {filepath}")


def load_from_csv(filepath: Path) -> pd.DataFrame:
    """
    Load DataFrame from CSV file.
    
    Args:
        filepath: Input file path
    
    Returns:
        Loaded DataFrame
    """
    if not filepath.exists():
        raise FileNotFoundError(f"File not found: {filepath}")
    
    return pd.read_csv(filepath, index_col=0, parse_dates=True)


def validate_dataframe(
    df: pd.DataFrame,
    required_columns: List[str],
    df_name: str = "DataFrame"
) -> bool:
    """
    Validate DataFrame has required columns and is not empty.
    
    Args:
        df: DataFrame to validate
        required_columns: List of required column names
        df_name: Name of DataFrame for error messages
    
    Returns:
        True if valid
    
    Raises:
        ValueError: If validation fails
    """
    if df.empty:
        raise ValueError(f"{df_name} is empty")
    
    missing_cols = set(required_columns) - set(df.columns)
    if missing_cols:
        raise ValueError(
            f"{df_name} missing required columns: {missing_cols}"
        )
    
    return True


def check_data_leakage(
    df: pd.DataFrame,
    feature_columns: List[str],
    target_column: str
) -> bool:
    """
    Check for potential data leakage in features.
    
    Args:
        df: DataFrame to check
        feature_columns: List of feature column names
        target_column: Target column name
    
    Returns:
        True if no leakage detected
    
    Raises:
        ValueError: If potential leakage detected
    """
    # Check if any feature contains future information
    # This is a basic check - more sophisticated checks may be needed
    for col in feature_columns:
        if 'future' in col.lower() or 'next' in col.lower():
            raise ValueError(
                f"Potential data leakage detected in feature: {col}"
            )
    
    return True


def calculate_percentage_change(
    current: float,
    previous: float
) -> float:
    """
    Calculate percentage change between two values.
    
    Args:
        current: Current value
        previous: Previous value
    
    Returns:
        Percentage change
    """
    if previous == 0:
        return 0.0
    return ((current - previous) / previous) * 100


def format_number(
    value: float,
    decimals: int = 2
) -> str:
    """
    Format number with specified decimal places.
    
    Args:
        value: Number to format
        decimals: Number of decimal places
    
    Returns:
        Formatted string
    """
    return f"{value:.{decimals}f}"


def get_current_timestamp() -> str:
    """
    Get current timestamp as formatted string.
    
    Returns:
        Current timestamp string
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def split_data_by_time(
    df: pd.DataFrame,
    train_size: float = 0.7,
    val_size: float = 0.15,
    test_size: float = 0.15
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Split DataFrame by time (not random).
    
    Args:
        df: DataFrame with datetime index
        train_size: Proportion for training
        val_size: Proportion for validation
        test_size: Proportion for testing
    
    Returns:
        Tuple of (train, validation, test) DataFrames
    """
    n = len(df)
    train_end = int(n * train_size)
    val_end = int(n * (train_size + val_size))
    
    train = df.iloc[:train_end]
    val = df.iloc[train_end:val_end]
    test = df.iloc[val_end:]
    
    return train, val, test


def memory_usage(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Calculate memory usage of DataFrame.
    
    Args:
        df: DataFrame to analyze
    
    Returns:
        Dictionary with memory usage statistics
    """
    memory_bytes = df.memory_usage(deep=True).sum()
    memory_mb = memory_bytes / (1024 * 1024)
    
    return {
        "total_bytes": memory_bytes,
        "total_mb": round(memory_mb, 2),
        "rows": len(df),
        "columns": len(df.columns)
    }


def reduce_memory_usage(df: pd.DataFrame) -> pd.DataFrame:
    """
    Reduce memory usage of DataFrame by optimizing data types.
    
    Args:
        df: DataFrame to optimize
    
    Returns:
        Optimized DataFrame
    """
    # Convert numeric types to smallest possible
    for col in df.select_dtypes(include=['int64']).columns:
        df[col] = pd.to_numeric(df[col], downcast='integer')
    
    for col in df.select_dtypes(include=['float64']).columns:
        df[col] = pd.to_numeric(df[col], downcast='float')
    
    # Convert object to category if low cardinality
    for col in df.select_dtypes(include=['object']).columns:
        if df[col].nunique() / len(df[col]) < 0.5:
            df[col] = df[col].astype('category')
    
    return df
