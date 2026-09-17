import pandas as pd


def detect_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    Detect missing values in every column.
    """

    missing = df.isna().sum()

    result = pd.DataFrame(
        {
            "Column": missing.index,
            "Missing Values": missing.values,
        }
    )

    result["Missing %"] = (
        result["Missing Values"]
        / len(df)
        * 100
    ).round(2)

    return result[
        result["Missing Values"] > 0
    ].reset_index(drop=True)


def detect_duplicates(df: pd.DataFrame) -> int:
    """
    Count duplicate rows.
    """

    return int(
        df.duplicated().sum()
    )


def detect_numeric_outliers(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Detect numerical outliers using the IQR method.
    """

    numeric_columns = df.select_dtypes(
        include=["number"]
    ).columns

    results = []

    for column in numeric_columns:

        series = df[column].dropna()

        if series.empty:
            continue

        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)

        iqr = q3 - q1

        if iqr == 0:
            continue

        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr

        outliers = (
            (series < lower_bound)
            | (series > upper_bound)
        ).sum()

        if outliers > 0:

            results.append(
                {
                    "Column": column,
                    "Outliers": int(outliers),
                    "Lower Bound": round(
                        lower_bound,
                        2,
                    ),
                    "Upper Bound": round(
                        upper_bound,
                        2,
                    ),
                }
            )

    return pd.DataFrame(results)


def generate_cleaning_report(
    df: pd.DataFrame,
) -> dict:
    """
    Generate complete data-quality report.
    """

    return {
        "missing_values": (
            detect_missing_values(df)
        ),
        "duplicate_rows": (
            detect_duplicates(df)
        ),
        "outliers": (
            detect_numeric_outliers(df)
        ),
    }


# ============================================================
# CLEANING OPERATIONS
# ============================================================


def remove_duplicate_rows(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Remove duplicate rows.
    """

    return df.drop_duplicates().reset_index(
        drop=True
    )


def fill_missing_values(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Fill missing values using sensible defaults.

    Numerical columns:
        Median

    Categorical columns:
        Mode
    """

    cleaned_df = df.copy()

    numerical_columns = cleaned_df.select_dtypes(
        include=["number"]
    ).columns

    categorical_columns = cleaned_df.select_dtypes(
        include=[
            "object",
            "category",
            "bool",
        ]
    ).columns

    # Numerical columns → median
    for column in numerical_columns:

        if cleaned_df[column].isna().any():

            median_value = cleaned_df[
                column
            ].median()

            cleaned_df[column] = cleaned_df[
                column
            ].fillna(median_value)

    # Categorical columns → mode
    for column in categorical_columns:

        if cleaned_df[column].isna().any():

            mode_values = cleaned_df[
                column
            ].mode()

            if not mode_values.empty:

                cleaned_df[column] = cleaned_df[
                    column
                ].fillna(mode_values.iloc[0])

    return cleaned_df


def remove_outliers(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Remove numerical rows identified as IQR outliers.
    """

    cleaned_df = df.copy()

    numerical_columns = cleaned_df.select_dtypes(
        include=["number"]
    ).columns

    if len(numerical_columns) == 0:
        return cleaned_df

    valid_rows = pd.Series(
        True,
        index=cleaned_df.index,
    )

    for column in numerical_columns:

        series = cleaned_df[column]

        if series.dropna().empty:
            continue

        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)

        iqr = q3 - q1

        if iqr == 0:
            continue

        lower_bound = (
            q1 - 1.5 * iqr
        )

        upper_bound = (
            q3 + 1.5 * iqr
        )

        column_valid = (
            series.isna()
            | (
                (series >= lower_bound)
                & (series <= upper_bound)
            )
        )

        valid_rows &= column_valid

    return cleaned_df[
        valid_rows
    ].reset_index(drop=True)


def clean_dataset(
    df: pd.DataFrame,
    remove_duplicates: bool = False,
    fill_missing: bool = False,
    remove_outlier_rows: bool = False,
) -> pd.DataFrame:
    """
    Apply selected cleaning operations.
    """

    cleaned_df = df.copy()

    if remove_duplicates:

        cleaned_df = remove_duplicate_rows(
            cleaned_df
        )

    if fill_missing:

        cleaned_df = fill_missing_values(
            cleaned_df
        )

    if remove_outlier_rows:

        cleaned_df = remove_outliers(
            cleaned_df
        )

    return cleaned_df.reset_index(
        drop=True
    )