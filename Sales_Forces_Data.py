import streamlit as st
import requests
import base64
import pandas as pd
import time
from io import BytesIO

class RateLimitedAPI:
    def __init__(self, api_key, max_requests=499, cooldown=300):
        self.api_key = api_key
        self.max_requests = max_requests
        self.cooldown = cooldown
        self.request_count = 0

    def get_encoded_api_key(self):
        api_key_bytes = self.api_key.encode('ascii')
        base64_bytes = base64.b64encode(api_key_bytes)
        return base64_bytes.decode('ascii')

    def make_request(self, url, params=None):
        if self.request_count >= self.max_requests:
            print(f"Rate limit reached. Cooling down for {self.cooldown} seconds.")
            time.sleep(self.cooldown)
            self.request_count = 0

        headers = {"Authorization": f"Basic {self.get_encoded_api_key()}"}
        response = requests.get(url, headers=headers, params=params)
        self.request_count += 1
        return response

    def search_company(self, company_name):
        search_url = "https://api.company-information.service.gov.uk/search/companies"
        params = {"q": company_name}
        response = self.make_request(search_url, params)
        if response.status_code == 200:
            companies = response.json().get('items', [])
            if companies:
                return companies[0]['company_number']
            else:
                return "Not Found"
        else:
            return "Error: " + response.reason

def process_excel(df, df_master, api):
    df['Company Registration Number'] = ''
    results = []

    for index, row in df.iterrows():
        company_name = row['Name']
        company_number = api.search_company(company_name)
        df.at[index, 'Company Registration Number'] = company_number
        results.append(company_number)
        update = company_number + " " + company_name
        st.write(update)

    # Append processed data to the master dataframe
    updated_master_df = pd.concat([df_master, df], ignore_index=True)
    return updated_master_df, results

# Streamlit User Interface
st.title("New Salesforce Accounts")
st.write("Please upload new Salesforce accounts and the master file.")

uploaded_file = st.file_uploader("Upload new Salesforce accounts", key="new_accounts")
uploaded_master_file = st.file_uploader("Upload master file", key="master_file")

if uploaded_file and uploaded_master_file and st.button('Dedupe'):
    df_new_accounts = pd.read_excel(uploaded_file)
    df_master = pd.read_excel(uploaded_master_file)
    master_file_name = uploaded_master_file.name  # Remember the original file name
    api_key = "eb7007ef-7b53-414c-9d07-b9cef8224a68"  # Use your actual API key
    api = RateLimitedAPI(api_key)
    processed_master_df, results = process_excel(df_new_accounts, df_master, api)
    st.write("Updated Master Dataframe with New Company Numbers:")
    st.dataframe(processed_master_df)

    # Prepare to download the updated Excel file
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        processed_master_df.to_excel(writer, index=False, sheet_name='Master Results')
    processed_data = output.getvalue()

    st.download_button(label="Download Updated Master Excel File",
                       data=processed_data,
                       file_name=master_file_name,
                       mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
