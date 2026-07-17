import streamlit as st
import pandas as pd
import io
import os

def run_log_admin(stats, total):
    LOG_FILE_LOKAL = "admin_activity_log.csv"
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📊 Total Log Entries", f"{total:,}")
    with col2:
        st.metric("🟢 Database Health", "99.9%")
    with col3:
        st.metric("👤 Active Sessions", "24")
    with col4:
        st.metric("💾 Storage Used", "1.2GB")
    
    st.divider()
    
    # Database Stats
    st.markdown("### 📊 Statistik Database")
    cols = st.columns(len(stats) + 1)
    for i, (name, val) in enumerate(stats.items()):
        with cols[i]:
            st.metric(label=name.upper(), value=f"{val:,}")
    with cols[-1]:
        st.metric(label="TOTAL", value=f"{total:,}")

    st.divider()

    # Activity Log
    st.markdown("### 🕒 Activity Log")
    
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
            if os.path.exists(LOG_FILE_LOKAL):
                os.remove(LOG_FILE_LOKAL)
            st.success("Log telah dibersihkan!")
            st.rerun()
    else:
        st.info("Belum ada riwayat aktivitas yang tercatat di database lokal.")
