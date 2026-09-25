# app.py
# Entry point utama SmartBizz AI — landing page & navigasi global
# -------------------------------------------------------

import streamlit as st
from utils.auth import init_session
from utils.styles import apply_global_css

# ── Konfigurasi halaman ───────────────────────────────────────────────────────
st.set_page_config(
    page_title="SmartBizz AI",
    page_icon="assets/logo.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Design tokens (konsisten di semua halaman) ────────────────────────────────
# Primary   : #1D4ED8  (biru tua)
# Secondary : #10B981  (hijau aksen)
# Surface   : #F1F5F9  (abu biru)
# Text      : #0F172A  (near-black)

# ── Global CSS (sidebar, tipografi, card, grid responsif) ────────────────────
# CSS didefinisikan terpusat di utils/styles.py agar konsisten di semua halaman
apply_global_css()

# ── Inisialisasi session ──────────────────────────────────────────────────────
init_session()

# ── Sidebar branding ──────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        "<div style='padding:0.5rem 0 0.25rem;'>"
        "<span style='font-size:1.05rem; font-weight:700; color:#F8FAFC;'>SmartBizz AI</span><br>"
        "<span style='font-size:0.72rem; color:#94A3B8;'>Demand Forecasting — UMKM Kuliner</span>"
        "</div>",
        unsafe_allow_html=True,
    )
    st.divider()

    if st.session_state.logged_in:
        profile = st.session_state.user_profile
        st.markdown(
            f"<div style='font-size:0.85rem; line-height:1.7;'>"
            f"<b>{profile.get('name', 'User')}</b><br>"
            f"<span style='color:#94A3B8; font-size:0.78rem;'>{profile.get('business', '-')}</span>"
            f"</div>",
            unsafe_allow_html=True,
        )
        st.divider()
        if st.button("Logout", use_container_width=True):
            from utils.auth import logout_user
            logout_user()
            st.rerun()
    else:
        st.markdown(
            "<span style='font-size:0.78rem; color:#94A3B8;'>"
            "Silakan login untuk mengakses fitur.</span>",
            unsafe_allow_html=True,
        )

# ── Konten halaman utama ──────────────────────────────────────────────────────
if not st.session_state.logged_in:

    st.markdown("<h1>SmartBizz AI</h1>", unsafe_allow_html=True)
    st.markdown(
        "<p style='color:#475569; font-size:0.95rem; margin-top:0;'>"
        "Platform demand forecasting berbasis AI untuk UMKM kuliner.</p>",
        unsafe_allow_html=True,
    )
    st.divider()

    # Dua kolom responsif via CSS Grid (bukan st.columns)
    # Di mobile (<640px) otomatis stack jadi 1 kolom
    st.markdown(
        "<div class='sb-two-col'>"

        # Kolom kiri: tentang platform
        "<div>"
        "<div class='sb-card'>"
        "<div class='sb-card-label'>Tentang Platform</div>"
        "<p style='font-size:0.88rem; color:#334155; margin:0.75rem 0 0;'>"
        "SmartBizz AI membantu pelaku usaha kuliner dalam:"
        "</p>"
        "<ul style='font-size:0.85rem; color:#475569; margin-top:0.5rem; padding-left:1.2rem; line-height:1.8;'>"
        "<li>Memprediksi demand produk hingga 7 hari ke depan</li>"
        "<li>Mengoptimalkan jumlah produksi dan stok</li>"
        "<li>Menganalisis performa produk secara visual</li>"
        "<li>Mendapatkan rekomendasi produksi otomatis</li>"
        "</ul>"
        "</div>"
        "</div>"

        # Kolom kanan: akun demo
        "<div>"
        "<div class='sb-card'>"
        "<div class='sb-card-label'>Akun Demo</div>"
        "<div style='font-size:0.85rem; color:#475569; margin-top:0.75rem; line-height:2;'>"
        "<b>Email</b><br><code style='background:#F1F5F9; padding:2px 6px; border-radius:4px;'>demo@smartbizz.ai</code><br>"
        "<b>Password</b><br><code style='background:#F1F5F9; padding:2px 6px; border-radius:4px;'>demo123</code>"
        "</div>"
        "<p style='font-size:0.78rem; color:#94A3B8; margin-top:1rem; margin-bottom:0;'>"
        "Pilih halaman Login di sidebar untuk masuk.</p>"
        "</div>"
        "</div>"

        "</div>",
        unsafe_allow_html=True,
    )

else:
    # Sudah login
    profile = st.session_state.user_profile

    st.markdown(
        f"<h1>Selamat datang, {profile.get('name', 'User')}</h1>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<p style='color:#475569; font-size:0.9rem; margin-top:0;'>"
        f"{profile.get('business', '')} &mdash; {profile.get('role', '')}</p>",
        unsafe_allow_html=True,
    )
    st.divider()

    # Navigasi cepat — CSS Grid, auto-fill, responsif di semua ukuran layar
    nav_items = [
        ("Dashboard",        "Ringkasan bisnis & chart utama"),
        ("Data Management",  "Upload & kelola data penjualan"),
        ("Forecast",         "Prediksi demand 7 hari ke depan"),
        ("Recommendation",   "Rekomendasi produksi per produk"),
        ("Product Analysis", "Ranking & distribusi produk"),
        ("AI Assistant",     "Tanya jawab berbasis data bisnis"),
        ("Settings",         "Pengaturan profil bisnis"),
    ]

    cards_html = "".join(
        f"<div class='sb-card'>"
        f"<div class='sb-card-label'>{name}</div>"
        f"<div style='font-size:0.8rem; color:#64748B; margin-top:0.3rem; line-height:1.5;'>{desc}</div>"
        f"</div>"
        for name, desc in nav_items
    )

    st.markdown(
        f"<div class='sb-nav-grid'>{cards_html}</div>",
        unsafe_allow_html=True,
    )
