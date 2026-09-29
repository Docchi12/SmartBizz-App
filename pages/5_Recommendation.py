import streamlit as st
import pandas as pd
from utils.recommendations import get_product_recommendations

# ── Proteksi Halaman ──────────────────────────────────────────────────────────
# Jika belum login, render ulang. app.py akan otomatis navigasi ke Login.
if not st.session_state.get("logged_in", False):
    st.rerun()

try:
    df_sales_raw = st.session_state.get("uploaded_sales_data")
    if df_sales_raw is None or len(df_sales_raw) == 0:
        st.info("Anda belum mengupload data penjualan. Silakan upload data terlebih dahulu di halaman Data Management.")
        if st.button("Ke Halaman Data Management", type="primary", key="rec_to_dm"):
            st.switch_page(st.Page("pages/3_Data_Management.py", title="Data Management", icon=":material/upload_file:"))
        st.stop()
        
    st.markdown("<h2 style='margin-bottom:0.1rem;'>Rekomendasi Produksi & Stok</h2>", unsafe_allow_html=True)
    st.markdown("<p style='font-size:0.85rem; color:#64748B;'>Rekomendasi otomatis berbasis perbandingan antara stok saat ini dan perkiraan permintaan 7 hari ke depan.</p>", unsafe_allow_html=True)
    st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)
    
    rekomendasi = get_product_recommendations(df_sales_raw)
    
    total_recs = len(rekomendasi["kurang_stok"]) + len(rekomendasi["stok_aman"])
    
    if total_recs == 0:
        st.info("Belum ada rekomendasi yang bisa ditampilkan saat ini. Coba upload data dengan riwayat penjualan yang lebih panjang agar tren bisa dianalisis dengan baik.")
        st.stop()
        
    def render_section(title, icon, items, is_warning=False):
        if not items:
            return
        st.markdown(f"<h5>{icon} {title}</h5>", unsafe_allow_html=True)
        
        warna_status = "#DC2626" if is_warning else "#059669"
        bg_status = "#FEF2F2" if is_warning else "#ECFDF5"
        
        for item in items:
            with st.container(border=True):
                st.markdown(f"<h6 style='margin-bottom: 0.5rem; font-size:1.05rem;'>{item['nama']}</h6>", unsafe_allow_html=True)
                
                c1, c2, c3 = st.columns(3)
                c1.metric("Prediksi Demand", f"{item['prediksi_demand']} unit")
                c2.metric("Stok Saat Ini", f"{item['stok_saat_ini']} unit")
                
                c3.markdown(
                    f"<div style='background-color:{bg_status}; color:{warna_status}; padding:0.5rem; border-radius:0.5rem; text-align:center; font-weight:600; font-size:1rem; height: 100%; display: flex; align-items: center; justify-content: center;'>"
                    f"{item['rekomendasi_produksi']}"
                    f"</div>",
                    unsafe_allow_html=True
                )
                
                st.markdown("<div style='height:0.5rem;'></div>", unsafe_allow_html=True)
                st.markdown(f"<p style='font-size:0.9rem; color:#475569; margin:0;'>💡 <b>Alasan:</b> {item['alasan']}</p>", unsafe_allow_html=True)
        st.markdown("<div style='height:1.5rem;'></div>", unsafe_allow_html=True)
        
    render_section("Produk yang Perlu Segera Ditambah", "🚨", rekomendasi["kurang_stok"], is_warning=True)
    render_section("Stok Aman", "✅", rekomendasi["stok_aman"], is_warning=False)
        
except Exception as e:
    st.error(f"Terjadi masalah saat memproses data Anda. Silakan periksa kembali data di halaman Data Management. Pesan Error: {e}")
    if st.button("Ke Halaman Data Management", type="primary", key="err_btn_recommendation"):
        st.switch_page(st.Page("pages/3_Data_Management.py", title="Data Management", icon=":material/upload_file:"))
    st.stop()
