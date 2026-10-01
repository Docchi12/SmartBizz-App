# utils/styles.py
# Fungsi CSS global SmartBizz AI — dipanggil di SETIAP halaman
# -------------------------------------------------------
# PENTING: Streamlit tidak mewarisi CSS dari app.py ke sub-pages secara otomatis.
# Solusi: panggil apply_global_css() di baris paling atas setiap file halaman,
# tepat setelah st.set_page_config().
#
# Design tokens:
#   Primary   : #37633D  (hijau tua)
#   Secondary : #A1FCAB  (mint terang - aksen) / #A9C9AD (sage muda)
#   Sidebar   : #123316  (hijau sangat gelap)
#   Text      : #0F172A  (near-black)
#   Border    : #A9C9AD  (sage muda)
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

/* ── Sidebar: warna hijau sangat gelap — berlaku di SEMUA halaman ── */
section[data-testid="stSidebar"] {
    background-color: #123316 !important;
}
section[data-testid="stSidebar"] > div:first-child {
    background-color: #123316 !important;
}
section[data-testid="stSidebar"] * {
    color: #FFFFFF !important;
}
section[data-testid="stSidebar"] .stButton > button {
    background-color: #37633D !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 6px !important;
    font-weight: 500 !important;
    width: 100% !important;
}
section[data-testid="stSidebar"] .stButton > button:hover {
    background-color: #A9C9AD !important;
    color: #123316 !important;
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

/* ── Input fields (Global) ── */
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stDateInput > div > div > input,
.stTimeInput > div > div > input,
.stTextArea > div > div > textarea {
    border-radius: 6px !important;
    border: 1px solid #CBD5E1 !important;
    font-size: 0.88rem !important;
    padding: 0.5rem 0.75rem !important;
    color: #0F172A !important;
    background-color: #FFFFFF !important;
}
.stTextInput > div > div > input:focus,
.stNumberInput > div > div > input:focus,
.stDateInput > div > div > input:focus,
.stTimeInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: #37633D !important;
    box-shadow: 0 0 0 2px rgba(55, 99, 61, 0.12) !important;
    outline: none !important;
}
.stTextInput label,
.stNumberInput label,
.stSelectbox label,
.stMultiSelect label,
.stDateInput label,
.stTimeInput label,
.stTextArea label,
.stFileUploader label {
    font-size: 0.82rem !important;
    font-weight: 600 !important;
    color: #374151 !important;
}

/* ── Selectbox & MultiSelect ── */
.stSelectbox div[data-baseweb="select"] > div,
.stMultiSelect div[data-baseweb="select"] > div {
    background-color: #FFFFFF !important;
    border-radius: 6px !important;
    border: 1px solid #CBD5E1 !important;
}
.stSelectbox div[data-baseweb="select"] > div:focus-within,
.stMultiSelect div[data-baseweb="select"] > div:focus-within {
    border-color: #37633D !important;
    box-shadow: 0 0 0 2px rgba(55, 99, 61, 0.12) !important;
}

/* ── Chat Input ── */
.stChatInputContainer {
    background-color: #FFFFFF !important;
    border-radius: 6px !important;
    border: 1px solid #CBD5E1 !important;
}
.stChatInputContainer:focus-within {
    border-color: #37633D !important;
    box-shadow: 0 0 0 2px rgba(55, 99, 61, 0.12) !important;
}
.stChatInputContainer textarea {
    color: #0F172A !important;
    background-color: transparent !important;
}

/* ── File Uploader ── */
[data-testid="stFileUploadDropzone"] {
    background-color: #FFFFFF !important;
    border: 1px dashed #CBD5E1 !important;
    border-radius: 6px !important;
}
[data-testid="stFileUploadDropzone"]:hover {
    border-color: #37633D !important;
    background-color: #F8FAFC !important;
}

/* ── Card reusable ── */
.sb-card {
    background: #FFFFFF;
    border: 1px solid #A9C9AD;
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
    color: #729677;
    margin-bottom: 0.25rem;
}
.sb-card-value {
    font-size: clamp(1.25rem, 3vw, 1.5rem);
    font-weight: 700;
    color: #37633D;
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
hr { border-color: #729677; margin: 1rem 0; }

/* ── Alert ── */
.stAlert { border-radius: 8px; }

/* ── Metric: perkecil font agar proporsional dengan elemen lain ──
   Selector dikonfirmasi dari source Streamlit 1.64 (Metric.B02FwwbX.js):
   testid yang valid: stMetric, stMetricLabel, stMetricValue, stMetricDelta
   Di-apply global tanpa .main (karena st.metric saat ini hanya ada di Data Management).
   Targeting inner div juga ditambahkan agar specificity menang melawan emotion-cache Streamlit.
*/
[data-testid="stMetricValue"], [data-testid="stMetricValue"] > div, [data-testid="stMetricValue"] * {
    font-size: 1.4rem !important;
    font-weight: 700 !important;
    color: #37633D !important;
    line-height: 1.2 !important;
}
[data-testid="stMetricLabel"], [data-testid="stMetricLabel"] > div, [data-testid="stMetricLabel"] * {
    font-size: 0.8rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.04em !important;
    color: #729677 !important;
}
[data-testid="stMetricDelta"] { display: none !important; }
</style>
"""


def apply_global_css() -> None:
    """
    Inject CSS global SmartBizz AI ke halaman aktif.
    Panggil di setiap file halaman tepat setelah st.set_page_config().
    """
    st.markdown(_GLOBAL_CSS, unsafe_allow_html=True)
