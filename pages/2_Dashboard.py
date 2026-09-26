# pages/2_Dashboard.py
# Halaman Dashboard utama SmartBizz AI
# -------------------------------------------------------
# Komponen:
#   A. Business Summary — 4 kartu sejajar (st.columns)
#   B. Chart: Sales Trend (line chart, 30 hari)
#   C. Chart: Actual vs Forecast (2 garis)
# Data bisnis: DUMMY STATIS — sambungkan ke backend asli via fungsi TODO di bawah
# Tanggal header: datetime.now() — real-time, bukan dummy
# -------------------------------------------------------

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta


# ── Pengecekan Data (Empty State) ─────────────────────────────────────────────
df_sales_raw = st.session_state.get("uploaded_sales_data")
if df_sales_raw is None or len(df_sales_raw) == 0:
    st.info("Anda belum mengupload data penjualan. Silakan upload data terlebih dahulu di halaman Data Management.")
    if st.button("Ke Halaman Data Management", type="primary", key="dash_to_dm"):
        st.switch_page(st.Page("pages/3_Data_Management.py", title="Data Management", icon=":material/upload_file:"))
    st.stop()

# Siapkan data agregasi harian secara global untuk dashboard
df_sales = df_sales_raw.copy()
df_sales['tanggal'] = pd.to_datetime(df_sales['tanggal'])
df_daily_all = df_sales.groupby('tanggal')['jumlah_terjual'].sum().reset_index()

# ══════════════════════════════════════════════════════════════════════════════
# DATA FUNCTIONS — ganti implementasi dummy dengan yang asli saat backend siap
# ══════════════════════════════════════════════════════════════════════════════

def get_summary_data() -> dict:
    # TODO: BE - Ganti dengan query summary ke database asli
    total_produk = df_sales['nama_produk'].nunique()
    
    # Dummy logic untuk forecast hari ini: rata-rata harian dari 7 hari terakhir
    recent_daily = df_daily_all.tail(7)['jumlah_terjual'].mean()
    forecast_hari = int(recent_daily) if not pd.isna(recent_daily) else 0
    
    # Dummy logic untuk restock count: statis 3 atau persentase produk
    restock_count = min(3, total_produk)
    
    # Dummy logic untuk risk status
    risk_status = "Aman"
    if recent_daily < 50:
        risk_status = "Perhatian"
        
    return {
        "total_produk":   total_produk,
        "forecast_hari":  forecast_hari,
        "restock_count":  restock_count,
        "risk_status":    risk_status,
    }


def get_sales_trend_data() -> pd.DataFrame:
    # Filter 30 hari terakhir
    max_date = df_daily_all['tanggal'].max()
    min_date = max_date - pd.Timedelta(days=30)
    df_trend = df_daily_all[df_daily_all['tanggal'] > min_date].copy()
    df_trend.rename(columns={'jumlah_terjual': 'penjualan'}, inplace=True)
    return df_trend


def get_actual_vs_forecast_data() -> pd.DataFrame:
    # TODO: BE - Ganti dengan query aktual + output forecast engine asli
    df_trend = get_sales_trend_data()
    df_trend.rename(columns={'penjualan': 'aktual'}, inplace=True)
    
    from utils.forecasting import generate_dummy_historical_forecast
    df_avf = generate_dummy_historical_forecast(df_trend)
    return df_avf



# ── Helper: format tanggal Indonesia ─────────────────────────────────────────
_HARI_ID = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
_BULAN_ID = [
    "", "Januari", "Februari", "Maret", "April", "Mei", "Juni",
    "Juli", "Agustus", "September", "Oktober", "November", "Desember",
]

def _format_tanggal_id(dt: datetime) -> str:
    hari  = _HARI_ID[dt.weekday()]
    bulan = _BULAN_ID[dt.month]
    return f"{hari}, {dt.day} {bulan} {dt.year}"


# ══════════════════════════════════════════════════════════════════════════════
# RENDER HALAMAN
# ══════════════════════════════════════════════════════════════════════════════

