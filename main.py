import streamlit as st
import pandas as pd
from io import BytesIO
import io

from GabunganFile import merge_files
from rekonDataFinpay import perform_analysis, select_finpay_file, select_mutasi_file, select_location
from cleansLinkajaCustomId import main as cleans_linkaja_custom_id_main, convert_df_to_excel
from cleansLinkajaCustomIdKedua import main as cleans_linkaja_custom_id_kedua_main , convert_df_to_excel
from rekonDataLinkAja import perform_linkaja_analysis, select_linkaja_file, select_mutasi_file as select_linkaja_mutasi_file
from groupingGenerateTemplate import generate_journal_template
from groupingGenerateTemplateV2 import generate_journal_template_v2
from GenerateTemplateCirebonPenjualan import mainPenjualan as penjualanCirebon
from GenerateTemplateCirebonPayment import mainPayment as paymentCirebon
from CleansLinkAjaCustomIdVersi2 import main_VERSIDUA as cleans_linkaja_custom_id_main_versi2_2 , convert_df_to_excel_VERSIDUA
from cleansReversalLinkAja import main as cleans_reversal_linkaja_main
from rekonBulkSA import main_BulkSA as rekon_bulkSA
from cleansLinkajaBulkSA import main_BulkSA as cleans_linkaja_custom_id_main_BulkSA, convert_df_to_excel_BulkSA
from generateTemplateBulk import main_Bulk as bulk_jurnal
from rekonDataFinpayVBulkSA import main_Bulks as finpay_vs_Bulks
from cleansLinkajaBulkSaKedua import main_Bulk2 as complition_time_Bulk2
from GenerateTemplateCirebonPembelian import mainPembelian as pembelianCirebon
from cleansingCirebon import mainCirebonCleansing as cirebonCleansing
from groupingGenerateTemplateTahap1 import generate_jurnal_template_menu
from GenerateTemplateSementaraBulk import main_jurnal_template
from misingDataMakasar import main_missing_data
from cleansMatch import main_Cleans_Match

# CSS custom untuk tema aplikasi
st.markdown("""
    <style>
    body {
        background-color: #23272a; /* Warna latar belakang */
        color: #ffffff; /* Warna teks */
    }
    .css-18e3th9 {
        background-color: #007bff !important; /* Warna latar sidebar */
        color: #ffffff !important; /* Warna teks sidebar */
    }
    .css-1d391kg {
        background-color: #343a40 !important; /* Warna latar header */
        color: #ffffff !important; /* Warna teks header */
    }
    .stButton>button {
        background-color: #007bff; /* Warna latar tombol */
        color: #ffffff; /* Warna teks tombol */
    }
    .stButton>button:hover {
        background-color: #0056b3; /* Warna latar tombol saat dihover */
    }
    .stButton>button:active {
        background-color: #ff0000; /* Warna latar tombol saat diklik */
        color: #ffffff; /* Warna teks tombol saat diklik */
    }
    .stSelectbox>div>div {
        background-color: #343a40; /* Warna latar dropdown */
        color: #ffffff; /* Warna teks dropdown */
    }
    .stDownloadButton>button {
        background-color: #007bff; /* Warna latar tombol download */
        color: #ffffff; /* Warna teks tombol download */
    }
    </style>
""", unsafe_allow_html=True)

