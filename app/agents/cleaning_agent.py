# AI-assisted data cleaning agent
import json

from app.core.groq_client import client


def generate_cleaning_recommendations(
    report: dict,
) -> str:
    """
    Ask the LLM to interpret the data-quality report
    and recommend appropriate cleaning actions.
    """

    missing_values = report["missing_values"]

    if not missing_values.empty:
        missing_data = missing_values.to_dict(
            orient="records"
        )
    else:
        missing_data = []

    outliers = report["outliers"]

    if not outliers.empty:
        outlier_data = outliers.to_dict(
            orient="records"
        )
    else:
        outlier_data = []

    cleaning_context = {
        "missing_values": missing_data,
        "duplicate_rows": report["duplicate_rows"],
        "outliers": outlier_data,
    }

    prompt = f"""
You are a professional data quality analyst.

Analyze this dataset quality report:

{json.dumps(cleaning_context, indent=2)}

Provide concise recommendations for cleaning the dataset.

For each issue:
1. Identify the problem.
2. Explain why it matters.
3. Recommend a safe action.

Do not invent problems that are not present.

Do not directly modify the dataset.

Return the answer in clear Markdown.
"""

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an expert data quality "
                    "and data cleaning assistant."
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

    return response.choices[0].message.content