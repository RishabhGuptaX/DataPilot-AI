import pandas as pd


# ============================================================
# BASIC OPERATIONS
# ============================================================

def count_rows(
    df: pd.DataFrame,
) -> int:
    """Return the number of rows."""

    return len(df)


def unique_count(
    df: pd.DataFrame,
    column: str,
) -> int:
    """Return number of unique values."""

    return int(
        df[column].nunique()
    )


def value_counts(
    df: pd.DataFrame,
    column: str,
    limit: int = 10,
) -> pd.DataFrame:
    """Return most frequent values."""

    result = (
        df[column]
        .value_counts()
        .head(limit)
        .reset_index()
    )

    result.columns = [
        column,
        "Count",
    ]

    return result


# ============================================================
# GROUP OPERATIONS
# ============================================================

def group_mean(
    df: pd.DataFrame,
    group_by: str,
    value_column: str,
    limit: int = 10,
) -> pd.DataFrame:
    """Calculate mean grouped by a column."""

    result = (
        df.groupby(group_by)[value_column]
        .mean()
        .sort_values(
            ascending=False
        )
        .head(limit)
        .reset_index()
    )

    result[value_column] = (
        result[value_column]
        .round(2)
    )

    return result


def group_sum(
    df: pd.DataFrame,
    group_by: str,
    value_column: str,
    limit: int = 10,
) -> pd.DataFrame:
    """Calculate sum grouped by a column."""

    result = (
        df.groupby(group_by)[value_column]
        .sum()
        .sort_values(
            ascending=False
        )
        .head(limit)
        .reset_index()
    )

    return result


# ============================================================
# TOP N
# ============================================================

def top_n(
    df: pd.DataFrame,
    column: str,
    limit: int = 10,
) -> pd.DataFrame:
    """Return top N rows based on a column."""

    return (
        df.sort_values(
            by=column,
            ascending=False,
        )
        .head(limit)
        .reset_index(drop=True)
    )


# ============================================================
# DESCRIPTIVE STATISTICS
# ============================================================

def describe_dataset(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Return descriptive statistics."""

    return df.describe(
        include="all"
    ).transpose().reset_index()


# ============================================================
# FILTER
# ============================================================

def filter_dataset(
    df: pd.DataFrame,
    column: str,
    value,
    limit: int = 100,
) -> pd.DataFrame:
    """
    Simple equality filter.
    """

    result = df[
        df[column].astype(str)
        == str(value)
    ]

    return result.head(
        limit
    ).reset_index(drop=True)


# ============================================================
# MAIN ANALYSIS ENGINE
# ============================================================

def execute_analysis_plan(
    df: pd.DataFrame,
    plan: dict,
):
    """
    Execute a validated structured analysis plan.

    The LLM never directly executes Python.
    """

    operation = plan.get(
        "operation"
    )

    column = plan.get(
        "column"
    )

    group_by = plan.get(
        "group_by"
    )

    value_column = plan.get(
        "value_column"
    )

    limit = plan.get(
        "limit",
        10,
    )


    # --------------------------------------------------------
    # COUNT
    # --------------------------------------------------------

    if operation == "count":

        return count_rows(
            df
        )


    # --------------------------------------------------------
    # UNIQUE COUNT
    # --------------------------------------------------------

    if operation == "unique_count":

        return unique_count(
            df,
            column,
        )


    # --------------------------------------------------------
    # VALUE COUNTS
    # --------------------------------------------------------

    if operation == "value_counts":

        return value_counts(
            df,
            column,
            limit,
        )


    # --------------------------------------------------------
    # GROUP MEAN
    # --------------------------------------------------------

    if operation == "group_mean":

        return group_mean(
            df,
            group_by,
            value_column,
            limit,
        )


    # --------------------------------------------------------
    # GROUP SUM
    # --------------------------------------------------------

    if operation == "group_sum":

        return group_sum(
            df,
            group_by,
            value_column,
            limit,
        )


    # --------------------------------------------------------
    # TOP N
    # --------------------------------------------------------

    if operation == "top_n":

        return top_n(
            df,
            column,
            limit,
        )


    # --------------------------------------------------------
    # FILTER
    # --------------------------------------------------------

    if operation == "filter":

        filter_value = plan.get(
            "filter"
        )

        if not filter_value:

            raise ValueError(
                "Filter value is missing."
            )

        return filter_dataset(
            df,
            column,
            filter_value,
            limit,
        )


    # --------------------------------------------------------
    # DESCRIBE
    # --------------------------------------------------------

    if operation == "describe":

        return describe_dataset(
            df
        )


    # --------------------------------------------------------
    # UNKNOWN OPERATION
    # --------------------------------------------------------

    raise ValueError(
        f"Unsupported operation: {operation}"
    )