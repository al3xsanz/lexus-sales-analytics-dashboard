from pathlib import Path
import sqlite3

import pandas as pd

from modules.data_loader import (
    clean_data,
    load_all_months,
    transform_data,
)


PROJECT_FOLDER = Path(__file__).resolve().parent
DATABASE_FILE = PROJECT_FOLDER / "lexus_sales.db"


def create_sales_database():
    """
    Load all monthly CSV files, clean the data,
    and save the finished dataset to SQLite.
    """
    print("Loading monthly CSV files...")

    dataframe = load_all_months()
    dataframe = clean_data(dataframe)
    dataframe = transform_data(dataframe)

    if dataframe.empty:
        raise ValueError(
            "The transformed sales dataset is empty."
        )

    # SQLite stores dates safely as ISO-formatted text.
    if "date" in dataframe.columns:
        dataframe["date"] = (
            pd.to_datetime(
                dataframe["date"],
                errors="coerce",
            )
            .dt.strftime("%Y-%m-%d")
        )

    print(
        f"Writing {len(dataframe):,} records "
        f"to {DATABASE_FILE.name}..."
    )

    with sqlite3.connect(DATABASE_FILE) as connection:
        dataframe.to_sql(
            name="sales",
            con=connection,
            if_exists="replace",
            index=False,
        )

        create_database_indexes(
            connection,
            dataframe.columns,
        )

        record_count = connection.execute(
            """
            SELECT COUNT(*)
            FROM sales
            """
        ).fetchone()[0]

        month_count = connection.execute(
            """
            SELECT COUNT(DISTINCT month)
            FROM sales
            """
        ).fetchone()[0]

    print("")
    print("Database created successfully.")
    print(f"Database: {DATABASE_FILE}")
    print(f"Sales records: {record_count:,}")
    print(f"Months loaded: {month_count:,}")


def create_database_indexes(connection, columns):
    """
    Create indexes for columns commonly used by dashboard filters.
    """
    index_columns = [
        "date",
        "month",
        "model",
        "salesperson",
        "powertrain",
    ]

    available_columns = set(columns)

    for column in index_columns:
        if column not in available_columns:
            continue

        connection.execute(
            f"""
            CREATE INDEX IF NOT EXISTS
            idx_sales_{column}
            ON sales ({column})
            """
        )

    connection.commit()


if __name__ == "__main__":
    create_sales_database()