import streamlit as st
import pandas as pd
import io
import os

def run_log_admin(stats, total):
    LOG_FILE_LOKAL = "admin_activity_log.csv"
    
    # Metrics Bento Grid
    st.markdown("""
    <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 24px;">
    """, unsafe_allow_html=True)
    
    # Metric cards
    metrics = [
        ("Total Log Entries", f"{total:,}", "📊", "success"),
        ("Database Health", "99.9%", "🟢", "success"),
        ("Active Sessions", "24", "👤", "info"),
        ("Storage Used", "1.2GB", "💾", "warning")
    ]
    
    for label, value, icon, status in metrics:
        st.markdown(f"""
        <div style="background: white; border: 1px solid #E2E8F0; border-radius: 12px; padding: 20px;">
            <div style="font-family: 'Inter', sans-serif; font-size: 12px; font-weight: 600; color: #42474f; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 8px;">
                {label}
            </div>
            <div style="display: flex; align-items: end; justify-content: space-between;">
                <span style="font-family: 'Montserrat', sans-serif; font-size: 32px; font-weight: 700; color: #003B70;">
                    {value}
                </span>
                <span style="font-family: 'Inter', sans-serif; font-size: 14px; color: #10B981; margin-bottom: 4px;">
                    {icon}
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Database Stats
    st.markdown("""
    <div class="card">
        <h3 class="card-title">📊 Statistik Database</h3>
        <div style="display: grid; grid-template-columns: repeat(5, 1fr); gap: 12px;">
    """, unsafe_allow_html=True)
    
    for name, val in stats.items():
        st.markdown(f"""
        <div style="background: #f8fafc; padding: 12px; border-radius: 8px; text-align: center;">
            <div style="font-family: 'Inter', sans-serif; font-size: 10px; font-weight: 600; color: #42474f; text-transform: uppercase; letter-spacing: 0.05em;">
                {name}
            </div>
            <div style="font-family: 'Montserrat', sans-serif; font-size: 20px; font-weight: 700; color: #003B70;">
                {val:,}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div></div>", unsafe_allow_html=True)

    # Activity Log
    st.markdown("""
    <div class="card">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
            <h3 class="card-title" style="margin-bottom: 0;">🕒 Activity Log</h3>
        </div>
    """, unsafe_allow_html=True)
    
    if os.path.exists(LOG_FILE_LOKAL):
        try:
            log_df = pd.read_csv(LOG_FILE_LOKAL)
        except:
            log_df = pd.DataFrame(columns=["Timestamp", "User", "Aksi", "Keterangan"])
    else:
        log_df = pd.DataFrame(columns=["Timestamp", "User", "Aksi", "Keterangan"])

    if not log_df.empty:
        col1, col2 = st.columns([4, 1])
        with col2:
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                log_df.to_excel(writer, index=False, sheet_name='Log_Aktivitas')
            
            st.download_button(
                label="📥 Download Log",
                data=output.getvalue(),
                file_name="Riwayat_Aktivitas_Admin.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        
        st.dataframe(
            log_df.sort_values(by="Timestamp", ascending=False), 
            use_container_width=True, 
            hide_index=True
        )
        
        if st.button("🗑️ Kosongkan Riwayat Log", use_container_width=True):
            os.remove(LOG_FILE_LOKAL)
            st.success("Log telah dibersihkan!")
            st.rerun()
    else:
        st.info("Belum ada riwayat aktivitas yang tercatat di database lokal.")
    
    st.markdown("</div>", unsafe_allow_html=True)
