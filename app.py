import streamlit as st
import pandas as pd

st.set_page_config(page_title="Patching Report Dashboard", layout="wide")

st.title("Patching Report Dashboard")
st.write("View, search, filter, and visualize patching report CSV data.")

uploaded_file = st.file_uploader("Upload patching report CSV", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    st.subheader("Full Report")
    st.dataframe(df, use_container_width=True)

    st.sidebar.header("Filters")

    selected_host = st.sidebar.selectbox(
        "Hostname",
        ["All"] + sorted(df["hostname"].dropna().unique().tolist())
    )

    selected_package = st.sidebar.selectbox(
        "Package",
        ["All"] + sorted(df["package_info"].dropna().unique().tolist())
    )

    filtered_df = df.copy()

    if selected_host != "All":
        filtered_df = filtered_df[filtered_df["hostname"] == selected_host]

    if selected_package != "All":
        filtered_df = filtered_df[filtered_df["package_info"] == selected_package]

    st.subheader("Filtered Results")
    st.dataframe(filtered_df, use_container_width=True)

    st.subheader("Packages Installed Per Host")
    host_counts = df.groupby("hostname")["package_info"].count()
    st.bar_chart(host_counts)

    st.subheader("Most Common Packages")
    package_counts = df["package_info"].value_counts()
    st.bar_chart(package_counts)

else:
    st.info("Upload a CSV file to begin.")
