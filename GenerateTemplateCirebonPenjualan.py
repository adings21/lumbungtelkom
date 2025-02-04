import pandas as pd
import streamlit as st
from babel.numbers import format_decimal
from io import BytesIO
import locale

# Set locale for number formatting
locale.setlocale(locale.LC_ALL, 'id_ID.UTF-8')

def map_product_name(kode):
    mapping = {
        "16K-K": "Emas Tua 16K", "16K-T": "Emas Tua 16K",
        "17K-K": "Emas Tua 17K", "17K-T": "Emas Tua 17K",
        "24K-K": "Emas Tua 24K", "24K-T": "Emas Tua 24K",
        "6K-K": "Emas Muda 6K", "6K-T": "Emas Muda 6K",
        "8K-K": "Emas Muda 8K", "8K-T": "Emas Muda 8K",
        "9K-K": "Emas Muda 9K", "9K-T": "Emas Muda 9K",
        "BT16K": "Emas Tua 16K", "BT17K": "Emas Tua 17K",
        "BT24K": "Emas Tua 24K", "BT6K": "Emas Muda 6K",
        "BT8K": "Emas Muda 8K", "BT9K": "Emas Muda 9K",
        "BTLM": "Logam Mulia", "BTSM": "Emas Muda SM",
        "LM": "Logam Mulia", "LM-K": "Logam Mulia",
        "LM-T": "Logam Mulia", "LMATM": "Logam Mulia",
        "LMHTA": "Logam Mulia", "LMLTS": "Logam Mulia",
        "LMUBS": "Logam Mulia", "SK24K": "Emas Tua 24K",
        "SK300": "Emas Muda 6K", "SK375": "Emas Muda 8K",
        "SK420": "Emas Muda 9K", "SK4M": "Emas Muda 9K",
        "SK700": "Emas Tua 16K", "SK750": "Emas Tua 17K",
        "SKOB": "Emas Muda 6K", "SKSM": "Emas Muda SM",
        "SKUKN": "Emas Muda 8K", "SKUKT": "Emas Muda 8K",
        "SM-K": "Emas Muda SM", "SM-T": "Emas Muda SM",
        "ST300": "Emas Muda 6K", "ST375": "Emas Muda 8K",
        "ST420": "Emas Muda 9K", "ST700": "Emas Tua 16K",
        "ST750": "Emas Tua 17K", "STNC": "Emas Muda 8K",
        "STOB": "Emas Muda 6K", "STSM": "Emas Muda SM"
    }
    if kode in mapping:
        return mapping[kode]
    elif kode in {"18K", "22K", "24K", "ACC", "BTOKO", "LTT30", "SKMX", "SKT22", "STMX"}:
        return None  # Kode yang tidak terdaftar
    else:
        return "Kode tidak terdaftar"  # Kode yang tidak dikenali

