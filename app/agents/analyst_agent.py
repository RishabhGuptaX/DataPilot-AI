import json
import re

import pandas as pd

from app.core.groq_client import client


# ============================================================
# SUPPORTED OPERATIONS
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


# ============================================================
# DATASET SCHEMA
# ============================================================

def build_dataset_schema(
    df: pd.DataFrame,
) -> dict:

    columns = []

    for column in df.columns:

        sample_values = (
            df[column]
            .dropna()
            .astype(str)
            .head(3)
            .tolist()
        )

        columns.append(
            {
                "name": str(column),
                "dtype": str(
                    df[column].dtype
                ),
                "sample_values": (
                    sample_values
                ),
            }
        )

    return {
        "rows": int(len(df)),
        "columns": columns,
    }


# ============================================================
# EXTRACT JSON
# ============================================================

def extract_json(
    text: str,
) -> dict:

    if not text:

        raise ValueError(
            "The AI returned an empty response."
        )


    text = text.strip()


    text = re.sub(
        r"```json\s*",
        "",
        text,
        flags=re.IGNORECASE,
    )

    text = re.sub(
        r"```python\s*",
        "",
        text,
        flags=re.IGNORECASE,
    )

    text = text.replace(
        "```",
        "",
    ).strip()


    decoder = json.JSONDecoder()


    candidates = [
        match.start()
        for match in re.finditer(
            r"\{",
            text,
        )
    ]


    for start in candidates:

        try:

            obj, _ = decoder.raw_decode(
                text[start:]
            )

            if isinstance(
                obj,
                dict,
            ):

                return obj

        except json.JSONDecodeError:

            continue


    raise ValueError(
        "The AI did not return a valid "
        "JSON analysis plan."
    )


# ============================================================
# VALIDATE PLAN
# ============================================================

def validate_analysis_plan(
    plan: dict,
    df: pd.DataFrame,
) -> tuple[bool, str]:

    if not isinstance(
        plan,
        dict,
    ):

        return (
            False,
            "Analysis plan must be a JSON object.",
        )


    operation = plan.get(
        "operation"
    )


    if operation not in SUPPORTED_OPERATIONS:

        return (
            False,
            f"Unsupported operation: {operation}",
        )


    column = plan.get(
        "column"
    )


    if column is not None:

        if column not in df.columns:

            return (
                False,
                f"Column '{column}' does not exist.",
            )


    group_by = plan.get(
        "group_by"
    )


    if group_by is not None:

        if group_by not in df.columns:

            return (
                False,
                f"Group column '{group_by}' does not exist.",
            )


    value_column = plan.get(
        "value_column"
    )


    if value_column is not None:

        if value_column not in df.columns:

            return (
                False,
                f"Value column '{value_column}' does not exist.",
            )


    chart = plan.get(
        "chart"
    )


    if chart not in SUPPORTED_CHARTS:

        return (
            False,
            f"Unsupported chart type: {chart}",
        )


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


    return (
        True,
        "Analysis plan is valid.",
    )


# ============================================================
# GENERATE CONTEXT-AWARE ANALYSIS PLAN
# ============================================================

def generate_analysis_plan(
    df: pd.DataFrame,
    question: str,
    conversation: list | None = None,
    last_plan: dict | None = None,
) -> dict:
    """
    Generate a context-aware analysis plan.

    Previous conversation and the previous analysis plan
    are provided so the AI can understand follow-up
    questions such as:

    "show those as a pie chart"

    or:

    "what about locations?"
    """

    schema = build_dataset_schema(
        df
    )


    # --------------------------------------------------------
    # Conversation context
    # --------------------------------------------------------

    if conversation:

        recent_conversation = (
            conversation[-6:]
        )

    else:

        recent_conversation = []


    conversation_text = (
        json.dumps(
            recent_conversation,
            indent=2,
            default=str,
        )
    )


    last_plan_text = (
        json.dumps(
            last_plan,
            indent=2,
            default=str,
        )
        if last_plan
        else "None"
    )


    # --------------------------------------------------------
    # Prompt
    # --------------------------------------------------------

    prompt = f"""
You are DataPilot AI, an expert data analyst.

Convert the user's question into ONE structured
JSON analysis plan.

You MUST use the conversation context to understand
follow-up questions.

DATASET:

{json.dumps(schema, indent=2)}

RECENT CONVERSATION:

{conversation_text}

PREVIOUS ANALYSIS PLAN:

{last_plan_text}

CURRENT USER QUESTION:

{question}

SUPPORTED OPERATIONS:

1. count
2. unique_count
3. value_counts
4. group_mean
5. group_sum
6. top_n
7. filter
8. describe

SUPPORTED CHARTS:

null
bar
line
pie
histogram
scatter

RETURN EXACTLY ONE JSON OBJECT.

JSON FORMAT:

{{
    "operation": "value_counts",
    "column": "Company",
    "group_by": null,
    "value_column": null,
    "limit": 10,
    "filter": null,
    "chart": "bar"
}}

IMPORTANT FOLLOW-UP RULES:

If the user says:

"show those as a pie chart"

"make it a bar chart"

"visualize that"

"change the chart"

then preserve the previous analysis and only
change the chart when appropriate.

If the user says:

"what about locations?"

then create a new analysis using the Location
column if it exists.

If the user says:

"show the top 5"

then preserve the previous analysis and
change the limit to 5 when appropriate.

If the user refers to "those", "that", "them",
"same", "again", or similar words, use the
previous analysis context.

RULES:

- Only use columns that exist.
- Never invent columns.
- Use null when a field is unnecessary.
- Use count for row-count questions.
- Use unique_count for unique-value questions.
- Use value_counts for frequency questions.
- Use group_mean for averages by category.
- Use group_sum for totals by category.
- Use top_n for top numerical records.
- Use bar for category comparisons.
- Use histogram for distributions.
- Use scatter for numerical relationships.
- Use line for time-series questions.
- Use null when visualization is not useful.
- limit should normally be 10.
- limit must be between 1 and 100.

DO NOT return:

- Markdown
- Python
- explanations
- multiple JSON objects
- commentary

Return ONLY one JSON object.
"""


    # --------------------------------------------------------
    # Groq request
    # --------------------------------------------------------

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a strict JSON-producing "
                    "data analysis planner. "
                    "Return exactly one valid JSON "
                    "object and nothing else."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        temperature=0,
        include_reasoning=False,
    )


    raw_response = (
        response
        .choices[0]
        .message
        .content
    )


    # --------------------------------------------------------
    # Parse JSON
    # --------------------------------------------------------

    plan = extract_json(
        raw_response
    )


    # --------------------------------------------------------
    # Validate
    # --------------------------------------------------------

    is_valid, message = (
        validate_analysis_plan(
            plan,
            df,
        )
    )


    if not is_valid:

        raise ValueError(
            message
        )


    return plan