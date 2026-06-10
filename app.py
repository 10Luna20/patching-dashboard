import streamlit as st
import pandas as pd

st.set_page_config(page_title="Patching Report Dashboard", layout="wide")

st.title("Patching Report Dashboard")

uploaded_file = st.file_uploader("Upload a patching report CSV", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
else:
    df = pd.read_csv("mock_patching_report.csv")

# Rename ALL column to package_info if needed
if "ALL" in df.columns and "package_info" not in df.columns:
    df = df.rename(columns={"ALL": "package_info"})

# Show available columns for debugging
st.write("CSV columns found:", df.columns.tolist())

st.subheader("Full Patching Report")
st.dataframe(df, use_container_width=True)

# Stop if required columns are missing
required_columns = ["hostname", "package_info"]

missing_columns = [col for col in required_columns if col not in df.columns]

if missing_columns:
    st.error(f"Missing required columns: {missing_columns}")
    st.stop()

st.subheader("Filters")

col1, col2 = st.columns(2)

with col1:
    selected_hostname = st.selectbox(
        "Filter by hostname",
        ["All"] + sorted(df["hostname"].dropna().unique().tolist())
    )

with col2:
    selected_package = st.selectbox(
        "Filter by package",
        ["All"] + sorted(df["package_info"].dropna().unique().tolist())
    )

filtered_df = df.copy()

if selected_hostname != "All":
    filtered_df = filtered_df[filtered_df["hostname"] == selected_hostname]

if selected_package != "All":
    filtered_df = filtered_df[filtered_df["package_info"] == selected_package]

st.subheader("Filtered Results")
st.dataframe(filtered_df, use_container_width=True)

st.subheader("Packages Installed Per Host")
host_counts = df.groupby("hostname")["package_info"].count()
st.bar_chart(host_counts)

st.subheader("Most Common Installed Packages")
package_counts = df["package_info"].value_counts()
st.bar_chart(package_counts)

st.subheader("Summary")

col1, col2, col3 = st.columns(3)

col1.metric("Total Patch Records", len(df))
col2.metric("Total Hostnames", df["hostname"].nunique())
col3.metric("Unique Packages", df["package_info"].nunique())
