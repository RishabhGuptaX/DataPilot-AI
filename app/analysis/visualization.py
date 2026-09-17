# Plotly visualization utilities
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


# ============================================================
# MAIN VISUALIZATION ENGINE
# ============================================================

def create_visualization(
    result,
    plan: dict,
):
    """
    Create an interactive Plotly visualization
    based on the analysis result and AI plan.

    Returns:
        Plotly Figure
        None when visualization is not appropriate.
    """

    if result is None:
        return None


    chart_type = plan.get(
        "chart"
    )


    if chart_type is None:
        return None


    # ========================================================
    # CONVERT SERIES TO DATAFRAME
    # ========================================================

    if isinstance(
        result,
        pd.Series,
    ):

        result = (
            result
            .to_frame()
            .reset_index()
        )


    # ========================================================
    # SCALAR RESULTS
    # ========================================================

    if not isinstance(
        result,
        pd.DataFrame,
    ):

        return None


    if result.empty:
        return None


    # ========================================================
    # CLEAN COLUMN NAMES
    # ========================================================

    result = result.copy()

    result.columns = [
        str(column)
        for column in result.columns
    ]


    # ========================================================
    # BAR CHART
    # ========================================================

    if chart_type == "bar":

        if len(result.columns) < 2:
            return None


        x_column = result.columns[0]
        y_column = result.columns[1]


        figure = px.bar(
            result,
            x=x_column,
            y=y_column,
            title=(
                f"{y_column} by "
                f"{x_column}"
            ),
            text=y_column,
        )


        figure.update_layout(
            xaxis_title=x_column,
            yaxis_title=y_column,
            hovermode="x unified",
        )


        figure.update_traces(
            textposition="outside"
        )


        return figure


    # ========================================================
    # LINE CHART
    # ========================================================

    if chart_type == "line":

        if len(result.columns) < 2:
            return None


        x_column = result.columns[0]
        y_column = result.columns[1]


        figure = px.line(
            result,
            x=x_column,
            y=y_column,
            title=(
                f"{y_column} over "
                f"{x_column}"
            ),
            markers=True,
        )


        figure.update_layout(
            xaxis_title=x_column,
            yaxis_title=y_column,
            hovermode="x unified",
        )


        return figure


    # ========================================================
    # PIE CHART
    # ========================================================

    if chart_type == "pie":

        if len(result.columns) < 2:
            return None


        label_column = result.columns[0]
        value_column = result.columns[1]


        figure = px.pie(
            result,
            names=label_column,
            values=value_column,
            title=(
                f"Distribution of "
                f"{label_column}"
            ),
        )


        figure.update_traces(
            textposition="inside",
            textinfo="percent+label",
        )


        return figure


    # ========================================================
    # HISTOGRAM
    # ========================================================

    if chart_type == "histogram":

        column = plan.get(
            "column"
        )


        if column is None:
            return None


        figure = px.histogram(
            result,
            x=column,
            title=(
                f"Distribution of "
                f"{column}"
            ),
        )


        figure.update_layout(
            xaxis_title=column,
            yaxis_title="Count",
        )


        return figure


    # ========================================================
    # SCATTER PLOT
    # ========================================================

    if chart_type == "scatter":

        column = plan.get(
            "column"
        )

        value_column = plan.get(
            "value_column"
        )


        if (
            column is None
            or value_column is None
        ):

            if len(result.columns) < 2:
                return None

            column = result.columns[0]
            value_column = result.columns[1]


        figure = px.scatter(
            result,
            x=column,
            y=value_column,
            title=(
                f"{value_column} vs "
                f"{column}"
            ),
        )


        figure.update_layout(
            xaxis_title=column,
            yaxis_title=value_column,
        )


        return figure


    # ========================================================
    # UNKNOWN CHART
    # ========================================================

    return None