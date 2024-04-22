#Checks data from data agency against master database

import streamlit as st
import pandas as pd

def update_check_file_with_master_data(master, check):
    # Create a dictionary from the master file with company names as keys and 'Account Partner' values as values.
    company_data = pd.Series(master['Account Partner'].values, index=master['Name']).to_dict()
    
    # Update check file: Copy value from 'Account Partner' of master file if company exists, else 'Safe'.
    check['Updated Column B'] = check['Name'].apply(lambda x: company_data.get(x, 'Safe'))

    return check

def update_check_file_with_master_reg(master, check):
    # Create a dictionary from the master file with company names as keys and 'Account Partner' values as values.
    company_data = pd.Series(master['Account Partner'].values, index=master['Company Registration Number']).to_dict()
    
    # Update check file based on registration number.
    check['Reg Compare'] = check['Company Registration Number'].apply(lambda x: company_data.get(x, 'Safe'))

    return check

def main():
    st.title('Telesales Data')
    st.write("Please upload the master file and the check file.")

    uploaded_master_file = st.file_uploader("Upload master data sheet", key="master", type=['xlsx'])
    uploaded_check_file = st.file_uploader("Upload Telesales data", key="check", type=['xlsx'])

    if uploaded_master_file and uploaded_check_file:
        master = pd.read_excel(uploaded_master_file, sheet_name=0)  # Assuming data is in the first sheet
        check = pd.read_excel(uploaded_check_file, sheet_name=0)  # Assuming data is in the first sheet

        # Process the data based on company names
        updated_check = update_check_file_with_master_data(master, check)
        
        # Process the data based on company registration numbers
        updated_check = update_check_file_with_master_reg(master, check)

        # Display the updated check file
        st.write("Check file after updating with data from the master file:")
        st.dataframe(updated_check)

if __name__ == "__main__":
    main()
