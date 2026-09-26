# pages/4_Forecast.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import random

# ── Proteksi Halaman ──────────────────────────────────────────────────────────
# Jika belum login, render ulang. app.py akan otomatis navigasi ke Login.
if not st.session_state.get("logged_in", False):
    st.rerun()

# ── Header Halaman ────────────────────────────────────────────────────────────
st.markdown(
    "<h2 style='margin-bottom:0.5rem;'>Perkiraan Penjualan (Forecast)</h2>"
    "<p style='font-size:0.9rem; color:#64748B; margin-top:0;'>"
    "Lihat perkiraan tren penjualan di masa depan untuk merencanakan stok dengan lebih baik."
    "</p>",
    unsafe_allow_html=True,
)
st.markdown("<div style='height:0.5rem;'></div>", unsafe_allow_html=True)

# ── Pengecekan Data (Empty State) ─────────────────────────────────────────────
df_sales = st.session_state.get("uploaded_sales_data")
if df_sales is None or len(df_sales) == 0:
    st.info("Anda belum mengupload data penjualan. Silakan upload data terlebih dahulu di halaman Data Management.")
    if st.button("Ke Halaman Data Management", type="primary"):
        # Menggunakan st.Page object seperti konvensi migrasi
        page_dm = st.Page("pages/3_Data_Management.py", title="Data Management", icon=":material/upload_file:")
        st.switch_page(page_dm)
    st.stop()  # Hentikan eksekusi halaman di sini

# ── Data Processing ───────────────────────────────────────────────────────────
# Agregasi data per produk dan tanggal
# Normalisasi tipe data tanggal jika belum datetime
df = df_sales.copy()
df['tanggal'] = pd.to_datetime(df['tanggal'])
df_agg = df.groupby(['nama_produk', 'tanggal'])['jumlah_terjual'].sum().reset_index()

# ── 1. KONTROL PILIHAN ────────────────────────────────────────────────────────
with st.container(border=True):
    # Penentuan default: Produk dengan total penjualan terbanyak historis
    # Alasan: Produk terlaris (best seller) biasanya adalah prioritas utama 
    # UMKM untuk selalu dijaga stoknya karena paling menguntungkan.
    total_sales_per_product = df.groupby('nama_produk')['jumlah_terjual'].sum()
    default_product = total_sales_per_product.idxmax()
    
    unique_products = sorted(df['nama_produk'].unique())
    default_index = unique_products.index(default_product) if default_product in unique_products else 0
    
    col_p, col_h = st.columns([1, 1])
    with col_p:
        selected_product = st.selectbox(
            "Pilih Produk",
            options=unique_products,
            index=default_index,
        )
    with col_h:
        # Menggunakan st.radio horizontal karena st.segmented_control belum ada/tidak stabil di versi Streamlit lama
        horizon_label = st.radio(
            "Prediksi untuk berapa hari ke depan?",
            options=["7 Hari", "14 Hari", "30 Hari"],
            horizontal=True,
        )

horizon_days = int(horizon_label.split()[0])

# Filter data aktual untuk produk terpilih
df_prod = df_agg[df_agg['nama_produk'] == selected_product].sort_values('tanggal')

