# pages/1_Login.py
# Halaman Login + Register SmartBizz AI (satu halaman, toggle via session_state)
# -------------------------------------------------------
# MODE "login"    : form login (default)
# MODE "register" : form daftar akun baru
# Toggle antar mode pakai st.button bergaya link teks (.sb-link-btn)
# Auth  : login_user(), register_user() dari utils/auth.py
# Layout: layout="centered" + st.container(border=True)
# -------------------------------------------------------

import streamlit as st
from utils.auth import init_session, login_user, register_user


# ── CSS lokal ─────────────────────────────────────────────────────────────────
# Token: Primary #1D4ED8 | Surface #F1F5F9 | Text #0F172A | Border #E2E8F0
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* ── Container utama ── */
    .main > .block-container {
        max-width: 440px;
        padding-top: 3rem;
        padding-left:  1.25rem;
        padding-right: 1.25rem;
    }

    /* ── Card (st.container border=True) ── */
    [data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 12px !important;
        border: 1px solid #E2E8F0 !important;
        padding: 2rem 2rem 1.5rem !important;
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.07) !important;
        background: #FFFFFF !important;
    }

    /* ── Input field ── */
    .stTextInput > div > div > input {
        border-radius: 6px;
        border: 1px solid #CBD5E1;
        font-size: 0.88rem;
        padding: 0.5rem 0.75rem;
        color: #0F172A;
    }
    .stTextInput > div > div > input:focus {
        border-color: #1D4ED8 !important;
        box-shadow: 0 0 0 2px rgba(29, 78, 216, 0.12) !important;
        outline: none;
    }
    .stTextInput label {
        font-size: 0.82rem;
        font-weight: 600;
        color: #374151;
    }

    /* ── Tombol aksi utama (Masuk / Daftar): full width, primary color ── */
    .stButton > button[kind="secondaryFormSubmit"],
    .stButton > button[kind="primary"],
    .sb-action-btn .stButton > button {
        width: 100%;
        background-color: #1D4ED8;
        color: #FFFFFF !important;
        border: none;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.9rem;
        padding: 0.55rem 0;
        margin-top: 0.25rem;
        transition: background-color 0.15s ease;
    }

    /* Fallback: semua button di dalam container ── */
    [data-testid="stVerticalBlockBorderWrapper"] .stButton > button {
        width: 100%;
        background-color: #1D4ED8;
        color: #FFFFFF !important;
        border: none;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.9rem;
        padding: 0.55rem 0;
        transition: background-color 0.15s ease;
    }
    [data-testid="stVerticalBlockBorderWrapper"] .stButton > button:hover {
        background-color: #1E40AF !important;
    }
    [data-testid="stVerticalBlockBorderWrapper"] .stButton > button:active {
        background-color: #1E3A8A !important;
    }

    /* ── Tombol link toggle mode — tampak seperti teks link ── */
    /* Wrapper .sb-link-btn membungkus button yang ingin di-style sebagai link */
    .sb-link-btn > div > .stButton > button,
    .sb-link-btn .stButton > button {
        background: none !important;
        border: none !important;
        color: #1D4ED8 !important;
        font-size: 0.82rem !important;
        font-weight: 500 !important;
        padding: 0.1rem 0 !important;
        margin: 0 auto !important;
        width: auto !important;
        min-height: unset !important;
        text-decoration: underline !important;
        box-shadow: none !important;
        display: block !important;
        text-align: center !important;
    }
    .sb-link-btn > div > .stButton > button:hover,
    .sb-link-btn .stButton > button:hover {
        background: none !important;
        color: #1E40AF !important;
    }

    /* ── Alert ── */
    .stAlert {
        border-radius: 7px;
        font-size: 0.85rem;
        margin-top: 0.5rem;
    }

    /* ── Mobile ── */
    @media (max-width: 480px) {
        .main > .block-container {
            padding-top: 1.75rem;
            padding-left: 1rem;
            padding-right: 1rem;
        }
        [data-testid="stVerticalBlockBorderWrapper"] {
            padding: 1.5rem 1.25rem 1.25rem !important;
        }
    }
    /* ── Footer baris tunggal (Login & Register) ── */
    /* Flex-row pada container yang langsung mengikuti marker div */
    div:has(.marker-footer-login) + div[data-testid="stVerticalBlock"],
    div:has(.marker-footer-reg)   + div[data-testid="stVerticalBlock"] {
        flex-direction: row !important;
        justify-content: center !important;
        align-items: center !important;
        gap: 0.3rem !important;
    }
    div:has(.marker-footer-login) + div[data-testid="stVerticalBlock"] [data-testid="stMarkdown"],
    div:has(.marker-footer-reg)   + div[data-testid="stVerticalBlock"] [data-testid="stMarkdown"] {
        margin: 0 !important;
        padding: 0 !important;
        width: auto !important;
        flex: 0 0 auto !important;
    }
    div:has(.marker-footer-login) + div[data-testid="stVerticalBlock"] [data-testid="stMarkdown"] p,
    div:has(.marker-footer-reg)   + div[data-testid="stVerticalBlock"] [data-testid="stMarkdown"] p {
        margin: 0 !important;
        font-size: 0.82rem !important;
        color: #64748B !important;
        white-space: nowrap;
    }
    div:has(.marker-footer-login) + div[data-testid="stVerticalBlock"] [data-testid="stButton"],
    div:has(.marker-footer-reg)   + div[data-testid="stVerticalBlock"] [data-testid="stButton"] {
        width: auto !important;
        flex: 0 0 auto !important;
    }
    div:has(.marker-footer-login) + div[data-testid="stVerticalBlock"] button,
    div:has(.marker-footer-reg)   + div[data-testid="stVerticalBlock"] button {
        background: none !important;
        border: none !important;
        box-shadow: none !important;
        color: #0F172A !important;
        font-size: 0.82rem !important;
        font-weight: 600 !important;
        padding: 0 !important;
        width: auto !important;
        min-height: unset !important;
    }
    div:has(.marker-footer-login) + div[data-testid="stVerticalBlock"] button p,
    div:has(.marker-footer-reg)   + div[data-testid="stVerticalBlock"] button p {
        color: #0F172A !important;
        font-size: 0.82rem !important;
        font-weight: 600 !important;
        margin: 0 !important;
    }
    div:has(.marker-footer-login) + div[data-testid="stVerticalBlock"] button:hover p,
    div:has(.marker-footer-reg)   + div[data-testid="stVerticalBlock"] button:hover p {
        text-decoration: underline !important;
        color: #0F172A !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Inisialisasi session ──────────────────────────────────────────────────────
init_session()

# Init state mode: "login" atau "register"
if "auth_mode" not in st.session_state:
    st.session_state.auth_mode = "login"

# Dengan st.navigation(), rerun menyebabkan app.py rebuild pages list berdasarkan
# logged_in=True → st.navigation() otomatis navigasi ke halaman pertama (Dashboard)
if st.session_state.logged_in:
    st.rerun()

# ── Brand header ──────────────────────────────────────────────────────────────
st.markdown(
    "<div style='text-align:center; margin-bottom:1.75rem;'>"
    "<div style='font-size:1.65rem; font-weight:700; color:#0F172A; "
    "letter-spacing:-0.02em;'>SmartBizz AI</div>"
    "<div style='font-size:0.8rem; color:#64748B; margin-top:0.3rem;'>"
    "Demand Forecasting untuk UMKM Kuliner</div>"
    "</div>",
    unsafe_allow_html=True,
)

# ── Helper: tombol toggle mode ────────────────────────────────────────────────
def _switch_mode(target: str, keys_to_clear: list[str]):
    """Pindah auth_mode dan bersihkan input field mode sebelumnya."""
    st.session_state.auth_mode = target
    for k in keys_to_clear:
        st.session_state.pop(k, None)
    st.rerun()


def _send_reset_email(email: str) -> bool:
    # TODO: BACKEND - ganti dengan implementasi asli pengiriman email reset password
    # dari tim Software Engineer (integrasi SMTP / layanan email transaksional)
    return True  # dummy: selalu sukses


@st.dialog("Reset Password")
def _dialog_reset_password():
    """Dialog dummy reset password — tidak terhubung ke backend asli."""
    st.markdown(
        "<p style='font-size:0.875rem; color:#374151; margin-bottom:1rem;'>"
        "Masukkan email akun Anda, kami akan mengirimkan link reset password."
        "</p>",
        unsafe_allow_html=True,
    )

    reset_email = st.text_input(
        "Email",
        placeholder="contoh@email.com",
        key="reset_email_input",
    )

    if "_reset_sent" not in st.session_state:
        st.session_state["_reset_sent"] = False

    if st.session_state["_reset_sent"]:
        st.success(
            "Jika email terdaftar, link reset password telah dikirim. "
            "Silakan cek inbox Anda."
        )
        if st.button("Tutup", key="btn_reset_close"):
            st.session_state.pop("_reset_sent", None)
            st.session_state.pop("reset_email_input", None)
            st.rerun()
    else:
        if st.button("Kirim Link Reset", key="btn_reset_send"):
            if not reset_email.strip() or "@" not in reset_email:
                st.error("Masukkan email yang valid.")
            else:
                _send_reset_email(reset_email.strip())
                st.session_state["_reset_sent"] = True
                st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# MODE LOGIN
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.auth_mode == "login":

    with st.container(border=True):

        st.markdown(
            "<p style='font-size:0.95rem; font-weight:600; color:#0F172A; "
            "margin:0 0 1.25rem;'>Masuk ke akun Anda</p>",
            unsafe_allow_html=True,
        )

        email = st.text_input(
            "Email",
            placeholder="contoh@email.com",
            key="login_email",
        )
        password = st.text_input(
            "Password",
            type="password",
            placeholder="Masukkan password",
            key="login_password",
        )

        # ── Lupa kata sandi ─────────────────────────────────────────────
        # Marker untuk posisi button tepat di bawah password, rata kanan
        st.markdown("<div class='marker-lupa' style='display:none'></div>", unsafe_allow_html=True)
        if st.button("Lupa kata sandi?", type="tertiary", key="btn_lupa_sandi"):
            st.session_state.pop("_reset_sent", None)  # reset state dialog
            _dialog_reset_password()

        # CSS: posisi & gaya button Lupa kata sandi (scoped via marker)
        st.markdown(
            """
            <style>
            /* Wrapper stButton tepat setelah marker-lupa */
            div:has(.marker-lupa) + div[data-testid="stButton"] {
                display: flex !important;
                justify-content: flex-end !important;
                margin-top: -1.1rem !important;
                margin-bottom: 0.75rem !important;
            }
            div:has(.marker-lupa) + div[data-testid="stButton"] button {
                background: none !important;
                border: none !important;
                box-shadow: none !important;
                color: #0F172A !important;
                font-size: 0.75rem !important;
                font-weight: 500 !important;
                padding: 0 !important;
                width: auto !important;
                min-height: unset !important;
            }
            div:has(.marker-lupa) + div[data-testid="stButton"] button:hover p {
                text-decoration: underline !important;
                color: #0F172A !important;
            }
            div:has(.marker-lupa) + div[data-testid="stButton"] button p {
                color: #0F172A !important;
                font-size: 0.75rem !important;
                font-weight: 500 !important;
                margin: 0 !important;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )

        login_clicked = st.button("Masuk", use_container_width=True, key="btn_login")

        # ── Logika login ──────────────────────────────────────────────────────
        if login_clicked:
            if not email.strip() or not password:
                st.error("Email dan password tidak boleh kosong.")
            else:
                # TODO: BACKEND - ganti dengan validasi ke database asli & hashing password
                if login_user(email, password):
                    st.rerun()
                else:
                    st.error("Email atau password tidak sesuai.")

        # ── Info demo & link ke Register ─────────────────────────────────────
        st.markdown(
            "<p style='font-size:0.75rem; color:#94A3B8; text-align:center; "
            "margin:1rem 0 0.25rem;'>"
            "Demo: <code style='background:#F1F5F9; padding:1px 5px; "
            "border-radius:3px;'>demo@smartbizz.ai</code> / "
            "<code style='background:#F1F5F9; padding:1px 5px; "
            "border-radius:3px;'>demo123</code></p>",
            unsafe_allow_html=True,
        )

        # ── Footer Links (Daftar) ─────────────────────────────────────────────
        st.markdown(
            "<hr style='border-color:#F1F5F9; margin:0.75rem 0;'>",
            unsafe_allow_html=True,
        )
        # Marker agar CSS flex hanya berlaku pada container footer ini
        st.markdown("<div class='marker-footer-login' style='display:none'></div>", unsafe_allow_html=True)
        with st.container():
            st.markdown(
                "<p>Belum punya akun?</p>",
                unsafe_allow_html=True,
            )
            if st.button("Daftar", type="tertiary", key="go_register"):
                _switch_mode("register", ["login_email", "login_password"])


# ══════════════════════════════════════════════════════════════════════════════
# MODE REGISTER
# ══════════════════════════════════════════════════════════════════════════════
else:

    with st.container(border=True):

        st.markdown(
            "<p style='font-size:0.95rem; font-weight:600; color:#0F172A; "
            "margin:0 0 1.25rem;'>Buat akun baru</p>",
            unsafe_allow_html=True,
        )

        reg_name     = st.text_input("Nama Lengkap",     placeholder="Nama Anda",        key="reg_name")
        reg_business = st.text_input("Nama Usaha/Bisnis", placeholder="Nama warung/kedai", key="reg_business")
        reg_email    = st.text_input("Email",             placeholder="contoh@email.com", key="reg_email")
        reg_password = st.text_input("Password",          type="password",
                                     placeholder="Min. 6 karakter",                       key="reg_password")
        reg_confirm  = st.text_input("Konfirmasi Password", type="password",
                                     placeholder="Ulangi password",                       key="reg_confirm")

        st.markdown("<div style='height:0.4rem;'></div>", unsafe_allow_html=True)

        daftar_clicked = st.button("Daftar", use_container_width=True, key="btn_register")

        # ── Logika Register ───────────────────────────────────────────────────
        if daftar_clicked:
            # Validasi 1: field kosong
            if not all([reg_name.strip(), reg_business.strip(),
                        reg_email.strip(), reg_password, reg_confirm]):
                st.error("Semua field wajib diisi.")

            # Validasi 2: format email
            elif "@" not in reg_email or "." not in reg_email.split("@")[-1]:
                st.error("Format email tidak valid.")

            # Validasi 3: panjang password
            elif len(reg_password) < 6:
                st.error("Password minimal 6 karakter.")

            # Validasi 4: konfirmasi password
            elif reg_password != reg_confirm:
                st.error("Konfirmasi password tidak cocok.")

            else:
                # TODO: BACKEND - ganti dengan insert ke database asli & hashing password
                ok, err_msg = register_user(
                    name=reg_name,
                    business=reg_business,
                    email=reg_email,
                    password=reg_password,
                )
                if ok:
                    # Bersihkan field register, arahkan balik ke Login
                    for k in ["reg_name", "reg_business", "reg_email",
                              "reg_password", "reg_confirm"]:
                        st.session_state.pop(k, None)
                    st.session_state.auth_mode = "login"
                    st.session_state["_register_success"] = True
                    st.rerun()
                else:
                    st.error(err_msg)

        # ── Footer Links (Balik ke Login) ─────────────────────────────────────
        st.markdown(
            "<hr style='border-color:#F1F5F9; margin:0.75rem 0;'>",
            unsafe_allow_html=True,
        )
        # Marker agar CSS flex hanya berlaku pada container footer ini
        st.markdown("<div class='marker-footer-reg' style='display:none'></div>", unsafe_allow_html=True)
        with st.container():
            st.markdown(
                "<p>Sudah punya akun?</p>",
                unsafe_allow_html=True,
            )
            if st.button("Masuk", type="tertiary", key="go_login"):
                _switch_mode(
                    "login",
                    ["reg_name", "reg_business", "reg_email",
                     "reg_password", "reg_confirm"],
                )

# ── Tampilkan pesan sukses register (setelah rerun balik ke mode login) ───────
if st.session_state.pop("_register_success", False):
    st.success("Akun berhasil dibuat. Silakan masuk dengan akun baru Anda.")