def main():
    st.sidebar.title('Menu')
    menu = st.sidebar.selectbox('Pilih Menu', ["Penggabungan File", "Rekonsiliasi Data Finpay", "Rekonsiliasi Data LinkAja","Rekonsiliasi Data Bulk SA","Template Jurnal Cirebon"])

    if menu == "Penggabungan File":
        st.title("Penggabungan File Excel/CSV")
        merge_files()

        if 'merged_df_excel' in st.session_state:
            st.download_button(
                label="Download Excel",
                data=st.session_state.merged_df_excel,
                file_name=f'merged_file_{"_".join(st.session_state.file_names)}.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )

    elif menu == "Rekonsiliasi Data Finpay":
        st.title("Rekonsiliasi Data Finpay")
        finpay_file = select_finpay_file()
        mutasi_file = select_mutasi_file()
        location = select_location()

        if st.button("Lakukan Analisis"):
            try:
                if finpay_file is not None and mutasi_file is not None and location:
                    result_query1, result_query2, jurnal_template, not_in_query1_or_query2 = perform_analysis(finpay_file, mutasi_file, location)
                    st.session_state.result_query1 = convert_df_to_excel(result_query1)
                    st.session_state.result_query2 = convert_df_to_excel(result_query2)
                    st.session_state.jurnal_template = convert_df_to_excel(jurnal_template)
                    st.session_state.not_in_queries = convert_df_to_excel(not_in_query1_or_query2)
                    st.success("Analisis berhasil dilakukan.")
                else:
                    st.warning("Harap pilih kedua file dan lokasi.")
            except Exception as e:
                st.error(f"Terjadi kesalahan: {str(e)}")

        if 'result_query1' in st.session_state:
            st.download_button(
                label="Download data digipos dan finpay match",
                data=st.session_state.result_query1,
                file_name=f'Match_{st.session_state.mutasi_file_name}_{st.session_state.finpay_file_name}.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )

        if 'result_query2' in st.session_state:
            st.download_button(
                label="Download data finpay not match",
                data=st.session_state.result_query2,
                file_name=f'NotMatchFinpay_{st.session_state.mutasi_file_name}_{st.session_state.finpay_file_name}.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )

        if 'jurnal_template' in st.session_state:
            st.download_button(
                label="Download Template Jurnal",
                data=st.session_state.jurnal_template,
                file_name=f'TemplateJurnalFinpay_{st.session_state.mutasi_file_name}_{st.session_state.finpay_file_name}.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )

        if 'not_in_queries' in st.session_state:
            st.download_button(
                label="Download sisa data digipos",
                data=st.session_state.not_in_queries,
                file_name=f'NotUsedDigipos_{st.session_state.mutasi_file_name}_{st.session_state.finpay_file_name}.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )

    elif menu == "Rekonsiliasi Data LinkAja":
        st.title("Rekonsiliasi Data LinkAja")
        sub_menu = st.sidebar.selectbox('Pilih Sub Menu', ["Cleansing & Generate ID Tahap 1","Cleansing & Generate ID Tahap 2","Cleansing & Generate ID Tahap 3", "Rekon Data LinkAja", "Get Missing Data", "Cleans Match","Generate Template Sementara","Grouping & Generate Template V1","Grouping & Generate Template V2","Cleansing Reversal Link AJa"])

        if sub_menu == "Cleansing & Generate ID Tahap 1":

            cleans_linkaja_custom_id_main()
        
        elif sub_menu =="Cleansing & Generate ID Tahap 2":

            cleans_linkaja_custom_id_main_versi2_2()

        elif sub_menu == "Cleansing & Generate ID Tahap 3":
           
            cleans_linkaja_custom_id_kedua_main()

        elif sub_menu == "Rekon Data LinkAja":
           
            linkaja_file = select_linkaja_file()
            mutasi_file = select_linkaja_mutasi_file()
            location = select_location()

            if st.button("Lakukan Analisis"):
                try:
                    if linkaja_file is not None and mutasi_file is not None and location:
                        matched_data, unmatched_linkaja, unmatched_mutasi, jurnal_template = perform_linkaja_analysis(linkaja_file, mutasi_file, location)
                        st.session_state.result_query1_linkaja = convert_df_to_excel(matched_data)
                        st.session_state.result_query2_linkaja = convert_df_to_excel(unmatched_linkaja)
                        st.session_state.unmatched_mutasi = convert_df_to_excel(unmatched_mutasi)
                        st.session_state.jurnal_template_linkaja = convert_df_to_excel(jurnal_template)
                        st.success("Analisis berhasil dilakukan.")
                    else:
                        st.warning("Harap pilih kedua file dan lokasi.")
                except Exception as e:
                    st.error(f"Terjadi kesalahan: {str(e)}")

            if 'result_query1_linkaja' in st.session_state:
                st.download_button(
                    label="Download data LinkAja dan digipos match",
                    data=st.session_state.result_query1_linkaja,
                    file_name=f'Match_{st.session_state.mutasi_file_name}_{st.session_state.linkaja_file_name}.xlsx',
                    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )

            if 'result_query2_linkaja' in st.session_state:
                st.download_button(
                    label="Download data LinkAja not match",
                    data=st.session_state.result_query2_linkaja,
                    file_name=f'NotMatchLinkAJa_{st.session_state.mutasi_file_name}_{st.session_state.linkaja_file_name}.xlsx',
                    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )

            if 'unmatched_mutasi' in st.session_state:
                st.download_button(
                    label="Download data digipos not match",
                    data=st.session_state.unmatched_mutasi,
                    file_name=f'NotMatchDigipos_{st.session_state.mutasi_file_name}_{st.session_state.linkaja_file_name}.xlsx',
                    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
        elif sub_menu == "Get Missing Data":
            main_missing_data()

        elif sub_menu == "Cleans Match":
            main_Cleans_Match()

        elif sub_menu == "Generate Template Sementara":
            generate_jurnal_template_menu()

        elif sub_menu == "Grouping & Generate Template V1":
            st.header("Grouping dan Generate Template V1(UNTUK FILE CLEANSING DAN GENERATE ID TAHAP 1 DAN 2)")
            uploaded_file = st.file_uploader("Upload Excel File", type=['xlsx'])
            if uploaded_file is not None:
                invoice_date = st.date_input('Choose Invoice Date')
                due_date = st.date_input('Choose Due Date')
                invoice_month = st.selectbox('Choose Invoice Month', range(1, 13))
                invoice_year = st.selectbox('Choose Invoice Year', range(2020, 2031))
                invoice_month_year = "{:02d}/{:d}".format(invoice_month, invoice_year)  # Format bulan/tahun diubah di sini

                if st.button("Generate Template"):
                    try:
                        invoice_date_str = invoice_date.strftime('%d/%m/%Y')
                        due_date_str = due_date.strftime('%d/%m/%Y')
                        jurnal_template = generate_journal_template(uploaded_file, invoice_date_str, due_date_str, invoice_month_year)
                        uploaded_filename = uploaded_file.name
                        save_filename = f"TemplateJurnalFix_{uploaded_filename}"
                        st.download_button(
                            label="Download Journal Template",
                            data=convert_df_to_excel(jurnal_template),
                            file_name=save_filename,
                            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                        )
                    except Exception as e:
                        st.error(f"Terjadi kesalahan: {str(e)}")

        elif sub_menu == "Grouping & Generate Template V2":
            st.header("Grouping dan Generate Template V2(UNTUK FILE CLEANSING DAN GENERATE ID TAHAP 3)")
            uploaded_file = st.file_uploader("Upload Excel File", type=['xlsx'])
            if uploaded_file is not None:
                invoice_date = st.date_input('Choose Invoice Date')
                due_date = st.date_input('Choose Due Date')
                invoice_month = st.selectbox('Choose Invoice Month', range(1, 13))
                invoice_year = st.selectbox('Choose Invoice Year', range(2020, 2031))
                invoice_month_year = "{:02d}/{:d}".format(invoice_month, invoice_year)  # Format bulan/tahun diubah di sini

                if st.button("Generate Template"):
                    try:
                        invoice_date_str = invoice_date.strftime('%d/%m/%Y')
                        due_date_str = due_date.strftime('%d/%m/%Y')
                        jurnal_template = generate_journal_template_v2(uploaded_file, invoice_date_str, due_date_str, invoice_month_year)
                        uploaded_filename = uploaded_file.name
                        save_filename = f"TemplateJurnalFix_{uploaded_filename}"
                        st.download_button(
                            label="Download Journal Template",
                            data=convert_df_to_excel(jurnal_template),
                            file_name=save_filename,
                            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                        )
                    except Exception as e:
                        st.error(f"Terjadi kesalahan: {str(e)}")
        elif sub_menu == "Cleansing Reversal Link AJa":
            cleans_reversal_linkaja_main()

    elif menu == "Rekonsiliasi Data Bulk SA":
        st.title("Rekonsiliasi Data Bulk SA")
        sub_menu_3 = st.sidebar.selectbox('Pilih Sub Menu', ["Rekon Data Bulk SA","Cleansing & Generate ID","Cleansing & Generate ID 2","Generate Template Sementara","Generate Template Jurnal","Rekon Finpay dan BulkSa"])

        if sub_menu_3 == "Rekon Data Bulk SA":
            rekon_bulkSA()

        elif sub_menu_3 == "Cleansing & Generate ID":
            cleans_linkaja_custom_id_main_BulkSA()
        
        elif sub_menu_3 == "Generate Template Jurnal":
            bulk_jurnal()
        
        elif sub_menu_3 == "Rekon Finpay dan BulkSa":
            finpay_vs_Bulks()
        elif sub_menu_3 == "Cleansing & Generate ID 2":
            complition_time_Bulk2()
        elif sub_menu_3 == "Generate Template Sementara":
            main_jurnal_template()

    elif menu == "Template Jurnal Cirebon":
        st.title('Template Jurnal Cirebon')
        sub_menu_2 = st.sidebar.selectbox('Pilih Sub Menu', ["Generate Jurnal Template Penjualan","Generate Jurnal Template Payment","Generate Jurnal Template Pembelian","Cleansing Cirebon"])
        if sub_menu_2 == "Generate Jurnal Template Penjualan":
            penjualanCirebon()

        elif sub_menu_2 == "Generate Jurnal Template Payment":
            paymentCirebon()
        elif sub_menu_2 == "Generate Jurnal Template Pembelian":
            pembelianCirebon()
        elif sub_menu_2 == "Cleansing Cirebon":
            cirebonCleansing()


        

if __name__ == "__main__":
    main()

