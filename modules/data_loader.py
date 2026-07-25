from pathlib import Path

import pandas as pd


DATA_FOLDER = Path("Sales By Month")

def read_csv_safely(file_path):
    """
    Read a CSV file while handling common text encodings.
    """

    encodings = [
        "utf-8",
        "utf-8-sig",
        "latin-1",
        "cp1252",
    ]

    for encoding in encodings:
        try:
            return pd.read_csv(
                file_path,
                encoding=encoding
            )

        except UnicodeDecodeError:
            continue

        except pd.errors.ParserError as error:
            raise pd.errors.ParserError(
                f"Could not parse {file_path.name}: {error}"
            ) from error

    raise ValueError(
        f"Could not decode CSV file: {file_path.name}"
    )


def load_all_months():
    """
    Load every CSV file inside the Sales By Month folder
    and combine them into one DataFrame.
    """

    csv_files = sorted(
        DATA_FOLDER.glob("*.csv")
    )

    if not csv_files:
        raise FileNotFoundError(
            f"No CSV files were found inside: "
            f"{DATA_FOLDER.resolve()}"
        )

    dataframes = []

    for file_path in csv_files:
        print(f"Reading: {file_path.name}")

        try:
            dataframe = read_csv_safely(
                file_path
            )

        except Exception as error:
            print(
                f"Could not load "
                f"{file_path.name}"
            )
            print(f"Reason: {error}")
            raise

        dataframe["source_file"] = (
            file_path.name
        )

        dataframes.append(dataframe)

        print(
            f"Loaded: {file_path.name} "
            f"— {len(dataframe)} rows"
        )

    combined_dataframe = pd.concat(
        dataframes,
        ignore_index=True
    )

    print(
        f"\nTotal rows loaded: "
        f"{len(combined_dataframe)}"
    )

    return combined_dataframe

def clean_data(dataframe):
    """
    Standardize column names and clean important fields.
    """

    dataframe = dataframe.copy()

    dataframe.columns = (
        dataframe.columns
        .astype(str)
        .str.lower()
        .str.strip()
        .str.replace(
            " ",
            "_",
            regex=False
        )
    )

    required_columns = {
        "date",
        "model",
        "salesperson",
        "units",
        "revenue",
    }

    missing_columns = (
        required_columns
        - set(dataframe.columns)
    )

    if missing_columns:
        raise KeyError(
            "Missing required columns: "
            f"{sorted(missing_columns)}"
        )

    dataframe["date"] = pd.to_datetime(
        dataframe["date"],
        errors="coerce"
    )

    dataframe["revenue"] = (
        dataframe["revenue"]
        .astype(str)
        .str.replace(
            "$",
            "",
            regex=False
        )
        .str.replace(
            ",",
            "",
            regex=False
        )
        .str.strip()
    )

    dataframe["revenue"] = (
        pd.to_numeric(
            dataframe["revenue"],
            errors="coerce"
        )
    )

    dataframe["units"] = (
        pd.to_numeric(
            dataframe["units"],
            errors="coerce"
        )
        .fillna(1)
    )
    
    text_columns = [
        "make",
        "model",
        "color",
        "trim",
        "stock_type",
        "salesperson",
    ]

    for column in text_columns:
        if column in dataframe.columns:
            dataframe[column] = (
                dataframe[column]
                .astype(str)
                .str.strip()
            )

    invalid_dates = (
        dataframe["date"]
        .isna()
        .sum()
    )

    invalid_revenue = (
        dataframe["revenue"]
        .isna()
        .sum()
    )

    print(
        f"\nInvalid dates: "
        f"{invalid_dates}"
    )

    print(
        f"Invalid revenue values: "
        f"{invalid_revenue}"
    )

    dataframe = dataframe.dropna(
        subset=[
            "date",
            "revenue",
        ]
    )

    return dataframe

def classify_powertrain(model):
    """
    Classify a Lexus model as Gas, Hybrid, Plug-in Hybrid, or EV.
    """

    model_name = str(model).lower()

    if model_name.startswith("rz"):
        return "EV"
    
    if "h+" in model_name:
        return "Plug-in Hybrid"
    
    if (
        model_name.endswith("h")
        or "500h" in model_name
        or "550h" in model_name
        or "300h" in model_name
    ):
        return "Hybrid"
    
    return "Gas"

def transform_data(dataframe):
    """
    Create helper columns used for analysis,
    filters, and reports.
    """

    dataframe = dataframe.copy()

    dataframe["month"] = (
        dataframe["date"]
        .dt.month_name()
    )

    dataframe["month_number"] = (
        dataframe["date"]
        .dt.month
    )

    dataframe["weekday"] = (
        dataframe["date"]
        .dt.day_name()
    )

    dataframe["year_number"] = (
        dataframe["date"]
        .dt.year
    )

    dataframe["powertrain"] = (
        dataframe["model"]
        .apply(classify_powertrain)
    )

    return dataframe