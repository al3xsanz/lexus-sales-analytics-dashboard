import pandas as pd
import plotly.express as px
import streamlit as st

from modules.database import (
    create_indexes,
    get_filter_options,
    get_index_information,
    get_matching_record_count,
    get_model_rankings,
    get_model_summary,
    get_monthly_summary,
    get_monthly_window_analytics,
    get_powertrain_summary,
    get_salesperson_rankings,
    get_salesperson_summary,
    load_sales_data,
)

st.set_page_config(
    page_title="Lexus Sales Analytics",
    page_icon="🚗",
    layout="wide",
)

def apply_custom_theme():
    """
    Apply Lexus-inspired styling to the Streamlit dashboard.
    """
    st.markdown(
        """
        <style>
        .stApp {
            background:
                linear-gradient(
                    135deg,
                    #0b0d10 0%,
                    #12151a 55%,
                    #0b0d10 100%
                );
        }

        .block-container {
            max-width: 1450px;
            padding-top: 2rem;
            padding-bottom: 3rem;
        }

        .dashboard-title {
            font-size: 2.65rem;
            font-weight: 700;
            letter-spacing: -0.04rem;
            margin-bottom: 0.2rem;
            color: #ffffff;
        }

        .dashboard-subtitle {
            font-size: 1.05rem;
            color: #b2b5ba;
            margin-bottom: 0.35rem;
        }

        .dashboard-author {
            font-size: 0.9rem;
            color: #7f848c;
            margin-bottom: 1.5rem;
        }

        .section-kicker {
            color: #8f949c;
            font-size: 0.78rem;
            font-weight: 700;
            letter-spacing: 0.1rem;
            text-transform: uppercase;
            margin-bottom: -0.35rem;
        }

        h2, h3 {
            color: #f5f5f5;
            letter-spacing: -0.02rem;
        }

        .kpi-card {
            min-height: 160px;
            padding: 1.35rem 1.4rem;
            border-radius: 14px;
            background:
                linear-gradient(
                    145deg,
                    rgba(34, 38, 45, 0.98),
                    rgba(19, 22, 27, 0.98)
                );
            border: 1px solid rgba(195, 198, 203, 0.18);
            box-shadow: 0 8px 22px rgba(0, 0, 0, 0.28);
            transition:
                transform 0.18s ease,
                border-color 0.18s ease;
        }

        .kpi-card:hover {
            transform: translateY(-3px);
            border-color: rgba(220, 222, 225, 0.42);
        }

        .kpi-icon {
            font-size: 1.35rem;
            margin-bottom: 0.55rem;
        }

        .kpi-label {
            color: #aeb2b8;
            font-size: 0.8rem;
            font-weight: 700;
            letter-spacing: 0.06rem;
            text-transform: uppercase;
            margin-bottom: 0.5rem;
        }

        .kpi-value {
            color: #ffffff;
            font-size: 1.75rem;
            font-weight: 700;
            line-height: 1.15;
            margin-bottom: 0.55rem;
        }

        .kpi-positive {
            color: #78d8a0;
            font-size: 0.82rem;
            font-weight: 600;
        }

        .kpi-negative {
            color: #ff9696;
            font-size: 0.82rem;
            font-weight: 600;
        }

        .kpi-neutral {
            color: #a7a9ac;
            font-size: 0.82rem;
            font-weight: 500;
        }



        .leader-card {
            min-height: 145px;
            padding: 1.2rem 1.3rem;
            border-radius: 14px;
            background: linear-gradient(
                145deg,
                rgba(31, 35, 42, 0.98),
                rgba(17, 20, 25, 0.98)
            );
            border: 1px solid rgba(210, 213, 218, 0.18);
            box-shadow: 0 7px 20px rgba(0, 0, 0, 0.24);
        }

        .leader-rank {
            color: #8f949c;
            font-size: 0.76rem;
            font-weight: 700;
            letter-spacing: 0.08rem;
            text-transform: uppercase;
            margin-bottom: 0.5rem;
        }

        .leader-name {
            color: #ffffff;
            font-size: 1.25rem;
            font-weight: 700;
            line-height: 1.25;
            margin-bottom: 0.45rem;
        }

        .leader-detail {
            color: #b6bac1;
            font-size: 0.86rem;
        }

        .summary-card {
            padding: 1rem 1.1rem;
            border-radius: 12px;
            background: rgba(25, 29, 35, 0.92);
            border: 1px solid rgba(190, 193, 198, 0.14);
        }

        .summary-label {
            color: #9499a1;
            font-size: 0.78rem;
            text-transform: uppercase;
            letter-spacing: 0.05rem;
            font-weight: 700;
        }

        .summary-value {
            color: #ffffff;
            font-size: 1.2rem;
            font-weight: 700;
            margin-top: 0.25rem;
        }

        section[data-testid="stSidebar"] {
            background:
                linear-gradient(
                    180deg,
                    #12151a 0%,
                    #0c0e12 100%
                );
            border-right: 1px solid rgba(180, 183, 188, 0.14);
        }

        section[data-testid="stSidebar"] h1,
        section[data-testid="stSidebar"] h2,
        section[data-testid="stSidebar"] h3 {
            color: #ffffff;
        }

        div[data-baseweb="select"] > div,
        div[data-baseweb="input"] > div {
            border-radius: 9px;
        }

        div[data-testid="stDataFrame"] {
            border: 1px solid rgba(180, 183, 188, 0.18);
            border-radius: 12px;
            overflow: hidden;
        }

        div.stDownloadButton > button {
            border-radius: 9px;
            border: 1px solid #a7a9ac;
            font-weight: 600;
            padding: 0.55rem 1.1rem;
        }

        div.stDownloadButton > button:hover {
            border-color: #ffffff;
            color: #ffffff;
        }

        hr {
            border-color: rgba(180, 183, 188, 0.15);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


@st.cache_data



def calculate_percentage_change(current_value, previous_value):
    """
    Calculate percentage change between two values.

    Return None when a valid comparison cannot be calculated.
    """
    if previous_value is None or previous_value == 0:
        return None

    return ((current_value - previous_value) / previous_value) * 100


def format_kpi_change(change, comparison_text):
    """
    Return formatted HTML for a KPI comparison.
    """
    if change is None:
        return (
            '<div class="kpi-neutral">'
            f"{comparison_text}"
            "</div>"
        )

    if change > 0:
        return (
            '<div class="kpi-positive">'
            f"▲ {change:.1f}% {comparison_text}"
            "</div>"
        )

    if change < 0:
        return (
            '<div class="kpi-negative">'
            f"▼ {abs(change):.1f}% {comparison_text}"
            "</div>"
        )

    return (
        '<div class="kpi-neutral">'
        f"— 0.0% {comparison_text}"
        "</div>"
    )


def render_kpi_card(icon, label, value, supporting_html):
    """
    Render one custom KPI card.
    """
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-icon">{icon}</div>
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            {supporting_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def display_kpi_cards(dataframe):
    """
    Display custom executive KPI cards with monthly comparisons.
    """
    if dataframe.empty:
        st.warning("No sales records match the selected filters.")
        return

    total_units = dataframe["units"].sum()
    total_revenue = dataframe["revenue"].sum()
    average_revenue = dataframe["revenue"].mean()

    monthly_summary = (
        dataframe.groupby(
            ["month_number", "month"],
            as_index=False,
        )
        .agg(
            units=("units", "sum"),
            revenue=("revenue", "sum"),
        )
        .sort_values("month_number")
    )

    best_month_row = monthly_summary.loc[
        monthly_summary["units"].idxmax()
    ]

    best_month = best_month_row["month"]
    best_month_units = best_month_row["units"]

    latest_month = monthly_summary.iloc[-1]
    previous_month = monthly_summary.iloc[-2] if len(monthly_summary) >= 2 else None

    unit_change = None
    revenue_change = None

    if previous_month is not None:
        unit_change = calculate_percentage_change(
            latest_month["units"],
            previous_month["units"],
        )

        revenue_change = calculate_percentage_change(
            latest_month["revenue"],
            previous_month["revenue"],
        )

    unit_support = format_kpi_change(
        unit_change,
        "vs previous month",
    )

    revenue_support = format_kpi_change(
        revenue_change,
        "vs previous month",
    )

    average_support = (
        '<div class="kpi-neutral">'
        "Average gross per sales record"
        "</div>"
    )

    best_month_support = (
        '<div class="kpi-positive">'
        f"{best_month_units:,.0f} units sold"
        "</div>"
    )

    column1, column2, column3, column4 = st.columns(4)

    with column1:
        render_kpi_card(
            icon="🚗",
            label="Units Sold",
            value=f"{total_units:,.0f}",
            supporting_html=unit_support,
        )

    with column2:
        render_kpi_card(
            icon="💵",
            label="Gross Revenue",
            value=f"${total_revenue:,.0f}",
            supporting_html=revenue_support,
        )

    with column3:
        render_kpi_card(
            icon="📊",
            label="Average Gross",
            value=f"${average_revenue:,.2f}",
            supporting_html=average_support,
        )

    with column4:
        render_kpi_card(
            icon="🏆",
            label="Best Sales Month",
            value=str(best_month),
            supporting_html=best_month_support,
        )


def display_summary_row(dataframe):
    """
    Display compact dataset statistics below the KPI cards.
    """
    statistics = [
        ("Months Loaded", dataframe["month"].nunique()),
        ("Models Sold", dataframe["model"].nunique()),
        ("Salespeople", dataframe["salesperson"].nunique()),
        ("Powertrains", dataframe["powertrain"].nunique()),
    ]

    columns = st.columns(len(statistics))

    for column, (label, value) in zip(columns, statistics):
        with column:
            st.markdown(
                f"""
                <div class="summary-card">
                    <div class="summary-label">{label}</div>
                    <div class="summary-value">{value:,}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )



