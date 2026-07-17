import streamlit as st
import pandas as pd
from thefuzz import fuzz
import re

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

    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    st.markdown("### 🚀 Bulk Screening Initiation")
    
    # Step 1: Select Database
    st.markdown("**Step 1: Select Target Database**")
    list_sheet = list(db_pemerintah.keys())
    db_tujuan = st.selectbox("Pilih Blacklist Database:", list_sheet, key="bulk_db_select")
    st.markdown("---")
    
    # Step 2: Upload
    st.markdown("**Step 2: Upload Excel File**")
    file_nasabah = st.file_uploader("Upload Excel Database Nasabah", type=['xlsx'], key="bulk_upload")
    st.markdown('</div>', unsafe_allow_html=True)

    if file_nasabah:
        df_nasabah = pd.read_excel(file_nasabah)
        
        for col in df_nasabah.columns:
            if pd.api.types.is_datetime64_any_dtype(df_nasabah[col]):
                df_nasabah[col] = df_nasabah[col].dt.strftime('%Y-%m-%d')

        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        st.markdown("**Step 3: Configuration & Mapping**")
        
        cols = df_nasabah.columns.tolist()
        col_target = st.selectbox("Column Mapping (Target Name)", ["-- Pilih Kolom --"] + cols, key="bulk_col_mapping")
        
        threshold = 85
        if col_target != "-- Pilih Kolom --":
            valid_samples = df_nasabah[col_target].dropna()
            sample_val = clean_number_string(valid_samples.iloc[0]) if not valid_samples.empty else ""
            
            is_nik = str(sample_val).isdigit() and len(str(sample_val)) >= 10
            is_tgl = bool(re.match(r'\d{4}-\d{2}-\d{2}', str(sample_val)))

            if not is_nik and not is_tgl:
                threshold = st.slider("Fuzzy Match Sensitivity", 50, 100, 85, key="bulk_threshold")
        
        st.markdown('</div>', unsafe_allow_html=True)

        # Execute
        if st.button("🚀 JALANKAN SCREENING", use_container_width=True, type="primary"):
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
                st.warning(f"⚠️ Terdeteksi {len(df_res)} data match!")
                st.dataframe(df_res, use_container_width=True, hide_index=True)
                
                csv_data = df_res.to_csv(index=False, sep=';').encode('utf-8')
                st.download_button(
                    label="📥 Download Hasil Bulk Screening",
                    data=csv_data,
                    file_name="Hasil_Bulk_Screening.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            else:
                st.success("✅ Bersih! Tidak ada data yang cocok.")
