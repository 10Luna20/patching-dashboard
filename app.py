import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Patching Report Dashboard", layout="wide")

st.title("Patching Report Dashboard")

st.write("Upload a patching CSV file to view, search, filter, and visualize patch data.")

uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])

if uploaded_file:
    # Read CSV with no headers because your file format looks custom
    df = pd.read_csv(uploaded_file, header=None)

    # Rename columns based on expected format
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

    # Create readable installed date column
    df["installed_date"] = (
        df["day_of_week"].astype(str) + " " +
        df["month"].astype(str) + " " +
        df["day"].astype(str) + " " +
        df["year"].astype(str) + " " +
        df["time"].astype(str) + " " +
        df["am_pm"].astype(str)
    )

    # Try to split package_info into useful parts
    # Example: package-version.OS.architecture
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

    filtered_df = df.copy()

    if hostname_filter:
        filtered_df = filtered_df[filtered_df["hostname"].isin(hostname_filter)]

    if package_filter:
        filtered_df = filtered_df[filtered_df["package_name"].isin(package_filter)]

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
    st.info("Please upload a CSV file to begin.")
