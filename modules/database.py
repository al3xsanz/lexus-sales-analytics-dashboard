from pathlib import Path
import sqlite3

import pandas as pd


DATABASE_FILE = (
    Path(__file__).resolve().parent.parent
    / "lexus_sales.db"
)


def get_connection():
    """
    Open a connection to the Lexus SQLite database.
    """
    if not DATABASE_FILE.exists():
        raise FileNotFoundError(
            f"Database not found: {DATABASE_FILE}\n"
            "Run: python create_database.py"
        )

    return sqlite3.connect(DATABASE_FILE)


def build_where_clause(
    month="All",
    model="All",
    powertrain="All",
    salesperson="All",
    search_term="",
):
    """
    Build a parameterized SQL WHERE clause.
    """
    conditions = []
    parameters = []

    filter_values = {
        "month": month,
        "model": model,
        "powertrain": powertrain,
        "salesperson": salesperson,
    }

    for column, value in filter_values.items():
        if value not in (None, "", "All"):
            conditions.append(f"{column} = ?")
            parameters.append(value)

    if search_term and search_term.strip():
        search_value = f"%{search_term.strip()}%"

        conditions.append(
            """
            (
                model LIKE ?
                OR trim LIKE ?
                OR color LIKE ?
                OR salesperson LIKE ?
                OR powertrain LIKE ?
                OR stock_type LIKE ?
            )
            """
        )
        parameters.extend([search_value] * 6)

    if not conditions:
        return "", parameters

    return "WHERE " + " AND ".join(conditions), parameters


def _filters_to_where(filters=None, search_term=""):
    """
    Convert a filter dictionary into a SQL WHERE clause.
    """
    filters = filters or {}

    return build_where_clause(
        month=filters.get("month", "All"),
        model=filters.get("model", "All"),
        powertrain=filters.get("powertrain", "All"),
        salesperson=filters.get("salesperson", "All"),
        search_term=search_term,
    )


def get_filter_options(column, filters=None):
    """
    Retrieve distinct cascading filter values from SQLite.
    """
    allowed_columns = {
        "month",
        "model",
        "powertrain",
        "salesperson",
    }

    if column not in allowed_columns:
        raise ValueError(
            f"Unsupported filter column: {column}"
        )

    where_clause, parameters = _filters_to_where(filters)
    null_condition = f"{column} IS NOT NULL"

    if where_clause:
        filter_clause = f"{where_clause} AND {null_condition}"
    else:
        filter_clause = f"WHERE {null_condition}"

    if column == "month":
        query = f"""
            SELECT
                month,
                MIN(month_number) AS month_number
            FROM sales
            {filter_clause}
            GROUP BY month
            ORDER BY month_number
        """
    else:
        query = f"""
            SELECT DISTINCT {column}
            FROM sales
            {filter_clause}
            ORDER BY {column}
        """

    with get_connection() as connection:
        result = pd.read_sql_query(
            query,
            connection,
            params=parameters,
        )

    return result[column].astype(str).tolist()


def load_sales_data(filters=None, search_term=""):
    """
    Load only the sales records matching the SQL filters.
    """
    where_clause, parameters = _filters_to_where(
        filters,
        search_term,
    )

    query = f"""
        SELECT *
        FROM sales
        {where_clause}
        ORDER BY date
    """

    with get_connection() as connection:
        dataframe = pd.read_sql_query(
            query,
            connection,
            params=parameters,
        )

    if "date" in dataframe.columns:
        dataframe["date"] = pd.to_datetime(
            dataframe["date"],
            errors="coerce",
        )

    return dataframe


def get_matching_record_count(filters=None, search_term=""):
    """
    Count matching records without loading the rows.
    """
    where_clause, parameters = _filters_to_where(
        filters,
        search_term,
    )

    query = f"""
        SELECT COUNT(*) AS record_count
        FROM sales
        {where_clause}
    """

    with get_connection() as connection:
        result = pd.read_sql_query(
            query,
            connection,
            params=parameters,
        )

    return int(result.loc[0, "record_count"])


