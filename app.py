import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# --- إعدادات الصفحة ---
st.set_page_config(page_title="PEB Management System", layout="wide", initial_sidebar_state="collapsed")

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
                  pricing_base TEXT, steel_weight REAL, items_data TEXT, status TEXT)''')
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
            st.error("Invalid Credentials")

if not st.session_state.logged_in:
    login_screen()
    st.stop()

# --- القائمة الجانبية (لخروج المستخدم فقط) ---
st.sidebar.title(f"👤 {st.session_state.username}")
if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.rerun()

# ==========================================
# --- واجهة البرنامج (Tabs في منتصف الشاشة) ---
# ==========================================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📝 Create a Quote", 
    "📋 Quotation Log", 
    "🏗️ Jobs", 
    "💰 Collections", 
    "📊 KPIs & Reports"
])

# --- الشاشة الأولى: Create a Quote ---
with tab1:
    st.header("📝 Create New Quotation")
    
    current_year = datetime.now().year
    next_seq = get_next_serial()
    
    with st.form("quotation_form", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            country = st.selectbox("Country Territory", list(countries_map.keys()))
            quote_date = st.date_input("Quote Date")
            sales_rep = st.text_input("Sales Responsible", value=st.session_state.username, disabled=True)
            
        with col2:
            project_name = st.text_input("Project Name")
            location = st.text_input("Project Location")
            buildings = st.number_input("Number of Buildings", min_value=1, step=1)
            
        with col3:
            scope = st.selectbox("Scope of Work", ["Supply Only", "Supply & Erection", "Ex-Work"])
            pricing_base = st.selectbox("Pricing Base", ["Re-Measurable", "Lump-sum"])
            steel_weight = st.number_input("Steel Weight (MT)", min_value=0.0)

        cc = countries_map[country]
        quotation_no = f"{cc}-{next_seq:03d}-{current_year}"
        st.info(f"**Generated Quotation Number:** {quotation_no}")

        st.divider()
        
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("🏢 Client Info")
            client_type = st.selectbox("Client Type", ["Enduser", "Contractor", "Consultant"])
            client_company = st.text_input("Company Name")
            client_contact = st.text_input("Client Contact Person")
            client_mobile = st.text_input("Client Mobile")
            client_email = st.text_input("Client Email")
            client_address = st.text_area("Client Company Address")
            
        with c2:
            st.subheader("👔 Consultant Info")
            consultant_office = st.text_input("Consultant
