import streamlit as st
import pandas as pd
from datetime import datetime
import io
from io import BytesIO

# Function to process the input file and generate the journal template
def process_file(uploaded_file, tag):
    # Use try-except block to handle file format and engine issues
    try:
        df = pd.read_excel(uploaded_file)
    except ValueError:
        # If pandas cannot determine the Excel file format, specify the engine explicitly
        try:
            df = pd.read_excel(uploaded_file, engine='openpyxl')  # Try openpyxl engine
        except Exception as e:
            st.error(f"Error reading file: {str(e)}")
            return None

    # Filter out rows where 'tukar rp' > 0
    df = df[df['tukar rp'] <= 0]
    st.write("Data sebelum penyaringan:")
    st.write(df)

    df_filtered = df[df['tukar rp'] <= 0]

    st.write("Data setelah penyaringan:")
    st.write(df_filtered)

    # Add Quantity, Unit Price, and Total columns
    df['Quantity'] = df['berat'] * 1000
    df['Unit Price'] = df['harga gram'] / 1000
    df['Total'] = (df['Quantity'] * df['Unit Price']) + df['harga atribut'] + df['ongkos']

    # Update *Amount column based on conditions
    df.loc[(df['transfer rp'] > 0) & (df['cash rp'] > 0), 'transfer rp'] = df['Total'] - df['cash rp']
    df.loc[(df['debet rp'] > 0) & (df['cash rp'] > 0), 'debet rp'] = df['Total'] - df['cash rp']

    # Update *Amount column based on conditions
    df.loc[(df['transfer rp'] > 0) & (df['cash rp'] == 0), 'transfer rp'] = df['Total']
    df.loc[(df['debet rp'] > 0) & (df['cash rp'] == 0), 'debet rp'] = df['Total']

    # Format Total to ensure comma as decimal separator
    df['Total_formatted'] = df['Total'].apply(lambda x: '{:,.2f}'.format(x))

    # Initialize an empty DataFrame for the journal template
    jurnal_template = pd.DataFrame(columns=[
        '*Payment Date', '*Payment Number', '*Invoice Number',
        '*Pay to account (Code)', '*Amount', '*PaymentMethod',
        'WitholdingAccountCode', 'WitholdingAmount(value or %)',
        'Tags (use ; to separate tags)', 'Quantity', 'Unit Price', 'Total'
    ])
    
    # Function to get account code based on tag and payment method
    def get_account_code(tag, payment_method):
        if payment_method == "CASH":
            if tag == "DAMAI":
                return "1-110003"
            elif tag == "CANTIK":
                return "1-110004"
            elif tag == "POJOK":
                return "1-110005"
            return ""
        elif payment_method == "DEBET":
            return "1-110011"
        elif payment_method == "TRANSFER":
            return "1-110012"
        return ""

    # Process each row and generate journal entries
    for index, row in df.iterrows():
        # Convert Timestamp to string format '%d/%m/%Y'
        payment_date = row['tgl system'].strftime('%d/%m/%Y')
        no_fakturjual = row['no fakturjual']

        # If transfer rp > 0 and cash rp > 0
        if row['transfer rp'] > 0 and row['cash rp'] > 0:
            jurnal_template = pd.concat([jurnal_template, pd.DataFrame({
                '*Payment Date': [payment_date],
                '*Payment Number': [f"{no_fakturjual}_cash"],
                '*Invoice Number': [no_fakturjual],
                '*Pay to account (Code)': [get_account_code(tag, "CASH")],
                '*Amount': [row['cash rp']],
                '*PaymentMethod': ["CASH"],
                'WitholdingAccountCode': [""],
                'WitholdingAmount(value or %)': [""],
                'Tags (use ; to separate tags)': [tag],
                'Quantity': [row['Quantity']],
                'Unit Price': [row['Unit Price']],
                'Total': [row['Total_formatted']]
            })], ignore_index=True)
            jurnal_template = pd.concat([jurnal_template, pd.DataFrame({
                '*Payment Date': [payment_date],
                '*Payment Number': [f"{no_fakturjual}_transfer"],
                '*Invoice Number': [no_fakturjual],
                '*Pay to account (Code)': [get_account_code(tag, "TRANSFER")],
                '*Amount': [row['transfer rp']],
                '*PaymentMethod': ["TRANSFER"],
                'WitholdingAccountCode': [""],
                'WitholdingAmount(value or %)': [""],
                'Tags (use ; to separate tags)': [tag],
                'Quantity': [row['Quantity']],
                'Unit Price': [row['Unit Price']],
                'Total': [row['Total_formatted']]
            })], ignore_index=True)

        # If debet rp > 0 and cash rp > 0
        elif row['debet rp'] > 0 and row['cash rp'] > 0:
            jurnal_template = pd.concat([jurnal_template, pd.DataFrame({
                '*Payment Date': [payment_date],
                '*Payment Number': [f"{no_fakturjual}_cash"],
                '*Invoice Number': [no_fakturjual],
                '*Pay to account (Code)': [get_account_code(tag, "CASH")],
                '*Amount': [row['cash rp']],
                '*PaymentMethod': ["CASH"],
                'WitholdingAccountCode': [""],
                'WitholdingAmount(value or %)': [""],
                'Tags (use ; to separate tags)': [tag],
                'Quantity': [row['Quantity']],
                'Unit Price': [row['Unit Price']],
                'Total': [row['Total_formatted']]
            })], ignore_index=True)
            jurnal_template = pd.concat([jurnal_template, pd.DataFrame({
                '*Payment Date': [payment_date],
                '*Payment Number': [f"{no_fakturjual}_debet"],
                '*Invoice Number': [no_fakturjual],
                '*Pay to account (Code)': [get_account_code(tag, "DEBET")],
                '*Amount': [row['debet rp']],
                '*PaymentMethod': ["DEBET"],
                'WitholdingAccountCode': [""],
                'WitholdingAmount(value or %)': [""],
                'Tags (use ; to separate tags)': [tag],
                'Quantity': [row['Quantity']],
                'Unit Price': [row['Unit Price']],
                'Total': [row['Total_formatted']]
            })], ignore_index=True)

        # If only transfer rp > 0
        elif row['transfer rp'] > 0:
            jurnal_template = pd.concat([jurnal_template, pd.DataFrame({
                '*Payment Date': [payment_date],
                '*Payment Number': [f"{no_fakturjual}_transfer"],
                '*Invoice Number': [no_fakturjual],
                '*Pay to account (Code)': [get_account_code(tag, "TRANSFER")],
                '*Amount': [row['transfer rp']],
                '*PaymentMethod': ["TRANSFER"],
                'WitholdingAccountCode': [""],
                'WitholdingAmount(value or %)': [""],
                'Tags (use ; to separate tags)': [tag],
                'Quantity': [row['Quantity']],
                'Unit Price': [row['Unit Price']],
                'Total': [row['Total_formatted']]
            })], ignore_index=True)

        # If only debet rp > 0
        elif row['debet rp'] > 0:
            jurnal_template = pd.concat([jurnal_template, pd.DataFrame({
                '*Payment Date': [payment_date],
                '*Payment Number': [f"{no_fakturjual}_debet"],
                '*Invoice Number': [no_fakturjual],
                '*Pay to account (Code)': [get_account_code(tag, "DEBET")],
                '*Amount': [row['debet rp']],
                '*PaymentMethod': ["DEBET"],
                'WitholdingAccountCode': [""],
                'WitholdingAmount(value or %)': [""],
                'Tags (use ; to separate tags)': [tag],
                'Quantity': [row['Quantity']],
                'Unit Price': [row['Unit Price']],
                'Total': [row['Total_formatted']]
            })], ignore_index=True)

    return jurnal_template

def convert_df_to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Sheet1')
    writer.close()  # Use close instead of save
    processed_data = output.getvalue()
    return processed_data


def mainPayment():
    st.title('Generate Jurnal Template Payment')
    location = st.selectbox('Pilih Lokasi', ['DAMAI', 'CANTIK', 'POJOK'])
    uploaded_file = st.file_uploader('Upload file payments', type=['csv', 'xlsx'])

    if uploaded_file:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        if st.button('Generate Template'):
            st.session_state.generated_payment = True  # Update session state when the template is generated
            jurnal_template_payment = process_file(uploaded_file, location)
            st.session_state.jurnal_template_payment = convert_df_to_excel(jurnal_template_payment)
            st.session_state.file_name = f"jurnalTemplatePayment_{uploaded_file.name}"  # Set the file name in session state
            st.write('Generated Journal Template Payment')
            st.dataframe(jurnal_template_payment)
            
    # Add a download button if the template has been generated
    if st.session_state.get('generated_payment', False):
        st.download_button(
            label='Download Jurnal Template Payment',
            data=st.session_state.jurnal_template_payment,
            file_name=st.session_state.file_name,
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

if __name__ == '__main__':
    mainPayment()