def get_monthly_summary(filters=None):
    """
    Aggregate monthly sales with SQL GROUP BY.
    """
    where_clause, parameters = _filters_to_where(filters)

    query = f"""
        SELECT
            month_number,
            month,
            SUM(units) AS units,
            SUM(revenue) AS revenue,
            CASE
                WHEN SUM(units) = 0 THEN 0
                ELSE SUM(revenue) / SUM(units)
            END AS average_revenue
        FROM sales
        {where_clause}
        GROUP BY month_number, month
        ORDER BY month_number
    """

    with get_connection() as connection:
        return pd.read_sql_query(
            query,
            connection,
            params=parameters,
        )


def get_model_summary(filters=None, limit=10):
    """
    Aggregate model performance with SQL GROUP BY.
    """
    where_clause, parameters = _filters_to_where(filters)

    query = f"""
        SELECT
            model,
            SUM(units) AS units,
            SUM(revenue) AS revenue
        FROM sales
        {where_clause}
        GROUP BY model
        ORDER BY units DESC, revenue DESC
        LIMIT ?
    """

    parameters.append(int(limit))

    with get_connection() as connection:
        return pd.read_sql_query(
            query,
            connection,
            params=parameters,
        )


def get_salesperson_summary(filters=None, limit=10):
    """
    Aggregate salesperson performance with SQL GROUP BY.
    """
    where_clause, parameters = _filters_to_where(filters)

    query = f"""
        SELECT
            salesperson,
            SUM(units) AS units,
            SUM(revenue) AS revenue
        FROM sales
        {where_clause}
        GROUP BY salesperson
        ORDER BY units DESC, revenue DESC
        LIMIT ?
    """

    parameters.append(int(limit))

    with get_connection() as connection:
        return pd.read_sql_query(
            query,
            connection,
            params=parameters,
        )


def get_powertrain_summary(filters=None):
    """
    Aggregate powertrain performance with SQL GROUP BY.
    """
    where_clause, parameters = _filters_to_where(filters)

    query = f"""
        SELECT
            powertrain,
            SUM(units) AS units,
            SUM(revenue) AS revenue
        FROM sales
        {where_clause}
        GROUP BY powertrain
        ORDER BY units DESC, revenue DESC
    """

    with get_connection() as connection:
        return pd.read_sql_query(
            query,
            connection,
            params=parameters,
        )

def create_indexes():
    """
    Create indexes used by common dashboard filters and sorting.
    """
    statements = [
        """
        CREATE INDEX IF NOT EXISTS idx_sales_month
        ON sales(month)
        """,
        """
        CREATE INDEX IF NOT EXISTS idx_sales_month_number
        ON sales(month_number)
        """,
        """
        CREATE INDEX IF NOT EXISTS idx_sales_model
        ON sales(model)
        """,
        """
        CREATE INDEX IF NOT EXISTS idx_sales_powertrain
        ON sales(powertrain)
        """,
        """
        CREATE INDEX IF NOT EXISTS idx_sales_salesperson
        ON sales(salesperson)
        """,
        """
        CREATE INDEX IF NOT EXISTS idx_sales_date
        ON sales(date)
        """,
        """
        CREATE INDEX IF NOT EXISTS idx_sales_month_model
        ON sales(month, model)
        """,
    ]

    with get_connection() as connection:
        for statement in statements:
            connection.execute(statement)

        connection.commit()


def get_index_information():
    """
    Return metadata for indexes created on the sales table.
    """
    query = """
        SELECT
            name AS index_name,
            tbl_name AS table_name,
            sql AS definition
        FROM sqlite_master
        WHERE type = 'index'
          AND tbl_name = 'sales'
          AND name NOT LIKE 'sqlite_autoindex%'
        ORDER BY name
    """

    with get_connection() as connection:
        return pd.read_sql_query(query, connection)


