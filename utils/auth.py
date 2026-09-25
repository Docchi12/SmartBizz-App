# utils/auth.py
# Modul autentikasi SmartBizz AI
# -------------------------------------------------------
# Semua fungsi login/session di sini menggunakan data dummy.
# TODO: BACKEND - ganti dengan implementasi asli dari tim Software Engineer
#   (misal: query ke database user, validasi token JWT, dsb)
# -------------------------------------------------------

import streamlit as st

# ── Dummy user credential (hardcode 1 akun demo) ──────────────────────────────
# TODO: BACKEND - ganti dengan lookup ke database user asli
DUMMY_USERS = {
    "admin@smartbizz.ai": "smartbizz123",
    "demo@smartbizz.ai": "demo123",
}

# ── Dummy user profile ────────────────────────────────────────────────────────
# TODO: BACKEND - ganti dengan data profil dari database
DUMMY_PROFILES = {
    "admin@smartbizz.ai": {
        "name": "Admin SmartBizz",
        "business": "Warung Kopi Nusantara",
        "role": "Owner",
    },
    "demo@smartbizz.ai": {
        "name": "Demo User",
        "business": "Kedai Makan Barokah",
        "role": "Manager",
    },
}


def check_login(email: str, password: str) -> bool:
    """
    Validasi credential login.

    # TODO: BACKEND - ganti dengan autentikasi ke database/API asli
    Saat ini hanya mengecek terhadap DUMMY_USERS hardcode.

    Returns:
        True jika credential valid, False jika tidak.
    """
    return DUMMY_USERS.get(email.strip().lower()) == password


def get_user_profile(email: str) -> dict:
    """
    Ambil profil user berdasarkan email.

    # TODO: BACKEND - ganti dengan query profil dari database asli

    Returns:
        dict profil user, atau dict kosong kalau tidak ditemukan.
    """
    return DUMMY_PROFILES.get(email.strip().lower(), {})


def init_session():
    """Inisialisasi session state jika belum ada."""
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "user_email" not in st.session_state:
        st.session_state.user_email = ""
    if "user_profile" not in st.session_state:
        st.session_state.user_profile = {}


def login_user(email: str, password: str) -> bool:
    """
    Proses login: validasi credential & simpan ke session state.

    Returns:
        True jika berhasil login, False jika gagal.
    """
    if check_login(email, password):
        st.session_state.logged_in = True
        st.session_state.user_email = email.strip().lower()
        st.session_state.user_profile = get_user_profile(email)
        return True
    return False


def logout_user():
    """Hapus session state & logout user."""
    st.session_state.logged_in = False
    st.session_state.user_email = ""
    st.session_state.user_profile = {}


def require_login():
    """
    Guard: hentikan render halaman jika user belum login.
    Tampilkan pesan & tombol redirect ke Login.
    Panggil di bagian atas setiap halaman yang butuh autentikasi.
    """
    init_session()
    if not st.session_state.logged_in:
        st.warning("Anda harus login terlebih dahulu.")
        st.info("Silakan kembali ke halaman Login melalui sidebar.")
        st.stop()
