import pandas as pd
from pathlib import Path


SUPPORTED_EXTENSIONS = {".csv", ".xlsx", ".xls"}


def load_dataset(file) -> pd.DataFrame:
    """
    Load a CSV or Excel file into a pandas DataFrame.
    """

    file_extension = Path(file.name).suffix.lower()

    if file_extension not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"Unsupported file type: {file_extension}. "
            f"Supported formats: CSV, XLSX, XLS."
        )

    if file_extension == ".csv":
        return pd.read_csv(file)

    return pd.read_excel(file)


def validate_dataset(df: pd.DataFrame) -> None:
    """
    Validate that the uploaded dataset contains usable data.
    """

    if df.empty:
        raise ValueError("The uploaded dataset is empty.")

    if len(df.columns) == 0:
        raise ValueError("The dataset contains no columns.")# CSV / Excel loading utilities
