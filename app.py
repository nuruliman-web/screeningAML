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
    initial_sidebar_state="expanded"
)

# ============ CUSTOM CSS (SEDERHANA) ============
def apply_custom_css():
    st.markdown("""
    <style>
        /* Global */
        .stApp {
            background-color: #f5f7fa;
        }
        
        /* Hide default Streamlit elements */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        .stDeployButton {display: none;}
        
        /* Card style */
        .custom-card {
            background: white;
            border-radius: 12px;
            padding: 24px;
            border: 1px solid #e2e8f0;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
            margin-bottom: 20px;
        }
        
        /* Metric card */
        .metric-card {
            background: white;
            border-radius: 12px;
            padding: 20px;
            border: 1px solid #e2e8f0;
            text-align: center;
        }
        
        .metric-value {
            font-size: 28px;
            font-weight: 700;
            color: #003B70;
        }
        
        .metric-label {
            font-size: 12px;
            color: #64748b;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        
        /* Button primary */
        .stButton button {
            background-color: #F36E21 !important;
            color: white !important;
            border: none !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
            transition: all 0.2s !important;
        }
        
        .stButton button:hover {
            opacity: 0.9 !important;
            transform: scale(0.98) !important;
        }
        
        /* Sidebar */
        .css-1d391kg, .css-12oz5g7 {
            background-color: #ffffff;
            border-right: 1px solid #e2e8f0;
        }
        
        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
        }
        
        .stTabs [data-baseweb="tab"] {
            padding: 12px 24px;
            border-radius: 8px;
            font-weight: 600;
            font-size: 14px;
        }
        
        .stTabs [aria-selected="true"] {
            background-color: #003B70 !important;
            color: white !important;
        }
        
        /* Dataframe */
        .stDataFrame {
            border-radius: 8px;
            border: 1px solid #e2e8f0;
        }
        
        /* File uploader */
        .stFileUploader {
            border: 2px dashed #cbd5e1;
            border-radius: 12px;
            padding: 20px;
        }
        
        /* Badge */
        .badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 9999px;
            font-size: 11px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        
        .badge-danger {
            background: #fee2e2;
            color: #991b1b;
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
    </style>
    """, unsafe_allow_html=True)

# ============ SIDEBAR ============
def render_sidebar():
    with st.sidebar:
        # Logo/Header
        st.markdown("""
        <div style="padding: 12px 0 24px 0; border-bottom: 1px solid #e2e8f0; margin-bottom: 20px;">
            <h1 style="font-size: 24px; font-weight: 700; color: #003B70; margin: 0;">BPR Screening</h1>
            <p style="font-size: 11px; color: #64748b; text-transform: uppercase; letter-spacing: 0.05em; margin: 4px 0 0 0;">Administrator</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Navigation
        menu = st.radio(
            "",
            ["🔍 Single Screening", "🚀 Bulk Screening", "🕒 Admin Log"],
            index=0,
            key="nav_menu",
            label_visibility="collapsed"
        )
        
        # User profile
        st.markdown("---")
        st.markdown("""
        <div style="display: flex; align-items: center; gap: 12px; padding: 12px 0;">
            <div style="width: 40px; height: 40px; border-radius: 50%; background: #dbeafe; display: flex; align-items: center; justify-content: center; font-weight: 700; color: #003B70;">
                AD
            </div>
            <div>
                <div style="font-weight: 600; font-size: 14px;">Admin User</div>
                <div style="font-size: 11px; color: #64748b;">Administrator</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    return menu

# ============ MAIN ============
def main_interface():
    # Apply CSS
    apply_custom_css()
    
    # Set default user
    if 'user' not in st.session_state:
        st.session_state['user'] = "Admin_User"
    if 'role' not in st.session_state:
        st.session_state['role'] = "Admin"
    
    # Render sidebar and get selected menu
    selected_menu = render_sidebar()
    
    # Load data
    db_p, stats, total = sc.fetch_all_data()
    
    # Main content area
    st.markdown('<div style="padding: 20px 32px;">', unsafe_allow_html=True)
    
    # Header
    st.markdown(f"""
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; padding-bottom: 16px; border-bottom: 1px solid #e2e8f0;">
        <h2 style="font-size: 24px; font-weight: 600; color: #003B70; margin: 0;">{selected_menu}</h2>
        <button onclick="location.reload()" style="padding: 8px 16px; border: 1px solid #e2e8f0; border-radius: 8px; background: white; cursor: pointer; font-size: 13px;">
            🔄 Refresh
        </button>
    </div>
    """, unsafe_allow_html=True)
    
    # Render content based on selected menu
    if selected_menu == "🔍 Single Screening":
        sc.run_pencarian(st.session_state.get('user', "Admin_User"), db_p, True)
    elif selected_menu == "🚀 Bulk Screening":
        bat.run_bulk_screening()
    elif selected_menu == "🕒 Admin Log":
        lt.run_log_admin(stats, total)
    
    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main_interface()
