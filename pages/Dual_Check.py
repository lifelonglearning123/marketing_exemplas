import streamlit as st
import pandas as pd
import requests
import base64
import time
from io import BytesIO

# Function to clean company name
def clean_company_name(name):
    if not isinstance(name, str):
        return ""
    name = name.lower().strip()
    if name.endswith(" ltd"):
        name = name[:-4]
    elif name.endswith(" limited"):
        name = name[:-8]
    return name.strip()

# Function to update check file with master data
def update_check_file_with_master_data(master, check):
    master['Cleaned Name'] = master['Name'].apply(clean_company_name)
    company_data = pd.Series(master['Account Partner'].values, index=master['Cleaned Name']).to_dict()
    check['Cleaned Name'] = check['Name'].apply(clean_company_name)
    check['Updated Column B'] = check['Cleaned Name'].apply(lambda x: company_data.get(x, 'Safe'))
    return check

# Function to update check file with master registration number
def update_check_file_with_master_reg(master, check):
    master['Company Registration Number'] = master['Company Registration Number'].fillna('').astype(str)
    check['Company Registration Number'] = check['Company Registration Number'].fillna('').astype(str)
    company_data = pd.Series(master['Account Partner'].values, index=master['Company Registration Number']).to_dict()
    check['Reg Compare'] = check['Company Registration Number'].apply(lambda x: company_data.get(x, 'Safe'))
    return check

# Function to combine statuses
def update_check_with_combined_status(check):
    def combine_status(row):
        if row['Updated Column B'] == 'Safe' and row['Reg Compare'] == 'Safe':
            return 'Safe'
        if row['Updated Column B'] != 'Safe':
            return row['Updated Column B']
        if row['Reg Compare'] != 'Safe':
            return row['Reg Compare']
        return 'Safe'
    check['Combined Status'] = check.apply(combine_status, axis=1)
    return check

# API handler with rate limiting
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

# Function to get the company status from Companies House API
def get_company_status(company_number):
    api_key = "eb7007ef-7b53-414c-9d07-b9cef8224a68"  # Use your actual API key
    url = f"https://api.company-information.service.gov.uk/company/{company_number}"
    response = requests.get(url, auth=(api_key, ''))
    if response.status_code == 200:
        data = response.json()
        # You might need to adjust the key depending on the structure of the response
        status = data.get('company_status', 'Status not found')
        st.write("Company Status Check", company_number)
        return status
    else:
        return "Failed to fetch data"

def process_excel(df, api):
    df['Company Registration Number'] = df['Company Registration Number'].fillna('')
    for index, row in df.iterrows():
        if not row['Company Registration Number']:
            company_name = row['Name']
            company_number = api.search_company(company_name)
            df.at[index, 'Company Registration Number'] = company_number
            st.write("Company check", row['Name'])
    return df

# Streamlit User Interface
st.title("Telesales Data - Dual Check")
st.write("Please upload the master file and the check file. Ensure each file has a column 'Name' and 'Company Registration Number'.")


uploaded_master_file = st.file_uploader("Upload master data sheet", key="master", type=['xlsx'])
uploaded_check_file = st.file_uploader("Upload Telesales data", key="check", type=['xlsx'])

if uploaded_master_file and uploaded_check_file:
    master = pd.read_excel(uploaded_master_file, sheet_name=0)
    check = pd.read_excel(uploaded_check_file, sheet_name=0)

    api_key = "eb7007ef-7b53-414c-9d07-b9cef8224a68"  # Replace with your Companies House API key
    api = RateLimitedAPI(api_key)

    check = process_excel(check, api)

    updated_check = update_check_file_with_master_data(master, check)
    updated_check = update_check_file_with_master_reg(master, updated_check)

    updated_check = update_check_with_combined_status(updated_check)

    # Get company status for each company registration number
    updated_check['Company Status'] = updated_check['Company Registration Number'].apply(get_company_status)

    st.write("Check file after updating with data from the master file and fetching company status:")
    st.dataframe(updated_check)

    # Prepare to download the updated check file
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        updated_check.to_excel(writer, index=False, sheet_name='Updated Check')
    processed_data = output.getvalue()

    st.download_button(label="Download Updated Check Excel File",
                       data=processed_data,
                       file_name='Updated_Check_File.xlsx',
                       mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
