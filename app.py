import streamlit as st
import pandas as pd
import sqlite3
import json
from datetime import datetime

# --- إعدادات الصفحة ---
st.set_page_config(page_title="Sales Bay - PEB System", layout="wide", initial_sidebar_state="collapsed")

# --- قاعدة البيانات ---
def create_db():
    conn = sqlite3.connect('peb_system.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS quotations 
                 (quotation_no TEXT PRIMARY KEY, quote_date TEXT, country TEXT, 
                  sales_rep TEXT, project_name TEXT, location TEXT, buildings INTEGER, 
                  scope TEXT, client_type TEXT, client_company TEXT, client_contact TEXT, 
                  client_mobile TEXT, client_email TEXT, client_address TEXT,
                  consultant_office TEXT, consultant_contact TEXT, consultant_mobile TEXT, 
                  consultant_email TEXT, consultant_address TEXT,
                  pricing_base TEXT, steel_weight REAL, steel_amount REAL, total_value REAL, 
                  items_data TEXT, status TEXT)''')
    
    try: c.execute("ALTER TABLE quotations ADD COLUMN steel_amount REAL DEFAULT 0.0")
    except: pass
    try: c.execute("ALTER TABLE quotations ADD COLUMN total_value REAL DEFAULT 0.0")
    except: pass
    
    conn.commit()
    conn.close()

create_db()

# --- دوال مساعدة ---
countries_map = {
    "Egypt": "EG", "Saudi Arabia": "SA", "Libya": "LY", "United Arab Emirates": "AE", 
    "Qatar": "QA", "Kuwait": "KW", "Oman": "OM", "Jordan": "JO", "Iraq": "IQ", "Sudan": "SD"
}

def get_next_serial():
    conn = sqlite3.connect('peb_system.db')
    c = conn.cursor()
    c.execute("SELECT quotation_no FROM quotations")
    records = c.fetchall()
    conn.close()
    
    max_seq = 0
    for r in records:
        try:
            seq = int(r[0].split('-')[1])
            if seq > max_seq:
                max_seq = seq
        except:
            pass
    return max_seq + 1

# --- نظام تسجيل الدخول ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

def login_screen():
    st.title("🏗️ Sales Bay - PEB System")
    user = st.text_input("Username")
    pw = st.text_input("Password", type="password")
    if st.button("Login"):
        users = {"eng_ahmed": "123", "eng_mohamed": "456", "admin": "admin789"}
        if user in users and users[user] == pw:
            st.session_state.logged_in = True
            st.session_state.username = user
            st.rerun()
        else:
            st.error("Invalid Credentials")

if not st.session_state.logged_in:
    login_screen()
    st.stop()

# --- القائمة العلوية للتنقل ---
st.sidebar.title(f"👤 {st.session_state.username}")
if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.rerun()

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📝 Quotation Workspace", 
    "📋 Quotation Log", 
    "🏗️ Jobs", 
    "💰 Collections", 
    "📊 KPIs & Reports"
])

# ==========================================
# --- الشاشة الأولى: Quotation Workspace ---
# ==========================================
with tab1:
    st.header("📝 Quotation Workspace")
    
    mode = st.radio("Select Action:", ["Create New Quotation", "Revise Existing Quotation"], horizontal=True)
    st.divider()

    q_data = {}
    is_revision = False

    if mode == "Revise Existing Quotation":
        is_revision = True
        conn = sqlite3.connect('peb_system.db')
        df_quotes = pd.read_sql_query("SELECT quotation_no FROM quotations ORDER BY quotation_no DESC", conn)
        conn.close()
        
        if not df_quotes.empty:
            selected_q = st.selectbox("Select Quotation to Revise", df_quotes['quotation_no'])
            if selected_q:
                conn = sqlite3.connect('peb_system.db')
                c = conn.cursor()
                c.execute("SELECT * FROM quotations WHERE quotation_no=?", (selected_q,))
                row = c.fetchone()
                col_names = [description[0] for description in c.description]
                q_data = dict(zip(col_names, row))
                conn.close()
                st.info(f"Editing Mode Active for: **{selected_q}**")
        else:
            st.warning("No quotations available to revise.")
            st.stop()
    
    current_year = datetime.now().year
    
    def get_val(key, default):
        return q_data.get(key, default) if is_revision else default

    with st.form("quotation_form"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            country = st.selectbox("Country Territory", list(countries_map.keys()), 
                                   index=list(countries_map.keys()).index(get_val('country', "
