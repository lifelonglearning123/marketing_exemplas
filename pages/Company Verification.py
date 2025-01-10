import streamlit as st
import pandas as pd
import requests
import base64
import time
from io import BytesIO
from simple_password_auth import authenticate_user  # Import the function from the separate file


# Configure the default theme and page layout
st.set_page_config(
    page_title="Purgo: Smart Data Deduplication & Compliance for Targeted Marketing Outreach",
    page_icon="purgo.ico",
    layout="wide",
    initial_sidebar_state="expanded"
)



# Sidebar Logo at the very top
st.sidebar.image("purgo.png", use_column_width=True)  # Display the logo at the top of the sidebar

# Convert image to base64 for embedding in CSS
def get_base64_image(file_path):
    with open(file_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()

# Get base64 encoding of the background image
background_image = get_base64_image("main_bk.jpg")



# Streamlit User Interface
st.title("Streamlined Company Verification for Active Partnerships")
st.write("Company verification app that validates company activity, consortium partnerships, and interest in Innovation Support within a dataset.")

# Instructions Section
st.markdown("""
    <style>
        /* Instructions styling with improved contrast */
        .instructions {
            background-color: #f0f8ff;  /* Light blue background for visibility */
            padding: 20px;
            border-radius: 10px;
            border-left: 6px solid #004aad;
            margin-bottom: 20px;
            color: #333333;  /* Dark text for readability */
        }
        .instructions h3 {
            font-size: 1.2em;
            color: #004aad;
            font-weight: bold;
        }
        .instructions p {
            margin: 5px 0;
            color: #333333;
        }
        .instructions code {
            background-color: #e1ecf4;
            padding: 2px 4px;
            border-radius: 4px;
            font-size: 0.9em;
        }
    </style>
""", unsafe_allow_html=True)

# Instructions Section
st.markdown("""
    <div class="instructions">
        <h3>Instructions for Uploading Files</h3>
        <p><b>Telesales Data File:</b> Ensure the file contains a column named <code>Name</code>  and <code>Company Registration Number</code></p>
        <p><b>Master File:</b> Ensure the file contains columns named <code>Name</code> and <code>Company Registration Number</code> for tracking registered companies.</p>
        <p><i>Note:</i> Only files with the required columns will be accepted.</p>
    </div>
""", unsafe_allow_html=True)


# Function to verify required columns in each file
def verify_required_columns(dataframe, required_columns, file_name):
    dataframe.columns = dataframe.columns.str.strip()  # Remove any leading/trailing whitespace
    missing_columns = [col for col in required_columns if col not in dataframe.columns]
    if missing_columns:
        st.error(f"'{file_name}' is missing the following required columns: {', '.join(missing_columns)}")
        return False
    return True

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
        status = data.get('company_status', 'Status not found')
        st.write("Company Status Check", company_number)
        return status
    else:
        st.write(f"Initial check failed for {company_number}, retrying with '0' prefixed.")
        company_number = '0' + company_number
        url = f"https://api.company-information.service.gov.uk/company/{company_number}"
        response = requests.get(url, auth=(api_key, ''))
        if response.status_code == 200:
            data = response.json()
            status = data.get('company_status', 'Status not found')
            st.write("Company Status Check (after retry)", company_number)
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
if authenticate_user():
    st.write("Please upload the master file and the check file. Ensure each file has the required columns.")

    # File upload section
    uploaded_check_file = st.file_uploader("Upload Telesales data", key="check", type=['xlsx'])
    uploaded_master_file = st.file_uploader("Upload master data sheet", key="master", type=['xlsx'])

    # Required columns for each file
    required_master_columns = ["Name", "Company Registration Number", "Account Partner"]
    required_check_columns = ["Name", "Company Registration Number"]

    if uploaded_master_file and uploaded_check_file:
        # Load files and standardize column names by stripping whitespace
        master = pd.read_excel(uploaded_master_file, sheet_name=0)
        check = pd.read_excel(uploaded_check_file, sheet_name=0)
        print("print data table")
        print("check", type(check))
        print(check.iloc[0])
        
        # Get the actual file names from the uploaded files
        master_file_name = uploaded_master_file.name
        check_file_name = uploaded_check_file.name

        # Verify if the required columns are present in each file using actual file names
        valid_master = verify_required_columns(master, required_master_columns, master_file_name)
        print("valid master", valid_master)
        valid_check = verify_required_columns(check, required_check_columns, check_file_name)
        print("valid check", valid_check)
        if valid_master and valid_check:
            api_key = "eb7007ef-7b53-414c-9d07-b9cef8224a68"  # Replace with your Companies House API key
            api = RateLimitedAPI(api_key)
            
            check = process_excel(check, api)
            updated_check = update_check_file_with_master_data(master, check)
            updated_check = update_check_file_with_master_reg(master, updated_check)
            updated_check = update_check_with_combined_status(updated_check)

            updated_check['Company Status'] = updated_check['Company Registration Number'].apply(get_company_status)
            
            st.write("Check file after updating with data from the master file and fetching company status:")
            st.dataframe(updated_check)

            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                updated_check.to_excel(writer, index=False, sheet_name='Updated Check')
            processed_data = output.getvalue()

            st.download_button(label="Download Updated Check Excel File",
                            data=processed_data,
                            file_name='Updated_Check_File.xlsx',
                            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        else:
            st.error("Please upload files with the correct columns.")
else:
    st.error("Authentication failed. Please try again.")