import streamlit as st
import pandas as pd
from io import BytesIO

def perform_linkaja_analysis(linkaja_df, mutasi_df, location):
    # existing code
    pass  # Placeholder for the existing code

def convert_df_to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Sheet1')
    writer.close()
    processed_data = output.getvalue()
    return processed_data

def generate_jurnal_template_menu():
    st.title("Generate Jurnal Template")
    location = st.selectbox("Pilih Lokasi", ["Kolaka", "Kendari"])
    matched_data = st.file_uploader("Pilih File Matched Data", type=['xlsx'])
    if matched_data:
        matched_data_df = pd.read_excel(matched_data)

       
        invoice_numbers = matched_data_df.apply(lambda row: f"{location}_{row['custom_transaction_id_linkaja'].split('_')[0]}_{row['Initiate Date'].split('/')[1]}/{row['Initiate Date'].split('/')[2]}" if isinstance(row['Initiate Date'], str) and len(row['Initiate Date'].split('/')) == 3 else '', axis=1)
        
        jurnal_template = pd.DataFrame({
            '*Customer': matched_data_df['Counter Party'],
            'Email': '',
            'BillingAddress': '',
            'ShippingAddress': '',
            '*InvoiceDate': '',
            '*DueDate': '',
            'ShippingDate': '',
            'ShipVia': '',
            'TrackingNo': '',
            'CustomerRefNo': '',
            '*InvoiceNumber': invoice_numbers,
            'Message': '',
            'Memo': '',
            '*ProductName': 'Voucherless Bulk 10JT NGRS - Mitra SBP (V841)',
            'Description': '',
            '*Quantity': '',
            'Unit': '',
            '*UnitPrice': '',
            'Credit': matched_data_df['Credit'],
            'Withdrawn': matched_data_df['Withdrawn'],
            'ProductDiscountRate(%)': '',
            'InvoiceDiscountRate(%)': '',
            'TaxName': 'PPN',
            'TaxRate(%)': '11%',
            'ShippingFee': '',
            'WitholdingAccountCode': '',
            'WitholdingAmount(value or %)': '',
            '#paid?(yes/no)': 'YES',
            '#PaymentMethod': 'TRANSFER',
            '#PaidToAccountCode': '1-110006',
            'Tags (use': f'Link Aja, {location}',
            'WarehouseName': location,
            '#currency code(example: IDR, USD, CAD)': ''
        })

        st.write("Template Jurnal:")
        st.dataframe(jurnal_template)
        st.download_button(
            label="Download Jurnal Template as Excel",
            data=convert_df_to_excel(jurnal_template),
            file_name='jurnal_template_sementara.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

if __name__ == "__main__":
    generate_jurnal_template_menu()
