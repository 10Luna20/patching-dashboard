import streamlit as st
import pandas as pd
import plotly.express as px
import zipfile

st.set_page_config(page_title="Patching Report Dashboard", layout="wide")

st.title("Patching Report Dashboard")

st.write("Upload CSV files individually or upload a ZIP folder containing CSV files.")

uploaded_files = st.file_uploader(
    "Upload CSV file(s) or a ZIP folder",
    type=["csv", "zip"],
    accept_multiple_files=True
)

expected_columns = [
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

all_data = []

if uploaded_files:
    for uploaded_file in uploaded_files:

        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file, header=None)
            df.columns = expected_columns
            df["source_file"] = uploaded_file.name
            all_data.append(df)

        elif uploaded_file.name.endswith(".zip"):
            with zipfile.ZipFile(uploaded_file) as z:
                csv_files = [
                    file for file in z.namelist()
                    if file.endswith(".csv") and not file.startswith("__MACOSX")
                ]

                for csv_file in csv_files:
                    with z.open(csv_file) as f:
                        df = pd.read_csv(f, header=None)
                        df.columns = expected_columns
                        df["source_file"] = csv_file
                        all_data.append(df)

    if all_data:
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
        st.warning("No CSV files were found.")

else:
    st.info("Please upload CSV files or a ZIP folder to begin.")
