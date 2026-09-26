# utils/layout.py
# Komponen layout bersama SmartBizz AI
# -------------------------------------------------------
# Fungsi di sini dipanggil di SETIAP halaman yang membutuhkan
# komponen layout yang sama (sidebar, header, dll).
# Pola ini memastikan perubahan cukup dilakukan di 1 tempat.
# -------------------------------------------------------

import streamlit as st


def render_sidebar() -> None:
    """
    Render sidebar navigasi & profil SmartBizz AI.
    Panggil di setiap halaman setelah set_page_config() dan apply_global_css().
    """
    with st.sidebar:
        # ── Brand header ──────────────────────────────────────────────
        st.markdown(
            "<div style='padding:0.5rem 0 0.25rem;'>"
            "<span style='font-size:1.05rem; font-weight:700; color:#F8FAFC;'>SmartBizz AI</span><br>"
            "<span style='font-size:0.72rem; color:#94A3B8;'>Demand Forecasting — UMKM Kuliner</span>"
            "</div>",
            unsafe_allow_html=True,
        )
        st.divider()

        # ── Profil & logout (hanya jika sudah login) ──────────────────
        if st.session_state.get("logged_in", False):
            profile = st.session_state.get("user_profile", {})
            st.markdown(
                f"<div style='font-size:0.85rem; line-height:1.7;'>"
                f"<b>{profile.get('name', 'User')}</b><br>"
                f"<span style='color:#94A3B8; font-size:0.78rem;'>{profile.get('business', '-')}</span>"
                f"</div>",
                unsafe_allow_html=True,
            )
            st.divider()
            if st.button("Logout", use_container_width=True, key="sidebar_logout"):
                from utils.auth import logout_user
                logout_user()
                st.rerun()
        else:
            st.markdown(
                "<span style='font-size:0.78rem; color:#94A3B8;'>"
                "Silakan login untuk mengakses fitur.</span>",
                unsafe_allow_html=True,
            )

def render_table_interactive_tip() -> None:
    """
    Menampilkan tip/affordance di atas st.dataframe untuk memberi tahu
    user bahwa header kolom bisa di-klik untuk fitur interaktif (sort/stats).
    """
    st.markdown(
        "<p style='font-size:0.8rem; color:#1D4ED8; font-weight:500; margin-top:-0.5rem; margin-bottom:0.75rem;'>"
        "💡 Tip: Klik ikon pada judul kolom untuk mengurutkan atau melihat statistik data."
        "</p>",
        unsafe_allow_html=True
    )
