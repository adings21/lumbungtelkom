import streamlit as st
import pandas as pd
from io import BytesIO
import os

def load_data(file):
    if file.name.endswith('.csv'):
        data = pd.read_csv(file)
    else:
        data = pd.read_excel(file)
    return data, file.name

def cleanse_data(data):
    if "Original Transaction ID" not in data.columns or "Transaction ID" not in data.columns:
        st.error("Kolom 'Original Transaction ID' atau 'Transaction ID' tidak ditemukan di file yang diunggah.")
        return data, 0, 0, 0

    data_to_delete = data[
        (data["Original Transaction ID"].isin(data["Transaction ID"]) | 
         data["Transaction ID"].isin(data["Original Transaction ID"]) |
         (data["Original Transaction ID"].notnull() & ~data["Original Transaction ID"].isin(data["Transaction ID"]))
        )
    ]

    original_id_non_empty_count = data["Original Transaction ID"].notnull().sum()
    
    data_cleaned = data[
        ~(data["Original Transaction ID"].isin(data["Transaction ID"]) | 
          data["Transaction ID"].isin(data["Original Transaction ID"]) |
          (data["Original Transaction ID"].notnull() & ~data["Original Transaction ID"].isin(data["Transaction ID"]))
         )
    ]

    total_removed_count = len(data_to_delete)

    return data_cleaned, original_id_non_empty_count, total_removed_count, data_to_delete


def to_excel(df, file_name, prefix):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Sheet1')
    writer.close()
    
    # Menentukan nama file berdasarkan prefix yang diberikan
    if prefix == 'to_delete':
        output_file_name = f"YangAkanDiHapus_{os.path.splitext(file_name)[0]}.xlsx"
    elif prefix == 'cleansed':
        output_file_name = f"cleansedReversal_{os.path.splitext(file_name)[0]}.xlsx"
    else:
        output_file_name = f"{os.path.splitext(file_name)[0]}.xlsx"
    
    return output.getvalue(), output_file_name

def main():
    st.title("Pembersihan Data untuk LinkAja Reversals")

    uploaded_file = st.file_uploader("Unggah file CSV atau Excel Anda", type=["csv", "xlsx", "xls"])
    
    if uploaded_file is not None:
        data, file_name = load_data(uploaded_file)

        cleansed_data, original_id_non_empty_count, transaction_id_remove_count, data_to_delete = cleanse_data(data)

        st.write(f"Jumlah baris dengan 'Original Transaction ID' yang tidak kosong: {original_id_non_empty_count}")
        st.write(f"Jumlah baris yang akan dihapus berdasarkan 'Transaction ID': {transaction_id_remove_count}")

        # Unduh data yang akan dihapus sebagai file Excel
        if not data_to_delete.empty:
            excel_data_to_delete, output_file_name_to_delete = to_excel(data_to_delete, file_name, 'to_delete')
            st.download_button(label='Unduh Data yang Akan Dihapus',
                               data=excel_data_to_delete,
                               file_name=output_file_name_to_delete,
                               mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

        # Unduh data yang sudah dibersihkan sebagai file Excel
        if not cleansed_data.empty:
            excel_data_cleaned, output_file_name_cleaned = to_excel(cleansed_data, file_name, 'cleansed')
            st.download_button(label='Unduh Data yang Sudah Dibersihkan',
                               data=excel_data_cleaned,
                               file_name=output_file_name_cleaned,
                               mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

if __name__ == "__main__":
    main()
