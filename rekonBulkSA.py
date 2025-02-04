import streamlit as st
import pandas as pd
from io import BytesIO

# Fungsi untuk membersihkan data
def cleanse_data(df):
    # Buat DataFrame kosong untuk hasil yang telah dibersihkan
    cleaned_df = pd.DataFrame(columns=df.columns)
    
    # Dapatkan total jumlah unique Receipt No.
    total_receipts = df['Receipt No.'].nunique()
    
    # Buat progress bar
    progress_bar = st.progress(0)
    progress_text = st.empty()
    
    # Iterasi setiap Receipt No. dan pilih satu Transaction ID unik
    for i, receipt_no in enumerate(df['Receipt No.'].unique()):
        subset = df[df['Receipt No.'] == receipt_no]
        
        # Pilih satu baris dengan Transaction ID yang belum ada di hasil
        for _, row in subset.iterrows():
            if cleaned_df[cleaned_df['Transaction ID'] == row['Transaction ID']].empty:
                cleaned_df = pd.concat([cleaned_df, pd.DataFrame([row])], ignore_index=True)
                break
        
        # Update progress bar dan teks persentase
        progress_percentage = int((i + 1) / total_receipts * 100)
        progress_bar.progress(progress_percentage)
        progress_text.text(f'Progress: {progress_percentage}%')
    
    return cleaned_df.reset_index(drop=True)

# Fungsi untuk mengunduh file sebagai excel
def to_excel(df):
    output = BytesIO()
    df.to_excel(output, index=False, sheet_name='Sheet1')
    output.seek(0)
    return output.getvalue()

def perform_linkaja_analysis_BulkSA(linkaja_df, mutasi_df, location):
    linkaja_df.columns = [col.replace('_linkaja', '') for col in linkaja_df.columns]
    mutasi_df.columns = [col.replace('_mutasi', '') for col in mutasi_df.columns]
    
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
    
    st.write("Jumlah data Link Aja:", len(linkaja_df))
    st.write("Jumlah data BulkSA:", len(mutasi_df))

    # Gabungkan data
    matched_data = pd.merge(
        mutasi_df,
        linkaja_df,
        left_on='custom_transaction_id_mutasi',
        right_on='custom_transaction_id_linkaja',
        how='inner'
    )

    st.write("Jumlah data yang match sebelum filter:", len(matched_data))

    # Filter matched_data untuk hanya menampilkan baris dengan Credit > 0
    matched_data_filtered = matched_data[matched_data['Credit'] > 0]

    st.write("Jumlah data yang match dengan Credit > 0 setelah hapus duplikat:", len(matched_data_filtered))

    # Data matched_data dengan Credit <= 0
    matched_data_credit_zero = matched_data[matched_data['Credit'] <= 0]

    st.write("Jumlah data yang match (Credit > 0):", len(matched_data_filtered))

    # Data LinkAja yang tidak match
    unmatched_linkaja = linkaja_df[~linkaja_df['custom_transaction_id_linkaja'].isin(matched_data['custom_transaction_id_linkaja'])]
    
    # Gabungkan unmatched_linkaja dengan matched_data_credit_zero
    unmatched_linkaja_combined = pd.concat([unmatched_linkaja, matched_data_credit_zero], ignore_index=True)

    unmatched_mutasi = mutasi_df[~mutasi_df['custom_transaction_id_mutasi'].isin(matched_data['custom_transaction_id_mutasi'])]

    st.write("Jumlah data LinkAja yang tidak match dan Credit <= 0:", len(unmatched_linkaja_combined))
    st.write("Jumlah data BulkSA yang tidak match:", len(unmatched_mutasi))

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

    # Perform data cleansing on the filtered data
    cleaned_df = cleanse_data(matched_data_filtered)

    return cleaned_df, unmatched_linkaja_combined, unmatched_mutasi

def convert_df_to_excel(df, sheet_size=1000000):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')

    num_sheets = (len(df) // sheet_size) + 1
    for i in range(num_sheets):
        start_row = i * sheet_size
        end_row = (i + 1) * sheet_size
        sheet_df = df.iloc[start_row:end_row]
        sheet_name = f'Sheet{i+1}'
        sheet_df.to_excel(writer, index=False, sheet_name=sheet_name)
    
    writer.close()
    processed_data = output.getvalue()
    return processed_data

def select_linkaja_file_BulkSA():
    linkaja_file = st.file_uploader("Pilih File LinkAja", type=['xlsx'])
    if linkaja_file:
        st.session_state.linkaja_file_name = linkaja_file.name.split('.')[0]
        linkaja_df = pd.read_excel(linkaja_file)
    else:
        linkaja_df = None
    return linkaja_df

def select_mutasi_file_BulkSA():
    mutasi_file = st.file_uploader("Pilih File BulkSA", type=['xlsx'])
    if mutasi_file:
        st.session_state.mutasi_file_name = mutasi_file.name.split('.')[0]
        mutasi_df = pd.read_excel(mutasi_file, dtype={'Receipt No.': str})
    else:
        mutasi_df = None
    return mutasi_df

def select_location_BulkSA():
    return st.selectbox("Pilih Lokasi", ["Kolaka", "Kendari"])

def main_BulkSA():
    location = select_location_BulkSA()
    linkaja_df = select_linkaja_file_BulkSA()
    mutasi_df = select_mutasi_file_BulkSA()

    if linkaja_df is not None and mutasi_df is not None:
        cleaned_df, unmatched_linkaja_combined, unmatched_mutasi = perform_linkaja_analysis_BulkSA(linkaja_df, mutasi_df, location)
        
        st.write("Data yang match (Credit > 0) setelah dibersihkan:")
        st.dataframe(cleaned_df)
        st.download_button(
            label="Download Matched Data as Excel",
            data=convert_df_to_excel(cleaned_df),
            file_name=f"matched_data_{st.session_state.mutasi_file_name}.xlsx",
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

        st.write("Data LinkAja yang tidak match dan Credit <= 0:")
        st.dataframe(unmatched_linkaja_combined)
        st.download_button(
            label="Download Unmatched LinkAja Data as Excel",
            data=convert_df_to_excel(unmatched_linkaja_combined),
            file_name=f"unmatched_linkaja_{st.session_state.linkaja_file_name}.xlsx",
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

        st.write("Data BulkSA yang tidak match:")
        st.dataframe(unmatched_mutasi)
        st.download_button(
            label="Download Unmatched BulkSA Data as Excel",
            data=convert_df_to_excel(unmatched_mutasi),
            file_name=f"unmatched_BulkSA_{st.session_state.mutasi_file_name}.xlsx",
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

if __name__ == "__main__":
   main_BulkSA()
