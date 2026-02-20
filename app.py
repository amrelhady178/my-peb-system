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
            if seq > max_seq: max_seq = seq
        except: pass
    return max_seq + 1

# --- نظام تسجيل الدخول ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

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

st.sidebar.title(f"👤 {st.session_state.username}")
if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.rerun()

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📝 Quotation Workspace", "📋 Quotation Log", "🏗️ Jobs", "💰 Collections", "📊 KPIs & Reports"
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
    selected_q = None

    # دالة لتنسيق الأرقام بفواصل الألوف بدون كسور عشرية للفلوس
    def format_money():
        try:
            val_a = str(st.session_state.sa_input).replace(',', '')
            if val_a: st.session_state.sa_input = f"{float(val_a):,.0f}"
        except: pass
        try:
            val_w = str(st.session_state.sw_input).replace(',', '')
            if val_w: st.session_state.sw_input = f"{float(val_w):,.3f}"
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
                st.session_state['sw_input'] = f"{float(q_data.get('steel_weight', 0)):,.3f}"
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
            st.session_state['sw_input'] = "0.000"
            if 'current_items_df' in st.session_state: del st.session_state['current_items_df']
            st.session_state['last_q'] = None
    
    current_year = datetime.now().year
    def get_val(key, default): return q_data.get(key, default) if is_revision else default
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        country = st.selectbox("Country Territory", list(countries_map.keys()), 
                               index=list(countries_map.keys()).index(get_val('country', "Egypt")) if is_revision else 0)
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
    else: quotation_no = f"{countries_map[country]}-{get_next_serial():03d}-{current_year}"
    
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
                df = pd.DataFrame(parsed_data) if parsed_data else pd.DataFrame(columns=default_cols)
                for col in default_cols:
                    if col not in df.columns: df[col] = 0.0
                st.session_state['current_items_df'] = df
            except: st.session_state['current_items_df'] = pd.DataFrame(columns=default_cols)
        else: st.session_state['current_items_df'] = pd.DataFrame(columns=default_cols)

    old_total_val = st.session_state['current_items_df']['Item Value'].sum() if not st.session_state['current_items_df'].empty else 0.0

    st.markdown("*Note: Press **Enter** or click outside the cell after typing to instantly update the 'Item Value'.*")
    edited_items = st.data_editor(
        st.session_state['current_items_df'],
        num_rows="dynamic",
        column_config={
            "Item": st.column_config.SelectboxColumn("Item", options=item_options, required=True),
            "QTY": st.column_config.NumberColumn("QTY", min_value=0.0),
            "Unit Price": st.column_config.NumberColumn("Unit Price (Rate)", min_value=0.0),
            "Item Value": st.column_config.NumberColumn("Item Value (Auto)", disabled=True)
        },
        use_container_width=True
    )

    edited_items['QTY'] = pd.to_numeric(edited_items['QTY'], errors='coerce').fillna(0)
    edited_items['Unit Price'] = pd.to_numeric(edited_items['Unit Price'], errors='coerce').fillna(0)
    edited_items['Item Value'] = edited_items['QTY'] * edited_items['Unit Price']
    
    st.session_state['current_items_df'] = edited_items
    new_total_val = edited_items['Item Value'].sum()
    
    if abs(new_total_val - old_total_val) > 0.001: st.rerun()

    items_json = edited_items.to_json(orient='records')
    total_val = float(steel_amount) + float(new_total_val)

    # عرض النتيجة بدون كسور عشرية للفلوس
    st.success(f"### 💰 Live Grand Total: {total_val:,.0f} EGP")
    st.write(f"*(Steel: {steel_amount:,.0f} EGP + Other Items: {new_total_val:,.0f} EGP)*")

    st.divider()
    status_options = ["In Progress", "Signed", "Hold", "Rejected", "Lost"]
    status = st.selectbox("Quotation Status", status_options, 
                          index=status_options.index(get_val('status', "In Progress")) if get_val('status', "In Progress") in status_options else 0)
    
    submit_btn_text = "Update Quotation" if is_revision else "Save New Quotation"
    submit = st.button(submit_btn_text, type="primary", use_container_width=True)

    if submit:
        if project_name == "" or client_company == "":
            st.error("Please fill in Project Name and Client Company Name.")
        else:
            conn = sqlite3.connect('peb_system.db')
            c = conn.cursor()
            if is_revision:
                c.execute('''UPDATE quotations SET 
                             quote_date=?, country=?, project_name=?, location=?, buildings=?, 
                             scope=?, client_type=?, client_company=?, client_contact=?, client_mobile=?, 
                             client_email=?, client_address=?, consultant_office=?, consultant_contact=?, 
                             consultant_mobile=?, consultant_email=?, consultant_address=?, pricing_base=?, 
                             steel_weight=?, steel_amount=?, total_value=?, items_data=?, status=?
                             WHERE quotation_no=?''',
                          (str(quote_date), country, project_name, location, buildings, scope, client_type, 
                           client_company, client_contact, client_mobile, client_email, client_address, 
                           consultant_office, consultant_contact, consultant_mobile, consultant_email, 
                           consultant_address, pricing_base, steel_weight, steel_amount, total_val, items_json, status, quotation_no))
                st.toast(f"✅ Quotation {quotation_no} Updated successfully!")
            else:
                try:
                    c.execute('''INSERT INTO quotations VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
                              (quotation_no, str(quote_date), country, sales_rep, project_name, location, buildings, 
                               scope, client_type, client_company, client_contact, client_mobile, client_email, 
                               client_address, consultant_office, consultant_contact, consultant_mobile, consultant_email, 
                               consultant_address, pricing_base, steel_weight, steel_amount, total_val, items_json, status))
                    st.toast(f"✅ Quotation {quotation_no} saved successfully!")
                except sqlite3.IntegrityError:
                    st.error("A quotation with this number already exists.")
            conn.commit()
            conn.close()

# ==========================================
# --- الشاشة الثانية: Quotation Log ---
# ==========================================
with tab2:
    st.header("📋 Quotation Log")
    conn = sqlite3.connect('peb_system.db')
    # جلب الخانات الجديدة بدون الكميات
    df_log = pd.read_sql_query('''
        SELECT quotation_no as "Quote No.", project_name as "Project Name", client_company as "Client Name", 
               sales_rep as "Sales Name", quote_date as "Entry Date", pricing_base as "Pricing Bases",
               scope as "Scope of Work", status as "Status", 
               steel_weight as "Steel Weight", 
               steel_amount as "Steel Amount",
               (total_value - steel_amount) as "Other Items Amount",
               total_value as "Total Value"
        FROM quotations ORDER BY quotation_no DESC
    ''', conn)
    conn.close()
    
    if not df_log.empty:
        def style_status(val):
            if val == 'Signed': return 'background-color: #28a745; color: white'
            if val == 'Lost': return 'background-color: #dc3545; color: white'
            if val == 'Hold': return 'background-color: #ffc107; color: black'
            if val == 'Rejected': return 'background-color: #add8e6; color: black'
            return ''
        
        # تنسيق الفلوس عشان تظهر بفاصلة الألوف وبدون كسور، والحديد بـ 3 كسور
        df_log['Steel Weight'] = df_log['Steel Weight'].apply(lambda x: f"{x:,.3f}")
        df_log['Steel Amount'] = df_log['Steel Amount'].apply(lambda x: f"{x:,.0f}")
        df_log['Other Items Amount'] = df_log['Other Items Amount'].apply(lambda x: f"{x:,.0f}")
        df_log['Total Value'] = df_log['Total Value'].apply(lambda x: f"{x:,.0f}")

        styled_df = df_log.style.map(style_status, subset=['Status'])
        st.dataframe(styled_df, use_container_width=True, hide_index=True)
    else: st.info("No quotations found yet.")

# --- باقي الشاشات ---
with tab3: st.header("🏗️ Jobs"); st.info("Projects with 'Signed' status will automatically appear here.")
with tab4: st.header("💰 Collections"); st.info("Payment tracking will be managed here.")
with tab5: st.header("📊 KPIs & Reports"); st.info("Dashboards and data exports will be generated here.")