def sidebar_filters():
    """
    Create cascading sidebar filters using SQLite queries.
    """
    st.sidebar.title("🚗 Lexus")
    st.sidebar.caption("Sales Analytics Dashboard")
    st.sidebar.divider()
    st.sidebar.markdown("### Filters")

    filters = {}

    month_options = get_filter_options("month")
    filters["month"] = st.sidebar.selectbox(
        "Month",
        ["All"] + month_options,
    )

    model_options = get_filter_options(
        "model",
        filters={"month": filters["month"]},
    )
    filters["model"] = st.sidebar.selectbox(
        "Model",
        ["All"] + model_options,
    )

    powertrain_options = get_filter_options(
        "powertrain",
        filters={
            "month": filters["month"],
            "model": filters["model"],
        },
    )
    filters["powertrain"] = st.sidebar.selectbox(
        "Powertrain",
        ["All"] + powertrain_options,
    )

    salesperson_options = get_filter_options(
        "salesperson",
        filters={
            "month": filters["month"],
            "model": filters["model"],
            "powertrain": filters["powertrain"],
        },
    )
    filters["salesperson"] = st.sidebar.selectbox(
        "Salesperson",
        ["All"] + salesperson_options,
    )

    return filters





def sort_records(dataframe):
    """
    Display sorting controls and sort the Sales Explorer records.
    """
    if dataframe.empty:
        return dataframe

    sort_options = {
        "Date": "date",
        "Revenue": "revenue",
        "Model": "model",
        "Salesperson": "salesperson",
        "Units": "units",
        "Color": "color",
        "Trim": "trim",
    }

    available_options = {
        label: column
        for label, column in sort_options.items()
        if column in dataframe.columns
    }

    control_column1, control_column2 = st.columns([3, 1])

    with control_column1:
        selected_label = st.selectbox(
            "Sort By",
            list(available_options.keys()),
        )

    with control_column2:
        sort_direction = st.selectbox(
            "Direction",
            ["Descending", "Ascending"],
        )

    sort_column = available_options[selected_label]
    ascending = sort_direction == "Ascending"

    return dataframe.sort_values(
        by=sort_column,
        ascending=ascending,
        na_position="last",
    )

