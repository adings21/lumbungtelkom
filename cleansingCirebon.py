import pandas as pd
import streamlit as st
from io import BytesIO
import os

def cleanse_data(df):
    # Mencari baris yang memiliki kolom kosong
    rows_with_empty_cells = df[df.isnull().any(axis=1)]
    # Membuang baris yang memiliki kolom kosong
    cleansed_data = df.dropna()

    return cleansed_data, rows_with_empty_cells

def convert_df_to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Sheet1')
    writer.close()
    processed_data = output.getvalue()
    return processed_data

def mainCirebonCleansing():
    st.title('Cleansing Data Cirebon')

    uploaded_file = st.file_uploader("Unggah file Excel", type=["xlsx"])

    if uploaded_file is not None:
        df = pd.read_excel(uploaded_file)
        filename = os.path.splitext(uploaded_file.name)[0]

        cleansed_data, removed_data = cleanse_data(df)

        st.dataframe(cleansed_data)

        cleansed_excel_data = convert_df_to_excel(cleansed_data)
        cleansed_download_filename = f'CleansingCirebon_{filename}.xlsx'
        st.download_button(
            label="Unduh Data yang Sudah Dibersihkan",
            data=cleansed_excel_data,
            file_name=cleansed_download_filename
        )

        if not removed_data.empty:
            st.dataframe(removed_data)
            removed_excel_data = convert_df_to_excel(removed_data)
            removed_download_filename = f'DataTerhapus_{filename}.xlsx'
            st.download_button(
                label="Unduh Data yang Dihapus",
                data=removed_excel_data,
                file_name=removed_download_filename
            )

if __name__ == "__main__":
    mainCirebonCleansing()
