import streamlit as st
import pandas as pd
from datetime import datetime
from io import BytesIO
import numpy as np

def process_linkaja(df, location):
    df['Initiate Date'] = df['Initiate Date'].astype(str).str.strip()
    df['Initiate Time'] = df['Initiate Time'].astype(str).str.strip()
    df['Counter Party'] = df['Counter Party'].astype(str).str.strip()
    df['Account'] = df['Account'].astype(str).str.strip()
    
    df_filtered = df[df['Account'].str.contains('Organization MFS Purchase Account', na=False)]

    def parse_datetime(datetime_str):
        datetime_str = datetime_str.strip()  # Menghapus spasi tambahan di awal dan akhir string
        formats = [
            '%d-%m-%Y %H:%M:%S', '%Y-%m-%d %H:%M:%S', '%d/%m/%Y %H:%M:%S',
            '%d-%m-%Y %H:%M', '%Y-%m-%d %H:%M', '%d/%m/%Y %H:%M',
            '%d-%m-%Y', '%Y-%m-%d', '%d/%m/%Y',
            '%Y-%m-%d %H:%M:%S.%f', '%Y-%m-%d %H:%M:%S',
            '%m-%d-%Y', '%m/%d/%Y', '%Y-%m-%d',
            '%m-%d-%Y %H:%M:%S', '%m/%d/%Y %H:%M:%S',
            '%m-%d-%Y %H:%M', '%m/%d/%Y %H:%M',
            '%H:%M:%S'
        ]
        for fmt in formats:
            try:
                return datetime.strptime(datetime_str, fmt)
            except ValueError:
                continue
        raise ValueError(f"no valid datetime format found for {datetime_str}")

    def format_custom_transaction_id(counter_party, initiate_date, initiate_time, credit):
        try:
            initiate_time = datetime.strptime(initiate_time, '%H:%M:%S').strftime('%H.%M')
        except ValueError:
            initiate_time = datetime.strptime(initiate_time, '%H.%M').strftime('%H.%M')
        return f"{counter_party.split(' - ')[0].strip()}_{initiate_date}_{initiate_time}_{credit}"

    df_filtered['custom_transaction_id'] = df_filtered.apply(
        lambda row: format_custom_transaction_id(row['Counter Party'], parse_datetime(row['Initiate Date']).strftime('%d/%m/%Y'), row['Initiate Time'], row['Credit']), axis=1
    )

    cols = df_filtered.columns.tolist()
    cols = [cols[-1]] + cols[:-1]
    df_filtered = df_filtered[cols]

    return df_filtered

def select_location():
    return st.selectbox("Pilih Lokasi", ["Kolaka", "Kendari"])

from datetime import datetime
import pandas as pd

def process_digipos(df, location):
    # Menghapus spasi di awal dan akhir string pada kolom tertentu
    df['Completion Time'] = df['Completion Time'].astype(str).str.strip()
    df['Opposite Party'] = df['Opposite Party'].astype(str).str.strip()
    df['Receipt No.'] = df['Receipt No.'].astype(str).str.strip()
    df['Initiation Time'] = df['Initiation Time'].astype(str).str.strip()

    # Menghitung nilai absolut dan menetapkan nilai 'Withdrawn_processed'
    df['Withdrawn_processed'] = df['Withdrawn'].abs()
    df['Withdrawn'] = df['Withdrawn'].abs()

    # Fungsi untuk mengubah nilai withdrawn sesuai dengan lokasi
    def denom_keuntungan(withdrawn):
        if pd.notna(withdrawn):
            if location == 'Kolaka':
                if 1001 <= withdrawn <= 4999:
                    return withdrawn + 400
                elif 5000 <= withdrawn <= 18999:
                    return withdrawn + 1000
                elif 19000 <= withdrawn <= 39999:
                    return withdrawn + 800
                elif 40000 <= withdrawn <= 75000:
                    return withdrawn + 600
                elif 75001 <= withdrawn <= 99999:
                    return withdrawn + 5000
                elif 100000 <= withdrawn <= 1000000:
                    return withdrawn + 300
                else:
                    return withdrawn
            elif location == "Kendari":
                if 1001 <= withdrawn <= 3999:
                    return withdrawn + 300
                elif 4000 <= withdrawn <= 14900:
                    return withdrawn + 850
                elif 14901 <= withdrawn <= 18999:
                    return withdrawn + 700
                elif 19000 <= withdrawn <= 35000:
                    return withdrawn + 500
                elif 35001 <= withdrawn <= 81000:
                    return withdrawn + 350
                elif 81001 <= withdrawn <= 99999:
                    return withdrawn + 250
                elif 100000 <= withdrawn <= 1000000:
                    return withdrawn + 100
                else:
                    return withdrawn
        else:
            return withdrawn  # Jika withdrawn adalah NaN, kembalikan nilai NaN
        
    # Terapkan fungsi denom_keuntungan pada kolom Withdrawn_processed
    df['Withdrawn_processed'] = df['Withdrawn_processed'].apply(denom_keuntungan)

    # Buat salinan filtered DataFrame tanpa menghapus baris
    df_filtered = df.copy()

    # Fungsi untuk parsing datetime sesuai dengan format yang mungkin
    def parse_datetime(datetime_str):
        formats = [
            '%d-%m-%Y %H:%M:%S', '%Y-%m-%d %H:%M:%S', '%d/%m/%Y %H:%M:%S',
            '%d-%m-%Y %H:%M', '%Y-%m-%d %H:%M', '%d/%m/%Y %H:%M',
            '%d-%m-%Y', '%Y-%m-%d', '%d/%m/%Y',
        ]
        for fmt in formats:
            try:
                return datetime.strptime(datetime_str.strip(), fmt)
            except ValueError:
                pass
        raise ValueError(f"no valid datetime format found for {datetime_str}")

    # Buat kolom custom_transaction_id berdasarkan logika yang diinginkan
    df_filtered['custom_transaction_id'] = df_filtered.apply(
        lambda row: f"{row['Opposite Party'].split(' - ')[0].strip()}_{parse_datetime(row['Completion Time']).strftime('%d/%m/%Y')}_{parse_datetime(row['Initiation Time']).strftime('%H.%M')}_{int(row['Withdrawn_processed']) if not pd.isna(row['Withdrawn_processed']) else 'NaN'}", axis=1)

    # Susun ulang kolom agar custom_transaction_id berada di posisi pertama
    cols = df_filtered.columns.tolist()
    cols = [cols[-1]] + cols[:-1]
    df_filtered = df_filtered[cols]

    return df_filtered



