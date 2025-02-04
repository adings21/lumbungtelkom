import streamlit as st
import pandas as pd
from dateutil import parser
import locale

# Set locale untuk format mata uang (ID untuk Indonesia)
locale.setlocale(locale.LC_ALL, 'id_ID.UTF-8')

def parse_date(date_str):
    try:
        return parser.parse(date_str, dayfirst=True).strftime('%d/%m/%Y')
    except Exception as e:
        st.write(f"Kesalahan parsing tanggal: {e} pada nilai: {date_str}")
        return None

def perform_analysis(finpayKolaka, mutasi_kolaka_sebulan, location):
    finpayKolaka.columns = [
        'No', 'Transaction Date', 'Transaction ID', 'Saldo Awal', 'Kredit',
        'Debet', 'Saldo Akhir', 'Transaction Type', 'Transaction', 'Remarks'
    ]
    mutasi_kolaka_sebulan.columns = [
        'Receipt No.', 'Completion Time', 'Initiation Time', 'Details',
        'Transaction Status', 'Currency', 'Paid In', 'Withdrawn', 'Balance',
        'Reason Type', 'Opposite Party', 'Linked Transaction ID'
    ]

    finpayKolaka['Transaction Date'] = finpayKolaka['Transaction Date'].astype(str).str.split(' ').str[0]
    ## mutasi_kolaka_sebulan['Completion Time'] = mutasi_kolaka_sebulan['Completion Time'].astype(str).str.split(' ').str[0]

    finpayKolaka['Transaction ID'] = finpayKolaka['Transaction ID'].astype(str).str.replace('F_', '')
    mutasi_kolaka_sebulan['Receipt No.'] = mutasi_kolaka_sebulan['Receipt No.'].astype(str).apply(lambda x: x.zfill(20))

    st.write("Jumlah data di Finpay:", len(finpayKolaka))
    st.write("Jumlah data di Mutasi:", len(mutasi_kolaka_sebulan))

    # Query 1: Data yang match
    merged_data = pd.merge(
        finpayKolaka,
        mutasi_kolaka_sebulan,
        left_on='Transaction ID',
        right_on='Receipt No.',
        how='inner'
    )
    result_query1 = merged_data[merged_data['Kredit'].astype(float) != 0]
    # Query 2: Data Finpay yang tidak match ditambah yang Kredit-nya 0 dari query 1
    left_joined_data = pd.merge(
        finpayKolaka,
        mutasi_kolaka_sebulan,
        left_on='Transaction ID',
        right_on='Receipt No.',
        how='left'
    )
    result_query2 = left_joined_data[left_joined_data['Receipt No.'].isna()]
    # Menambahkan data dari query 1 yang Kredit-nya 0 ke hasil query 2
    query1_kredit_0 = merged_data[merged_data['Kredit'].astype(float) == 0]
    result_query2 = pd.concat([result_query2, query1_kredit_0], ignore_index=True)

    st.write("Jumlah data query1 (match):", len(result_query1))
    st.write("Jumlah data query2 (not match):", len(result_query2))
    
    jumlah_sisa_data_finpay = len(finpayKolaka) - len(result_query1) - len(result_query2)
    st.write(f"Jumlah sisa data finpay: {jumlah_sisa_data_finpay}")

    # Query 3: Data dari mutasi_kolaka_sebulan yang tidak terambil di query 1 dan 2
    not_in_query1_or_query2 = mutasi_kolaka_sebulan[
        ~mutasi_kolaka_sebulan['Receipt No.'].isin(result_query1['Receipt No.']) &
        ~mutasi_kolaka_sebulan['Receipt No.'].isin(result_query2['Receipt No.'])
    ]

    st.write("Jumlah sisa data digipos:", len(not_in_query1_or_query2))
    st.write("Detail data file sisa digipos:")
    st.write(not_in_query1_or_query2)

    result_query1 = result_query1[[
        'No', 'Transaction Date', 'Transaction ID', 'Saldo Awal', 'Kredit',
        'Debet', 'Saldo Akhir', 'Transaction Type', 'Transaction', 'Remarks',
        'Receipt No.', 'Opposite Party', 'Withdrawn', 'Completion Time'
    ]]
    result_query2 = result_query2[[
        'No', 'Transaction Date', 'Transaction ID', 'Saldo Awal', 'Kredit',
        'Debet', 'Saldo Akhir', 'Transaction Type', 'Transaction', 'Remarks'
    ]]

    # Menambahkan kolom 'total' ke jurnal_template
    result_query1['*Quantity'] = (result_query1['Withdrawn'].abs() / 1000)
    result_query1['*UnitPrice'] = result_query1['Kredit'] / result_query1['*Quantity']
    result_query1['total'] = result_query1['*UnitPrice'] * result_query1['*Quantity']
    result_query1['Transaction Date'] = result_query1['Transaction Date'].apply(parse_date)
    result_query1['Completion Time'] = result_query1['Completion Time'].apply(parse_date)

    jurnal_template = pd.DataFrame({
        '*Customer': result_query1['Opposite Party'],
        'Email': '',
        'BillingAddress': '',
        'ShippingAddress': '',
        '*InvoiceDate': result_query1['Transaction Date'],
        '*DueDate': result_query1['Completion Time'],
        'ShippingDate': '',
        'ShipVia': '',
        'TrackingNo': '',
        'CustomerRefNo': '',
        '*InvoiceNumber': result_query1['Receipt No.'].apply(lambda x: f"{location.lower()}_{x}"),
        'Message': '',
        'Memo': '',
        '*ProductName': 'Voucherless Bulk 10JT NGRS - Mitra SBP (V841)',
        'Description': '',
        '*Quantity': result_query1['*Quantity'],
        'Unit': '',
        '*UnitPrice': result_query1['*UnitPrice'],
        'total': result_query1['total'],
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
        'Tags (use ; to separate tags)': f'Finpay, {location}',
        'WarehouseName': location,
        '#currency code(example: IDR, USD, CAD)': ''
    })

    # Filter jurnal_template untuk menghapus baris dengan *UnitPrice = 0
    jurnal_template = jurnal_template.dropna(subset=['*UnitPrice'])

    # Log untuk jumlah baris template jurnal
    st.write("Jumlah baris template jurnal:", len(jurnal_template))
   
    # Log untuk jumlah rupiah dari sum kolom kredit di file hasil match
    total_kredit = result_query1['Kredit'].astype(float).sum()
    st.write("Total kredit di file hasil match: Rp {:,.2f}".format(total_kredit))

    # Log untuk sum dari hasil kolom 'total'
    total_sum = result_query1['total'].astype(float).sum()
    st.write("Total sum kolom 'total' di jurnal template: Rp {:,.2f}".format(total_sum))

    return result_query1, result_query2, jurnal_template, not_in_query1_or_query2

