import streamlit as st
import pandas as pd
import plotly.express as px
from utils.forecasting import generate_dummy_forecast

try:
    df_sales_raw = st.session_state.get("uploaded_sales_data")
    if df_sales_raw is None or len(df_sales_raw) == 0:
        st.markdown(
            "<div style='background-color:#E6F4EA; border:1px solid #A1FCAB; border-radius:8px; padding:1rem; margin-bottom:1rem; color:#123316; font-size:0.9rem;'>"
            "&#9432; Anda belum mengupload data penjualan. Silakan upload data terlebih dahulu di halaman Data Management."
            "</div>", unsafe_allow_html=True
        )
        if st.button("Ke Halaman Data Management", type="primary", key="pa_to_dm"):
            st.switch_page(st.Page("pages/3_Data_Management.py", title="Data Management", icon=":material/upload_file:"))
        st.stop()
        
    st.markdown("<h2 style='margin-bottom:0.1rem;'>Analisis Produk</h2>", unsafe_allow_html=True)
    st.markdown("<p style='font-size:0.85rem; color:#729677;'>Rincian performa setiap produk berdasarkan volume penjualan dan tren permintaan.</p>", unsafe_allow_html=True)
    st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)
    
    df = df_sales_raw.copy()
    if not pd.api.types.is_datetime64_any_dtype(df['tanggal']):
        df['tanggal'] = pd.to_datetime(df['tanggal'], format='mixed', dayfirst=True, errors='coerce')
    df = df.dropna(subset=['tanggal'])
    
    # Hitung total volume per produk
    df_prod = df.groupby("nama_produk")["jumlah_terjual"].sum().reset_index()
    
    total_jual_all = df_prod.loc[df_prod["jumlah_terjual"] > 0, "jumlah_terjual"].sum()
    df_prod["kontribusi_pct"] = df_prod.apply(lambda row: (row["jumlah_terjual"] / total_jual_all * 100) if (total_jual_all > 0 and row["jumlah_terjual"] > 0) else 0, axis=1)
    
    # Hitung tren demand per produk
    df_daily = df.groupby(['tanggal', 'nama_produk'])['jumlah_terjual'].sum().reset_index()
    
    tren_list = []
    for prod in df_prod['nama_produk']:
        df_p = df_daily[df_daily['nama_produk'] == prod].sort_values('tanggal')
        if len(df_p) > 0:
            recent_actual = df_p['jumlah_terjual'].tail(7).mean()
            df_pred = generate_dummy_forecast(df_p, horizon_days=7)
            avg_pred = df_pred['prediksi'].mean() if not df_pred.empty else recent_actual
            if recent_actual > 0:
                trend_pct = ((avg_pred - recent_actual) / recent_actual) * 100
            else:
                trend_pct = 0
            tren_list.append(trend_pct)
        else:
            tren_list.append(0)
            
    df_prod["tren_pct"] = tren_list
    
    # 1. HIGHLIGHT CARDS
    c1, c2 = st.columns(2)
    
    with c1:
        # Produk Terlaris (Volume)
        top_vol_row = df_prod.loc[df_prod['jumlah_terjual'].idxmax()]
        st.metric(
            label="Produk Terlaris", 
            value=top_vol_row['nama_produk'],
            delta=f"{top_vol_row['jumlah_terjual']:,} porsi terjual",
            delta_color="off"
        )
            
    with c2:
        # Tren Kenaikan Tertinggi
        top_trend_row = df_prod.loc[df_prod['tren_pct'].idxmax()]
        trend_val = top_trend_row['tren_pct']
        if trend_val > 0:
            delta_str = f"Naik {trend_val:.1f}%"
        elif trend_val < 0:
            delta_str = f"Turun {abs(trend_val):.1f}%"
        else:
            delta_str = "Stabil"
            
        st.metric(
            label="Tren Kenaikan Tertinggi",
            value=top_trend_row['nama_produk'],
            delta=delta_str,
            delta_color="normal"
        )
    
    st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)
    
    # 2. TABEL RANKING PRODUK
    st.markdown("<h5>Ranking Produk</h5>", unsafe_allow_html=True)
    
    from utils.layout import render_table_interactive_tip
    render_table_interactive_tip()
    
    # Format untuk tampilan
    df_display = df_prod.sort_values("jumlah_terjual", ascending=False)
        
    df_final = pd.DataFrame()
    df_final["Nama Produk"] = df_display["nama_produk"]
    df_final["Total Terjual"] = df_display["jumlah_terjual"]
    df_final["Kontribusi Penjualan (%)"] = df_display["kontribusi_pct"]
    df_final["Tren (naik/turun %)"] = df_display["tren_pct"]
    
    def format_tren(x):
        if x > 0:
            return f"📈 Naik {x:.1f}%"
        elif x < 0:
            return f"📉 Turun {abs(x):.1f}%"
        else:
            return "➖ Stabil"

    styled_df = df_final.style.format({
        "Total Terjual": lambda x: f"{int(x):,.0f}".replace(",", ".") if pd.notna(x) else "-",
        "Kontribusi Penjualan (%)": lambda x: f"{x:.1f}%" if pd.notna(x) else "-",
        "Tren (naik/turun %)": format_tren
    })
    
    st.dataframe(
        styled_df, 
        use_container_width=True, 
        hide_index=True
    )
    
    retur_rows = df[df["jumlah_terjual"] < 0]
    if not retur_rows.empty:
        retur_summary = retur_rows.groupby("nama_produk")["jumlah_terjual"].sum().reset_index()
        retur_texts = [f"{abs(r['jumlah_terjual'])} unit pada {r['nama_produk']}" for _, r in retur_summary.iterrows()]
        retur_str = ", ".join(retur_texts)
        st.markdown(f"<p style='font-size:0.8rem; color:#729677; margin-top:0.5rem;'>*Catatan: {retur_str} (retur) tidak dihitung dalam persentase kontribusi produk lain, namun tetap mengurangi Total Terjual produk tersebut.</p>", unsafe_allow_html=True)
    
    st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)
    
    # 3. CHART PERBANDINGAN VOLUME PENJUALAN
    st.markdown("<h5>Distribusi Penjualan Produk</h5>", unsafe_allow_html=True)
    
    df_chart = df_prod[df_prod["jumlah_terjual"] > 0].sort_values("jumlah_terjual", ascending=True)
    if not df_chart.empty:
        fig = px.bar(
            df_chart, 
            x="jumlah_terjual", 
            y="nama_produk", 
            orientation='h',
            text_auto='.2s',
            title="",
            labels={"jumlah_terjual": "Total Terjual (Unit)", "nama_produk": "Produk"}
        )
        fig.update_traces(marker_color='#37633D', textfont_size=12, textangle=0, textposition="outside", cliponaxis=False)
        fig.update_layout(
            margin=dict(l=0, r=0, t=10, b=0),
            height=max(300, len(df_chart) * 40),
            xaxis=dict(showgrid=True, gridcolor='#A9C9AD'),
            yaxis=dict(showgrid=False),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
        )
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    else:
        st.info("Belum ada data penjualan positif untuk ditampilkan.")
        
except Exception as e:
    st.error(f"Terjadi masalah saat memproses data Anda. Silakan periksa kembali data di halaman Data Management. Pesan error: {e}")
    if st.button("Ke Halaman Data Management", type="primary", key="err_btn_product_analysis"):
        st.switch_page(st.Page("pages/3_Data_Management.py", title="Data Management", icon=":material/upload_file:"))
    st.stop()
