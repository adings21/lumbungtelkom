import streamlit as st
import pandas as pd
from io import BytesIO

def main_Cleans_Match():
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

    # Streamlit app
    st.title('Data Cleansing Application')

    # Unggah file excel
    uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])

    if uploaded_file is not None:
        # Baca file excel dengan kolom `Receipt No.` sebagai teks
        df = pd.read_excel(uploaded_file, dtype={'Receipt No.': str})
        
        # Tampilkan data asli
        st.subheader('Original Data')
        st.write(df)
        
        # Membersihkan data
        cleaned_df = cleanse_data(df)
        
        # Tampilkan data yang telah dibersihkan
        st.subheader('Cleaned Data')
        st.write(cleaned_df)
        
        # Unduh file excel yang telah dibersihkan
        st.subheader('Download Cleaned Data')
        cleaned_data = to_excel(cleaned_df)
        st.download_button(
            label="Download Excel file",
            data=cleaned_data,
            file_name='cleaned_data.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
if __name__ == '__main__':
    main_Cleans_Match()