def select_finpay_file():
    finpay_file = st.file_uploader("Pilih File Finpay (Pastikan terdapat saldo akhir)", type=['xlsx'])
    if finpay_file:
        st.session_state.finpay_file_name = finpay_file.name
        finpay_df = pd.read_excel(finpay_file, skiprows=1)
    else:
        finpay_df = None
    return finpay_df

def select_mutasi_file():
    mutasi_file = st.file_uploader("Pilih File Digipos (Pastikan tidak terdapat header!)", type=['xlsx'])
    if mutasi_file:
        st.session_state.mutasi_file_name = mutasi_file.name
        mutasi_df = pd.read_excel(mutasi_file)
    else:
        mutasi_df = None
    return mutasi_df

def select_location():
    location = st.sidebar.radio("Pilih Lokasi", ['Kolaka', 'Kendari'])
    st.session_state.location = location
    return location

# Menampilkan UI untuk mengunggah file
finpayKolaka = select_finpay_file()
mutasi_kolaka_sebulan = select_mutasi_file()
location = select_location()

if finpayKolaka is not None and mutasi_kolaka_sebulan is not None:
    result_query1, result_query2, jurnal_template, not_in_query1_or_query2 = perform_analysis(finpayKolaka, mutasi_kolaka_sebulan, location)

    st.write("Query 1 - Data yang match:")
    st.write(result_query1)
    
    st.write("Query 2 - Data Finpay yang tidak match:")
    st.write(result_query2)

    st.write("Template Jurnal:")
    st.write(jurnal_template)

    st.write("Data sisa dari Digipos:")
    st.write(not_in_query1_or_query2)

    st.download_button("Download Hasil Query 1", result_query1.to_csv(index=False), "query1_result.csv", "text/csv")
    st.download_button("Download Hasil Query 2", result_query2.to_csv(index=False), "query2_result.csv", "text/csv")
    st.download_button("Download Template Jurnal", jurnal_template.to_csv(index=False), "jurnal_template.csv", "text/csv")
    st.download_button("Download Sisa Data Digipos", not_in_query1_or_query2.to_csv(index=False), "not_in_query1_or_query2.csv", "text/csv")
