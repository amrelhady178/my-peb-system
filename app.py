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