# ── Header halaman ────────────────────────────────────────────────────────────
today_str = _format_tanggal_id(datetime.now())
st.markdown(
    "<h2 style='margin-bottom:0.1rem;'>Dashboard</h2>"
    f"<p style='font-size:0.82rem; color:#64748B; margin-top:0;'>{today_str}</p>",
    unsafe_allow_html=True,
)
st.markdown("<div style='height:0.5rem;'></div>", unsafe_allow_html=True)


# ── A. Business Summary ───────────────────────────────────────────────────────
summary = get_summary_data()

risk_color_map = {
    "Aman":      {"text": "#047857", "bg": "#D1FAE5"},
    "Perhatian": {"text": "#92400E", "bg": "#FEF3C7"},
    "Kritis":    {"text": "#991B1B", "bg": "#FEE2E2"},
}
risk_colors = risk_color_map.get(summary["risk_status"], risk_color_map["Aman"])

# Kalimat penjelasan sederhana per status — untuk pemilik usaha yang tidak familiar istilah teknis
risk_desc_map = {
    "Aman":      "Stok Anda cukup untuk memenuhi permintaan dalam beberapa hari ke depan.",
    "Perhatian": "Beberapa produk mulai menipis. Sebaiknya segera siapkan bahan tambahan.",
    "Kritis":    "Stok hampir habis. Segera lakukan pengadaan bahan sebelum kehabisan.",
}
risk_desc = risk_desc_map.get(summary["risk_status"], "")

col1, col2, col3, col4 = st.columns(4, gap="small")

with col1:
    with st.container(border=True):
        st.markdown(
            "<div class='sb-card-label'>Total Produk</div>"
            f"<div class='sb-card-value'>{summary['total_produk']}</div>"
            "<div style='font-size:0.78rem; color:#64748B; margin-top:0.5rem; line-height:1.5;'>Jumlah menu atau produk yang terdaftar.</div>",
            unsafe_allow_html=True,
        )

with col2:
    with st.container(border=True):
        st.markdown(
            "<div class='sb-card-label'>Perkiraan Penjualan Hari Ini</div>"
            f"<div class='sb-card-value'>{summary['forecast_hari']} unit</div>"
            "<div style='font-size:0.78rem; color:#64748B; margin-top:0.5rem; line-height:1.5;'>Perkiraan total unit yang akan terjual hari ini.</div>",
            unsafe_allow_html=True,
        )

with col3:
    with st.container(border=True):
        st.markdown(
            "<div class='sb-card-label'>Rekomendasi</div>"
            f"<div class='sb-card-value'>{summary['restock_count']}</div>"
            "<div style='font-size:0.78rem; color:#64748B; margin-top:0.5rem; line-height:1.5;'>Produk yang stoknya perlu segera ditambah.</div>",
            unsafe_allow_html=True,
        )

with col4:
    with st.container(border=True):
        st.markdown(
            "<div class='sb-card-label'>Risk Status</div>"
            f"<div style='margin-top:0.4rem;'>"
            f"<span style='"
            f"display:inline-block; "
            f"font-size:0.92rem; font-weight:700; "
            f"color:{risk_colors['text']}; "
            f"background:{risk_colors['bg']}; "
            f"padding:0.2rem 0.75rem; border-radius:999px;'>"
            f"{summary['risk_status']}"
            f"</span></div>"
            f"<div style='font-size:0.78rem; color:#64748B; margin-top:0.5rem; line-height:1.5;'>{risk_desc}</div>",
            unsafe_allow_html=True,
        )

st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)


# ── B. Chart: Sales Trend ─────────────────────────────────────────────────────
st.markdown("<h3>Tren Penjualan (30 Hari Terakhir)</h3>", unsafe_allow_html=True)

df_sales = get_sales_trend_data()

fig_sales = go.Figure()
fig_sales.add_trace(go.Scatter(
    x=df_sales["tanggal"],
    y=df_sales["penjualan"],
    mode="lines+markers",
    name="Penjualan",
    line=dict(color="#1D4ED8", width=2.5),
    marker=dict(size=4, color="#1D4ED8"),
    hovertemplate="%{x|%d %b %Y}<br>%{y} unit<extra></extra>",
))

