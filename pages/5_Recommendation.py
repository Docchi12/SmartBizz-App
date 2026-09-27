import streamlit as st
import pandas as pd
from utils.recommendations import get_product_recommendations

try:
    df_sales_raw = st.session_state.get("uploaded_sales_data")
    if df_sales_raw is None or len(df_sales_raw) == 0:
        st.info("Anda belum mengupload data penjualan. Silakan upload data terlebih dahulu di halaman Data Management.")
        if st.button("Ke Halaman Data Management", type="primary", key="rec_to_dm"):
            st.switch_page(st.Page("pages/3_Data_Management.py", title="Data Management", icon=":material/upload_file:"))
        st.stop()
        
    prices_dict = st.session_state.get("product_prices", {})
    
    st.markdown("<h2 style='margin-bottom:0.1rem;'>Rekomendasi</h2>", unsafe_allow_html=True)
    st.markdown("<p style='font-size:0.85rem; color:#64748B;'>Rekomendasi otomatis berbasis analisis tren penjualan dan keuntungan per porsi produk Anda.</p>", unsafe_allow_html=True)
    st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)
    
    rekomendasi = get_product_recommendations(df_sales_raw, prices_dict)
    
    # Cek apakah ada data harga modal yang terisi di seluruh produk yang terdeteksi
    has_any_modal = False
    if prices_dict:
        unique_products = df_sales_raw['nama_produk'].unique()
        for p in unique_products:
            if prices_dict.get(p, {}).get("harga_modal", 0) > 0:
                has_any_modal = True
                break
    
    total_recs = sum(len(items) for items in rekomendasi.values())
    
    if total_recs == 0:
        st.info("Belum ada rekomendasi yang bisa ditampilkan saat ini. Coba upload data dengan riwayat penjualan yang lebih panjang (misal 7+ hari) agar tren bisa dianalisis dengan baik, dan sebagian besar mungkin masih stabil.")
        st.stop()
        
    def render_section(title, icon, items):
        if not items:
            return
        st.markdown(f"<h5>{icon} {title}</h5>", unsafe_allow_html=True)
        for item in items:
            with st.container(border=True):
                st.markdown(f"**{item['nama']}**")
                st.markdown(f"<p style='font-size:0.8rem; color:#64748B; margin-bottom:0.2rem;'>Alasan: {item['alasan']}</p>", unsafe_allow_html=True)
                st.markdown(f"<p style='font-size:0.85rem; font-weight:500; margin-bottom:0;'>Aksi: {item['aksi']}</p>", unsafe_allow_html=True)
        st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)
        
    render_section("Produk Andalan", "⭐", rekomendasi["produk_andalan"])
    render_section("Perlu Tambah Stok", "📈", rekomendasi["perlu_tambah_stok"])
    render_section("Pantau atau Kurangi Produksi", "📉", rekomendasi["pantau_kurangi"])
    
    # Kategori Tinjau Harga/Margin hanya relevan jika ada minimal satu produk dengan modal terisi
    if has_any_modal:
        render_section("Tinjau Harga Jual/Untung", "💰", rekomendasi["tinjau_harga"])
        
except Exception as e:
    st.error("Terjadi masalah saat memproses data Anda. Silakan periksa kembali data di halaman Data Management, atau upload ulang jika perlu.")
    if st.button("Ke Halaman Data Management", type="primary", key="err_btn_recommendation"):
        st.switch_page(st.Page("pages/3_Data_Management.py", title="Data Management", icon=":material/upload_file:"))
    st.stop()