def convert_df_to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    output.seek(0)
    return output

def main():
    st.title('Data Cleansing dan Custom ID Generator')

    location = select_location()

    # Upload file Link Aja
    uploaded_file_linkaja = st.file_uploader("Upload File Link Aja", type=['csv', 'xlsx'], key="file_uploader_linkaja")
    if uploaded_file_linkaja is not None:
        if uploaded_file_linkaja.name.endswith('.csv'):
            df_linkaja = pd.read_csv(uploaded_file_linkaja, dtype={'Receipt No.': str})
        elif uploaded_file_linkaja.name.endswith('.xlsx'):
            df_linkaja = pd.read_excel(uploaded_file_linkaja, dtype={'Receipt No.': str})
        st.session_state.df_linkaja = df_linkaja

    # Upload file Digipos
    uploaded_file_digipos = st.file_uploader("Upload File Digipos", type=['csv', 'xlsx'], key="file_uploader_digipos")
    if uploaded_file_digipos is not None:
        if uploaded_file_digipos.name.endswith('.csv'):
            df_digipos = pd.read_csv(uploaded_file_digipos, dtype={'Receipt No.': str})
        elif uploaded_file_digipos.name.endswith('.xlsx'):
            df_digipos = pd.read_excel(uploaded_file_digipos, dtype={'Receipt No.': str})
        st.session_state.df_digipos = df_digipos

    cleaned_linkaja = st.session_state.get('cleaned_linkaja', None)
    cleaned_digipos = st.session_state.get('cleaned_digipos', None)

    # Tombol untuk melakukan cleansing dan membuat custom ID
    if st.button("Lakukan Cleansing dan Custom ID"):
        if 'df_linkaja' in st.session_state:
            try:
                cleaned_linkaja = process_linkaja(st.session_state.df_linkaja, location)
                st.session_state.cleaned_linkaja = cleaned_linkaja
                st.success("Cleansing dan pembuatan Custom ID untuk Link Aja berhasil!")
            except ValueError as e:
                st.error(f"Error processing Link Aja data: {e}")
        
        if 'df_digipos' in st.session_state:
            try:
                cleaned_digipos = process_digipos(st.session_state.df_digipos, location)
                st.session_state.cleaned_digipos = cleaned_digipos
                st.success("Cleansing dan pembuatan Custom ID untuk Digipos berhasil!")
            except ValueError as e:
                st.error(f"Error processing Digipos data: {e}")

    # Tambahkan tombol untuk mengunduh hasil Link Aja
    if cleaned_linkaja is not None:
        excel_linkaja = convert_df_to_excel(cleaned_linkaja)
        st.download_button(
            label="Download Hasil Link Aja",
            data=excel_linkaja,
            file_name=f'Cleansed_{uploaded_file_linkaja.name}.xlsx',  # Ubah ekstensi menjadi .xlsx
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            key='download_linkaja'
        )

    # Tambahkan tombol untuk mengunduh hasil Digipos
    if cleaned_digipos is not None:
        excel_digipos = convert_df_to_excel(cleaned_digipos)
        st.download_button(
            label="Download Hasil Digipos",
            data=excel_digipos,
            file_name=f'Cleansed_{uploaded_file_digipos.name}.xlsx',  # Ubah ekstensi menjadi .xlsx
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            key='download_digipos'
        )

if __name__ == "__main__":
    main()