def generate_journal_template_Penjualan(df, location, log=True):
    df = df[df['tukar rp'] == 0]
    # Mapping lokasi to account codes and tags
    location_mapping = {
        'Toko Damai': ('1-110003', 'DAMAI'),
        'Toko Cantik': ('1-110004', 'CANTIK'),
        'Toko Pojok': ('1-110005', 'POJOK')
    }

    paid_to_account_code, location_tag = location_mapping[location]
    # Ubah format tanggal ke '%d/%m/%Y' jika formatnya adalah '%d/%m/%Y'
    if pd.api.types.is_string_dtype(df['tgl system']):
        df['tgl system'] = pd.to_datetime(df['tgl system'], format='%d/%m/%Y').dt.strftime('%d/%m/%Y')
    else:
        df['tgl system'] = pd.to_datetime(df['tgl system']).dt.strftime('%d/%m/%Y')
    # Generate journal_template DataFrame
    jurnal_template = pd.DataFrame({
        '*Customer': df['kode member'].astype(str) + '_' + df['nama customer'].astype(str),
        'Email': '',
        'BillingAddress': df['alamat customer'],
        'ShippingAddress': '',
        '*InvoiceDate': df['tgl system'],
        '*DueDate': df['tgl system'],
        'ShippingDate': '',
        'ShipVia': '',
        'TrackingNo': '',
        'CustomerRefNo': '',
        '*InvoiceNumber': df['no fakturjual'],
        'Message': '',
        'Memo': '',
        '*ProductName': df['kode group'].apply(map_product_name),
        'Description': df['nama barang'],
        '*Quantity': df['berat'] * 1000,  # Ensure numeric, multiply by 1000
        'Unit': '',
        '*UnitPrice': df['harga gram'] / 1000,  # Ensure numeric, divide by 1000
        'ProductDiscountRate(%)': '',
        'InvoiceDiscountRate(%)': '',
        'TaxName': '',
        'TaxRate(%)': '',
        'ShippingFee': '',
        'WitholdingAccountCode': '',
        'WitholdingAmount(value or %)': '',
        '#paid?(yes/no)': df.apply(lambda x: 'YES' if x['cash rp'] > 0 and (x['transfer rp'] == 0 and x['debet rp'] == 0) else '', axis=1),
        '#PaymentMethod':  df.apply(lambda x: 'CASH' if x['cash rp'] > 0 and (x['transfer rp'] == 0 and x['debet rp'] == 0) else '', axis=1),
        '#PaidToAccountCode': df.apply(lambda x: paid_to_account_code if x['cash rp'] > 0 and (x['transfer rp'] == 0 and x['debet rp'] == 0) else '', axis=1),
        'Tags (use ; to separate tags)': location_tag + ',' + df['kode sales'],
        'WarehouseName': location_tag,
        '#currency code(example: IDR, USD, CAD)': ''
    })
    
    # Add additional rows based on "ongkos" and "harga atribut"
    additional_rows = []

    for index, row in df.iterrows():
        invoice_number = str(row['no fakturjual'])  # Convert to string
        if row['ongkos'] > 0:
            additional_rows.append({
                '*Customer': str(row['kode member']) + '_' + str(row['nama customer']),
                'Email': '',
                'BillingAddress': str(row['alamat customer']),
                'ShippingAddress': '',
                '*InvoiceDate': str(row['tgl system']),
                '*DueDate': str(row['tgl system']),
                'ShippingDate': '',
                'ShipVia': '',
                'TrackingNo': '',
                'CustomerRefNo': '',
                '*InvoiceNumber': invoice_number,
                'Message': '',
                'Memo': '',
                '*ProductName': 'ONGKOS PENJUALAN',
                'Description': str(row['nama barang']),
                '*Quantity': 1,
                'Unit': '',
                '*UnitPrice': float(row['ongkos']),
                'ProductDiscountRate(%)': '',
                'InvoiceDiscountRate(%)': '',
                'TaxName': '',
                'TaxRate(%)': '',
                'ShippingFee': '',
                'WitholdingAccountCode': '',
                'WitholdingAmount(value or %)': '',
                '#paid?(yes/no)': 'YES' if row['cash rp'] > 0 and (row['transfer rp'] == 0 and row['debet rp'] == 0) else '',
                '#PaymentMethod': 'CASH' if row['cash rp'] > 0 and (row['transfer rp'] == 0 and row['debet rp'] == 0) else '',
                '#PaidToAccountCode': paid_to_account_code if row['cash rp'] > 0 and (row['transfer rp'] == 0 and row['debet rp'] == 0) else '',
                'Tags (use ; to separate tags)': location_tag + ',' + str(row['kode sales']),
                'WarehouseName': location_tag,
                '#currency code(example: IDR, USD, CAD)': ''
            })
        if row['harga atribut'] > 0:
            additional_rows.append({
                '*Customer': str(row['kode member']) + '_' + str(row['nama customer']),
                'Email': '',
                'BillingAddress': str(row['alamat customer']),
                'ShippingAddress': '',
                '*InvoiceDate': str(row['tgl system']),
                '*DueDate': str(row['tgl system']),
                'ShippingDate': '',
                'ShipVia': '',
                'TrackingNo': '',
                'CustomerRefNo': '',
                '*InvoiceNumber': invoice_number,
                'Message': '',
                'Memo': '',
                '*ProductName': 'PENDAPATAN ATRIBUT',
                'Description': str(row['nama barang']),
                '*Quantity': 1,
                'Unit': '',
                '*UnitPrice': float(row['harga atribut']),
                'ProductDiscountRate(%)': '',
                'InvoiceDiscountRate(%)': '',
                'TaxName': '',
                'TaxRate(%)': '',
                'ShippingFee': '',
                'WitholdingAccountCode': '',
                'WitholdingAmount(value or %)': '',
                '#paid?(yes/no)': 'YES' if row['cash rp'] > 0 and (row['transfer rp'] == 0 and row['debet rp'] == 0) else '',
                '#PaymentMethod': 'CASH' if row['cash rp'] > 0 and (row['transfer rp'] == 0 and row['debet rp'] == 0) else '',
                '#PaidToAccountCode': paid_to_account_code if row['cash rp'] > 0 and (row['transfer rp'] == 0 and row['debet rp'] == 0) else '',
                'Tags (use ; to separate tags)': location_tag + ',' + str(row['kode sales']),
                'WarehouseName': location_tag,
                '#currency code(example: IDR, USD, CAD)': ''
            })

    additional_df = pd.DataFrame(additional_rows)
    jurnal_template = pd.concat([jurnal_template, additional_df], ignore_index=True)
    # Remove columns that are not defined in the template
    jurnal_template = jurnal_template[['*Customer', 'Email', 'BillingAddress', 'ShippingAddress', '*InvoiceDate', '*DueDate', 'ShippingDate', 'ShipVia', 'TrackingNo', 'CustomerRefNo', '*InvoiceNumber', 'Message', 'Memo', '*ProductName', 'Description', '*Quantity', 'Unit', '*UnitPrice', 'ProductDiscountRate(%)', 'InvoiceDiscountRate(%)', 'TaxName', 'TaxRate(%)', 'ShippingFee', 'WitholdingAccountCode', 'WitholdingAmount(value or %)', '#paid?(yes/no)', '#PaymentMethod', '#PaidToAccountCode', 'Tags (use ; to separate tags)', 'WarehouseName', '#currency code(example: IDR, USD, CAD)']]

    if log:
        # Logging total Cash Rp
        total_cash_rp = df['cash rp'].sum()
        st.write(f"Total Cash Rp: Rp {format_decimal(total_cash_rp, locale='id_ID')}")

        # Logging total nilai tukar tambah
        total_nilai_tukar_tambah = df[df['tukar rp'] > 0]['cash rp'].sum()
        st.write(f"Total nilai tukar tambah: Rp {format_decimal(total_nilai_tukar_tambah, locale='id_ID')}")

        # Logging total Cash Rp di template jurnal
        total_cash_rp_jurnal = (jurnal_template.loc[jurnal_template['#paid?(yes/no)'] == 'YES', '*Quantity'] *
                                jurnal_template.loc[jurnal_template['#paid?(yes/no)'] == 'YES', '*UnitPrice']).sum()
        st.write(f"Total Cash Rp di template jurnal: Rp {format_decimal(total_cash_rp_jurnal, locale='id_ID')}")

         # Logging jumlah baris file input
        st.write(f"Jumlah baris file cirebon penjualan(inputan): {len(df)}")

        # Logging jumlah baris output
        st.write(f"Jumlah baris jurnal template: {len(jurnal_template)}")

    

    
    # Log if there are any non-mapped product codes
    non_mapped_codes = df['kode group'][df['kode group'].apply(map_product_name).isnull()]
    if not non_mapped_codes.empty:
        st.write("Terdapat kode yang tidak terdaftar:")
        for code in non_mapped_codes.unique():
            st.write(code)
    else:
        st.write("Kode group untuk kolom Product Name semua terdaftar")

    # Memformat *Quantity dan *UnitPrice dengan desimal titik dan tanpa pemisah ribuan
    jurnal_template['*Quantity'] = jurnal_template['*Quantity'].apply(lambda x: f"{x:.{len(str(x).split('.')[1])}f}" if '.' in str(x) else str(x))
    jurnal_template['*UnitPrice'] = jurnal_template['*UnitPrice'].apply(lambda x: f"{x:.{len(str(x).split('.')[1])}f}" if '.' in str(x) else str(x))


    return jurnal_template

