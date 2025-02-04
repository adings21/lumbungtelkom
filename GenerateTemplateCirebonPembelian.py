import pandas as pd
import streamlit as st
from babel.numbers import format_decimal
from io import BytesIO
import locale
import os

# Mengatur locale untuk format angka
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
        return "Terdapat Kode di Product Name yang tidak Terdaftar"
    else:
        return "Kode tidak terdaftar"

def format_date(date_str):
    try:
        return pd.to_datetime(date_str).strftime('%d/%m/%Y')
    except Exception as e:
        st.error(f"Error in date format: {e}")
        return date_str

def format_number(value):
    # Menghilangkan separator ribuan dan menggunakan titik sebagai pemisah desimal
    if pd.isnull(value):
        return ""
    try:
        return format_decimal(value, locale='id_ID').replace('.', '').replace(',', '.')
    except Exception as e:
        st.error(f"Error in number formatting: {e}")
        return value

def generate_journal_template_Pembelian(df, lokasi):
    rows = []
    unregistered_rows = []
    for index, row in df.iterrows():
        product_name = map_product_name(row['kode_group'])
        if product_name == "Terdapat Kode di Product Name yang tidak Terdaftar" or product_name == "Kode tidak terdaftar":
            unregistered_rows.append(row)
            continue
        purchase_date = format_date(row['tgl_system'])
        quantity = row['berat'] * 1000
        unit_price = row['harga_rata'] / 1000
        rows.append({
            "*Vendor": f"{row['kode_member']}_{row['nama_customer']}",
            "Email": "",
            "BillingAddress": row['alamat_customer'],
            "ShippingAddress": "",
            "*PurchaseDate": purchase_date,
            "*DueDate": purchase_date,
            "ShippingDate": "",
            "ShipVia": "",
            "TrackingNo": "",
            "VendorRefNo": "",
            "*PurchaseNumber": row['no_fakturbeli'],
            "Message": "",
            "Memo": "",
            "*ProductName": product_name,
            "Description": f"{row['nama_barang']} ({row['berat_nota']} gram)",
            "*Quantity": format_number(quantity),
            "Unit": "",
            "*UnitPrice": format_number(unit_price),
            "ProductDiscountRate(%)": "",
            "PurchaseDiscountRate(%)": "",
            "TaxName": "",
            "TaxRate(%)": "",
            "ShippingFee": "",
            "WitholdingAccountCode": "",
            "WitholdingAmount(value or %)": "",
            "#paid?(yes/no)": "YES" if row['cash_rp'] > 0 else "",
            "#PaymentMethod": "CASH" if row['cash_rp'] > 0 else "",
            "#PaidFromAccountCode": "1-110003" if lokasi == "DAMAI" else "1-110004" if lokasi == "CANTIK" else "1-110005" if lokasi == "POJOK" else "",
            "Tags (use ; to separate tags)": f"{lokasi},{row['kode_sales']},{row['kondisi']},BUYBACK",
            "WarehouseName": lokasi,
            "#currency code(example: IDR,USD,CAD)": ""
        })

    jurnal_template = pd.DataFrame(rows)
    unregistered_template = pd.DataFrame(unregistered_rows)

    return jurnal_template, unregistered_template

def convert_df_to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Sheet1')
    writer.close()
    processed_data = output.getvalue()
    return processed_data

def mainPembelian():
    st.title('Template Jurnal Pembelian')
    
    lokasi = st.selectbox('Pilih Lokasi', ['DAMAI', 'CANTIK', 'POJOK'])
    uploaded_file = st.file_uploader("Unggah file Excel", type=["xlsx"])

    if uploaded_file is not None:
        df = pd.read_excel(uploaded_file)
        filename = os.path.splitext(uploaded_file.name)[0]
        jurnal_template, unregistered_template = generate_journal_template_Pembelian(df, lokasi)
        st.dataframe(jurnal_template)

        excel_data = convert_df_to_excel(jurnal_template)
        download_filename = f'JurnalTemplatePembelian_{filename}.xlsx'
        st.download_button(
            label="Unduh Jurnal Template",
            data=excel_data,
            file_name=download_filename
        )

        if not unregistered_template.empty:
            st.dataframe(unregistered_template)
            unregistered_excel_data = convert_df_to_excel(unregistered_template)
            unregistered_download_filename = f'UnregisteredCodesPembelian_{filename}.xlsx'
            st.download_button(
                label="Unduh Data Kode Tidak Terdaftar",
                data=unregistered_excel_data,
                file_name=unregistered_download_filename
            )

if __name__ == "__main__":
    mainPembelian()
