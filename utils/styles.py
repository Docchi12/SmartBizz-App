# utils/styles.py
# Fungsi CSS global SmartBizz AI — dipanggil di SETIAP halaman
# -------------------------------------------------------
# PENTING: Streamlit tidak mewarisi CSS dari app.py ke sub-pages secara otomatis.
# Solusi: panggil apply_global_css() di baris paling atas setiap file halaman,
# tepat setelah st.set_page_config().
#
# Design tokens:
#   Primary   : #1D4ED8  (biru tua)
#   Secondary : #10B981  (hijau aksen)
#   Surface   : #F1F5F9  (abu biru)
#   Text      : #0F172A  (near-black)
#   Border    : #E2E8F0
# -------------------------------------------------------

import streamlit as st

_GLOBAL_CSS = """
<style>
/* ── Google Font ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

/* ── Base ── */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* ── Typography ── */
h1 { font-size: clamp(1.25rem, 3vw, 1.75rem); font-weight: 700;
     color: #0F172A; margin-bottom: 0.25rem; }
h2 { font-size: clamp(1rem, 2vw, 1.25rem);    font-weight: 600; color: #1E293B; }
h3 { font-size: 1rem;                          font-weight: 600; color: #334155; }

/* ── Sidebar: warna navy gelap — berlaku di SEMUA halaman ── */
section[data-testid="stSidebar"] {
    background-color: #0F172A !important;
}
section[data-testid="stSidebar"] > div:first-child {
    background-color: #0F172A !important;
}
section[data-testid="stSidebar"] * {
    color: #E2E8F0 !important;
}
section[data-testid="stSidebar"] .stButton > button {
    background-color: #1D4ED8 !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 6px !important;
    font-weight: 500 !important;
    width: 100% !important;
}
section[data-testid="stSidebar"] .stButton > button:hover {
    background-color: #1E40AF !important;
}

/* ── Tombol collapse sidebar — selalu terlihat ── */
button[data-testid="stSidebarCollapseButton"],
button[data-testid="collapsedControl"] {
    display: flex !important;
    visibility: visible !important;
    opacity: 1 !important;
    z-index: 9999 !important;
}

/* ── Sidebar responsif: mobile ── */
@media (max-width: 640px) {
    section[data-testid="stSidebar"] {
        width: 72% !important;
        min-width: 72% !important;
        max-width: 72% !important;
    }
    button[data-testid="stSidebarCollapseButton"] {
        width: 2.5rem !important;
        height: 2.5rem !important;
        min-width: 2.5rem !important;
    }
}

/* ── Sidebar responsif: tablet ── */
@media (min-width: 641px) and (max-width: 1024px) {
    section[data-testid="stSidebar"] {
        min-width: 220px !important;
        max-width: 260px !important;
    }
}

/* ── Main content area ── */
.main .block-container {
    padding-left:  clamp(1rem, 3vw, 3rem);
    padding-right: clamp(1rem, 3vw, 3rem);
    padding-top: 1.5rem;
    max-width: 100%;
}

/* ── Card reusable ── */
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

/* ── Responsive grids ── */
.sb-nav-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
    gap: 1rem;
    margin-top: 0.5rem;
}
.sb-two-col {
    display: grid;
    grid-template-columns: 3fr 2fr;
    gap: 1.5rem;
    align-items: start;
}
@media (max-width: 640px) {
    .sb-two-col { grid-template-columns: 1fr; }
    .sb-nav-grid { grid-template-columns: 1fr 1fr; }
}
@media (max-width: 480px) {
    .sb-card { padding: 1rem 1.1rem; }
}

/* ── Divider ── */
hr { border-color: #E2E8F0; margin: 1rem 0; }

/* ── Alert ── */
.stAlert { border-radius: 8px; }
</style>
"""


def apply_global_css() -> None:
    """
    Inject CSS global SmartBizz AI ke halaman aktif.
    Panggil di setiap file halaman tepat setelah st.set_page_config().
    """
    st.markdown(_GLOBAL_CSS, unsafe_allow_html=True)
