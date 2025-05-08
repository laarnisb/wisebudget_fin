#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import streamlit as st

# Initialize session state flags
if 'exploration_done' not in st.session_state:
    st.session_state.exploration_done = False
if 'cleaning_done' not in st.session_state:
    st.session_state.cleaning_done = False
if 'modeling_done' not in st.session_state:
    st.session_state.modeling_done = False
import pandas as pd
import numpy as np
import requests
from io import StringIO

st.title("WiseBudget: Personal Finance Dashboard")

# File upload
st.header("1. Upload Your Financial Data")
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.success("File uploaded successfully!")

# URL input
st.header("2. Load Data from URL")
url = st.text_input("Enter the URL of a CSV file")
if url:
    try:
        response = requests.get(url)
        df = pd.read_csv(StringIO(response.text))
        st.success("Data loaded from URL successfully!")
    except Exception as e:
        st.error(f"Failed to load data from URL: {e}")

# Data exploration
if 'df' in locals():
    st.header("3. Data Exploration")
    st.write("Preview of Data:")
    st.dataframe(df.head())

    st.write("Summary Statistics:")
    st.write(df.describe())

    # Data visualization
    st.header("4. Data Visualization")
    if 'Category' in df.columns and 'Amount' in df.columns:
        category_totals = df.groupby('Category')['Amount'].sum().reset_index()
        st.bar_chart(category_totals.set_index('Category'))
    else:
        st.warning("Columns 'Category' and 'Amount' are required for visualization.")

    # Data cleaning options
    st.header("5. Data Cleaning Options")
    if df.isnull().values.any():
        st.write("Missing values detected.")
        if st.button("Drop rows with missing values"):
            df = df.dropna()
            st.success("Missing values dropped.")
    else:
        st.write("No missing values detected.")
else:
    st.info("Please upload a file or enter a URL to proceed.")



# -------------------------
# 6. Choose an Analysis Type (Only after data is uploaded)
# -------------------------
if 'df' in locals() and df is not None:
    st.header("6. Choose an Analysis Type")
    analysis_type = st.selectbox("Select analysis method", ["None", "Spending Summary", "Top Categories", "Clustering"])

    if analysis_type == "Spending Summary":
        st.subheader("Spending Summary by Category")
        st.write(df.groupby('Category')['Amount'].sum())

    elif analysis_type == "Top Categories":
        st.subheader("Top N Spending Categories")
        top_n = st.slider("Top N Categories", 1, 10, 5)
        top_categories = df.groupby('Category')['Amount'].sum().nlargest(top_n)
        st.bar_chart(top_categories)

    elif analysis_type == "Clustering":
        st.subheader("Spending Clustering (KMeans)")
        from sklearn.cluster import KMeans
        if 'Amount' in df.columns:
            kmeans = KMeans(n_clusters=3, n_init=10)
            df['Cluster'] = kmeans.fit_predict(df[['Amount']])
            st.write(df[['Amount', 'Cluster']])
else:
    st.info("Please upload a dataset first to access analysis options.")

# -------------------------
# 7. Generate and Download CSV Report
# -------------------------
import base64

if 'df' in locals() and df is not None:
    st.header("7. Download Processed Data")
    if st.button("Generate CSV Report"):
        csv = df.to_csv(index=False)
        b64 = base64.b64encode(csv.encode()).decode()
        href = f'<a href="data:file/csv;base64,{b64}" download="WiseBudget_Report.csv">Download CSV File</a>'
        st.markdown(href, unsafe_allow_html=True)

# -------------------------
# 8. Help Section
# -------------------------
st.sidebar.header("Need Help?")
with st.sidebar.expander("Help Guide"):
    st.markdown("""
    **Steps to Use WiseBudget:**
    1. Upload a CSV or enter a data URL
    2. View stats and explore charts
    3. Select an analysis method
    4. Clean missing data
    5. Generate and download a report
    """)


# -------------------------
# 9. Execution Mode Selection (Full vs Step-by-Step)
# -------------------------

# Step 9: Conditional display
if df is not None and st.session_state.exploration_done and st.session_state.cleaning_done and st.session_state.modeling_done:
    st.header("9. Pipeline Execution Mode")
    # User selects between a full automatic run or a manual step-by-step pipeline
    execution_mode = st.radio("Choose execution mode", ["Full Automatic Run", "Manual Step-by-Step"], index=0)
# Advanced Options Toggle
show_advanced = st.checkbox("Show Advanced Options")

# If full run selected, simulate running each stage of the OSEMN pipeline
if execution_mode == "Full Automatic Run":
    st.success("Running full pipeline...")
    if show_advanced:
        st.write("Advanced logging enabled...")
    # Simulate each step briefly
    st.write("Obtaining data... ✅")
    st.write("Scrubbing data... ✅")
    st.write("Exploring data... ✅")
    st.write("Modeling data... ✅")
    st.write("Interpreting data... ✅")
    st.info("Pipeline executed successfully.")
else:
    st.warning("Manual mode selected. Please step through each section manually using the UI above.")

# -------------------------
# 10. Keyword Search in Description
# -------------------------
if 'df' in locals() and df is not None and 'Description' in df.columns:
    st.header("10. Search Transactions by Description")
# User enters keyword to search for transaction descriptions
    keyword = st.text_input("Enter keyword to search for in descriptions")
    if keyword:
# Filter the dataframe for rows containing the keyword in the 'Description' column
        filtered_df = df[df['Description'].str.contains(keyword, case=False, na=False)]
        st.write(f"Filtered results for '{keyword}':", filtered_df)
