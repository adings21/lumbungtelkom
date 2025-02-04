import streamlit as st
import pandas as pd
from io import BytesIO 

def convert_df_to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    processed_data = output.getvalue()
    return processed_data

def merge_files():
    st.title("Penggabungan File")

    # Checkbox untuk memilih tipe penggabungan
    merge_type = st.radio(
        "Pilih tipe penggabungan file:",
        ("Link Aja", "Digipos", "Finpay", "Template Jurnal")
    )

    files = st.file_uploader("Pilih File Excel/CSV", type=['xlsx', 'xls', 'csv'], accept_multiple_files=True)

    if st.button("Gabungkan File"):
        if files:
            dataframes = []
            file_names = []
            for file in files:
                file_names.append(file.name)
                dtype = {'no generate': str, 'no fakturgroup': str}
                if merge_type == "Digipos":
                    if file.name.endswith('.csv'):
                        df = pd.read_csv(file, skiprows=5, dtype=str)
                    else:
                        df = pd.read_excel(file, skiprows=5, dtype=str)
                elif merge_type == "Link Aja":
                    if file.name.endswith('.csv'):
                        df = pd.read_csv(file, dtype=str)
                    else:
                        df = pd.read_excel(file, dtype=str)
                elif merge_type == "Finpay":
                    if file.name.endswith('.csv'):
                        df = pd.read_csv(file, skiprows=1, dtype=str)  # Skip 1 row for header
                    else:
                        df = pd.read_excel(file, skiprows=1, dtype=str)  # Skip 1 row for header
                elif merge_type == "Template Jurnal":
                    if file.name.endswith('.csv'):
                        df = pd.read_csv(file, dtype=str)
                    else:
                        df = pd.read_excel(file, dtype=str)
                dataframes.append(df)

            # Memastikan semua DataFrame memiliki kolom yang sama
            column_set = set(dataframes[0].columns)
            for df in dataframes[1:]:
                if set(df.columns) != column_set:
                    st.warning("Kolom dalam file tidak konsisten. Pastikan semua file memiliki nama kolom yang sama.")
                    return

            # Menggabungkan semua DataFrame
            merged_df = pd.concat(dataframes, ignore_index=True)
            output_excel = convert_df_to_excel(merged_df)
            st.session_state.merged_df_excel = output_excel
            st.session_state.file_names = file_names

            st.success("File berhasil digabungkan.")
        else:
            st.warning("Silakan pilih setidaknya satu file untuk digabungkan.")

if __name__ == "__main__":
    merge_files()