def get_monthly_window_analytics(filters=None):
    """
    Calculate LAG values, growth rates, and running totals in SQLite.
    """
    where_clause, parameters = _filters_to_where(filters)

    query = f"""
        WITH monthly_sales AS (
            SELECT
                month_number,
                month,
                SUM(units) AS units,
                SUM(revenue) AS revenue
            FROM sales
            {where_clause}
            GROUP BY month_number, month
        ),
        lagged_sales AS (
            SELECT
                month_number,
                month,
                units,
                revenue,
                LAG(units) OVER (
                    ORDER BY month_number
                ) AS previous_units,
                LAG(revenue) OVER (
                    ORDER BY month_number
                ) AS previous_revenue,
                SUM(units) OVER (
                    ORDER BY month_number
                    ROWS BETWEEN UNBOUNDED PRECEDING
                    AND CURRENT ROW
                ) AS running_units,
                SUM(revenue) OVER (
                    ORDER BY month_number
                    ROWS BETWEEN UNBOUNDED PRECEDING
                    AND CURRENT ROW
                ) AS running_revenue
            FROM monthly_sales
        )
        SELECT
            month_number,
            month,
            units,
            revenue,
            previous_units,
            previous_revenue,
            units - previous_units AS unit_change,
            revenue - previous_revenue AS revenue_change,
            CASE
                WHEN previous_units IS NULL
                     OR previous_units = 0
                THEN NULL
                ELSE
                    (units - previous_units)
                    * 100.0 / previous_units
            END AS unit_growth_percent,
            CASE
                WHEN previous_revenue IS NULL
                     OR previous_revenue = 0
                THEN NULL
                ELSE
                    (revenue - previous_revenue)
                    * 100.0 / ABS(previous_revenue)
            END AS revenue_growth_percent,
            running_units,
            running_revenue
        FROM lagged_sales
        ORDER BY month_number
    """

    with get_connection() as connection:
        return pd.read_sql_query(
            query,
            connection,
            params=parameters,
        )


def get_salesperson_rankings(filters=None, limit=10):
    """
    Rank salespeople by units and revenue with SQL window functions.
    """
    where_clause, parameters = _filters_to_where(filters)

    query = f"""
        WITH salesperson_totals AS (
            SELECT
                salesperson,
                SUM(units) AS units,
                SUM(revenue) AS revenue
            FROM sales
            {where_clause}
            GROUP BY salesperson
        ),
        ranked_salespeople AS (
            SELECT
                salesperson,
                units,
                revenue,
                RANK() OVER (
                    ORDER BY units DESC
                ) AS unit_rank,
                RANK() OVER (
                    ORDER BY revenue DESC
                ) AS revenue_rank
            FROM salesperson_totals
        )
        SELECT *
        FROM ranked_salespeople
        ORDER BY unit_rank, revenue_rank, salesperson
        LIMIT ?
    """

    parameters.append(int(limit))

    with get_connection() as connection:
        return pd.read_sql_query(
            query,
            connection,
            params=parameters,
        )


def get_model_rankings(filters=None, limit=10):
    """
    Rank models by units and revenue with SQL window functions.
    """
    where_clause, parameters = _filters_to_where(filters)

    query = f"""
        WITH model_totals AS (
            SELECT
                model,
                SUM(units) AS units,
                SUM(revenue) AS revenue
            FROM sales
            {where_clause}
            GROUP BY model
        ),
        ranked_models AS (
            SELECT
                model,
                units,
                revenue,
                RANK() OVER (
                    ORDER BY units DESC
                ) AS unit_rank,
                RANK() OVER (
                    ORDER BY revenue DESC
                ) AS revenue_rank
            FROM model_totals
        )
        SELECT *
        FROM ranked_models
        ORDER BY unit_rank, revenue_rank, model
        LIMIT ?
    """

    parameters.append(int(limit))

    with get_connection() as connection:
        return pd.read_sql_query(
            query,
            connection,
            params=parameters,
        )
