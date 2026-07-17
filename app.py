import streamlit as st
import pandas as pd
from auth_utils import load_user_db

# Import modul yang diperlukan
import screening_tab as sc
import bulk_admin_tab as bat
import log_tab as lt

st.set_page_config(page_title="Screening System", layout="wide", initial_sidebar_state="collapsed")

def main_interface():
    # Identitas Default
    if 'user' not in st.session_state:
        st.session_state['user'] = "Admin_System"
    if 'role' not in st.session_state:
        st.session_state['role'] = "Admin"

    # Header
    c1, c2 = st.columns([10, 2])
    c1.markdown(f"👤 **Mode:** Direct Access | 🏷️ **Role:** {st.session_state['role']}")
    if c2.button("🔄 Refresh App", use_container_width=True):
        st.rerun()
    
    st.divider()
    
    # Load Data Utama
    db_p, stats, total = sc.fetch_all_data()

    # Navigasi Tab (Hanya 3 Menu)
    tabs = st.tabs([
        "🔍 Single Screening",
        "🚀 Bulk Screening",
        "🕒 Admin Log"
    ])

    # Jalankan fungsi sesuai tab masing-masing
    with tabs[0]:
        sc.run_pencarian(st.session_state.get('user', "Admin_System"), db_p, True)
    
    with tabs[1]:
        bat.run_bulk_screening()
    
    with tabs[2]:
        lt.run_log_admin(stats, total)

if __name__ == "__main__":
    main_interface()
