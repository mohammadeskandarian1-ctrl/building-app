import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

st.set_page_config(
    page_title="مدیریت ساخت‌وساز | مهندس اسکندریان",
    page_icon="🏗️",
    layout="centered"
)

def get_db_connection():
    conn = sqlite3.connect("building_costs.db")
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            amount REAL,
            payment_method TEXT,
            purpose TEXT,
            stage TEXT,
            product_name TEXT,
            quantity TEXT,
            dimensions TEXT,
            shop_address TEXT,
            destination_address TEXT,
            market_price REAL,
            transaction_price REAL
        )
    """)
    conn.commit()
    conn.close()

init_db()

st.title("🏗️ سامانه مدیریت هزینه")
st.caption("توسعه داده شده برای: **مهندس محمد اسکندریان**")
st.divider()

tab1, tab2, tab3 = st.tabs(["➕ ثبت فاکتور جدید", "📊 مشاهده و جستجو", "📥 خروجی اکسل"])

with tab1:
    st.subheader("ثبت هزینه جدید")
    
    with st.form("expense_form", clear_on_submit=True):
        date_val = st.date_input("تاریخ", datetime.today())
        amount_val = st.number_input("مبلغ کل (تومان)", min_value=0, step=100000)
        purpose_val = st.text_input("دلیل خرید / بابت")
        stage_val = st.selectbox("مرحله ساخت", ["فونداسیون", "اسکلت و سقف", "سفت‌کاری", "نازک‌کاری", "تأسیسات", "متفرقه"])
        
        product_val = st.text_input("نام محصول / مصالح")
        quantity_val = st.text_input("تعداد / متراژ / تناژ")
        payment_val = st.selectbox("نحوه پرداخت", ["نقد", "کارت به کارت", "چک", "پایا / ساتنا"])
        
        with st.expander("جزئیات بیشتر (اختیاری)"):
            dimensions_val = st.text_input("ابعاد / مشخصات فنی")
            shop_val = st.text_input("نام / آدرس فروشگاه")
            dest_val = st.text_input("محل تحویل / مقصد")
            market_price_val = st.number_input("قیمت پایه بازار", min_value=0)
            trans_price_val = st.number_input("قیمت معامله شده", min_value=0)

        submitted = st.form_submit_button("💾 ثبت فاکتور در سیستم", use_container_width=True)
        
        if submitted:
            if amount_val > 0 and purpose_val:
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO expenses (
                        date, amount, payment_method, purpose, stage,
                        product_name, quantity, dimensions, shop_address,
                        destination_address, market_price, transaction_price
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    str(date_val), amount_val, payment_val, purpose_val,
                    stage_val, product_val, quantity_val, dimensions_val,
                    shop_val, dest_val, market_price_val, trans_price_val
                ))
                conn.commit()
                conn.close()
                st.success("✅ فاکتور با موفقیت در دیتابیس ثبت شد!")
            else:
                st.error("لطفاً مبلغ و بابت خرید را وارد کنید.")

with tab2:
    st.subheader("لیست هزینه‌ها")
    
    conn = get_db_connection()
    df = pd.read_sql_query("SELECT id, date, amount, purpose, stage, product_name, payment_method FROM expenses ORDER BY id DESC", conn)
    conn.close()
    
    if not df.empty:
        search = st.text_input("🔍 جستجو در فاکتورها")
        if search:
            df = df[df.apply(lambda row: row.astype(str).str.contains(search, case=False).any(), axis=1)]
        
        total = df['amount'].sum()
        st.metric(label="مجموع هزینه‌های نمایش داده شده", value=f"{int(total):,} تومان")
        
        st.dataframe(df, use_container_width=True)
    else:
        st.info("هنوز هیچ هزینه‌ای ثبت نشده است.")

with tab3:
    st.subheader("دانلود گزارش کامل")
    conn = get_db_connection()
    df_full = pd.read_sql_query("SELECT * FROM expenses", conn)
    conn.close()
    
    if not df_full.empty:
        excel_path = "building_costs.xlsx"
        df_full.to_excel(excel_path, index=False)
        
        with open(excel_path, "rb") as file:
            st.download_button(
                label="📥 دانلود فایل اکسل (Excel)",
                data=file,
                file_name="building_costs_report.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
