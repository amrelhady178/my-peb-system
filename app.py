import streamlit as st
import pandas as pd
import sqlite3
import json
from datetime import datetime
import os

# ==========================================
# --- إعدادات الصفحة والهوية البصرية ---
# ==========================================
# تم تغيير الأيقونة هنا لتأخذ صورة اللوجو
st.set_page_config(page_title="Sales Bay", page_icon="logo.png", layout="wide", initial_sidebar_state="collapsed")

# كود إخفاء علامات Streamlit
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

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

countries_map = {
    "Algeria": "AL", "Angola": "AO", "Bahrain": "BH", "Botswana": "BW", "Burkina Faso": "BF",
    "Burundi": "BI", "Cameroon": "CM", "Central African Republic": "CF", "Chad": "TD",
    "Democratic Republic of the Congo": "CD", "Djibouti": "DJ", "Egypt": "EG",
    "Equatorial Guinea": "GQ", "Eritrea": "ER", "Eswatini": "SZ", "Ethiopia": "ET",
    "Gabon": "GA", "Gambia": "GM", "Ghana": "GH", "Guinea": "GN", "Guinea-Bissau": "GW",
    "Iraq": "IQ", "Ivory Coast": "CI", "Jordan": "JO", "Kenya": "KE", "Kuwait": "KW",
    "Lebanon": "LB", "Lesotho": "LS", "Liberia": "LR", "Libya": "LY", "Madagascar": "MG",
    "Malawi": "MW", "Mali": "ML", "Mauritania": "MR", "Mauritius": "MU", "Morocco": "MA",
    "Mozambique": "MZ", "Namibia": "NA", "Niger": "NE", "Nigeria": "NG", "Oman": "OM",
    "Palestine": "PS", "Qatar": "QA", "Republic of the Congo": "CG", "Rwanda": "RW",
    "Sao Tome and Principe": "ST", "Saudi Arabia": "SA", "Senegal": "SN", "Seychelles": "SC",
    "Sierra Leone": "SL", "Somalia": "SO", "South Africa": "ZA", "Sudan": "SD", "Syria": "SY",
    "Tanzania": "TZ", "Togo": "TG", "Tunisia": "TN", "Uganda": "UG", "United Arab Emirates": "AE",
    "Yemen": "YE", "Zambia": "ZM", "Zimbabwe": "ZW"
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
            if seq > max_seq: max_seq = seq
        except: pass
    return max_seq + 1

# ==========================================
# --- شاشة تسجيل الدخول ---
# ==========================================
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

def login_screen():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.write("")
        st.write("")
        logo_path = "logo.png" if os.path.exists("logo.png") else ("logo.jpg" if os.path.exists("logo.jpg") else None)
        if logo_path:
            st.image(logo_path, use_container_width=True)
        else:
            st.markdown("<h1 style='text-align: center;'>Sales Bay</h1>", unsafe_allow_html=True)
        
        st.markdown("<h3 style='text-align: center; color: gray;'>Welcome Back</h3>", unsafe_allow_html=True)
        
        user = st.text_input("Username")
        pw = st.text_input("Password", type="password")
        if st.button("Login", use_container_width=True, type="primary"):
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

# ==========================================
# --- الواجهة الداخلية بعد تسجيل الدخول ---
# ==========================================

# القائمة الجانبية (Sidebar)
logo_path = "logo.png" if os.path.exists("logo.png") else ("logo.jpg" if os.path.exists("logo.jpg") else None)
if logo_path:
    st.sidebar.image(logo_path, use_container_width=True)
st.sidebar.title(f"👤 {st.session_state.username}")
if st.sidebar.button("Logout", use_container_width=True):
    st.session_state.logged_in = False
    st.rerun()

# اللوجو داخل الصفحات الرئيسية (فوق الـ Tabs)
if logo_path:
    c_logo, c_title = st.columns([1, 8])
    with c_logo:
        st.image(logo_path, width=80)
    with c_title:
        st.title("Sales Bay Workspace")
else:
    st.title("Sales Bay Workspace")

st.divider()

is_admin = (st.session_state.username == "admin")
tabs_titles = ["📝 Quotation Workspace", "📋 Quotation Log", "🏗️ Jobs", "💰 Collections", "📊 KPIs & Reports"]
if is_admin: tabs_titles.append("🕵️ Prospect List")

tabs = st.tabs(tabs_titles)
tab1, tab2, tab3, tab4, tab5 = tabs[0], tabs[1], tabs[2], tabs[3], tabs[4]

# ==========================================
# --- الشاشة الأولى: Quotation Workspace ---
# ==========================================
with tab1:
    
    mode = st.radio("Select Action:", ["Create New Quotation", "Revise Existing Quotation"], horizontal=True)
    st.divider()

    q_data = {}
    is_revision = False
    selected_q = None

    def format_money():
        try:
            val_a = str(st.session_state.sa_input).replace(',', '')
            if val_a: st.session_state.sa_input = f"{float(val_a):,.0f}"
        except: pass
        try:
            val_w = str(st.session_state.sw_input).replace(',', '')
            if val_w: st.session_state.sw_input = f"{float(val_w):,.0f}"
        except: pass

    if mode == "Revise Existing Quotation":
        is_revision = True
        conn = sqlite3.connect('peb_system.db')
        df_quotes = pd.read_sql_query("SELECT quotation_no FROM quotations ORDER BY quotation_no DESC", conn)
        conn.close()
        
        if not df_quotes.empty:
            selected_q = st.selectbox("Select Quotation to Revise", df_quotes['quotation_no'])
            if st.session_state.get('last_q') != selected_q:
                st.session_state['last_q'] = selected_q
                conn = sqlite3.connect('peb_system.db')
                c = conn.cursor()
                c.execute("SELECT * FROM quotations WHERE quotation_no=?", (selected_q,))
                row = c.fetchone()
                col_names = [desc[0] for desc in c.description]
                q_data = dict(zip(col_names, row))
                conn.close()
                
                st.session_state['sa_input'] = f"{float(q_data.get('steel_amount', 0)):,.0f}"
                st.session_state['sw_input'] = f"{float(q_data.get('steel_weight', 0)):,.0f}"
                if 'current_items_df' in st.session_state: del st.session_state['current_items_df']
            else:
                conn = sqlite3.connect('peb_system.db')
                c = conn.cursor()
                c.execute("SELECT * FROM quotations WHERE quotation_no=?", (selected_q,))
                q_data = dict(zip([desc[0] for desc in c.description], c.fetchone()))
                conn.close()
                
            st.info(f"Editing Mode Active for: **{selected_q}**")
        else:
            st.warning("No quotations available to revise.")
            st.stop()
    else:
        if st.session_state.get('last_mode') != mode:
            st.session_state['last_mode'] = mode
            st.session_state['sa_input'] = "0"
            st.session_state['sw_input'] = "0"
            if 'current_items_df' in st.session_state: del st.session_state['current_items_df']
            st.session_state['last_q'] = None
    
    current_year = datetime.now().year
    def get_val(key, default): return q_data.get(key, default) if is_revision else default
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        country_list = sorted(list(countries_map.keys()))
        db_country = get_val('country', "Egypt")
        
        if is_revision and db_country not in country_list and db_country != "":
            default_index = len(country_list)
        else:
            default_index = country_list.index(db_country) if db_country in country_list else country_list.index("Egypt")
            
        country_selection = st.selectbox("Country Territory", country_list + ["Other"], index=default_index)
        
        matched_country = None
        if country_selection == "Other":
            sc_c1, sc_c2 = st.columns([2, 1])
            with sc_c1:
                final_country_input = st.text_input("Country Name", value=db_country if (is_revision and db_country not in country_list) else "")
            
            matched_country = next((k for k in countries_map.keys() if k.lower() == final_country_input.strip().lower()), None)
            
            with sc_c2:
                default_cc = q_data['quotation_no'].split('-')[0] if (is_revision and q_data.get('quotation_no')) else ""
                if matched_country:
                    custom_cc = st.text_input("Code (Auto)", value=countries_map[matched_country], disabled=True)
                    cc = countries_map[matched_country]
                    final_country = matched_country
                else:
                    custom_cc = st.text_input("Code", max_chars=2, value=default_cc).upper()
                    cc = custom_cc if len(custom_cc) == 2 else "XX"
                    final_country = final_country_input
        else:
            final_country = country_selection
            cc = countries_map[country_selection]

        try: default_date = datetime.strptime(get_val('quote_date', str(datetime.now().date())), '%Y-%m-%d').date()
        except: default_date = datetime.now().date()
        quote_date = st.date_input("Entry Date", value=default_date)
        sales_rep = st.text_input("Sales Responsible", value=get_val('sales_rep', st.session_state.username), disabled=True)
        
    with col2:
        project_name = st.text_input("Project Name", value=get_val('project_name', ""))
        location = st.text_input("Project Location", value=get_val('location', ""))
        buildings = st.number_input("Number of Buildings", min_value=1, step=1, value=int(get_val('buildings', 1)))
        
    with col3:
        scope = st.selectbox("Scope of Work", ["Supply Only", "Supply & Erection", "Ex-Work"], 
                             index=["Supply Only", "Supply & Erection", "Ex-Work"].index(get_val('scope', "Supply Only")) if is_revision else 0)
        pricing_base = st.selectbox("Pricing Base", ["Re-Measurable", "Lump-sum"], 
                                    index=["Re-Measurable", "Lump-sum"].index(get_val('pricing_base', "Re-Measurable")) if is_revision else 0)
        
        sc_1, sc_2 = st.columns(2)
        with sc_1: 
            sw_in = st.text_input("Steel Weight (MT)", key="sw_input", on_change=format_money)
            try: steel_weight = float(sw_in.replace(',', ''))
            except: steel_weight = 0.0
            
        with sc_2: 
            sa_in = st.text_input("Steel Amount (EGP)", key="sa_input", on_change=format_money)
            try: steel_amount = float(sa_in.replace(',', ''))
            except: steel_amount = 0.0

    if is_revision: quotation_no = q_data['quotation_no']
    else: quotation_no = f"{cc}-{get_next_serial():03d}-{current_year}"
    
    st.info(f"**Quotation Number:** {quotation_no}")
    st.divider()
    
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("🏢 Client Info")
        client_type = st.selectbox("Client Type", ["Enduser", "Contractor", "Consultant"], 
                                   index=["Enduser", "Contractor", "Consultant"].index(get_val('client_type', "Enduser")) if is_revision else 0)
        client_company = st.text_input("Company Name", value=get_val('client_company', ""))
        client_contact = st.text_input("Client Contact Person", value=get_val('client_contact', ""))
        client_mobile = st.text_input("Client Mobile", value=get_val('client_mobile', ""))
        client_email = st.text_input("Client Email", value=get_val('client_email', ""))
        client_address = st.text_area("Client Company Address", value=get_val('client_address', ""))
        
    with c2:
        st.subheader("👔 Consultant Info")
        consultant_office = st.text_input("Consultant Office Name", value=get_val('consultant_office', ""))
        consultant_contact = st.text_input("Consultant Contact Person", value=get_val('consultant_contact', ""))
        consultant_mobile = st.text_input("Consultant Mobile", value=get_val('consultant_mobile', ""))
        consultant_email = st.text_input("Consultant Email", value=get_val('consultant_email', ""))
        consultant_address = st.text_area("Consultant Office Address", value=get_val('consultant_address', ""))

    st.divider()
    
    st.subheader("🛠️ Other Items")
    item_options = ["Single Skin", "Sandwich Panel", "Standing Seam", "Rain Gutter", "Skylight", 
                    "Wall Light", "Grating", "Chequered Plate", "Metal Decking", "Lifeline", "Ridge Panel", "Other"]
    default_cols = ["Item", "Description", "Unit", "QTY", "Unit Price", "Item Value"]
    
    if 'current_items_df' not in st.session_state:
        if is_revision and q_data.get('items_data'):
            try:
                parsed_data = json.loads(q_data['items_data'])
                df
