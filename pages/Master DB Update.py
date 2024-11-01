import streamlit as st
import requests
import base64
import pandas as pd
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

def validate_columns(df, required_columns, file_name):
    """Check if the required columns are in the dataframe."""
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        st.error(f"The file '{file_name}' is missing the following required columns: {', '.join(missing_columns)}")
        return False
    return True

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

# Authenticate user before showing the main app content

# Streamlit User Interface
st.title("New Salesforce Accounts")
st.write("This app ensures our master database is continuously updated with new data, checks for existing companies, and automatically retrieves missing registration numbers from Companies House.")

# Instructions Section
st.markdown("""
    <style>
        .instructions {
            background-color: #f0f8ff;
            padding: 20px;
            border-radius: 10px;
            border-left: 6px solid #004aad;
            margin-bottom: 20px;
            color: #333333;
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

st.markdown("""
    <div class="instructions">
        <h3>Instructions for Uploading Files</h3>
        <p><b>New Salesforce Accounts File:</b> Ensure the file contains a column named <code>Name</code> with company names.</p>
        <p><b>Master File:</b> Ensure the file contains columns named <code>Name</code> and <code>Company Registration Number</code> for tracking registered companies.</p>
        <p><i>Note:</i> Only files with the required columns will be accepted.</p>
    </div>
""", unsafe_allow_html=True)
if authenticate_user():
    # File Upload Section
    uploaded_file = st.file_uploader("Upload New Salesforce Accounts (Excel format)", key="new_accounts")
    uploaded_master_file = st.file_uploader("Upload Master File (Excel format)", key="master_file")

    # Define required columns for each file
    required_columns_new = ["Name"]
    required_columns_master = ["Name", "Company Registration Number"]

    if uploaded_file and uploaded_master_file and st.button('Dedupe'):
        # Load data from uploaded files
        df_new_accounts = pd.read_excel(uploaded_file)
        df_master = pd.read_excel(uploaded_master_file)
        
        # Get actual file names
        new_accounts_file_name = uploaded_file.name
        master_file_name = uploaded_master_file.name
        
        # Validate columns
        valid_new_accounts = validate_columns(df_new_accounts, required_columns_new, new_accounts_file_name)
        valid_master_file = validate_columns(df_master, required_columns_master, master_file_name)
        
        if valid_new_accounts and valid_master_file:
            api_key = "eb7007ef-7b53-414c-9d07-b9cef8224a68"  # Use your actual API key
            api = RateLimitedAPI(api_key)
            
            # Process data if validation passed
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
        else:
            st.error("Please upload files with the correct columns.")
else:
    st.error("Authentication failed. Please try again.")
