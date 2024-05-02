import streamlit as st
import pandas as pd

def clean_company_name(name):
    if not isinstance(name, str):
        return ""
    
    name = name.lower().strip()
    
    if name.endswith(" ltd"):
        name = name[:-4]
    elif name.endswith(" limited"):
        name = name[:-8]

    return name.strip()

def update_check_file_with_master_data(master, check):
    master['Cleaned Name'] = master['Name'].apply(clean_company_name)
    company_data = pd.Series(master['Account Partner'].values, index=master['Cleaned Name']).to_dict()
    
    check['Cleaned Name'] = check['Name'].apply(clean_company_name)
    check['Updated Column B'] = check['Cleaned Name'].apply(lambda x: company_data.get(x, 'Safe'))

    return check

def update_check_file_with_master_reg(master, check):
    master['Company Registration Number'] = master['Company Registration Number'].fillna('').astype(str)
    check['Company Registration Number'] = check['Company Registration Number'].fillna('').astype(str)

    company_data = pd.Series(master['Account Partner'].values, index=master['Company Registration Number']).to_dict()
    
    check['Reg Compare'] = check['Company Registration Number'].apply(lambda x: company_data.get(x, 'Safe'))

    return check

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

def main():
    st.title('Telesales Data -Dual Check')
    st.write("Please upload the master file and the check file.")

    uploaded_master_file = st.file_uploader("Upload master data sheet", key="master", type=['xlsx'])
    uploaded_check_file = st.file_uploader("Upload Telesales data", key="check", type=['xlsx'])

    if uploaded_master_file and uploaded_check_file:
        master = pd.read_excel(uploaded_master_file, sheet_name=0)
        check = pd.read_excel(uploaded_check_file, sheet_name=0)

        updated_check = update_check_file_with_master_data(master, check)
        updated_check = update_check_file_with_master_reg(master, updated_check)

        updated_check['Company Registration Number'] = updated_check['Company Registration Number'].fillna('').astype(str)
        updated_check['Reg Compare'] = updated_check['Reg Compare'].fillna('').astype(str)
        updated_check['Updated Column B'] = updated_check['Updated Column B'].fillna('').astype(str)

        updated_check = update_check_with_combined_status(updated_check)

        st.write("Check file after updating with data from the master file:")
        st.dataframe(updated_check)

if __name__ == "__main__":
    main()
