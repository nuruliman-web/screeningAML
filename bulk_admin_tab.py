import streamlit as st
import pandas as pd
from thefuzz import fuzz
import re
import time

def clean_number_string(val):
    if pd.isna(val) or str(val).lower() == 'none' or str(val).strip() == '':
        return None
    s = str(val).strip().replace("'", "")
    if 'e+' in s.lower():
        try:
            s = format(float(s), '.0f')
        except:
            pass
    return s

def run_bulk_screening():
    import screening_tab as sc
    db_pemerintah, stats, total = sc.fetch_all_data()

    if db_pemerintah is None:
        st.error("Gagal memuat Blacklist Database.")
        return

    st.markdown("""
    <div class="card">
        <h3 class="card-title">Bulk Screening Initiation</h3>
        <div style="display: flex; align-items: center; gap: 24px; margin-bottom: 24px;">
            <div style="display: flex; align-items: center; gap: 8px;">
                <div style="width: 32px; height: 32px; border-radius: 50%; background: #003B70; color: white; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 12px;">1</div>
                <span style="font-family: 'Inter', sans-serif; font-size: 12px; font-weight: 600; color: #003B70;">Source</span>
            </div>
            <div style="width: 48px; height: 1px; background: #c3c6d1;"></div>
            <div style="display: flex; align-items: center; gap: 8px;">
                <div style="width: 32px; height: 32px; border-radius: 50%; background: #d8e3fa; color: #42474f; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 12px;">2</div>
                <span style="font-family: 'Inter', sans-serif; font-size: 12px; font-weight: 600; color: #42474f;">Upload</span>
            </div>
            <div style="width: 48px; height: 1px; background: #c3c6d1;"></div>
            <div style="display: flex; align-items: center; gap: 8px;">
                <div style="width: 32px; height: 32px; border-radius: 50%; background: #d8e3fa; color: #42474f; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 12px;">3</div>
                <span style="font-family: 'Inter', sans-serif; font-size: 12px; font-weight: 600; color: #42474f;">Execute</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Step 1: Select Database
    st.markdown("""
    <div class="card">
        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 16px;">
            <div style="width: 24px; height: 24px; border-radius: 50%; background: #d8e3fa; display: flex; align-items: center; justify-content: center;">
                <span class="material-symbols-outlined" style="font-size: 14px; color: #003B70;">database</span>
            </div>
            <h4 style="font-family: 'Inter', sans-serif; font-size: 14px; font-weight: 600; color: #111c2c; margin: 0;">Step 1: Select Target Database</h4>
        </div>
    """, unsafe_allow_html=True)
    
    list_sheet = list(db_pemerintah.keys())
    db_tujuan = st.selectbox("Pilih Blacklist Database:", list_sheet, key="bulk_db_select", label_visibility="collapsed")
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Step 2: Upload
    st.markdown("""
    <div class="card">
        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 16px;">
            <div style="width: 24px; height: 24px; border-radius: 50%; background: #d8e3fa; display: flex; align-items: center; justify-content: center;">
                <span class="material-symbols-outlined" style="font-size: 14px; color: #003B70;">upload_file</span>
            </div>
            <h4 style="font-family: 'Inter', sans-serif; font-size: 14px; font-weight: 600; color: #111c2c; margin: 0;">Step 2: Upload Excel File</h4>
        </div>
    """, unsafe_allow_html=True)
    
    file_nasabah = st.file_uploader("Drag & drop file here atau klik untuk browse", type=['xlsx'], key="bulk_upload", label_visibility="collapsed")
    st.markdown("</div>", unsafe_allow_html=True)

    if file_nasabah:
        df_nasabah = pd.read_excel(file_nasabah)
        
        for col in df_nasabah.columns:
            if pd.api.types.is_datetime64_any_dtype(df_nasabah[col]):
                df_nasabah[col] = df_nasabah[col].dt.strftime('%Y-%m-%d')

        # Step 3: Configuration
        st.markdown("""
        <div class="card">
            <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 16px;">
                <div style="width: 24px; height: 24px; border-radius: 50%; background: #d8e3fa; display: flex; align-items: center; justify-content: center;">
                    <span class="material-symbols-outlined" style="font-size: 14px; color: #003B70;">tune</span>
                </div>
                <h4 style="font-family: 'Inter', sans-serif; font-size: 14px; font-weight: 600; color: #111c2c; margin: 0;">Step 3: Configuration & Mapping</h4>
            </div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 24px;">
        """, unsafe_allow_html=True)
        
        cols = df_nasabah.columns.tolist()
        
        # Column mapping
        col_target = st.selectbox("Column Mapping (Target Name)", ["-- Pilih Kolom --"] + cols, key="bulk_col_mapping")
        
        # Threshold
        threshold = 85
        if col_target != "-- Pilih Kolom --":
            valid_samples = df_nasabah[col_target].dropna()
            sample_val = clean_number_string(valid_samples.iloc[0]) if not valid_samples.empty else ""
            
            is_nik = str(sample_val).isdigit() and len(str(sample_val)) >= 10
            is_tgl = bool(re.match(r'\d{4}-\d{2}-\d{2}', str(sample_val)))

            if not is_nik and not is_tgl:
                threshold = st.slider("Fuzzy Match Sensitivity", 50, 100, 85, key="bulk_threshold")
        
        st.markdown("</div></div>", unsafe_allow_html=True)

        # Execute button
        if st.button("🚀 Jalankan Screening", use_container_width=True, type="primary"):
            if col_target == "-- Pilih Kolom --":
                st.warning("Silakan pilih kolom data nasabah terlebih dahulu.")
                return
            
            target_db = db_pemerintah[db_tujuan]
            results = []
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for i, row_n in df_nasabah.iterrows():
                val_nasabah = clean_number_string(row_n[col_target])
                if val_nasabah is None:
                    continue
                
                if i % 10 == 0:
                    progress = (i + 1) / len(df_nasabah)
                    progress_bar.progress(progress)
                    status_text.text(f"Memproses data ke-{i+1} dari {len(df_nasabah)}...")

                for _, row_p in target_db.iterrows():
                    match_details = []
                    row_is_match = False

                    for col_db in target_db.columns:
                        val_db = clean_number_string(row_p[col_db])
                        if val_db is None:
                            continue
                            
                        score = 0
                        found = False

                        if is_nik or is_tgl:
                            if val_nasabah == val_db:
                                score, found = 100, True
                        else:
                            score = fuzz.token_sort_ratio(val_nasabah.lower(), val_db.lower())
                            if score >= threshold:
                                found = True
                        
                        if found:
                            match_details.append(f"{col_db} ({score}%)")
                            row_is_match = True
                    
                    if row_is_match:
                        res_entry = row_n.to_dict()
                        res_entry["Ket Match"] = ", ".join(match_details)
                        for k, v in row_p.items():
                            if isinstance(v, pd.Timestamp):
                                v = v.strftime('%Y-%m-%d')
                            res_entry[f"DB_{k}"] = v
                        results.append(res_entry)
                        break

            progress_bar.progress(1.0)
            status_text.text("Selesai!")

            if results:
                df_res = pd.DataFrame(results)
                
                # Results card
                st.markdown(f"""
                <div class="card">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
                        <h4 style="font-family: 'Montserrat', sans-serif; font-size: 18px; font-weight: 600; color: #003B70; margin: 0;">
                            ⚠️ Hasil Screening
                        </h4>
                        <span class="badge badge-danger">{len(df_res)} Data Match</span>
                    </div>
                """, unsafe_allow_html=True)
                
                st.dataframe(df_res, use_container_width=True, hide_index=True)
                
                csv_data = df_res.to_csv(index=False, sep=';').encode('utf-8')
                st.download_button(
                    label="📥 Download Hasil Bulk Screening",
                    data=csv_data,
                    file_name="Hasil_Bulk_Screening.csv",
                    mime="text/csv",
                    use_container_width=True
                )
                st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.success("✅ Bersih! Tidak ada data yang cocok.")
