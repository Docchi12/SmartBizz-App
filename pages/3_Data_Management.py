# pages/3_Data_Management.py
# Halaman Data Management SmartBizz AI
# -------------------------------------------------------
# Halaman ini menggunakan konfigurasi, global CSS, dan sidebar
# yang dirender secara terpusat dari app.py.

import streamlit as st
import pandas as pd

# ── Proteksi Halaman ──────────────────────────────────────────────────────────
# Jika belum login, render ulang. app.py akan otomatis navigasi ke Login.
if not st.session_state.get("logged_in", False):
    st.rerun()

# Inisialisasi state untuk menyimpan data CSV yang diupload
if "uploaded_sales_data" not in st.session_state:
    st.session_state["uploaded_sales_data"] = None

# ── Header Halaman ────────────────────────────────────────────────────────────
st.markdown(
    "<h2 style='margin-bottom:0.5rem;'>Data Management</h2>"
    "<p style='font-size:0.9rem; color:#64748B; margin-top:0;'>"
    "Unggah dan kelola data penjualan bisnis Anda untuk dianalisis oleh AI."
    "</p>",
    unsafe_allow_html=True,
)
st.markdown("<div style='height:0.5rem;'></div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# DATA FUNCTIONS
# ══════════════════════════════════════════════════════════════════════════════

def get_sample_data() -> pd.DataFrame:
    # TODO: BACKEND - ganti dengan data contoh yang diambil dari API/DB jika diperlukan
    return pd.DataFrame({
        "tanggal": [
            "2024-09-25", "2024-09-25", "2024-09-25", "2024-09-25", 
            "2024-09-26", "2024-09-26", "2024-09-26", "2024-09-26",
            "2024-09-27", "2024-09-27", "2024-09-27", "2024-09-27",
            "2024-09-28", "2024-09-28", "2024-09-28"
        ],
        "nama_produk": [
            "Es Kopi Susu", "Nasi Goreng Spesial", "Roti Bakar", "Mie Goreng",
            "Es Kopi Susu", "Nasi Goreng Spesial", "Roti Bakar", "Mie Goreng",
            "Es Kopi Susu", "Nasi Goreng Spesial", "Roti Bakar", "Mie Goreng",
            "Es Kopi Susu", "Nasi Goreng Spesial", "Roti Bakar"
        ],
        "jumlah_terjual": [
            45, 30, 20, 25,
            50, 28, 22, 26,
            42, 35, 18, 30,
            55, 40, 25
        ]
    })


# Mapping snake_case → label human-readable (hanya untuk tampilan, bukan data asli)
_COLUMN_LABELS = {
    "tanggal":        "Tanggal",
    "nama_produk":    "Nama Produk",
    "jumlah_terjual": "Jumlah Terjual",
}


def _format_rentang_tanggal(df: pd.DataFrame) -> str:
    """Kembalikan string rentang tanggal dari kolom 'tanggal', format: 'DD MMM - DD MMM YYYY'."""
    _BULAN = ["", "Jan", "Feb", "Mar", "Apr", "Mei", "Jun",
              "Jul", "Agu", "Sep", "Okt", "Nov", "Des"]
    try:
        tanggal = pd.to_datetime(df["tanggal"], dayfirst=False, errors="coerce").dropna()
        if tanggal.empty:
            return "-"
        tmin, tmax = tanggal.min(), tanggal.max()
        awal  = f"{tmin.day} {_BULAN[tmin.month]}"
        akhir = f"{tmax.day} {_BULAN[tmax.month]} {tmax.year}"
        return f"{awal} - {akhir}"
    except Exception:
        return "-"


def _get_template_csv_bytes() -> bytes:
    """
    Generate CSV template kosong (hanya header) untuk diunduh user.
    Baris pertama 'sep=,' adalah hint resmi Microsoft Excel agar selalu
    membaca file ini dengan delimiter koma, terlepas dari locale user.
    Baris 'sep=,' ini TIDAK terbaca oleh pd.read_csv karena engine Python
    akan skip baris yang tidak mengandung delimiter yang konsisten.
    Catatan: pd.read_csv dengan sep=None/engine='python' sudah menangani ini
    secara otomatis — baris sep= diabaikan saat parsing.
    """
    return "sep=,\nTanggal,Nama Produk,Jumlah Terjual\n2024-09-25,Es Kopi Susu,45\n".encode("utf-8-sig")


# ══════════════════════════════════════════════════════════════════════════════
# RENDER HALAMAN
# ══════════════════════════════════════════════════════════════════════════════

with st.container(border=True):
    st.markdown("<h4>Unggah Data Penjualan</h4>", unsafe_allow_html=True)
    st.markdown(
        "<p style='font-size:0.85rem; color:#64748B; margin-bottom:1rem;'>"
        "File CSV Anda harus memiliki 3 kolom: <b>Tanggal, Nama Produk, Jumlah Terjual</b>. "
        "Kapitalisasi dan spasi pada nama kolom tidak perlu persis sama."
        "</p>",
        unsafe_allow_html=True
    )
    
    if st.session_state["uploaded_sales_data"] is not None:
        df = st.session_state["uploaded_sales_data"]

        # TODO: BACKEND - ganti dengan validasi lebih lengkap dan penyimpanan permanen ke database asli
        st.success("Data berhasil dibaca. Dataset siap digunakan untuk perkiraan penjualan.")

        # ── Ringkasan Data (Summary Metrics) ──────────────────────────────
        jumlah_produk_unik = df["nama_produk"].nunique()
        rentang_tanggal = _format_rentang_tanggal(df)
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Baris Data", f"{len(df):,} baris")
        m2.metric("Rentang Tanggal", rentang_tanggal)
        m3.metric("Jumlah Produk Unik", f"{jumlah_produk_unik} produk")

        st.markdown("<div style='height:0.75rem;'></div>", unsafe_allow_html=True)

        # ── Preview: rename kolom untuk tampilan, index disembunyikan ─────
        st.markdown("<h5>Preview Data</h5>", unsafe_allow_html=True)
        st.markdown(
            f"<p style='font-size:0.8rem; color:#64748B; margin-top:-0.5rem;'>"
            f"Menampilkan {min(10, len(df))} dari total {len(df)} baris data.</p>",
            unsafe_allow_html=True
        )
        # Rename hanya untuk tampilan — data asli di session_state tetap snake_case
        df_display = df.head(10).rename(columns=_COLUMN_LABELS)
        
        # Tip interaktif untuk user mobile
        from utils.layout import render_table_interactive_tip
        render_table_interactive_tip()
        
        st.dataframe(df_display, use_container_width=True, hide_index=True)

        st.markdown("<div style='height:0.75rem;'></div>", unsafe_allow_html=True)
        if st.button("Hapus & Upload Ulang", key="btn_reset_upload"):
            st.session_state["uploaded_sales_data"] = None
            st.rerun()
            
    else:
        uploaded_file = st.file_uploader("Pilih file CSV", type=["csv"], label_visibility="collapsed")
        
        st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)
        
        if uploaded_file is not None:
            try:
                # Baca file CSV — auto-detect delimiter, buang BOM dari Excel.
                # Sebelum parsing, baca raw untuk strip baris 'sep=X' yang
                # sering disertakan Excel/app lain sebagai hint delimiter.
                # Pandas tidak mengenali baris ini dan akan salah baca jika dibiarkan.
                raw_bytes = uploaded_file.read()
                lines = raw_bytes.decode("utf-8-sig").splitlines(keepends=True)
                # Buang baris 'sep=...' di posisi mana pun sebelum header
                filtered = "".join(l for l in lines if not l.strip().lower().startswith("sep="))
                import io as _io
                df = pd.read_csv(_io.StringIO(filtered), sep=None, engine="python")
                
                # Normalisasi nama kolom: lowercase + ganti spasi dengan underscore
                # Ini agar user bisa menulis "Nama Produk", "nama produk", atau "NAMA_PRODUK"
                # dan semuanya diterima — validasi internal tetap pakai snake_case
                df.columns = (
                    df.columns
                    .str.strip()
                    .str.lower()
                    .str.replace(r"\s+", "_", regex=True)
                )
                
                # Cek eksistensi kolom
                required_cols = ["tanggal", "nama_produk", "jumlah_terjual"]
                missing_cols = [col for col in required_cols if col not in df.columns]
                
                if len(df) == 0:
                    st.error(
                        "File CSV kosong — tidak ada baris data yang ditemukan. "
                        "Pastikan file memiliki setidaknya 1 baris data di bawah baris header."
                    )
                elif missing_cols:
                    kolom_hilang = ', '.join(f"'{c}'" for c in missing_cols)
                    st.error(
                        f"Kolom {kolom_hilang} tidak ditemukan di file Anda. "
                        f"File harus memiliki kolom: Tanggal, Nama Produk, Jumlah Terjual "
                        f"(kapitalisasi dan spasi tidak masalah, cukup kata kuncinya ada)."
                    )
                else:
                    # Cek tipe data kolom jumlah_terjual (harus angka/numerik)
                    if not pd.api.types.is_numeric_dtype(df["jumlah_terjual"]):
                        st.error(
                            "Kolom 'jumlah_terjual' berisi nilai yang bukan angka. "
                            "Pastikan kolom ini hanya berisi angka bulat (contoh: 10, 50, 100), "
                            "bukan teks seperti '10 pcs' atau '10,5'."
                        )
                    else:
                        st.session_state["uploaded_sales_data"] = df
                        st.rerun()

            except pd.errors.EmptyDataError:
                st.error(
                    "File CSV tidak dapat dibaca — file tampaknya kosong atau tidak memiliki header. "
                    "Pastikan baris pertama berisi nama kolom: tanggal, nama_produk, jumlah_terjual."
                )
            except Exception as e:
                st.error(
                    f"Terjadi kesalahan saat membaca file CSV. "
                    f"Pastikan file tidak rusak dan formatnya benar. Detail teknis: {e}"
                )
                
        else:
            # ── Empty State ───────────────────────────────────────────────
            st.markdown(
                "<div style='text-align:center; padding:1.5rem 0 1rem;'>"
                "<div style='font-size:2.5rem; margin-bottom:0.75rem;'>&#128193;</div>"
                "<p style='font-size:0.95rem; font-weight:600; color:#0F172A; margin:0 0 0.3rem;'>"
                "Belum ada data penjualan.</p>"
                "<p style='font-size:0.85rem; color:#64748B; margin:0;'>"
                "Upload file CSV untuk mulai menganalisis dan membuat perkiraan penjualan."
                "</p></div>",
                unsafe_allow_html=True,
            )
            st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)

            # Info format kolom yang dibutuhkan + contoh satu baris
            with st.container(border=True):
                st.markdown(
                    "<p style='font-size:0.85rem; font-weight:600; color:#0F172A; margin:0 0 0.4rem;'>"
                    "Format kolom yang dibutuhkan</p>"
                    "<p style='font-size:0.8rem; color:#64748B; margin:0 0 0.75rem;'>"
                    "File CSV Anda harus memiliki 3 kolom berikut. "
                    "Kapitalisasi dan spasi tidak perlu persis sama — sistem akan menyesuaikan otomatis:</p>",
                    unsafe_allow_html=True,
                )
                contoh = pd.DataFrame({
                    "tanggal":        ["2024-09-25"],
                    "nama_produk":    ["Es Kopi Susu"],
                    "jumlah_terjual": [45],
                })
                st.dataframe(
                    contoh.rename(columns=_COLUMN_LABELS),
                    use_container_width=True,
                    hide_index=True,
                )
                st.markdown(
                    "<p style='font-size:0.78rem; color:#94A3B8; margin:0.5rem 0 0;'>"
                    "Kolom tanggal: format YYYY-MM-DD atau DD/MM/YYYY. "
                    "Kolom jumlah_terjual: angka bulat tanpa satuan."
                    "</p>",
                    unsafe_allow_html=True,
                )
                st.download_button(
                    label="Unduh Template CSV",
                    data=_get_template_csv_bytes(),
                    file_name="template_data_penjualan.csv",
                    mime="text/csv",
                    key="btn_download_template",
                )
