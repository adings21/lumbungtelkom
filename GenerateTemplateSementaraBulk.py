# jurnal_template.py
import streamlit as st
import pandas as pd
from io import BytesIO

def create_jurnal_template(matched_data_filtered, location):
    # Menghitung Invoice Number untuk setiap baris
    invoice_numbers = matched_data_filtered.apply(
        lambda row: f"{location}_{row['custom_transaction_id_linkaja'].split('_')[0]}_{row['Initiate Date'].split('/')[1]}/{row['Initiate Date'].split('/')[2]}" 
        if isinstance(row['Initiate Date'], str) and len(row['Initiate Date'].split('/')) == 3 
        else '', 
        axis=1
    )
    
    # Membuat template jurnal
    jurnal_template = pd.DataFrame({
        '*Customer': matched_data_filtered['Counter Party'],
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
        '*ProductName': 'Voucherless Bulk - SA (V847)',
        'Description': '',
        '*Quantity': '',
        'Unit': '',
        '*UnitPrice': '',
        'Credit': matched_data_filtered['Credit'],
        'Withdrawn': matched_data_filtered['Withdrawn'],
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
    
    return jurnal_template

def convert_df_to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Sheet1')
    writer.close()
    processed_data = output.getvalue()
    return processed_data

def main_jurnal_template():
    st.title("Jurnal Template Creator")
    
    # Pilih file dan lokasi
    location = st.selectbox("Pilih Lokasi", ["Kolaka", "Kendari"])
    matched_data_filtered = st.file_uploader("Pilih File Data Match", type=['xlsx'])
    
    if matched_data_filtered:
        matched_data_filtered = pd.read_excel(matched_data_filtered)
        
        jurnal_template = create_jurnal_template(matched_data_filtered, location)
        
        st.write("Template Jurnal:")
        st.dataframe(jurnal_template)
        st.download_button(
            label="Download Jurnal Template as Excel",
            data=convert_df_to_excel(jurnal_template),
            file_name=f"jurnal_Sementara_LinkAja_Vs_BulkSA.xlsx",
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

if __name__ == "__main__":
    main_jurnal_template()
