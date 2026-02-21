import streamlit as st
import pandas as pd
import sqlite3
import json
from datetime import datetime
import os

# ==========================================
# --- إعدادات الصفحة والهوية البصرية ---
# ==========================================
# الكود ده بيقرأ اللوجو بتاعك حتى لو اسمه logo.png.png زي ما في الصورة
logo_path = "logo.png" if os.path.exists("logo.png") else ("logo.png.png" if os.path.exists("logo.png.png") else "🏗️")

st.set_page_config(page_title="Sales Bay", page_icon=logo_path, layout="wide", initial_sidebar_state="expanded")

# كود إخفاء علامات Streamlit بالكامل
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
# --- شاشة تسجيل الدخول (Google Style) ---
# ==========================================
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

def login_screen():
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.write("")
        st.write("")
        st.write("")
        
        # تصغير اللوجو في شاشة الـ Login
        col_img1, col_img2, col_img3 = st.columns([1.5, 1, 1.5])
        with col_img2:
            if logo_path != "🏗️":
                st.image(logo_path, use_container_width=True)
            else:
                st.markdown("<h2 style='text-align: center;'>SB</h2>", unsafe_allow_html=True)
                
        st.markdown("<h2 style='text-align: center; margin-bottom: 0px;'>Sign in</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: gray; margin-top: 0px;'>Continue to Sales Bay</p>", unsafe_allow_html=True)
        
        st.write("")
        user = st.text_input("Username", placeholder="Enter your username")
        pw = st.text_input("Password", type="password", placeholder="Enter your password")
        
        st.write("")
        if st.button("Next", type="primary", use_container_width=True):
            users = {"eng_ahmed": "123", "eng_mohamed": "456", "admin": "admin789"}
            if user in users and users[user] == pw:
                st.session_state.logged_in = True
                st.session_state.username = user
                st.rerun()
            else:
                st.error("Invalid Username or Password.")

if not st.session_state.logged_in:
    login_screen()
    st.stop()

# ==========================================
# --- الواجهة الداخلية (نظام الـ Menu) ---
# ==========================================
is_admin = (st.session_state.username == "admin")

menu_options = [
    "Dashboard", 
    "Quotation Workspace", 
    "Quotation Log", 
    "Jobs", 
    "Collections"
]
if is_admin:
    menu_options.extend(["Reports", "KPIs", "Prospect List"])

if logo_path != "🏗️":
    st.sidebar.image(logo_path, use_container_width=True)

st.sidebar.markdown(f"**User:** `{st.session_state.username}`")
st.sidebar.divider()

choice = st.sidebar.radio("Main Menu", menu_options)

st.sidebar.divider()
if st.sidebar.button("🚪 Logout", use_container_width=True):
    st.session_state.logged_in = False
    st.rerun()

# تكبير اللوجو داخل الصفحات بجودة عالية
if logo_path != "🏗️":
    c_logo, c_title = st.columns([1.5, 8.5])
    with c_logo:
        st.image(logo_path, width=180) # المقاس ده هيخليه كبير وواضح جداً
    with c_title:
        st.title(f"{choice}")
else:
    st.title(f"{choice}")
st.divider()

# ==========================================
# --- 1. Dashboard ---
# ==========================================
if choice == "Dashboard":
    st.info("🚀 Dashboard is under development. Here we will add beautiful charts and summaries later!")

