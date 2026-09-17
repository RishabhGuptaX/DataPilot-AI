# Dataset profiling and quality checks
import pandas as pd


def get_dataset_overview(df: pd.DataFrame) -> dict:
    """
    Generate high-level information about the dataset.
    """

    numerical_columns = df.select_dtypes(
        include=["number"]
    ).columns.tolist()

    categorical_columns = df.select_dtypes(
        include=["object", "category", "bool"]
    ).columns.tolist()

    missing_cells = int(df.isna().sum().sum())
    total_cells = int(df.shape[0] * df.shape[1])

    missing_percentage = (
        (missing_cells / total_cells) * 100
        if total_cells > 0
        else 0
    )

    duplicate_rows = int(df.duplicated().sum())

    return {
        "rows": int(df.shape[0]),
        "columns": int(df.shape[1]),
        "numerical_columns": len(numerical_columns),
        "categorical_columns": len(categorical_columns),
        "missing_cells": missing_cells,
        "missing_percentage": round(missing_percentage, 2),
        "duplicate_rows": duplicate_rows,
    }


def get_column_profile(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate detailed information for every column.
    """

    profile = pd.DataFrame({
        "Column": df.columns,
        "Data Type": df.dtypes.astype(str).values,
        "Missing Values": df.isna().sum().values,
        "Unique Values": df.nunique().values,
    })

    profile["Missing %"] = (
        profile["Missing Values"] / len(df) * 100
    ).round(2)

    return profile


def get_numeric_statistics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate descriptive statistics for numerical columns.
    """

    numerical_df = df.select_dtypes(include=["number"])

    if numerical_df.empty:
        return pd.DataFrame()

    return numerical_df.describe().T