import streamlit as st
import pandas as pd
from io import BytesIO

def perform_linkaja_analysis_v2(linkaja_df, mutasi_df, location):
    linkaja_df.columns = [
        'custom_transaction_id_linkaja', 'No', 'Top Organization', 'Parent Organization',
        'Organization', 'Transaction ID', 'Original Transaction ID',
        'Partner Reference Number', 'Invoice ID', 'Finalized Date', 'Finalized Time',
        'Initiate Date', 'Initiate Time', 'Transaction Type', 'Transaction Scenario',
        'Transaction Status_linkaja', 'Transaction Statement', 'Account', 'Counter Party',
        'Debit', 'Credit', 'Balance_linkaja'
    ]
    
    mutasi_df.columns = [
        'custom_transaction_id_mutasi', 'Receipt No.', 'Completion Time', 'Initiation Time',
        'Details', 'Transaction Status_mutasi', 'Currency', 'Paid In', 'Withdrawn', 'Balance_mutasi',
        'Reason Type', 'Opposite Party', 'Linked Transaction ID'
    ]
    
    # Update custom_transaction_id_mutasi format
    mutasi_df['custom_transaction_id_mutasi'] = mutasi_df.apply(
        lambda row: f"{row['custom_transaction_id_mutasi'].rsplit('_', 1)[0]}_{row['Completion Time']}", axis=1)

    st.write("Jumlah data Link Aja:", len(linkaja_df))
    st.write("Jumlah data Digipos:", len(mutasi_df))

    matched_data = pd.merge(
        linkaja_df,
        mutasi_df,
        left_on='custom_transaction_id_linkaja',
        right_on='custom_transaction_id_mutasi',
        how='inner'
    )

    st.write("Jumlah data yang match sebelum filter credit > 0:", len(matched_data))

    # Filter matched_data untuk hanya menampilkan baris dengan Credit > 0
    matched_data_filtered = matched_data[matched_data['Credit'] > 0]
    
    # Data matched_data dengan Credit <= 0
    matched_data_credit_zero = matched_data[matched_data['Credit'] <= 0]

    st.write("Jumlah data yang match (Credit > 0):", len(matched_data_filtered))

    # Data LinkAja yang tidak match
    unmatched_linkaja = linkaja_df[~linkaja_df['custom_transaction_id_linkaja'].isin(matched_data['custom_transaction_id_linkaja'])]
    
    # Gabungkan unmatched_linkaja dengan matched_data_credit_zero
    unmatched_linkaja_combined = pd.concat([unmatched_linkaja, matched_data_credit_zero], ignore_index=True)

    unmatched_mutasi = mutasi_df[~mutasi_df['custom_transaction_id_mutasi'].isin(matched_data['custom_transaction_id_mutasi'])]

    st.write("Jumlah data LinkAja yang tidak match dan Credit <= 0:", len(unmatched_linkaja_combined))
    st.write("Jumlah data Digipos yang tidak match:", len(unmatched_mutasi))

    matched_columns = [col for col in [
        'custom_transaction_id_linkaja', 'custom_transaction_id_mutasi', 'No', 'Top Organization', 
        'Parent Organization', 'Organization', 'Transaction ID', 'Original Transaction ID', 
        'Partner Reference Number', 'Invoice ID', 'Finalized Date', 'Finalized Time', 
        'Initiate Date', 'Initiate Time', 'Transaction Type', 'Transaction Scenario', 
        'Transaction Status_linkaja', 'Transaction Status_mutasi', 'Transaction Statement', 'Account', 
        'Counter Party', 'Withdrawn', 'Debit', 'Credit', 'Balance_linkaja', 'Balance_mutasi', 
        'Receipt No.', 'Completion Time', 'Initiation Time', 'Details'
    ] if col in matched_data.columns]

    matched_data_filtered = matched_data_filtered[matched_columns]

    # Membuat template jurnal
    matched_data_filtered['Withdrawn'] = matched_data_filtered['Withdrawn'].abs()
    matched_data_filtered['Invoice Number'] = matched_data_filtered.apply(lambda row: f"{location}_{row['custom_transaction_id_linkaja'].split('_')[0]}_{row['Initiate Date'].split('/')[1]}/{row['Initiate Date'].split('/')[2]}" if len(row['Initiate Date'].split('/')) == 3 else '', axis=1)

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
        '*InvoiceNumber': matched_data_filtered['Invoice Number'],
        'Message': '',
        'Memo': '',
        '*ProductName': 'Voucherless Bulk 10JT NGRS - Mitra SBP (V841)',
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
        '#PaidToAccountCode': '1-110005',
        'Tags (use': f'Link AJa, {location}',
        'WarehouseName': location,
        '#currency code(example: IDR, USD, CAD)': ''
    })

    return matched_data_filtered, unmatched_linkaja_combined, unmatched_mutasi, jurnal_template

def convert_df_to_excel_v2(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Sheet1')
    writer.save()
    processed_data = output.getvalue()
    return processed_data

def select_linkaja_file_v2():
    linkaja_file = st.file_uploader("Pilih File LinkAja", type=['xlsx'])
    if linkaja_file:
        st.session_state.linkaja_file_name = linkaja_file.name.split('.')[0]
        linkaja_df = pd.read_excel(linkaja_file)
    else:
        linkaja_df = None
    return linkaja_df

def select_mutasi_file_v2():
    mutasi_file = st.file_uploader("Pilih File Mutasi Digipos", type=['xlsx'])
    if mutasi_file:
        st.session_state.mutasi_file_name = mutasi_file.name.split('.')[0]
        mutasi_df = pd.read_excel(mutasi_file, dtype={'Receipt No.': str})
    else:
        mutasi_df = None
    return mutasi_df

def select_location_v2():
    return st.selectbox("Pilih Lokasi", ["Kolaka", "Kendari"])

def main_v2():
    st.title("Analisis Data LinkAja dan Digipos")
    
    linkaja_df = select_linkaja_file_v2()
    mutasi_df = select_mutasi_file_v2()
    location = select_location_v2()

    if linkaja_df is not None and mutasi_df is not None:
        matched_data_filtered, unmatched_linkaja_combined, unmatched_mutasi, jurnal_template = perform_linkaja_analysis_v2(linkaja_df, mutasi_df, location)
        
        st.write("Data yang match (Credit > 0):")
        st.dataframe(matched_data_filtered)
        st.download_button(
            label="Download Matched Data as Excel",
            data=convert_df_to_excel_v2(matched_data_filtered),
            file_name='matched_data_v2.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

        st.write("Data LinkAja yang tidak match atau Credit <= 0:")
        st.dataframe(unmatched_linkaja_combined)
        st.download_button(
            label="Download Unmatched LinkAja Data as Excel",
            data=convert_df_to_excel_v2(unmatched_linkaja_combined),
            file_name='unmatched_linkaja_data_v2.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

        st.write("Data Digipos yang tidak match:")
        st.dataframe(unmatched_mutasi)
        st.download_button(
            label="Download Unmatched Digipos Data as Excel",
            data=convert_df_to_excel_v2(unmatched_mutasi),
            file_name='unmatched_digipos_data_v2.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

        st.write("Template Jurnal:")
        st.dataframe(jurnal_template)
        st.download_button(
            label="Download Jurnal Template as Excel",
            data=convert_df_to_excel_v2(jurnal_template),
            file_name='jurnal_template_v2.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

if __name__ == "__main__":
    main_v2()