fig_sales.update_layout(
    plot_bgcolor="#FFFFFF",
    paper_bgcolor="#FFFFFF",
    margin=dict(l=0, r=0, t=8, b=0),
    height=300,
    xaxis=dict(
        showgrid=False,
        tickfont=dict(family="Inter", size=11, color="#64748B"),
        tickformat="%d %b",
    ),
    yaxis=dict(
        showgrid=True,
        gridcolor="#F1F5F9",
        tickfont=dict(family="Inter", size=11, color="#64748B"),
        title=None,
    ),
    legend=dict(
        font=dict(family="Inter", size=11),
        bgcolor="rgba(0,0,0,0)",
    ),
    hoverlabel=dict(font=dict(family="Inter", size=12)),
)

st.plotly_chart(fig_sales, use_container_width=True)

# TODO: BE - Ganti dengan insight otomatis berdasarkan kemiringan tren asli
def get_sales_insight(df_trend: pd.DataFrame) -> str:
    if df_trend.empty:
        return "Belum ada data yang cukup untuk memberikan insight penjualan."
    avg_sales = int(df_trend['penjualan'].mean())
    return f"Penjualan Anda berada di rata-rata {avg_sales} unit per hari selama periode ini."

st.markdown(
    f"<p style='font-size:0.82rem; color:#64748B; margin-top:-0.25rem;'>"
    f"{get_sales_insight(df_sales)}"
    f"</p>",
    unsafe_allow_html=True,
)

st.markdown("<div style='height:0.5rem;'></div>", unsafe_allow_html=True)


# ── C. Chart: Actual vs Forecast ──────────────────────────────────────────────
st.markdown("<h3>Penjualan Aktual vs Perkiraan (30 Hari Terakhir)</h3>", unsafe_allow_html=True)

df_avf = get_actual_vs_forecast_data()

fig_avf = go.Figure()
fig_avf.add_trace(go.Scatter(
    x=df_avf["tanggal"],
    y=df_avf["aktual"],
    mode="lines+markers",
    name="Aktual",
    line=dict(color="#1D4ED8", width=2.5),
    marker=dict(size=4, color="#1D4ED8"),
    hovertemplate="%{x|%d %b}<br>Aktual: %{y} unit<extra></extra>",
))
fig_avf.add_trace(go.Scatter(
    x=df_avf["tanggal"],
    y=df_avf["forecast"],
    mode="lines+markers",
    name="Perkiraan",
    line=dict(color="#94A3B8", width=2, dash="dot"),
    marker=dict(size=4, color="#94A3B8"),
    hovertemplate="%{x|%d %b}<br>Perkiraan: %{y} unit<extra></extra>",
))

fig_avf.update_layout(
    plot_bgcolor="#FFFFFF",
    paper_bgcolor="#FFFFFF",
    margin=dict(l=0, r=0, t=8, b=0),
    height=300,
    xaxis=dict(
        showgrid=False,
        tickfont=dict(family="Inter", size=11, color="#64748B"),
        tickformat="%d %b",
    ),
    yaxis=dict(
        showgrid=True,
        gridcolor="#F1F5F9",
        tickfont=dict(family="Inter", size=11, color="#64748B"),
        title=None,
    ),
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1,
        font=dict(family="Inter", size=11),
        bgcolor="rgba(0,0,0,0)",
    ),
    hoverlabel=dict(font=dict(family="Inter", size=12)),
)

st.plotly_chart(fig_avf, use_container_width=True)

# TODO: BE - Ganti dengan insight otomatis yang di-generate dari analisis data asli
def get_avf_insight(df_avf: pd.DataFrame) -> str:
    if df_avf.empty:
        return "Belum ada data aktual/forecast yang cukup untuk diperbandingkan."
    
    # Dummy logic: Hitung selisih absolut rata-rata
    diffs = abs(df_avf['aktual'] - df_avf['forecast'])
    avg_err = (diffs.mean() / df_avf['aktual'].mean() * 100) if df_avf['aktual'].mean() > 0 else 0
    
    return (
        f"Perkiraan kami cukup dekat dengan penjualan nyata (rata-rata deviasi ~{avg_err:.1f}%) "
        f"— artinya persiapan stok Anda sudah berada di jalur yang benar."
    )

st.markdown(
    f"<p style='font-size:0.82rem; color:#64748B; margin-top:-0.25rem;'>"
    f"{get_avf_insight(df_avf)}"
    f"</p>",
    unsafe_allow_html=True,
)