# TODO: BE - Ganti logic dummy di bawah ini dengan model forecasting asli (Prophet/ARIMA/dll)
# Mulai Logic Dummy Prediksi: Rata-rata bergerak dari 7 data terakhir + variasi acak
if not df_prod.empty:
    last_date = df_prod['tanggal'].max()
    recent_sales = df_prod['jumlah_terjual'].tail(7).mean()
    if pd.isna(recent_sales):
        recent_sales = 0
    
    dummy_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=horizon_days)
    dummy_values = []
    
    current_val = recent_sales
    for _ in range(horizon_days):
        # Variasi acak ±10% dari nilai sebelumnya untuk efek tren ringan
        variasi = current_val * random.uniform(-0.1, 0.1)
        current_val = max(0, current_val + variasi) # Tidak boleh negatif
        dummy_values.append(int(current_val))
    
    df_pred = pd.DataFrame({
        'tanggal': dummy_dates,
        'prediksi': dummy_values
    })
    
    # ── 2. GRAFIK AKTUAL VS PREDIKSI ──────────────────────────────────────────
    st.markdown(f"<h4>Perkiraan Penjualan: {selected_product}</h4>", unsafe_allow_html=True)
    
    fig = go.Figure()
    
    # Trace Aktual
    fig.add_trace(go.Scatter(
        x=df_prod['tanggal'],
        y=df_prod['jumlah_terjual'],
        mode='lines+markers',
        name='Aktual',
        line=dict(color="#1D4ED8", width=2.5),
        marker=dict(size=5, color="#1D4ED8"),
        hovertemplate="%{x|%d %b %Y}<br>Aktual: %{y} unit<extra></extra>",
    ))
    
    # Trace Prediksi (Dashed)
    # Sambung garis dari titik aktual terakhir ke titik prediksi pertama agar grafik menyambung
    concat_x = [last_date] + list(df_pred['tanggal'])
    concat_y = [df_prod.iloc[-1]['jumlah_terjual']] + list(df_pred['prediksi'])
    
    fig.add_trace(go.Scatter(
        x=concat_x,
        y=concat_y,
        mode='lines+markers',
        name='Prediksi (Estimasi AI)',
        line=dict(color="#94A3B8", width=2.5, dash='dash'),
        marker=dict(size=5, color="#94A3B8"),
        hovertemplate="%{x|%d %b %Y}<br>Prediksi: %{y} unit<extra></extra>",
    ))
    
    fig.update_layout(
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        margin=dict(l=0, r=0, t=10, b=0),
        height=350,
        xaxis=dict(
            showgrid=False,
            tickfont=dict(family="Inter", size=11, color="#64748B"),
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
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        hovermode="x unified"
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # ── 3. INSIGHT TEKS ───────────────────────────────────────────────────────
    # TODO: BE - Generate kalimat insight berdasarkan kemiringan tren (slope) atau selisih data
    trend_diff = dummy_values[-1] - recent_sales
    trend_pct = (abs(trend_diff) / recent_sales * 100) if recent_sales > 0 else 0
    
    if trend_diff > 0:
        kata_tren = "naik"
        saran = "Pastikan Anda menambah stok bahan baku agar tidak kehabisan saat permintaan sedang tinggi."
        warna = "#059669" # Green
        bg_warna = "#ECFDF5"
    elif trend_diff < 0:
        kata_tren = "turun"
        saran = "Pertimbangkan strategi promosi atau pantau kembali minat pelanggan pada produk ini."
        warna = "#DC2626" # Red
        bg_warna = "#FEF2F2"
    else:
        kata_tren = "stabil"
        saran = "Pertahankan kualitas dan jumlah stok untuk menjaga ketersediaan."
        warna = "#2563EB" # Blue
        bg_warna = "#EFF6FF"
        
    insight_text = (
        f"Penjualan <b>{selected_product}</b> diprediksi <b>{kata_tren} sekitar {trend_pct:.0f}%</b> "
        f"dalam {horizon_days} hari ke depan. {saran}"
    )
    
    # Menggunakan styling ala box di Dashboard
    st.markdown(
        f"<div style='background-color:{bg_warna}; color:{warna}; padding:1rem; border-radius:0.5rem; border: 1px solid {warna}40; margin-bottom:1.5rem; font-size:0.9rem; line-height:1.6;'>"
        f"💡 {insight_text}"
        f"</div>",
        unsafe_allow_html=True
    )
    
    # ── 4. TABEL DETAIL PREDIKSI ──────────────────────────────────────────────
    st.markdown("<h5>Detail Prediksi Harian</h5>", unsafe_allow_html=True)
    
    # Tip interaktif untuk user mobile (reuse komponen)
    from utils.layout import render_table_interactive_tip
    render_table_interactive_tip()
    
    # Formatting tabel agar terlihat lebih rapi
    df_pred_display = df_pred.copy()
    df_pred_display['tanggal'] = df_pred_display['tanggal'].dt.strftime('%d %b %Y')
    df_pred_display.rename(columns={
        'tanggal': 'Tanggal', 
        'prediksi': 'Prediksi Penjualan'
    }, inplace=True)
    
    st.dataframe(df_pred_display, hide_index=True, use_container_width=True)

else:
    st.warning("Tidak ada data aktual untuk produk yang dipilih.")