# ==========================================
# --- 2. Quotation Workspace ---
# ==========================================
elif choice == "Quotation Workspace":
    
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

    st.success(f"### 💰 Live Grand Total: {total_val:,.0f} EGP")
    st.write(f"*(Steel: {steel_amount:,.0f} EGP + Other Items: {new_total_val:,.0f} EGP)*")

    st.divider()
    status_options = ["In Progress", "Signed", "Hold", "Rejected", "Lost"]
    status = st.selectbox("Quotation Status", status_options, 
                          index=status_options.index(get_val('status', "In Progress")) if get_val('status', "In Progress") in status_options else 0)
    
    submit_btn_text = "Update Quotation" if is_revision else "Save New Quotation"
    submit = st.button(submit_btn_text, type="primary", use_container_width=True)

    if submit:
        if project_name == "" or client_company == "" or final_country == "":
            st.error("Please fill in Project Name, Client Company Name, and Country Territory.")
        elif country_selection == "Other" and not matched_country and len(custom_cc) != 2:
            st.error("Please enter exactly 2 letters for the Custom Country Code.")
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
                          (str(quote_date), final_country, project_name, location, buildings, scope, client_type, 
                           client_company, client_contact, client_mobile, client_email, client_address, 
                           consultant_office, consultant_contact, consultant_mobile, consultant_email, 
                           consultant_address, pricing_base, steel_weight, steel_amount, total_val, items_json, status, quotation_no))
                st.toast(f"✅ Quotation {quotation_no} Updated successfully!")
            else:
                try:
                    c.execute('''INSERT INTO quotations VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
                              (quotation_no, str(quote_date), final_country, sales_rep, project_name, location, buildings, 
                               scope, client_type, client_company, client_contact, client_mobile, client_email, 
                               client_address, consultant_office, consultant_contact, consultant_mobile, consultant_email, 
                               consultant_address, pricing_base, steel_weight, steel_amount, total_val, items_json, status))
                    st.toast(f"✅ Quotation {quotation_no} saved successfully!")
                except sqlite3.IntegrityError:
                    st.error("A quotation with this number already exists.")
            conn.commit()
            conn.close()

# ==========================================
# --- 3. Quotation Log ---
# ==========================================
elif choice == "Quotation Log":
    conn = sqlite3.connect('peb_system.db')
    
    if is_admin:
        query = "SELECT * FROM quotations ORDER BY quotation_no DESC"
    else:
        query = f"SELECT * FROM quotations WHERE sales_rep='{st.session_state.username}' ORDER BY quotation_no DESC"
        
    df_raw = pd.read_sql_query(query, conn)
    conn.close()
    
    if not df_raw.empty:
        df_log = pd.DataFrame()
        df_log['Quote No.'] = df_raw['quotation_no']
        df_log['Project Name'] = df_raw['project_name']
        df_log['Client Name'] = df_raw['client_company']
        df_log['Sales Name'] = df_raw['sales_rep']
        df_log['Entry Date'] = df_raw['quote_date']
        df_log['Pricing Bases'] = df_raw['pricing_base']
        df_log['Scope of Work'] = df_raw['scope']
        df_log['Steel Weight'] = df_raw['steel_weight'].apply(lambda x: f"{x:,.0f}")
        df_log['Steel Amount'] = df_raw['steel_amount'].apply(lambda x: f"{x:,.0f}")
        df_log['Other Items Amount'] = (df_raw['total_value'] - df_raw['steel_amount']).apply(lambda x: f"{x:,.0f}")
        df_log['Total Value'] = df_raw['total_value'].apply(lambda x: f"{x:,.0f}")
        df_log['Status'] = df_raw['status']

        def style_status(val):
            if val == 'Signed': return 'background-color: #28a745; color: white'
            if val == 'Lost': return 'background-color: #dc3545; color: white'
            if val == 'Hold': return 'background-color: #ffc107; color: black'
            if val == 'Rejected': return 'background-color: #add8e6; color: black'
            return ''
            
        styled_df = df_log.style.map(style_status, subset=['Status'])
        st.dataframe(styled_df, use_container_width=True, hide_index=True)
    else: 
        st.info("No quotations found yet.")

# ==========================================
# --- 4. Jobs ---
# ==========================================
elif choice == "Jobs":
    st.info("🏗️ The Jobs Module will automatically pull all 'Signed' projects here. (Under Construction)")

# ==========================================
# --- 5. Collections ---
# ==========================================
elif choice == "Collections":
    if is_admin:
        st.success("💰 **Admin View:** You have full access to view and edit collections for ALL projects and Sales Reps.")
    else:
        st.info(f"💰 **Sales View:** You can only view and update collections for projects assigned to **{st.session_state.username}**.")
    st.write("(Module under construction)")

# ==========================================
# --- 6. Reports (Admin Only) ---
# ==========================================
elif choice == "Reports":
    st.info("📊 Reports Module: Export data and generate full Excel/PDF summaries. (Under Construction)")

# ==========================================
# --- 7. KPIs (Admin Only) ---
# ==========================================
elif choice == "KPIs":
    st.info("📈 KPIs Module: View Hit Rates, Total Tonnage, and Sales Performance. (Under Construction)")

# ==========================================
# --- 8. Prospect List (Admin Only) ---
# ==========================================
elif choice == "Prospect List":
    st.markdown("This list automatically extracts and organizes all client and consultant contacts from your quotations.")
    conn = sqlite3.connect('peb_system.db')
    
    df_clients = pd.read_sql_query('''
        SELECT DISTINCT client_contact as "Contact Name", client_company as "Company / Office",
               client_mobile as "Mobile", client_email as "Email", client_address as "Address", 'Client' as "Type"
        FROM quotations WHERE client_company != ''
    ''', conn)
    
    df_consultants = pd.read_sql_query('''
        SELECT DISTINCT consultant_contact as "Contact Name", consultant_office as "Company / Office",
               consultant_mobile as "Mobile", consultant_email as "Email", consultant_address as "Address", 'Consultant' as "Type"
        FROM quotations WHERE consultant_office != ''
    ''', conn)
    conn.close()
    
    if not df_clients.empty or not df_consultants.empty:
        df_prospects = pd.concat([df_clients, df_consultants], ignore_index=True)
        df_prospects = df_prospects.drop_duplicates(subset=["Company / Office", "Contact Name"])
        
        def style_type(val):
            if val == 'Client': return 'background-color: #17a2b8; color: white'
            if val == 'Consultant': return 'background-color: #6c757d; color: white'
            return ''
            
        styled_prospects = df_prospects.style.map(style_type, subset=['Type'])
        st.dataframe(styled_prospects, use_container_width=True, hide_index=True)
    else:
        st.info("No prospect data available yet.")
