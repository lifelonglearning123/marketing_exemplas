import streamlit as st
import pandas as pd
import requests
import os

# Function to get the company status from Companies House API
def get_company_status(company_number):
    api_key = "eb7007ef-7b53-414c-9d07-b9cef8224a68"
    url = f"https://api.company-information.service.gov.uk/company/{company_number}"
    response = requests.get(url, auth=(api_key, ''))
    if response.status_code == 200:
        data = response.json()
        # You might need to adjust the key depending on the structure of the response
        status = data.get('company_status', 'Status not found')
        return status
    else:
        return "Failed to fetch data"

# Streamlit app
def main():
    st.title("Company Trading Status Checker")
    
    # File uploader
    uploaded_file = st.file_uploader("Upload an Excel file with company numbers", type='xlsx')
    if uploaded_file:
        # Read Excel file
        df = pd.read_excel(uploaded_file)

        # Check if 'company house reg' column exists
        if 'company house reg' in df.columns:
            # Process each company number
            df['Status'] = df['company house reg'].apply(get_company_status)
            st.write(df)
        else:
            st.error("Excel file does not contain 'company house reg' column.")

if __name__ == "__main__":
    main()
