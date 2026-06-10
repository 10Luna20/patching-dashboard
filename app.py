import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Patching Report Dashboard", layout="wide")

st.title("Patching Report Dashboard")

st.write("Upload one or more patching CSV files to view, search, filter, and visualize patch data.")

uploaded_files = st.file_uploader(
    "Upload CSV file(s)",
    type=["csv"],
    accept_multiple_files=True
)

if uploaded_files:
    all_data = []

    for uploaded_file in uploaded_files:
        df = pd.read_csv(uploaded_file, header=None)

        df.columns = [
            "hostname",
            "package_info",
            "day_of_week",
            "day",
            "month",
            "year",
            "time",
            "am_pm",
            "timezone"
        ]

        df["source_file"] = uploaded_file.name

        all_data.append(df)

    df = pd.concat(all_data, ignore_index=True)

    df["installed_date"] = (
        df["day_of_week"].astype(str) + " " +
        df["month"].astype(str) + " " +
        df["day"].astype(str) + " " +
        df["year"].astype(str) + " " +
        df["time"].astype(str) + " " +
        df["am_pm"].astype(str)
    )

    df["package_name"] = df["package_info"].astype(str).str.split("-").str[0]
    df["package_version"] = df["package_info"].astype(str).str.split("-").str[1]

    st.subheader("Raw Data Preview")
    st.dataframe(df, use_container_width=True)

    st.sidebar.header("Filters")

    hostname_filter = st.sidebar.multiselect(
        "Filter by hostname",
        options=sorted(df["hostname"].dropna().unique())
    )

    package_filter = st.sidebar.multiselect(
        "Filter by package",
        options=sorted(df["package_name"].dropna().unique())
    )

    file_filter = st.sidebar.multiselect(
        "Filter by source file",
        options=sorted(df["source_file"].dropna().unique())
    )

    filtered_df = df.copy()

    if hostname_filter:
        filtered_df = filtered_df[filtered_df["hostname"].isin(hostname_filter)]

    if package_filter:
        filtered_df = filtered_df[filtered_df["package_name"].isin(package_filter)]

    if file_filter:
        filtered_df = filtered_df[filtered_df["source_file"].isin(file_filter)]

    st.subheader("Filtered Results")
    st.dataframe(filtered_df, use_container_width=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Patch Records", len(filtered_df))

    with col2:
        st.metric("Unique Systems", filtered_df["hostname"].nunique())

    with col3:
        st.metric("Unique Packages", filtered_df["package_name"].nunique())

    st.subheader("Patches per System")

    patches_per_host = (
        filtered_df.groupby("hostname")
        .size()
        .reset_index(name="patch_count")
        .sort_values(by="patch_count", ascending=False)
    )

    fig1 = px.bar(
        patches_per_host,
        x="hostname",
        y="patch_count",
        title="Number of Patch Records per System"
    )

    st.plotly_chart(fig1, use_container_width=True)

    st.subheader("Most Common Packages")

    common_packages = (
        filtered_df.groupby("package_name")
        .size()
        .reset_index(name="count")
        .sort_values(by="count", ascending=False)
        .head(20)
    )

    fig2 = px.bar(
        common_packages,
        x="count",
        y="package_name",
        orientation="h",
        title="Top 20 Most Common Packages"
    )

    st.plotly_chart(fig2, use_container_width=True)

else:
    st.info("Please upload one or more CSV files to begin.")
