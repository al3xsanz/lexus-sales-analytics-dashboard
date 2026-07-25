import pandas as pd


def analyze_months(dataframe):
    """
    Calculate monthly units, revenue,
    average revenue, and month-over-month growth.
    """

    monthly_sales = (
        dataframe.groupby(
            ["month_number", "month"],
            as_index=False
        )
        .agg(
            units=("units", "sum"),
            revenue=("revenue", "sum"),
            average_revenue=("revenue", "mean")
        )
        .sort_values("month_number")
    )

    monthly_sales["revenue"] = (
        monthly_sales["revenue"]
        .round(2)
    )

    monthly_sales["average_revenue"] = (
        monthly_sales["average_revenue"]
        .round(2)
    )

    monthly_sales["unit_growth_pct"] = (
        monthly_sales["units"]
        .pct_change()
        .mul(100)
        .round(2)
    )

    monthly_sales["revenue_growth_pct"] = (
        monthly_sales["revenue"]
        .pct_change()
        .mul(100)
        .round(2)
    )

    return monthly_sales


def analyze_models(dataframe):
    """
    Calculate performance by Lexus model.
    """

    model_sales = (
        dataframe.groupby("model")
        .agg(
            units=("units", "sum"),
            revenue=("revenue", "sum"),
            average_revenue=("revenue", "mean")
        )
        .sort_values(
            "revenue",
            ascending=False
        )
    )

    model_sales["revenue"] = (
        model_sales["revenue"]
        .round(2)
    )

    model_sales["average_revenue"] = (
        model_sales["average_revenue"]
        .round(2)
    )

    return model_sales


def analyze_salespeople(dataframe):
    """
    Calculate salesperson performance.
    """

    salesperson_sales = (
        dataframe.groupby("salesperson")
        .agg(
            units=("units", "sum"),
            revenue=("revenue", "sum"),
            average_revenue=("revenue", "mean")
        )
        .sort_values(
            "revenue",
            ascending=False
        )
    )

    salesperson_sales["revenue"] = (
        salesperson_sales["revenue"]
        .round(2)
    )

    salesperson_sales["average_revenue"] = (
        salesperson_sales["average_revenue"]
        .round(2)
    )

    return salesperson_sales


def analyze_weekdays(dataframe):
    """
    Calculate sales performance by weekday.
    """

    weekday_order = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]

    weekday_sales = (
        dataframe.groupby("weekday")
        .agg(
            units=("units", "sum"),
            revenue=("revenue", "sum"),
            average_revenue=("revenue", "mean")
        )
        .reindex(weekday_order)
    )

    weekday_sales["revenue"] = (
        weekday_sales["revenue"]
        .round(2)
    )

    weekday_sales["average_revenue"] = (
        weekday_sales["average_revenue"]
        .round(2)
    )

    return weekday_sales


def get_executive_summary(
    dataframe,
    monthly_sales,
    model_sales,
    salesperson_sales,
    weekday_sales
):
    """
    Calculate the main dealership KPIs
    and return them as a dictionary.
    """

    total_units = dataframe["units"].sum()
    total_revenue = dataframe["revenue"].sum()
    average_revenue = dataframe["revenue"].mean()

    best_month_by_units = monthly_sales.loc[
        monthly_sales["units"].idxmax()
    ]

    best_month_by_revenue = monthly_sales.loc[
        monthly_sales["revenue"].idxmax()
    ]

    model_units_ranked = (
        model_sales
        .sort_values(
            "units",
            ascending=False
        )
    )

    top_model_name = (
        model_units_ranked.index[0]
    )

    top_model_data = (
        model_units_ranked.iloc[0]
    )

    top_salesperson_name = (
        salesperson_sales.index[0]
    )

    top_salesperson_data = (
        salesperson_sales.iloc[0]
    )

    weekday_revenue_ranked = (
        weekday_sales
        .sort_values(
            "revenue",
            ascending=False
        )
    )

    best_weekday_name = (
        weekday_revenue_ranked.index[0]
    )

    best_weekday_data = (
        weekday_revenue_ranked.iloc[0]
    )

    summary = {
        "total_units": int(total_units),
        "total_revenue": round(
            total_revenue,
            2
        ),
        "average_revenue": round(
            average_revenue,
            2
        ),
        "best_month_by_units": (
            best_month_by_units["month"]
        ),
        "best_month_units": int(
            best_month_by_units["units"]
        ),
        "best_month_by_revenue": (
            best_month_by_revenue["month"]
        ),
        "best_month_revenue": round(
            best_month_by_revenue["revenue"],
            2
        ),
        "top_model": top_model_name,
        "top_model_units": int(
            top_model_data["units"]
        ),
        "top_salesperson": (
            top_salesperson_name
        ),
        "top_salesperson_revenue": round(
            top_salesperson_data["revenue"],
            2
        ),
        "best_weekday": (
            best_weekday_name
        ),
        "best_weekday_revenue": round(
            best_weekday_data["revenue"],
            2
        ),
    }

    return summary


def display_executive_summary(
    dataframe,
    monthly_sales,
    model_sales,
    salesperson_sales,
    weekday_sales
):
    """
    Display the main dealership KPIs
    in a formatted terminal report.
    """

    summary = get_executive_summary(
        dataframe,
        monthly_sales,
        model_sales,
        salesperson_sales,
        weekday_sales
    )

    print("\n" + "=" * 60)
    print("              EXECUTIVE SALES SUMMARY")
    print("=" * 60)

    print(
        f"Total units sold:             "
        f"{summary['total_units']:,}"
    )

    print(
        f"Total revenue:                "
        f"${summary['total_revenue']:,.2f}"
    )

    print(
        f"Average revenue per vehicle:  "
        f"${summary['average_revenue']:,.2f}"
    )

    print(
        f"Best month by units:          "
        f"{summary['best_month_by_units']} "
        f"({summary['best_month_units']:,} units)"
    )

    print(
        f"Best month by revenue:        "
        f"{summary['best_month_by_revenue']} "
        f"(${summary['best_month_revenue']:,.2f})"
    )

    print(
        f"Best-selling model:           "
        f"{summary['top_model']} "
        f"({summary['top_model_units']:,} units)"
    )

    print(
        f"Top salesperson by revenue:   "
        f"{summary['top_salesperson']} "
        f"(${summary['top_salesperson_revenue']:,.2f})"
    )

    print(
        f"Best weekday by revenue:      "
        f"{summary['best_weekday']} "
        f"(${summary['best_weekday_revenue']:,.2f})"
    )

    print("=" * 60)