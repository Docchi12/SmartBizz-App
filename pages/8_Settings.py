import streamlit as st

# Set page config harus command pertama (jika dieksekusi sebagai halaman independen)
try:
    st.set_page_config(initial_sidebar_state="expanded")
except:
    pass # Abaikan jika sudah di-set oleh app.py

# Proteksi Halaman
if not st.session_state.get("logged_in", False):
    st.switch_page("pages/1_Login.py")

from utils.styles import apply_global_css
apply_global_css()

def save_business_profile(nama, kategori, lokasi):
    # TODO: BACKEND - ganti dengan implementasi asli simpan ke database dari tim Software Engineer
    st.session_state["nama_usaha"] = nama
    st.session_state["kategori_usaha"] = kategori
    st.session_state["lokasi_usaha"] = lokasi

st.markdown("<h2 style='margin-bottom:0.1rem;'>Pengaturan</h2>", unsafe_allow_html=True)
st.markdown("<p style='font-size:0.85rem; color:#64748B;'>Kelola informasi dasar bisnis Anda.</p>", unsafe_allow_html=True)
st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)

if st.session_state.get("_settings_success"):
    st.success("Profil bisnis berhasil diperbarui.")
    st.session_state["_settings_success"] = False

with st.container(border=True):
    with st.form("settings_form"):
        nama_usaha = st.text_input(
            "Nama Usaha", 
            value=st.session_state.get("nama_usaha", "Kedai Makan Barokah")
        )
        
        kategori_opsi = ["Makanan Berat", "Minuman", "Cemilan/Snack", "Roti & Kue", "Lainnya"]
        kategori_default = st.session_state.get("kategori_usaha", "Makanan Berat")
        idx = kategori_opsi.index(kategori_default) if kategori_default in kategori_opsi else 0
        kategori_usaha = st.selectbox(
            "Kategori Usaha",
            options=kategori_opsi,
            index=idx
        )
        
        lokasi_usaha = st.text_input(
            "Lokasi", 
            value=st.session_state.get("lokasi_usaha", ""),
            placeholder="Nama kota/kecamatan"
        )
        
        submitted = st.form_submit_button("Simpan Perubahan", type="primary")
        
        if submitted:
            save_business_profile(nama_usaha, kategori_usaha, lokasi_usaha)
            st.session_state["_settings_success"] = True
            st.rerun()