def display_executive_insights(dataframe):
    """
    Display executive scorecards for the selected sales data.
    """
    if dataframe.empty:
        return

    monthly_summary = (
        dataframe.groupby(
            ["month_number", "month"],
            as_index=False,
        )
        .agg(
            units=("units", "sum"),
            revenue=("revenue", "sum"),
        )
        .sort_values("month_number")
    )

    model_summary = (
        dataframe.groupby("model", as_index=False)
        .agg(
            units=("units", "sum"),
            revenue=("revenue", "sum"),
        )
        .sort_values("units", ascending=False)
    )

    salesperson_summary = (
        dataframe.groupby("salesperson", as_index=False)
        .agg(
            units=("units", "sum"),
            revenue=("revenue", "sum"),
        )
        .sort_values("units", ascending=False)
    )

    powertrain_summary = (
        dataframe.groupby("powertrain", as_index=False)
        .agg(
            units=("units", "sum"),
        )
        .sort_values("units", ascending=False)
    )

    best_month = monthly_summary.loc[
        monthly_summary["revenue"].idxmax()
    ]

    top_model = model_summary.iloc[0]
    top_salesperson = salesperson_summary.iloc[0]
    top_powertrain = powertrain_summary.iloc[0]

    total_units = dataframe["units"].sum()

    powertrain_share = (
        top_powertrain["units"] / total_units * 100
        if total_units
        else 0
    )

    scorecards = [
        (
            "🚗",
            "Best-Selling Model",
            top_model["model"],
            f"{top_model['units']:,.0f} units sold",
        ),
        (
            "👤",
            "Top Performer",
            top_salesperson["salesperson"],
            f"{top_salesperson['units']:,.0f} units sold",
        ),
        (
            "💰",
            "Highest Revenue Month",
            best_month["month"],
            f"${best_month['revenue']:,.0f} gross revenue",
        ),
        (
            "⚡",
            "Leading Powertrain",
            top_powertrain["powertrain"],
            f"{powertrain_share:.1f}% of unit sales",
        ),
    ]

    columns = st.columns(4)

    for column, (icon, label, value, detail) in zip(
        columns,
        scorecards,
    ):
        with column:
            st.markdown(
                f"""
                <div class="leader-card">
                    <div class="kpi-icon">{icon}</div>
                    <div class="leader-rank">{label}</div>
                    <div class="leader-name">{value}</div>
                    <div class="leader-detail">{detail}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

def display_performance_leaders(dataframe):
    """
    Display ranked sales leaders and concentration statistics.
    """
    if dataframe.empty:
        return

    salesperson_summary = (
        dataframe.groupby("salesperson", as_index=False)
        .agg(
            units=("units", "sum"),
            revenue=("revenue", "sum"),
        )
    )

    model_summary = (
        dataframe.groupby("model", as_index=False)
        .agg(
            units=("units", "sum"),
            revenue=("revenue", "sum"),
        )
    )

    powertrain_summary = (
        dataframe.groupby("powertrain", as_index=False)
        .agg(units=("units", "sum"))
        .sort_values("units", ascending=False)
    )

    top_salesperson_units = salesperson_summary.loc[
        salesperson_summary["units"].idxmax()
    ]
    top_salesperson_revenue = salesperson_summary.loc[
        salesperson_summary["revenue"].idxmax()
    ]
    top_model_units = model_summary.loc[model_summary["units"].idxmax()]
    top_model_revenue = model_summary.loc[model_summary["revenue"].idxmax()]

    total_units = dataframe["units"].sum()
    top_three_model_units = (
        model_summary.nlargest(3, "units")["units"].sum()
    )
    concentration = (
        top_three_model_units / total_units * 100
        if total_units
        else 0
    )

    leaders = [
        (
            "Top Salesperson · Units",
            top_salesperson_units["salesperson"],
            f"{top_salesperson_units['units']:,.0f} vehicles sold",
        ),
        (
            "Top Salesperson · Gross",
            top_salesperson_revenue["salesperson"],
            f"${top_salesperson_revenue['revenue']:,.0f} gross revenue",
        ),
        (
            "Top Model · Units",
            top_model_units["model"],
            f"{top_model_units['units']:,.0f} vehicles sold",
        ),
        (
            "Top Model · Gross",
            top_model_revenue["model"],
            f"${top_model_revenue['revenue']:,.0f} gross revenue",
        ),
    ]

    columns = st.columns(4)

    for column, (rank, name, detail) in zip(columns, leaders):
        with column:
            st.markdown(
                f"""
                <div class="leader-card">
                    <div class="leader-rank">{rank}</div>
                    <div class="leader-name">{name}</div>
                    <div class="leader-detail">{detail}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.write("")

    chart_column1, chart_column2 = st.columns(2)

    top_salespeople = salesperson_summary.nlargest(5, "units").sort_values(
        "units"
    )
    top_models = model_summary.nlargest(5, "units").sort_values("units")

    with chart_column1:
        salesperson_chart = px.bar(
            top_salespeople,
            x="units",
            y="salesperson",
            orientation="h",
            title="Top 5 Salespeople",
            labels={
                "units": "Units Sold",
                "salesperson": "Salesperson",
            },
            text_auto=True,
            hover_data={"revenue": ":$,.2f"},
        )
        salesperson_chart.update_layout(showlegend=False)
        st.plotly_chart(salesperson_chart, width="stretch")

    with chart_column2:
        model_chart = px.bar(
            top_models,
            x="units",
            y="model",
            orientation="h",
            title="Top 5 Models",
            labels={
                "units": "Units Sold",
                "model": "Model",
            },
            text_auto=True,
            hover_data={"revenue": ":$,.2f"},
        )
        model_chart.update_layout(showlegend=False)
        st.plotly_chart(model_chart, width="stretch")

    leading_powertrain = powertrain_summary.iloc[0]
    powertrain_share = (
        leading_powertrain["units"] / total_units * 100
        if total_units
        else 0
    )

    st.caption(
        f"Top-three model concentration: {concentration:.1f}% of units. "
        f"Leading powertrain: {leading_powertrain['powertrain']} "
        f"({powertrain_share:.1f}% of units)."
    )

def display_model_drilldown(dataframe):
    """
    Display detailed performance information for one selected model.
    """
    if dataframe.empty:
        return

    model_options = sorted(
        dataframe["model"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    if not model_options:
        st.warning("No models are available for detailed analysis.")
        return

    selected_model = st.selectbox(
        "Select a model to analyze",
        model_options,
        key="model_detail_selector",
    )

    model_data = dataframe[
        dataframe["model"].astype(str) == selected_model
    ].copy()

    if model_data.empty:
        st.warning("No records were found for the selected model.")
        return

    total_units = model_data["units"].sum()
    total_revenue = model_data["revenue"].sum()

    average_gross = (
        model_data["revenue"].sum() / model_data["units"].sum()
        if model_data["units"].sum()
        else 0
    )

    salesperson_count = model_data["salesperson"].nunique()

    st.markdown(
        f"### {selected_model} Performance Overview"
    )

    metric_column1, metric_column2, metric_column3, metric_column4 = (
        st.columns(4)
    )

    with metric_column1:
        render_kpi_card(
            icon="🚗",
            label="Model Units",
            value=f"{total_units:,.0f}",
            supporting_html=(
                '<div class="kpi-neutral">'
                "Total units sold"
                "</div>"
            ),
        )

    with metric_column2:
        render_kpi_card(
            icon="💵",
            label="Model Gross",
            value=f"${total_revenue:,.0f}",
            supporting_html=(
                '<div class="kpi-neutral">'
                "Total gross revenue"
                "</div>"
            ),
        )

    with metric_column3:
        render_kpi_card(
            icon="📊",
            label="Average Gross",
            value=f"${average_gross:,.2f}",
            supporting_html=(
                '<div class="kpi-neutral">'
                "Average gross per unit"
                "</div>"
            ),
        )

    with metric_column4:
        render_kpi_card(
            icon="👥",
            label="Sales Team",
            value=f"{salesperson_count:,}",
            supporting_html=(
                '<div class="kpi-neutral">'
                "Salespeople with deliveries"
                "</div>"
            ),
        )

    st.write("")

    monthly_model_summary = (
        model_data.groupby(
            ["month_number", "month"],
            as_index=False,
        )
        .agg(
            units=("units", "sum"),
            revenue=("revenue", "sum"),
        )
        .sort_values("month_number")
    )

    salesperson_model_summary = (
        model_data.groupby("salesperson", as_index=False)
        .agg(
            units=("units", "sum"),
            revenue=("revenue", "sum"),
        )
        .sort_values("units", ascending=False)
        .head(10)
    )

    chart_column1, chart_column2 = st.columns(2)

    with chart_column1:
        monthly_chart = px.line(
            monthly_model_summary,
            x="month",
            y="units",
            markers=True,
            title=f"{selected_model} Monthly Sales",
            labels={
                "month": "Month",
                "units": "Units Sold",
            },
            hover_data={
                "revenue": ":$,.2f",
            },
        )

        monthly_chart.update_layout(
            title_x=0.05,
            showlegend=False,
        )

        st.plotly_chart(
            monthly_chart,
            width="stretch",
        )

    with chart_column2:
        salesperson_chart = px.bar(
            salesperson_model_summary.sort_values("units"),
            x="units",
            y="salesperson",
            orientation="h",
            title=f"Top Salespeople for {selected_model}",
            labels={
                "units": "Units Sold",
                "salesperson": "Salesperson",
            },
            text_auto=True,
            hover_data={
                "revenue": ":$,.2f",
            },
        )

        salesperson_chart.update_layout(
            title_x=0.05,
            showlegend=False,
        )

        st.plotly_chart(
            salesperson_chart,
            width="stretch",
        )

    breakdown_column1, breakdown_column2 = st.columns(2)

    if "color" in model_data.columns:
        color_summary = (
            model_data.groupby("color", as_index=False)
            .agg(units=("units", "sum"))
            .sort_values("units", ascending=False)
            .head(10)
        )

        with breakdown_column1:
            color_chart = px.bar(
                color_summary.sort_values("units"),
                x="units",
                y="color",
                orientation="h",
                title=f"Top Colors for {selected_model}",
                labels={
                    "units": "Units Sold",
                    "color": "Color",
                },
                text_auto=True,
            )

            color_chart.update_layout(
                title_x=0.05,
                showlegend=False,
            )

            st.plotly_chart(
                color_chart,
                width="stretch",
            )

    if "trim" in model_data.columns:
        trim_summary = (
            model_data.groupby("trim", as_index=False)
            .agg(units=("units", "sum"))
            .sort_values("units", ascending=False)
            .head(10)
        )

        with breakdown_column2:
            trim_chart = px.bar(
                trim_summary.sort_values("units"),
                x="units",
                y="trim",
                orientation="h",
                title=f"Top Trims for {selected_model}",
                labels={
                    "units": "Units Sold",
                    "trim": "Trim",
                },
                text_auto=True,
            )

            trim_chart.update_layout(
                title_x=0.05,
                showlegend=False,
            )

            st.plotly_chart(
                trim_chart,
                width="stretch",
            )

    with st.expander(
        f"View {selected_model} sales records"
    ):
        model_records = model_data.copy()

        if "date" in model_records.columns:
            model_records["date"] = (
                pd.to_datetime(
                    model_records["date"],
                    errors="coerce",
                )
                .dt.strftime("%m/%d/%Y")
            )

        st.dataframe(
            model_records,
            width="stretch",
            hide_index=True,
        )


def display_monthly_trends(filters):
    """
    Display monthly units and revenue charts using SQL aggregation.
    """
    monthly_summary = get_monthly_summary(filters)

    if monthly_summary.empty:
        return

    chart_column1, chart_column2 = st.columns(2)

    with chart_column1:
        units_chart = px.bar(
            monthly_summary,
            x="month",
            y="units",
            title="Units Sold by Month",
            labels={
                "month": "Month",
                "units": "Units Sold",
            },
            text_auto=True,
            hover_data={
                "revenue": ":$,.2f",
                "average_revenue": ":$,.2f",
            },
        )

        units_chart.update_layout(
            title_x=0.05,
            showlegend=False,
        )

        st.plotly_chart(
            units_chart,
            width="stretch",
        )

    with chart_column2:
        revenue_chart = px.line(
            monthly_summary,
            x="month",
            y="revenue",
            title="Gross Revenue by Month",
            labels={
                "month": "Month",
                "revenue": "Gross Revenue",
            },
            markers=True,
            hover_data={
                "units": ":,.0f",
                "average_revenue": ":$,.2f",
            },
        )

        revenue_chart.update_layout(
            title_x=0.05,
            yaxis_tickprefix="$",
            yaxis_tickformat=",",
        )

        st.plotly_chart(
            revenue_chart,
            width="stretch",
        )



def display_sales_breakdowns(filters):
    """
    Display model, salesperson, and powertrain charts using SQL aggregation.
    """
    model_summary = get_model_summary(filters, limit=10)
    salesperson_summary = get_salesperson_summary(filters, limit=10)
    powertrain_summary = get_powertrain_summary(filters)

    if (
        model_summary.empty
        and salesperson_summary.empty
        and powertrain_summary.empty
    ):
        return

    chart_column1, chart_column2 = st.columns(2)

    with chart_column1:
        model_chart = px.bar(
            model_summary,
            x="units",
            y="model",
            orientation="h",
            title="Top 10 Models by Units Sold",
            labels={
                "units": "Units Sold",
                "model": "Model",
            },
            text_auto=True,
            hover_data={
                "revenue": ":$,.2f",
            },
        )

        model_chart.update_layout(
            yaxis={
                "categoryorder": "total ascending",
            },
            showlegend=False,
        )

        st.plotly_chart(
            model_chart,
            width="stretch",
        )

    with chart_column2:
        salesperson_chart = px.bar(
            salesperson_summary,
            x="units",
            y="salesperson",
            orientation="h",
            title="Top 10 Salespeople by Units Sold",
            labels={
                "units": "Units Sold",
                "salesperson": "Salesperson",
            },
            text_auto=True,
            hover_data={
                "revenue": ":$,.2f",
            },
        )

        salesperson_chart.update_layout(
            yaxis={
                "categoryorder": "total ascending",
            },
            showlegend=False,
        )

        st.plotly_chart(
            salesperson_chart,
            width="stretch",
        )

    st.markdown("### Powertrain Mix")

    powertrain_chart = px.pie(
        powertrain_summary,
        names="powertrain",
        values="units",
        hole=0.45,
        title="Vehicle Sales by Powertrain",
    )

    powertrain_chart.update_traces(
        textposition="inside",
        textinfo="percent+label",
    )

    st.plotly_chart(
        powertrain_chart,
        width="stretch",
    )


def display_sales_table(dataframe):
    """
    Display the searchable and sortable sales records table.
    """
    if dataframe.empty:
        st.warning("No sales records are available to display.")
        return

    sorted_dataframe = sort_records(dataframe)
    display_dataframe = sorted_dataframe.copy()

    if "date" in display_dataframe.columns:
        display_dataframe["date"] = (
            pd.to_datetime(
                display_dataframe["date"],
                errors="coerce",
            )
            .dt.strftime("%m/%d/%Y")
        )

    st.caption(
        f"Displaying {len(display_dataframe):,} matching sales records."
    )

    st.dataframe(
        display_dataframe,
        width="stretch",
        hide_index=True,
    )


def display_download_section(dataframe):
    """
    Allow the user to download the currently filtered sales records.
    """
    if dataframe.empty:
        return

    export_dataframe = dataframe.copy()

    if "date" in export_dataframe.columns:
        export_dataframe["date"] = (
            pd.to_datetime(
                export_dataframe["date"],
                errors="coerce",
            )
            .dt.strftime("%m/%d/%Y")
        )

    csv_data = export_dataframe.to_csv(
        index=False,
    ).encode("utf-8")

    st.download_button(
        label="Download Filtered Sales CSV",
        data=csv_data,
        file_name="filtered_lexus_sales.csv",
        mime="text/csv",
    )



def display_sql_analytics(filters):
    """
    Display advanced analytics calculated with SQLite window functions.
    """
    st.markdown(
        '<div class="section-kicker">Advanced SQL</div>',
        unsafe_allow_html=True,
    )
    st.header("🧠 SQL Analytics")
    st.caption(
        "Rankings, month-over-month changes, and running totals are "
        "calculated inside SQLite using window functions."
    )

    monthly_analytics = get_monthly_window_analytics(filters)
    salesperson_rankings = get_salesperson_rankings(filters, limit=10)
    model_rankings = get_model_rankings(filters, limit=10)

    if monthly_analytics.empty:
        st.warning("No monthly analytics are available for these filters.")
        return

    latest_month = monthly_analytics.iloc[-1]

    metric_column1, metric_column2, metric_column3, metric_column4 = (
        st.columns(4)
    )

    revenue_growth = latest_month["revenue_growth_percent"]
    unit_growth = latest_month["unit_growth_percent"]

    with metric_column1:
        st.metric(
            "Latest Month",
            latest_month["month"],
        )

    with metric_column2:
        st.metric(
            "Monthly Revenue",
            f"${latest_month['revenue']:,.0f}",
            (
                f"{revenue_growth:+.1f}%"
                if pd.notna(revenue_growth)
                else None
            ),
        )

    with metric_column3:
        st.metric(
            "Monthly Units",
            f"{latest_month['units']:,.0f}",
            (
                f"{unit_growth:+.1f}%"
                if pd.notna(unit_growth)
                else None
            ),
        )

    with metric_column4:
        st.metric(
            "Cumulative Revenue",
            f"${latest_month['running_revenue']:,.0f}",
        )

    st.divider()

    chart_column1, chart_column2 = st.columns(2)

    with chart_column1:
        running_revenue_chart = px.area(
            monthly_analytics,
            x="month",
            y="running_revenue",
            title="Running Revenue Total",
            labels={
                "month": "Month",
                "running_revenue": "Cumulative Revenue",
            },
            hover_data={
                "revenue": ":$,.2f",
                "revenue_change": ":$,.2f",
                "revenue_growth_percent": ":.1f",
            },
        )
        running_revenue_chart.update_layout(
            yaxis_tickprefix="$",
            yaxis_tickformat=",",
        )
        st.plotly_chart(
            running_revenue_chart,
            width="stretch",
        )

    with chart_column2:
        growth_chart = px.bar(
            monthly_analytics.dropna(
                subset=["revenue_growth_percent"]
            ),
            x="month",
            y="revenue_growth_percent",
            title="Month-over-Month Revenue Growth",
            labels={
                "month": "Month",
                "revenue_growth_percent": "Revenue Growth (%)",
            },
            text_auto=".1f",
            hover_data={
                "revenue": ":$,.2f",
                "previous_revenue": ":$,.2f",
                "revenue_change": ":$,.2f",
            },
        )
        growth_chart.add_hline(y=0)
        st.plotly_chart(
            growth_chart,
            width="stretch",
        )

    st.divider()
    st.subheader("🏅 SQL Rankings")

    ranking_column1, ranking_column2 = st.columns(2)

    with ranking_column1:
        st.markdown("#### Salesperson Rankings")

        salesperson_chart = px.bar(
            salesperson_rankings.sort_values("unit_rank", ascending=False),
            x="units",
            y="salesperson",
            orientation="h",
            title="Ranked by Units Sold",
            labels={
                "units": "Units Sold",
                "salesperson": "Salesperson",
            },
            text="unit_rank",
            hover_data={
                "revenue": ":$,.2f",
                "unit_rank": True,
                "revenue_rank": True,
            },
        )
        st.plotly_chart(
            salesperson_chart,
            width="stretch",
        )

        st.dataframe(
            salesperson_rankings,
            width="stretch",
            hide_index=True,
            column_config={
                "revenue": st.column_config.NumberColumn(
                    "Revenue",
                    format="$%.2f",
                ),
                "unit_rank": st.column_config.NumberColumn(
                    "Unit Rank",
                    format="%d",
                ),
                "revenue_rank": st.column_config.NumberColumn(
                    "Revenue Rank",
                    format="%d",
                ),
            },
        )

    with ranking_column2:
        st.markdown("#### Model Rankings")

        model_chart = px.bar(
            model_rankings.sort_values("unit_rank", ascending=False),
            x="units",
            y="model",
            orientation="h",
            title="Ranked by Units Sold",
            labels={
                "units": "Units Sold",
                "model": "Model",
            },
            text="unit_rank",
            hover_data={
                "revenue": ":$,.2f",
                "unit_rank": True,
                "revenue_rank": True,
            },
        )
        st.plotly_chart(
            model_chart,
            width="stretch",
        )

        st.dataframe(
            model_rankings,
            width="stretch",
            hide_index=True,
            column_config={
                "revenue": st.column_config.NumberColumn(
                    "Revenue",
                    format="$%.2f",
                ),
                "unit_rank": st.column_config.NumberColumn(
                    "Unit Rank",
                    format="%d",
                ),
                "revenue_rank": st.column_config.NumberColumn(
                    "Revenue Rank",
                    format="%d",
                ),
            },
        )

    st.divider()
    st.subheader("📋 Monthly Window-Function Results")

    display_monthly = monthly_analytics.copy()

    percentage_columns = [
        "unit_growth_percent",
        "revenue_growth_percent",
    ]

    for column in percentage_columns:
        if column in display_monthly.columns:
         display_monthly[column] = (
            pd.to_numeric(
                display_monthly[column],
                errors="coerce",
            )
            .round(2)
        )

    st.dataframe(
        display_monthly,
        width="stretch",
        hide_index=True,
        column_config={
            "revenue": st.column_config.NumberColumn(
                "Revenue",
                format="$%.2f",
            ),
            "previous_revenue": st.column_config.NumberColumn(
                "Previous Revenue",
                format="$%.2f",
            ),
            "revenue_change": st.column_config.NumberColumn(
                "Revenue Change",
                format="$%.2f",
            ),
            "running_revenue": st.column_config.NumberColumn(
                "Running Revenue",
                format="$%.2f",
            ),
            "revenue_growth_percent": st.column_config.NumberColumn(
                "Revenue Growth",
                format="%.2f%%",
            ),
            "unit_growth_percent": st.column_config.NumberColumn(
                "Unit Growth",
                format="%.2f%%",
            ),
        },
    )

    st.divider()
    st.subheader("⚙️ SQLite Indexes")

    index_information = get_index_information()

    st.caption(
        "Indexes accelerate common month, model, powertrain, salesperson, "
        "and date lookups as the database grows."
    )

    st.dataframe(
        index_information,
        width="stretch",
        hide_index=True,
    )


def display_dashboard_page(dataframe, filters):
    """
    Display the original executive dashboard page.
    """
    with st.container():
        st.markdown(
            '<div class="section-kicker">Overview</div>',
            unsafe_allow_html=True,
        )
        st.header("📊 Executive KPIs")
        display_kpi_cards(dataframe)
        st.write("")
        display_summary_row(dataframe)

    st.divider()

    with st.container():
        st.markdown(
            '<div class="section-kicker">Highlights</div>',
            unsafe_allow_html=True,
        )
        st.header("💡 Executive Insights")
        display_executive_insights(dataframe)

    st.divider()

    with st.container():
        st.markdown(
            '<div class="section-kicker">Leaders</div>',
            unsafe_allow_html=True,
        )
        st.header("🏅 Performance Leaders")
        display_performance_leaders(dataframe)

    st.divider()

    with st.container():
        st.markdown(
            '<div class="section-kicker">Drill Down</div>',
            unsafe_allow_html=True,
        )
        st.header("🔎 Model Detail Dashboard")
        st.caption(
            "Select a Lexus model to examine its monthly performance, "
            "sales team, colors, trims, and individual sales records."
        )
        display_model_drilldown(dataframe)

    st.divider()

    with st.container():
        st.markdown(
            '<div class="section-kicker">Trends</div>',
            unsafe_allow_html=True,
        )
        st.header("📈 Monthly Performance")
        display_monthly_trends(filters)

    st.divider()

    with st.container():
        st.markdown(
            '<div class="section-kicker">Performance</div>',
            unsafe_allow_html=True,
        )
        st.header("🏆 Sales Breakdown")
        display_sales_breakdowns(filters)

    st.divider()

    with st.container():
        st.markdown(
            '<div class="section-kicker">Records</div>',
            unsafe_allow_html=True,
        )
        st.header("📋 Sales Explorer")
        display_sales_table(dataframe)

    st.divider()

    with st.container():
        st.markdown(
            '<div class="section-kicker">Export</div>',
            unsafe_allow_html=True,
        )
        st.header("⬇ Download Reports")
        display_download_section(dataframe)

def main():
    """
    Run the Streamlit dashboard and SQL analytics pages.
    """
    apply_custom_theme()

    try:
        create_indexes()
    except Exception as error:
        st.error("The SQLite indexes could not be created.")
        st.exception(error)
        st.stop()

    st.markdown(
        """
        <div class="dashboard-title">
            Lexus Sales Analytics
        </div>

        <div class="dashboard-subtitle">
            Executive Business Intelligence and Advanced SQL Analytics
        </div>

        <div class="dashboard-author">
            Created by Alejandro Sanz ·
            Python · SQL · SQLite · Pandas · Plotly · Streamlit
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.sidebar.markdown("### Navigation")

    selected_page = st.sidebar.radio(
        "Page",
        ["Executive Dashboard", "SQL Analytics"],
        label_visibility="collapsed",
    )

    st.sidebar.divider()

    try:
        filters = sidebar_filters()

        search_term = ""

        if selected_page == "Executive Dashboard":
            search_term = st.text_input(
                "🔍 Search Sales Records",
                placeholder=(
                    "Search model, salesperson, color, trim..."
                ),
            )

        dataframe = load_sales_data(
            filters=filters,
            search_term=search_term,
        )

        matching_records = get_matching_record_count(
            filters=filters,
            search_term=search_term,
        )

        st.sidebar.divider()
        st.sidebar.metric(
            "Matching Records",
            f"{matching_records:,}",
        )

    except Exception as error:
        st.error("The dashboard could not load the sales data.")
        st.exception(error)
        st.stop()

    if dataframe.empty:
        st.warning(
            "No sales records match the current filters or search."
        )
        st.stop()

    st.divider()

    if selected_page == "Executive Dashboard":
        display_dashboard_page(dataframe, filters)
    else:
        display_sql_analytics(filters)

    st.divider()

    st.caption(
        "Created by Alejandro Sanz • 2026 • "
        "Python | SQL | SQLite | Pandas | Plotly | Streamlit"
    )


if __name__ == "__main__":
    main()