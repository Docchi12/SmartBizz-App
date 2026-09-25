# app.py
# Entry point utama SmartBizz AI — landing page & navigasi global
# -------------------------------------------------------

import streamlit as st
from utils.auth import init_session

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

# ── Global CSS ────────────────────────────────────────────────────────────────
# CATATAN RESPONSIVE:
# - Sidebar Streamlit di mobile adalah overlay drawer (perilaku default Streamlit).
#   CSS di bawah TIDAK menambahkan position:fixed atau width hardcode, sehingga
#   tidak memperparah overlay. Kita mengandalkan mekanisme bawaan Streamlit.
# - Layout konten menggunakan CSS Grid dengan auto-fill + minmax, bukan kolom
#   fixed st.columns, sehingga otomatis wrap di layar sempit.
# - Semua ukuran menggunakan satuan relatif (rem, %, vw) — tidak ada px hardcode
#   pada elemen layout utama.
st.markdown(
    """
    <style>
    /* ── Google Font ── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    /* ── Base ── */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* ── Typography hierarchy ── */
    h1 { font-size: clamp(1.25rem, 3vw, 1.75rem); font-weight: 700; color: #0F172A; margin-bottom: 0.25rem; }
    h2 { font-size: clamp(1rem, 2vw, 1.25rem);    font-weight: 600; color: #1E293B; }
    h3 { font-size: 1rem;                          font-weight: 600; color: #334155; }

    /* ── Sidebar — warna & lebar responsif ── */
    section[data-testid="stSidebar"] {
        background-color: #0F172A;
    }
    section[data-testid="stSidebar"] * {
        color: #E2E8F0 !important;
    }
    section[data-testid="stSidebar"] .stButton > button {
        background-color: #1D4ED8;
        color: #FFFFFF !important;
        border: none;
        border-radius: 6px;
        font-weight: 500;
        width: 100%;
    }
    section[data-testid="stSidebar"] .stButton > button:hover {
        background-color: #1E40AF;
    }

    /* ── Tombol collapse — selalu tampil & mudah dijangkau ── */
    button[data-testid="stSidebarCollapseButton"],
    button[data-testid="collapsedControl"] {
        display: flex !important;
        visibility: visible !important;
        opacity: 1 !important;
        z-index: 9999 !important;
    }

    /* ── Mobile: batasi lebar sidebar ── */
    /* Sengaja tidak 100% agar area konten di belakang tetap terlihat   */
    /* sebagai indikasi visual bahwa sidebar adalah overlay, bukan halaman penuh */
    @media (max-width: 640px) {
        section[data-testid="stSidebar"] {
            width: 72% !important;
            min-width: 72% !important;
            max-width: 72% !important;
        }
        /* Tombol collapse lebih besar di mobile agar mudah di-tap dengan jari */
        button[data-testid="stSidebarCollapseButton"] {
            width: 2.5rem !important;
            height: 2.5rem !important;
            min-width: 2.5rem !important;
        }
    }

    /* ── Tablet: sidebar sedikit lebih sempit dari desktop ── */
    @media (min-width: 641px) and (max-width: 1024px) {
        section[data-testid="stSidebar"] {
            min-width: 220px !important;
            max-width: 260px !important;
        }
    }

    /* ── Main content area — beri max-width & padding responsif ── */
    .main .block-container {
        padding-left:  clamp(1rem, 3vw, 3rem);
        padding-right: clamp(1rem, 3vw, 3rem);
        padding-top: 1.5rem;
        max-width: 100%;
    }

    /* ── Card dasar ── */
    .sb-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 1.25rem 1.5rem;
        box-shadow: 0 1px 4px rgba(0,0,0,0.06);
        height: 100%;
        box-sizing: border-box;
    }
    .sb-card-label {
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        color: #64748B;
        margin-bottom: 0.25rem;
    }
    .sb-card-value {
        font-size: clamp(1.25rem, 3vw, 1.5rem);
        font-weight: 700;
        color: #1D4ED8;
    }

    /* ── Responsive CSS Grid untuk nav cards ── */
    /* auto-fill: jumlah kolom otomatis menyesuaikan lebar container */
    /* minmax(180px, 1fr): minimal 180px, tumbuh hingga 1 fraksi sisa ruang */
    .sb-nav-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
        gap: 1rem;
        margin-top: 0.5rem;
    }

    /* ── Dua kolom responsif untuk landing page ── */
    /* Di layar sempit (<640px): stack jadi 1 kolom */
    .sb-two-col {
        display: grid;
        grid-template-columns: 3fr 2fr;
        gap: 1.5rem;
        align-items: start;
    }
    @media (max-width: 640px) {
        .sb-two-col {
            grid-template-columns: 1fr;
        }
    }

    /* ── Divider ── */
    hr { border-color: #E2E8F0; margin: 1rem 0; }

    /* ── Button primary ── */
    .stButton > button[kind="primary"] {
        background-color: #1D4ED8;
        border-radius: 6px;
        font-weight: 600;
    }

    /* ── Alert/Info strip ── */
    .stAlert {
        border-radius: 8px;
    }

    /* ── Mobile: kurangi padding card ── */
    @media (max-width: 480px) {
        .sb-card {
            padding: 1rem 1.1rem;
        }
        .sb-nav-grid {
            grid-template-columns: 1fr 1fr;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

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
