import streamlit as st
import pandas as pd
from io import BytesIO

def main_missing_data():
    st.title('Data Reconciliation App')

    # Pilihan kolom pencarian
    search_option = st.radio(
        "Cari berdasarkan:",
        ("Transaction ID", "Receipt No.", "custom_transaction_id")
    )

    # Fungsi untuk mencari data yang hilang berdasarkan kolom yang dipilih
    def find_missing_data(cleansed_df, match_df, not_match_df, search_column):
        combined_df = pd.concat([match_df, not_match_df])
        missing_data_df = cleansed_df[~cleansed_df[search_column].isin(combined_df[search_column])]
        return missing_data_df

    # Fungsi untuk mengonversi DataFrame ke file Excel dalam buffer
    def to_excel(df):
        output = BytesIO()
        writer = pd.ExcelWriter(output, engine='xlsxwriter')
        df.to_excel(writer, index=False, sheet_name='Sheet1')
        writer.close()
        processed_data = output.getvalue()
        return processed_data

    # Fungsi untuk membaca file Excel dan mengatur kolom Receipt No. sebagai string
    def read_excel(file, columns_to_str=None):
        df = pd.read_excel(file, dtype={col: str for col in columns_to_str} if columns_to_str else None)
        return df

    # Mengunggah file Excel
    cleansed_file = st.file_uploader("Upload Cleansed File", type=["xlsx"])
    match_file = st.file_uploader("Upload Match File", type=["xlsx"])
    not_match_file = st.file_uploader("Upload Not Match File", type=["xlsx"])

    if cleansed_file and match_file and not_match_file:
        # Menentukan kolom yang perlu diatur sebagai string
        columns_to_str = ["Receipt No."] if search_option in ["Receipt No.", "custom_transaction_id"] else None

        # Membaca file Excel
        cleansed_df = read_excel(cleansed_file, columns_to_str)
        match_df = read_excel(match_file, columns_to_str)
        not_match_df = read_excel(not_match_file, columns_to_str)

        # Mencari data yang hilang
        missing_data_df = find_missing_data(cleansed_df, match_df, not_match_df, search_option)

        # Menampilkan data yang hilang
        st.write("Data yang hilang:")
        st.dataframe(missing_data_df)

        # Mengonversi data yang hilang ke file Excel dalam buffer
        missing_data_xlsx = to_excel(missing_data_df)

        # Tombol untuk mengunduh data yang hilang
        st.download_button(
            label="Download Missing Data",
            data=missing_data_xlsx,
            file_name='Missing_Data.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    else:
        st.write("Silakan unggah semua file yang diperlukan untuk menemukan data yang hilang.")

# Menambahkan pemanggilan main_missing_data jika file ini dijalankan langsung
if __name__ == '__main__':
    main_missing_data()
