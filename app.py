import streamlit as st
import pandas as pd
from auth_utils import load_user_db

# Import modul yang diperlukan
import screening_tab as sc
import bulk_admin_tab as bat
import log_tab as lt

# ============ KONFIGURASI HALAMAN ============
st.set_page_config(
    page_title="BPR Screening System",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============ CUSTOM CSS (Desain dari Referensi) ============
def apply_custom_css():
    st.markdown("""
    <style>
        /* ===== FONTS ===== */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Montserrat:wght@600;700;800&display=swap');
        
        /* ===== GLOBAL ===== */
        .stApp {
            background-color: #f9f9ff !important;
        }
        
        /* ===== HIDE DEFAULT STREAMLIT ELEMENTS ===== */
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        footer {visibility: hidden;}
        .stDeployButton {display: none;}
        
        /* ===== SIDEBAR NAVIGATION ===== */
        .sidebar-nav {
            position: fixed;
            left: 0;
            top: 0;
            width: 256px;
            height: 100vh;
            background: #ffffff;
            border-right: 1px solid #E2E8F0;
            padding: 32px 16px;
            z-index: 100;
            display: flex;
            flex-direction: column;
        }
        
        .sidebar-logo {
            padding: 0 16px 24px 16px;
            border-bottom: 1px solid #E2E8F0;
            margin-bottom: 24px;
        }
        
        .sidebar-logo h1 {
            font-family: 'Montserrat', sans-serif;
            font-size: 24px;
            font-weight: 700;
            color: #003B70;
            margin: 0;
        }
        
        .sidebar-logo p {
            font-family: 'Inter', sans-serif;
            font-size: 12px;
            font-weight: 600;
            color: #42474f;
            letter-spacing: 0.05em;
            margin: 4px 0 0 0;
            text-transform: uppercase;
        }
        
        .nav-item {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 12px 16px;
            border-radius: 8px;
            font-family: 'Inter', sans-serif;
            font-size: 12px;
            font-weight: 600;
            color: #42474f;
            text-decoration: none;
            transition: all 0.2s;
            cursor: pointer;
            margin-bottom: 4px;
            letter-spacing: 0.05em;
            text-transform: uppercase;
        }
        
        .nav-item:hover {
            background: #e7eeff;
        }
        
        .nav-item.active {
            background: #f0f3ff;
            color: #00254a;
            border-right: 4px solid #00254a;
        }
        
        .nav-item .material-symbols-outlined {
            font-size: 20px;
        }
        
        .sidebar-footer {
            margin-top: auto;
            padding: 16px;
            border-top: 1px solid #E2E8F0;
        }
        
        .user-profile {
            display: flex;
            align-items: center;
            gap: 12px;
        }
        
        .user-avatar {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            background: #d4e3ff;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 700;
            color: #00254a;
        }
        
        .user-name {
            font-family: 'Inter', sans-serif;
            font-size: 12px;
            font-weight: 600;
            color: #111c2c;
        }
        
        .user-role {
            font-family: 'Inter', sans-serif;
            font-size: 10px;
            color: #42474f;
        }
        
        /* ===== TOP HEADER ===== */
        .top-header {
            margin-left: 256px;
            padding: 16px 32px;
            background: #ffffff;
            border-bottom: 1px solid #E2E8F0;
            display: flex;
            justify-content: space-between;
            align-items: center;
            position: sticky;
            top: 0;
            z-index: 50;
        }
        
        .top-header h2 {
            font-family: 'Montserrat', sans-serif;
            font-size: 24px;
            font-weight: 600;
            color: #003B70;
            margin: 0;
        }
        
        .header-actions {
            display: flex;
            align-items: center;
            gap: 16px;
        }
        
        .btn-refresh {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 8px 16px;
            border: 1px solid #E2E8F0;
            border-radius: 8px;
            background: white;
            font-family: 'Inter', sans-serif;
            font-size: 12px;
            font-weight: 600;
            color: #42474f;
            cursor: pointer;
            transition: all 0.2s;
        }
        
        .btn-refresh:hover {
            background: #f8fafc;
        }
        
        /* ===== MAIN CONTENT ===== */
        .main-content {
            margin-left: 256px;
            padding: 24px 32px 40px 32px;
            min-height: calc(100vh - 80px);
        }
        
        /* ===== CARD STYLES ===== */
        .card {
            background: white;
            border: 1px solid #E2E8F0;
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 20px;
        }
        
        .card-title {
            font-family: 'Montserrat', sans-serif;
            font-size: 18px;
            font-weight: 600;
            color: #00254a;
            margin-bottom: 16px;
        }
        
        /* ===== METRIC CARDS ===== */
        .metric-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 16px;
            margin-bottom: 24px;
        }
        
        .metric-card {
            background: white;
            border: 1px solid #E2E8F0;
            border-radius: 12px;
            padding: 20px;
        }
        
        .metric-label {
            font-family: 'Inter', sans-serif;
            font-size: 12px;
            font-weight: 600;
            color: #42474f;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 8px;
        }
        
        .metric-value {
            font-family: 'Montserrat', sans-serif;
            font-size: 32px;
            font-weight: 700;
            color: #003B70;
        }
        
        /* ===== BUTTONS ===== */
        .btn-primary {
            background: #F36E21;
            color: white;
            padding: 12px 32px;
            border: none;
            border-radius: 8px;
            font-family: 'Inter', sans-serif;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
            display: inline-flex;
            align-items: center;
            gap: 8px;
        }
        
        .btn-primary:hover {
            opacity: 0.9;
            transform: scale(0.98);
        }
        
        .btn-primary:active {
            transform: scale(0.95);
        }
        
        .btn-secondary {
            background: #00254a;
            color: white;
            padding: 12px 32px;
            border: none;
            border-radius: 8px;
            font-family: 'Inter', sans-serif;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
        }
        
        .btn-secondary:hover {
            background: #003B70;
        }
        
        .btn-outline {
            background: transparent;
            color: #00254a;
            padding: 10px 24px;
            border: 1px solid #00254a;
            border-radius: 8px;
            font-family: 'Inter', sans-serif;
            font-size: 12px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
        }
        
        .btn-outline:hover {
            background: #e7eeff;
        }
        
        .btn-danger {
            background: transparent;
            color: #ba1a1a;
            padding: 10px 24px;
            border: 1px solid #ba1a1a;
            border-radius: 8px;
            font-family: 'Inter', sans-serif;
            font-size: 12px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
        }
        
        .btn-danger:hover {
            background: #ffdad6;
        }
        
        /* ===== TABLE ===== */
        .data-table {
            width: 100%;
            border-collapse: collapse;
        }
        
        .data-table th {
            font-family: 'Inter', sans-serif;
            font-size: 12px;
            font-weight: 600;
            color: #42474f;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            padding: 12px 16px;
            text-align: left;
            border-bottom: 1px solid #E2E8F0;
            background: #f8fafc;
        }
        
        .data-table td {
            padding: 12px 16px;
            border-bottom: 1px solid #E2E8F0;
            font-family: 'Inter', sans-serif;
            font-size: 14px;
            color: #111c2c;
        }
        
        .data-table tr:hover {
            background: #f8fafc;
        }
        
        /* ===== BADGE ===== */
        .badge {
            padding: 4px 12px;
            border-radius: 9999px;
            font-size: 11px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        
        .badge-danger {
            background: #ffdad6;
            color: #ba1a1a;
        }
        
        .badge-success {
            background: #d1fae5;
            color: #065f46;
        }
        
        .badge-warning {
            background: #fef3c7;
            color: #92400e;
        }
        
        .badge-info {
            background: #dbeafe;
            color: #1e40af;
        }
        
        /* ===== FORM ELEMENTS ===== */
        .form-label {
            font-family: 'Inter', sans-serif;
            font-size: 12px;
            font-weight: 600;
            color: #42474f;
            display: block;
            margin-bottom: 6px;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        
        .form-input, .form-select {
            width: 100%;
            padding: 10px 16px;
            border: 1px solid #E2E8F0;
            border-radius: 8px;
            font-family: 'Inter', sans-serif;
            font-size: 14px;
            background: white;
            transition: all 0.2s;
            outline: none;
        }
        
        .form-input:focus, .form-select:focus {
            border-color: #003B70;
            box-shadow: 0 0 0 3px rgba(0,59,112,0.1);
        }
        
        /* ===== FILE UPLOAD ===== */
        .upload-zone {
            border: 2px dashed #c3c6d1;
            background: #f8fafc;
            padding: 40px;
            border-radius: 12px;
            text-align: center;
            cursor: pointer;
            transition: all 0.2s;
        }
        
        .upload-zone:hover {
            border-color: #003B70;
            background: #f0f3ff;
        }
        
        /* ===== SLIDER ===== */
        input[type="range"] {
            accent-color: #003B70;
            width: 100%;
        }
        
        /* ===== RESPONSIVE ===== */
        @media (max-width: 768px) {
            .sidebar-nav {
                display: none;
            }
            .top-header {
                margin-left: 0;
            }
            .main-content {
                margin-left: 0;
                padding: 16px;
            }
            .metric-grid {
                grid-template-columns: repeat(2, 1fr);
            }
        }
        
        /* ===== OVERRIDE STREAMLIT DEFAULTS ===== */
        .stTabs [data-baseweb="tab-list"] {
            display: none !important;
        }
        
        .stTabs [data-baseweb="tab-panel"] {
            padding: 0 !important;
        }
        
        /* ===== PROGRESS BAR ===== */
        .progress-bar {
            height: 4px;
            background: #d8e3fa;
            border-radius: 4px;
            overflow: hidden;
            margin: 12px 0;
        }
        
        .progress-bar-fill {
            height: 100%;
            background: #003B70;
            transition: width 0.3s;
        }
        
        /* ===== ICON WRAPPER ===== */
        .material-symbols-outlined {
            font-family: 'Material Symbols Outlined';
            font-weight: normal;
            font-style: normal;
            font-size: 20px;
            line-height: 1;
            letter-spacing: normal;
            text-transform: none;
            display: inline-block;
            white-space: nowrap;
            word-wrap: normal;
            direction: ltr;
            -webkit-font-smoothing: antialiased;
        }
    </style>
    <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap" rel="stylesheet" />
    """, unsafe_allow_html=True)

# ============ SIDEBAR NAVIGATION (HTML) ============
def render_sidebar(active_tab):
    st.markdown(f"""
    <div class="sidebar-nav">
        <div class="sidebar-logo">
            <h1>BPR Screening</h1>
            <p>Administrator</p>
        </div>
        
        <div class="nav-item {'active' if active_tab == 0 else ''}" onclick="window.location.href='?tab=0'">
            <span class="material-symbols-outlined">person_search</span>
            Single Screening
        </div>
        <div class="nav-item {'active' if active_tab == 1 else ''}" onclick="window.location.href='?tab=1'">
            <span class="material-symbols-outlined">layers</span>
            Bulk Screening
        </div>
        <div class="nav-item {'active' if active_tab == 2 else ''}" onclick="window.location.href='?tab=2'">
            <span class="material-symbols-outlined">history</span>
            Admin Log
        </div>
        
        <div class="sidebar-footer">
            <div class="user-profile">
                <div class="user-avatar">AD</div>
                <div>
                    <div class="user-name">Admin User</div>
                    <div class="user-role">Administrator</div>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ============ TOP HEADER ============
def render_top_header(title):
    st.markdown(f"""
    <div class="top-header">
        <h2>{title}</h2>
        <div class="header-actions">
            <button class="btn-refresh" onclick="location.reload()">
                <span class="material-symbols-outlined">refresh</span>
                Refresh
            </button>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ============ MAIN APP ============
def main_interface():
    # Apply custom CSS
    apply_custom_css()
    
    # Get active tab from URL params
    try:
        params = st.query_params
        tab = int(params.get("tab", [0])[0]) if "tab" in params else 0
    except:
        tab = 0
    
    # Set default user
    if 'user' not in st.session_state:
        st.session_state['user'] = "Admin_User"
    if 'role' not in st.session_state:
        st.session_state['role'] = "Admin"
    
    # Render sidebar
    render_sidebar(tab)
    
    # Load data
    db_p, stats, total = sc.fetch_all_data()
    
    # Tab titles
    tab_titles = ["🔍 Single Screening", "🚀 Bulk Screening", "🕒 Admin Log"]
    
    # Render top header based on active tab
    render_top_header(tab_titles[tab])
    
    # Main content area
    st.markdown('<div class="main-content">', unsafe_allow_html=True)
    
    # Render content based on active tab
    if tab == 0:
        sc.run_pencarian(st.session_state.get('user', "Admin_User"), db_p, True)
    elif tab == 1:
        bat.run_bulk_screening()
    elif tab == 2:
        lt.run_log_admin(stats, total)
    
    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main_interface()
