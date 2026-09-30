import streamlit as st
import pandas as pd
import json
import os
import plotly.express as px
from datetime import date

# -----------------------------
# Page Configuration
# -----------------------------
st.set_page_config(
    page_title="Expense Tracker",
    page_icon="💰",
    layout="wide"
)

FILE_NAME = "expenses.json"


# -----------------------------
# JSON File Functions
# -----------------------------
def load_expenses():
    if not os.path.exists(FILE_NAME):
        return []

    try:
        with open(FILE_NAME, "r") as file:
            return json.load(file)
    except:
        return []


def save_expenses(expenses):
    with open(FILE_NAME, "w") as file:
        json.dump(expenses, file, indent=4)


# -----------------------------
# Session State
# -----------------------------
if "expenses" not in st.session_state:
    st.session_state.expenses = load_expenses()

if "edit_id" not in st.session_state:
    st.session_state.edit_id = None


# -----------------------------
# Title
# -----------------------------
st.title("💰 Expense Tracker")
st.write("Track, manage and visualize your daily expenses.")

st.divider()


# -----------------------------
# Sidebar - Add Expense
# -----------------------------
st.sidebar.header("➕ Add Expense")

expense_date = st.sidebar.date_input(
    "Date",
    value=date.today()
)

category = st.sidebar.selectbox(
    "Category",
    [
        "Food",
        "Travel",
        "Shopping",
        "Education",
        "Entertainment",
        "Bills",
        "Health",
        "Other"
    ]
)

description = st.sidebar.text_input("Description")

amount = st.sidebar.number_input(
    "Amount (₹)",
    min_value=0.0,
    step=10.0
)


if st.sidebar.button("Add Expense", use_container_width=True):

    if description.strip() == "":
        st.sidebar.error("Please enter a description.")

    elif amount <= 0:
        st.sidebar.error("Amount must be greater than 0.")

    else:
        new_id = 1

        if st.session_state.expenses:
            new_id = max(
                expense["id"]
                for expense in st.session_state.expenses
            ) + 1

        new_expense = {
            "id": new_id,
            "date": str(expense_date),
            "category": category,
            "description": description,
            "amount": amount
        }

        st.session_state.expenses.append(new_expense)

        save_expenses(st.session_state.expenses)

        st.sidebar.success("Expense added successfully!")
        st.rerun()


# -----------------------------
# Convert Data to DataFrame
# -----------------------------
if st.session_state.expenses:

    df = pd.DataFrame(st.session_state.expenses)

    df["date"] = pd.to_datetime(df["date"])

else:

    df = pd.DataFrame(
        columns=[
            "id",
            "date",
            "category",
            "description",
            "amount"
        ]
    )


# -----------------------------
# Summary
# -----------------------------
st.subheader("📊 Expense Summary")

col1, col2, col3 = st.columns(3)

total_expense = df["amount"].sum() if not df.empty else 0
number_expenses = len(df)

average_expense = (
    df["amount"].mean()
    if not df.empty
    else 0
)

col1.metric(
    "Total Expense",
    f"₹{total_expense:,.2f}"
)

col2.metric(
    "Number of Expenses",
    number_expenses
)

col3.metric(
    "Average Expense",
    f"₹{average_expense:,.2f}"
)


st.divider()


# -----------------------------
# Expense Records
# -----------------------------
st.subheader("📋 Expense Records")

if df.empty:

    st.info("No expenses added yet.")

else:

    display_df = df.copy()

    display_df["date"] = display_df["date"].dt.strftime(
        "%Y-%m-%d"
    )

    display_df["amount"] = display_df["amount"].apply(
        lambda x: f"₹{x:,.2f}"
    )

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )


