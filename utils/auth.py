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
    Cek DUMMY_USERS (akun hardcode) + _temp_users (akun yang didaftarkan
    via Register dalam sesi ini, disimpan di session_state).

    Returns:
        True jika credential valid, False jika tidak.
    """
    email = email.strip().lower()
    # Cek akun hardcode
    if DUMMY_USERS.get(email) == password:
        return True
    # Cek akun yang baru didaftarkan dalam sesi ini
    temp_users = st.session_state.get("_temp_users", {})
    return temp_users.get(email) == password


def get_user_profile(email: str) -> dict:
    """
    Ambil profil user berdasarkan email.

    # TODO: BACKEND - ganti dengan query profil dari database asli
    Cek DUMMY_PROFILES dulu, lalu _temp_profiles (profil dari Register).

    Returns:
        dict profil user, atau dict kosong kalau tidak ditemukan.
    """
    email = email.strip().lower()
    if email in DUMMY_PROFILES:
        return DUMMY_PROFILES[email]
    temp_profiles = st.session_state.get("_temp_profiles", {})
    return temp_profiles.get(email, {})


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


def register_user(
    name: str,
    business: str,
    email: str,
    password: str,
) -> tuple[bool, str]:
    """
    Daftarkan user baru ke penyimpanan sementara (session_state).

    # TODO: BACKEND - ganti dengan insert ke database asli & hashing password
    Saat ini data hanya bertahan selama sesi browser aktif.

    Returns:
        (True, "") jika berhasil.
        (False, "pesan error") jika gagal validasi.
    """
    email = email.strip().lower()

    # Init penyimpanan sementara jika belum ada
    if "_temp_users" not in st.session_state:
        st.session_state._temp_users = {}
    if "_temp_profiles" not in st.session_state:
        st.session_state._temp_profiles = {}

    # Cek duplikat email di DUMMY_USERS & akun yang sudah didaftarkan
    if email in DUMMY_USERS or email in st.session_state._temp_users:
        return False, "Email sudah terdaftar."

    # Simpan credential & profil ke session_state
    st.session_state._temp_users[email] = password
    st.session_state._temp_profiles[email] = {
        "name": name.strip(),
        "business": business.strip(),
        "role": "Owner",
    }
    return True, ""


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
