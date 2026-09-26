# app.py
# Entry point SmartBizz AI — shell st.navigation()
# -------------------------------------------------------
# File ini hanya bertugas:
#   1. set_page_config (satu kali untuk seluruh app)
#   2. CSS global & session init
#   3. Menentukan daftar halaman secara KONDISIONAL (login vs tidak)
#   4. Render sidebar bersama
#   5. Menjalankan halaman aktif via pg.run()
#
# Semua konten halaman ada di masing-masing file pages/
#
# Design tokens:
#   Primary : #1D4ED8 | Surface : #F1F5F9 | Text : #0F172A | Border : #E2E8F0
# -------------------------------------------------------

import streamlit as st
from utils.auth import init_session
from utils.styles import apply_global_css
from utils.layout import render_sidebar

# ── set_page_config: SATU KALI untuk seluruh app ─────────────────────────────
# layout="wide" berlaku global; Login page mengatur lebarnya sendiri via CSS lokal
# initial_sidebar_state: "expanded" untuk Dashboard, sidebar Login otomatis minimal
#   karena tidak ada halaman lain yang tampil saat belum login
st.set_page_config(
    page_title="SmartBizz AI",
    page_icon="assets/logo.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global CSS & Session ──────────────────────────────────────────────────────
apply_global_css()
init_session()

# ── Daftar halaman — KONDISIONAL berdasarkan status login ────────────────────
# Sebelum login : hanya halaman Login yang tampil di sidebar (tidak ada "bocor")
# Sesudah login : Dashboard (dan halaman lain nanti) tampil di sidebar
if st.session_state.logged_in:
    pages = [
        st.Page("pages/2_Dashboard.py", title="Dashboard", icon=":material/dashboard:"),
        # Tambahkan halaman baru di sini setelah dibuat:
        st.Page("pages/3_Data_Management.py", title="Data Management",  icon=":material/upload_file:"),
        # st.Page("pages/4_Forecast.py",         title="Forecast",          icon=":material/trending_up:"),
        # st.Page("pages/5_Recommendation.py",   title="Rekomendasi",       icon=":material/recommend:"),
        # st.Page("pages/6_Product_Analysis.py", title="Analisis Produk",   icon=":material/bar_chart:"),
        # st.Page("pages/7_AI_Assistant.py",     title="AI Assistant",      icon=":material/smart_toy:"),
        # st.Page("pages/8_Settings.py",         title="Pengaturan",        icon=":material/settings:"),
    ]
    nav_position = "sidebar"   # Nav tampil di sidebar saat sudah login
else:
    pages = [
        st.Page("pages/1_Login.py", title="Login", default=True),
    ]
    nav_position = "hidden"    # Tidak ada nav saat belum login (hanya 1 halaman)

# ── Navigasi ──────────────────────────────────────────────────────────────────
pg = st.navigation(pages, position=nav_position)

# ── Sidebar brand & profil (bersama, semua halaman) ──────────────────────────
# Sidebar hanya ter-render bermakna saat logged_in=True (ada profil + logout)
# Saat Login, sidebar collapsed dan tidak menampilkan nav
render_sidebar()

# ── Jalankan halaman aktif ────────────────────────────────────────────────────
pg.run()