def generate_journal_template_TukarTambah(df, location):
    # Filtering for tukar tambah
    df_tukar_tambah = df[df['tukar rp'] > 0]

    return df_tukar_tambah

def convert_df_to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Sheet1')
    writer.close()  # Use close instead of save
    processed_data = output.getvalue()
    return processed_data

def generate_non_mapped_data(df):
    non_mapped_codes = df['kode group'][df['kode group'].apply(map_product_name).isnull()]
    if not non_mapped_codes.empty:
        non_mapped_data = df[df['kode group'].isin(non_mapped_codes)]
        return non_mapped_data
    else:
        return pd.DataFrame()

def mainPenjualan():
    st.title('Generate Jurnal Template Penjualan')
    location = st.selectbox('Pilih Lokasi', ['Toko Damai', 'Toko Cantik', 'Toko Pojok'])
    uploaded_file = st.file_uploader('Upload file penjualans', type=['csv', 'xlsx'])
    if uploaded_file:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        if st.button('Generate Template'):
            st.session_state.generated = True  # Update session state ketika template sudah dihasilkan
            jurnal_template = generate_journal_template_Penjualan(df, location)
            st.session_state.jurnal_template = convert_df_to_excel(jurnal_template)
            st.write('Generated Journal Template')
            st.dataframe(jurnal_template)
            jurnal_template_tukar_tambah = generate_journal_template_TukarTambah(df, location)
            st.session_state.jurnal_template_tukar_tambah = convert_df_to_excel(jurnal_template_tukar_tambah)
            st.write('Generated Journal Template Tukar Tambah')
            st.dataframe(jurnal_template_tukar_tambah)
            
            # Generate non-mapped data
            non_mapped_data = generate_non_mapped_data(df)
            if not non_mapped_data.empty:
                st.write("Data dengan kode yang tidak terdaftar:")
                st.dataframe(non_mapped_data)
                non_mapped_excel = convert_df_to_excel(non_mapped_data)
                st.download_button(
                    label='Download Non-Mapped Data as Excel',
                    data=non_mapped_excel,
                    file_name=f'non_mapped_data_{uploaded_file.name}',
                    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    key='download_non_mapped_data'
                )

    # Tambahkan tombol unduhan jika template sudah dihasilkan
    if st.session_state.get('generated'):
        st.download_button(
            label='Download Journal Template as Excel',
            data=st.session_state.jurnal_template,
            file_name=f'jurnal_template_Penjualan_{uploaded_file.name}',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            key='download_journal_template_generated'
        )

        st.download_button(
            label='Download Journal Template Tukar Tambah as Excel',
            data=st.session_state.jurnal_template_tukar_tambah,
            file_name=f'TukarTambah_{uploaded_file.name}',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            key='download_journal_template_tukar_tambah_generated'
        )

if __name__ == "__main__":
    mainPenjualan()