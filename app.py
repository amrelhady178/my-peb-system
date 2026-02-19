import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from datetime import datetime

# --- إنشاء قاعدة البيانات ---
def create_db():
    conn = sqlite3.connect('peb_system.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS projects 
                 (id TEXT, date TEXT, engineer TEXT, p_name TEXT, client TEXT, 
                  tonnage REAL, value REAL, status TEXT, revision INTEGER)''')
    conn.commit()
    conn.close()

create_db()

# --- نظام تسجيل الدخول ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

def login_screen():
    st.title("🏗️ PEB Management System")
    user = st.text_input("Username")
    pw = st.text_input("Password", type="password")
    if st.button("Login"):
        users = {"eng_ahmed": "123", "eng_mohamed": "456", "admin": "admin789"}
        if user in users and users[user] == pw:
            st.session_state.logged_in = True
            st.session_state.username = user
            st.rerun()
        else:
            st.error("بيانات الدخول غير صحيحة")

if not st.session_state.logged_in:
    login_screen()
    st.stop()

# --- واجهة البرنامج والـ Dashboard ---
st.sidebar.title(f"User: {st.session_state.username}")
menu = ["Dashboard", "Add Quotation"]
choice = st.sidebar.selectbox("Menu", menu)

if choice == "Dashboard":
    conn = sqlite3.connect('peb_system.db')
    df = pd.read_sql_query("SELECT * FROM projects", conn)
    conn.close()

    if not df.empty:
        st.header(f"📊 Dashboard - Welcome {st.session_state.username}")
        col1, col2 = st.columns(2)
        col1.metric("Total Quotations", len(df))
        col2.metric("Total Tonnage", f"{df['tonnage'].sum()} Tons")
        
        fig = px.bar(df, x='engineer', color='status', title="Performance by Engineer")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("لا توجد مشاريع مسجلة حتى الآن.")

elif choice == "Add Quotation":
    st.subheader("إضافة عرض سعر جديد")
    with st.form("add_form"):
        p_name = st.text_input("Project Name")
        client = st.text_input("Client")
        tonnage = st.number_input("Tonnage", min_value=0.0)
        value = st.number_input("Value (EGP)", min_value=0.0)
        status = st.selectbox("Status", ["Under Study", "Submitted", "Won", "Lost"])
        rev = st.number_input("Revision", min_value=0)
        
        if st.form_submit_button("Submit"):
            conn = sqlite3.connect('peb_system.db')
            c = conn.cursor()
            p_id = f"PEB-{datetime.now().strftime('%y%m%d%H%M')}"
            c.execute("INSERT INTO projects VALUES (?,?,?,?,?,?,?,?,?)",
                      (p_id, datetime.now().strftime("%Y-%m-%d"), st.session_state.username, 
                       p_name, client, tonnage, value, status, rev))
            conn.commit()
            conn.close()
            st.success("تم تسجيل المشروع بنجاح!")

if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.rerun()