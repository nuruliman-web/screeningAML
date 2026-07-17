import streamlit as st
import pandas as pd
from thefuzz import fuzz
import io
from auth_utils import log_activity

# Konfigurasi Link Database
LINK_SHEETS = {
    "JUDOL": "https://docs.google.com/spreadsheets/d/e/2PACX-1vTwj6BDBGvo9yWRYMkPGNxPi9KtLrbU8qT8zA5VdiogRlp1JoxBDADyh3xF2gWROuPS0pBujoYiKUn-/pub?gid=1397546375&single=true&output=csv",
    "DTTOT": "https://docs.google.com/spreadsheets/d/e/2PACX-1vTwj6BDBGvo9yWRYMkPGNxPi9KtLrbU8qT8zA5VdiogRlp1JoxBDADyh3xF2gWROuPS0pBujoYiKUn-/pub?gid=1229360429&single=true&output=csv",
    "DPPSPM": "https://docs.google.com/spreadsheets/d/e/2PACX-1vTwj6BDBGvo9yWRYMkPGNxPi9KtLrbU8qT8zA5VdiogRlp1JoxBDADyh3xF2gWROuPS0pBujoYiKUn-/pub?gid=1059062603&single=true&output=csv",
    "SIPENDAR": "https://docs.google.com/spreadsheets/d/e/2PACX-1vTwj6BDBGvo9yWRYMkPGNxPi9KtLrbU8qT8zA5VdiogRlp1JoxBDADyh3xF2gWROuPS0pBujoYiKUn-/pub?gid=288835560&single=true&output=csv"
}

@st.cache_data(ttl=600)
def fetch_all_data():
    all_d, stats, total = {}, {}, 0
    for name, url in LINK_SHEETS.items():
        try:
            df = pd.read_csv(url)
            all_d[name] = df
            stats[name] = len(df)
            total += len(df)
        except:
            continue
    return all_d, stats, total

def run_pencarian(user_email, db, is_admin):
    st.markdown("""
    <div class="card">
        <div style="display: grid; grid-template-columns: 2fr 1fr; gap: 24px;">
            <div>
                <label class="form-label">TIPE IDENTIFIKASI</label>
                <div style="display: flex; gap: 16px; margin-bottom: 16px;">
                    <label style="display: flex; align-items: center; gap: 8px; cursor: pointer;">
                        <input type="radio" name="search_type" value="Nama" checked style="accent-color: #003B70;">
                        <span style="font-family: 'Inter', sans-serif; font-size: 14px;">Nama</span>
                    </label>
                    <label style="display: flex; align-items: center; gap: 8px; cursor: pointer;">
                        <input type="radio" name="search_type" value="NIK" style="accent-color: #003B70;">
                        <span style="font-family: 'Inter', sans-serif; font-size: 14px;">NIK</span>
                    </label>
                    <label style="display: flex; align-items: center; gap: 8px; cursor: pointer;">
                        <input type="radio" name="search_type" value="Paspor" style="accent-color: #003B70;">
                        <span style="font-family: 'Inter', sans-serif; font-size: 14px;">Paspor</span>
                    </label>
                </div>
            </div>
            <div>
                <label class="form-label">SIMILARITY THRESHOLD</label>
                <div style="display: flex; align-items: center; gap: 12px;">
                    <span style="font-family: 'Inter', sans-serif; font-size: 14px; font-weight: 500; color: #003B70; background: #d4e3ff; padding: 2px 12px; border-radius: 4px;">85%</span>
                    <input type="range" min="50" max="100" value="85" style="flex: 1;" id="threshold-slider">
                </div>
                <div style="display: flex; justify-content: space-between; margin-top: 4px;">
                    <span style="font-family: 'Inter', sans-serif; font-size: 10px; color: #42474f;">Loose</span>
                    <span style="font-family: 'Inter', sans-serif; font-size: 10px; color: #42474f;">Strict</span>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Streamlit components (hidden with CSS)
    col1, col2 = st.columns([3, 1])
    with col1:
        metode = st.radio("", ["Nama", "NIK", "Paspor"], horizontal=True, key="search_method", label_visibility="collapsed")
        query = st.text_input("CARI DATA", placeholder="Masukkan nama atau nomor identitas...", key="search_query", label_visibility="collapsed")
    with col2:
        threshold = st.slider("", 50, 100, 85, key="threshold", label_visibility="collapsed")
    
    # Search button
    col1, col2, col3 = st.columns([1, 1, 4])
    with col1:
        if st.button("🔍 JALANKAN SCREENING", use_container_width=True, type="primary"):
            if query:
                perform_search(query, metode, threshold, user_email, db, is_admin)
            else:
                st.warning("Silakan masukkan data yang ingin dicari.")
    
    st.markdown("</div>", unsafe_allow_html=True)

def perform_search(query, metode, threshold, user_email, db, is_admin):
    q_strip = query.replace(" ", "").replace(".", "").replace("-", "")
    
    if metode == "NIK" and len(q_strip) < 16:
        st.error(f"❌ NIK minimal 16 digit! (Input Anda: {len(q_strip)} digit)")
        return
    
    log_activity(user_email, f"Cari {metode}: {query} (Acc: {threshold}%)")
    q_clean = " ".join(query.split()).lower()
    found = False
    res_dict = {}

    for name, df in db.items():
        def fuzzy_identify(row):
            best_score = 0
            match_details = []
            target_cols = df.columns if metode != "Nama" else [c for c in df.columns if 'nama' in c.lower()]
            
            for col in target_cols:
                val = str(row[col]).lower()
                score = fuzz.token_sort_ratio(q_clean, val)
                if score >= threshold:
                    match_details.append(f"{col} ({score}%)")
                    if score > best_score:
                        best_score = score
            
            if best_score > 0:
                return pd.Series([best_score, "MATCH: " + ", ".join(match_details)])
            else:
                return pd.Series([0, None])

        df_c = df.copy()
        df_c[['_score', 'HASIL IDENTIFIKASI']] = df_c.apply(fuzzy_identify, axis=1)
        matches = df_c[df_c['_score'] >= threshold].copy()
        
        if not matches.empty:
            found = True
            matches = matches.sort_values('_score', ascending=False).drop(columns=['_score'])
            cols = matches.columns.tolist()
            cols.insert(0, cols.pop(cols.index('HASIL IDENTIFIKASI')))
            matches = matches[cols]
            res_dict[name] = matches
            
            st.markdown(f"""
            <div class="card">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                    <h3 style="font-family: 'Montserrat', sans-serif; font-size: 16px; font-weight: 600; color: #003B70; margin: 0;">
                        🚩 Ditemukan di Database: {name}
                    </h3>
                    <span class="badge badge-danger">{len(matches)} ditemukan</span>
                </div>
            """, unsafe_allow_html=True)
            st.dataframe(matches, hide_index=True, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

    if found and is_admin:
        st.divider()
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            for sheet_name, data_frame in res_dict.items():
                data_frame.to_excel(writer, index=False, sheet_name=sheet_name[:31])
        
        st.download_button(
            label=f"📥 Download Temuan '{query}' (Excel Multi-Sheet)",
            data=output.getvalue(),
            file_name=f"Screening_{query}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    elif not found:
        st.info("✅ Data tidak ditemukan di semua database.")
