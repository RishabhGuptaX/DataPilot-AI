import pandas as pd


# ============================================================
# PYTHON CODE VALIDATION
# ============================================================

BLOCKED_NAMES = {
    "import",
    "__import__",
    "eval",
    "exec",
    "open",
    "compile",
    "input",
    "globals",
    "locals",
    "vars",
    "getattr",
    "setattr",
    "delattr",
    "breakpoint",
}


BLOCKED_ATTRIBUTES = {
    "__class__",
    "__dict__",
    "__bases__",
    "__subclasses__",
    "__globals__",
    "__code__",
    "__builtins__",
}


def validate_generated_code(
    code: str,
) -> tuple[bool, str]:
    """
    Validate LLM-generated Python code.

    This function is kept for backward compatibility
    with the earlier DataPilot analyst architecture.
    """

    import ast

    try:

        tree = ast.parse(code)

    except SyntaxError as error:

        return (
            False,
            f"Invalid Python syntax: {error}",
        )


    for node in ast.walk(tree):

        # Block imports
        if isinstance(
            node,
            ast.Import,
        ):

            return (
                False,
                "Import statements are not allowed.",
            )


        if isinstance(
            node,
            ast.ImportFrom,
        ):

            return (
                False,
                "Import statements are not allowed.",
            )


        # Block dangerous function calls
        if isinstance(
            node,
            ast.Call,
        ):

            if isinstance(
                node.func,
                ast.Name,
            ):

                if node.func.id in BLOCKED_NAMES:

                    return (
                        False,
                        f"Blocked function: "
                        f"{node.func.id}",
                    )


        # Block dangerous attributes
        if isinstance(
            node,
            ast.Attribute,
        ):

            if (
                node.attr.startswith("__")
                or node.attr
                in BLOCKED_ATTRIBUTES
            ):

                return (
                    False,
                    f"Blocked attribute: "
                    f"{node.attr}",
                )


    return (
        True,
        "Code passed validation.",
    )


# ============================================================
# STRUCTURED ANALYSIS PLAN VALIDATION
# ============================================================

SUPPORTED_OPERATIONS = {
    "count",
    "unique_count",
    "value_counts",
    "group_mean",
    "group_sum",
    "top_n",
    "filter",
    "describe",
}


SUPPORTED_CHARTS = {
    None,
    "bar",
    "line",
    "pie",
    "histogram",
    "scatter",
}


def validate_analysis_plan(
    plan: dict,
    df: pd.DataFrame,
) -> tuple[bool, str]:
    """
    Validate a structured analysis plan generated
    by the AI analyst.

    The LLM can only request operations that are
    explicitly supported by DataPilot.
    """

    # --------------------------------------------------------
    # Check plan type
    # --------------------------------------------------------

    if not isinstance(
        plan,
        dict,
    ):

        return (
            False,
            "Analysis plan must be a JSON object.",
        )


    # --------------------------------------------------------
    # Check operation
    # --------------------------------------------------------

    operation = plan.get(
        "operation"
    )

    if operation not in SUPPORTED_OPERATIONS:

        return (
            False,
            f"Unsupported operation: {operation}",
        )


    # --------------------------------------------------------
    # Check main column
    # --------------------------------------------------------

    column = plan.get(
        "column"
    )

    if column is not None:

        if column not in df.columns:

            return (
                False,
                (
                    f"Column '{column}' "
                    f"does not exist in the dataset."
                ),
            )


    # --------------------------------------------------------
    # Check group-by column
    # --------------------------------------------------------

    group_by = plan.get(
        "group_by"
    )

    if group_by is not None:

        if group_by not in df.columns:

            return (
                False,
                (
                    f"Group column '{group_by}' "
                    f"does not exist in the dataset."
                ),
            )


    # --------------------------------------------------------
    # Check value column
    # --------------------------------------------------------

    value_column = plan.get(
        "value_column"
    )

    if value_column is not None:

        if value_column not in df.columns:

            return (
                False,
                (
                    f"Value column '{value_column}' "
                    f"does not exist in the dataset."
                ),
            )


    # --------------------------------------------------------
    # Check chart
    # --------------------------------------------------------

    chart = plan.get(
        "chart"
    )

    if chart not in SUPPORTED_CHARTS:

        return (
            False,
            f"Unsupported chart type: {chart}",
        )


    # --------------------------------------------------------
    # Check limit
    # --------------------------------------------------------

    limit = plan.get(
        "limit"
    )

    if limit is not None:

        if not isinstance(
            limit,
            int,
        ):

            return (
                False,
                "Limit must be an integer.",
            )


        if limit < 1 or limit > 100:

            return (
                False,
                "Limit must be between 1 and 100.",
            )


    # --------------------------------------------------------
    # Check operation-specific requirements
    # --------------------------------------------------------

    if operation in {
        "unique_count",
        "value_counts",
        "top_n",
    }:

        if column is None:

            return (
                False,
                (
                    f"The '{operation}' operation "
                    f"requires a column."
                ),
            )


    if operation in {
        "group_mean",
        "group_sum",
    }:

        if group_by is None:

            return (
                False,
                (
                    f"The '{operation}' operation "
                    f"requires a group_by column."
                ),
            )

        if value_column is None:

            return (
                False,
                (
                    f"The '{operation}' operation "
                    f"requires a value_column."
                ),
            )


    if operation == "filter":

        if column is None:

            return (
                False,
                (
                    "The filter operation "
                    "requires a column."
                ),
            )

        if plan.get(
            "filter"
        ) is None:

            return (
                False,
                (
                    "The filter operation "
                    "requires a filter value."
                ),
            )


    # --------------------------------------------------------
    # Validation successful
    # --------------------------------------------------------

    return (
        True,
        "Analysis plan is valid.",
    )