# -----------------------------
# Update / Delete
# -----------------------------
if st.session_state.expenses:

    st.divider()

    st.subheader("✏️ Update or Delete Expense")

    expense_ids = [
        expense["id"]
        for expense in st.session_state.expenses
    ]

    selected_id = st.selectbox(
        "Select Expense ID",
        expense_ids
    )

    selected_expense = next(
        expense
        for expense in st.session_state.expenses
        if expense["id"] == selected_id
    )

    col1, col2 = st.columns(2)

    # UPDATE
    with col1:

        st.write("### Update Expense")

        new_date = st.date_input(
            "Date",
            value=pd.to_datetime(
                selected_expense["date"]
            ).date(),
            key="update_date"
        )

        new_category = st.selectbox(
            "Category",
            [
                "Food",
                "Travel",
                "Shopping",
                "Education",
                "Entertainment",
                "Bills",
                "Health",
                "Other"
            ],
            index=[
                "Food",
                "Travel",
                "Shopping",
                "Education",
                "Entertainment",
                "Bills",
                "Health",
                "Other"
            ].index(selected_expense["category"]),
            key="update_category"
        )

        new_description = st.text_input(
            "Description",
            value=selected_expense["description"],
            key="update_description"
        )

        new_amount = st.number_input(
            "Amount",
            min_value=0.0,
            value=float(selected_expense["amount"]),
            step=10.0,
            key="update_amount"
        )

        if st.button(
            "Update Expense",
            use_container_width=True
        ):

            selected_expense["date"] = str(new_date)
            selected_expense["category"] = new_category
            selected_expense["description"] = new_description
            selected_expense["amount"] = new_amount

            save_expenses(st.session_state.expenses)

            st.success("Expense updated successfully!")
            st.rerun()

    # DELETE
    with col2:

        st.write("### Delete Expense")

        st.warning(
            f"Selected Expense ID: {selected_id}"
        )

        if st.button(
            "🗑️ Delete Expense",
            use_container_width=True
        ):

            st.session_state.expenses = [
                expense
                for expense in st.session_state.expenses
                if expense["id"] != selected_id
            ]

            save_expenses(st.session_state.expenses)

            st.success("Expense deleted successfully!")
            st.rerun()


# -----------------------------
# Filters
# -----------------------------
if not df.empty:

    st.divider()

    st.subheader("🔎 Filter Expenses")

    col1, col2 = st.columns(2)

    with col1:

        filter_category = st.multiselect(
            "Select Category",
            df["category"].unique()
        )

    with col2:

        filter_date = st.date_input(
            "Select Date Range",
            value=(
                df["date"].min().date(),
                df["date"].max().date()
            )
        )

    filtered_df = df.copy()

    if filter_category:

        filtered_df = filtered_df[
            filtered_df["category"].isin(
                filter_category
            )
        ]

    if len(filter_date) == 2:

        start_date = pd.Timestamp(filter_date[0])
        end_date = pd.Timestamp(filter_date[1])

        filtered_df = filtered_df[
            (filtered_df["date"] >= start_date)
            &
            (filtered_df["date"] <= end_date)
        ]

    st.write(
        f"Filtered expenses: {len(filtered_df)}"
    )


# -----------------------------
# Charts
# -----------------------------
if not df.empty:

    st.divider()

    st.subheader("📈 Expense Visualizations")

    col1, col2 = st.columns(2)

    # Category Chart
    with col1:

        category_data = (
            df.groupby("category")["amount"]
            .sum()
            .reset_index()
        )

        fig_category = px.pie(
            category_data,
            names="category",
            values="amount",
            title="Expenses by Category"
        )

        st.plotly_chart(
            fig_category,
            use_container_width=True
        )

    # Daily Chart
    with col2:

        daily_data = (
            df.groupby("date")["amount"]
            .sum()
            .reset_index()
        )

        fig_daily = px.bar(
            daily_data,
            x="date",
            y="amount",
            title="Daily Expenses"
        )

        st.plotly_chart(
            fig_daily,
            use_container_width=True
        )

    # Monthly Chart
    monthly_data = df.copy()

    monthly_data["month"] = (
        monthly_data["date"]
        .dt.to_period("M")
        .astype(str)
    )

    monthly_data = (
        monthly_data
        .groupby("month")["amount"]
        .sum()
        .reset_index()
    )

    fig_monthly = px.line(
        monthly_data,
        x="month",
        y="amount",
        markers=True,
        title="Monthly Expense Trend"
    )

    st.plotly_chart(
        fig_monthly,
        use_container_width=True
    )