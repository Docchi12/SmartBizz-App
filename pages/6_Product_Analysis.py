import streamlit as st
import pandas as pd
import plotly.express as px

try:
    df_sales_raw = st.session_state.get("uploaded_sales_data")
    if df_sales_raw is None or len(df_sales_raw) == 0:
        st.info("Anda belum mengupload data penjualan. Silakan upload data terlebih dahulu di halaman Data Management.")
        if st.button("Ke Halaman Data Management", type="primary", key="pa_to_dm"):
            st.switch_page(st.Page("pages/3_Data_Management.py", title="Data Management", icon=":material/upload_file:"))
        st.stop()
        
    prices_dict = st.session_state.get("product_prices", {})
    
    st.markdown("<h2 style='margin-bottom:0.1rem;'>Analisis Produk</h2>", unsafe_allow_html=True)
    st.markdown("<p style='font-size:0.85rem; color:#64748B;'>Rincian performa setiap produk berdasarkan volume penjualan, omset, dan keuntungan per porsi.</p>", unsafe_allow_html=True)
    st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)
    
    df = df_sales_raw.copy()
    
    # Hitung total volume per produk
    df_prod = df.groupby("nama_produk")["jumlah_terjual"].sum().reset_index()
    
    has_any_jual = False
    has_any_modal = False
    
    # Tambahkan kolom harga
    df_prod["harga_jual"] = df_prod["nama_produk"].apply(lambda x: prices_dict.get(x, {}).get("harga_jual") or 0)
    df_prod["harga_modal"] = df_prod["nama_produk"].apply(lambda x: prices_dict.get(x, {}).get("harga_modal") or 0)
    
    if (df_prod["harga_jual"] > 0).any():
        has_any_jual = True
    if (df_prod["harga_modal"] > 0).any():
        has_any_modal = True
        
    # Hitung metrik
    df_prod["omset"] = df_prod["jumlah_terjual"] * df_prod["harga_jual"]
    
    total_omset_all = df_prod.loc[df_prod["omset"] > 0, "omset"].sum()
    df_prod["omset_pct"] = df_prod.apply(lambda row: (row["omset"] / total_omset_all * 100) if (total_omset_all > 0 and row["omset"] > 0) else 0, axis=1)
    
    df_prod["untung_per_porsi"] = df_prod["harga_jual"] - df_prod["harga_modal"]
    # Hanya hitung kontribusi untung jika harga_modal > 0 (karena jika 0 berarti tidak tahu, bukan gratis/100% untung)
    df_prod["kontribusi_untung"] = df_prod.apply(lambda row: (row["harga_jual"] - row["harga_modal"]) * row["jumlah_terjual"] if row["harga_modal"] > 0 else 0, axis=1)
    
    total_untung_all = df_prod.loc[df_prod["kontribusi_untung"] > 0, "kontribusi_untung"].sum()
    df_prod["untung_pct"] = df_prod.apply(lambda row: (row["kontribusi_untung"] / total_untung_all * 100) if (total_untung_all > 0 and row["kontribusi_untung"] > 0) else 0, axis=1)

    # 1. HIGHLIGHT CARDS
    # TODO: BE - Teks kartu bisa disesuaikan dengan kebutuhan masa depan jika definisi "terlaris/terbesar" berubah (misalnya dibobot profit)
    c1, c2 = st.columns(2)
    
    with c1:
        if has_any_jual:
            # Penyumbang Omset Terbesar
            top_omset_row = df_prod.loc[df_prod['omset'].idxmax()]
            st.metric(
                label="Penyumbang Omset Terbesar", 
                value=top_omset_row['nama_produk'],
                delta=f"{top_omset_row['omset_pct']:.0f}% dari total omset",
                delta_color="off"
            )
        else:
            # Produk Terlaris (Volume)
            top_vol_row = df_prod.loc[df_prod['jumlah_terjual'].idxmax()]
            st.metric(
                label="Produk Terlaris", 
                value=top_vol_row['nama_produk'],
                delta=f"{top_vol_row['jumlah_terjual']:,} porsi terjual",
                delta_color="off"
            )
            
    if has_any_modal:
        with c2:
            # Untung per Porsi Tertinggi
            # Filter hanya yang punya harga modal
            df_modal = df_prod[df_prod['harga_modal'] > 0]
            if not df_modal.empty:
                top_margin_row = df_modal.loc[df_modal['untung_per_porsi'].idxmax()]
                st.metric(
                    label="Untung per Porsi Tertinggi",
                    value=top_margin_row['nama_produk'],
                    delta=f"Rp {top_margin_row['untung_per_porsi']:,}",
                    delta_color="off"
                )
    
    st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)
    
    # 2. TABEL RANKING PRODUK
    st.markdown("<h5>Ranking Produk</h5>", unsafe_allow_html=True)
    
    from utils.layout import render_table_interactive_tip
    render_table_interactive_tip()
    
    # Format untuk tampilan
    df_display = df_prod.copy()
    
    # Default sorting
    if has_any_jual:
        df_display = df_display.sort_values("omset", ascending=False)
    else:
        df_display = df_display.sort_values("jumlah_terjual", ascending=False)
        
    df_final = pd.DataFrame()
    df_final["Nama Produk"] = df_display["nama_produk"]
    df_final["Total Terjual"] = df_display["jumlah_terjual"]
    
    df_final["Kontribusi Omset (Rp)"] = df_display.apply(lambda r: r['omset'] if r['harga_jual'] > 0 else None, axis=1)
    df_final["Kontribusi Omset (%)"] = df_display.apply(lambda r: r['omset_pct'] if r['harga_jual'] > 0 else None, axis=1)
    
    df_final["Untung per Porsi (Rp)"] = df_display.apply(lambda r: r['untung_per_porsi'] if r['harga_modal'] > 0 else None, axis=1)
    df_final["Kontribusi Untung (Rp)"] = df_display.apply(lambda r: r['kontribusi_untung'] if r['harga_modal'] > 0 else None, axis=1)
    df_final["Kontribusi Untung (%)"] = df_display.apply(lambda r: r['untung_pct'] if r['harga_modal'] > 0 else None, axis=1)
    
    # Format menggunakan Pandas Styler agar tampilan string (dengan separator titik) namun sorting tetap numerik
    styled_df = df_final.style.format({
        "Total Terjual": lambda x: f"{int(x):,.0f}".replace(",", ".") if pd.notna(x) else "-",
        "Kontribusi Omset (Rp)": lambda x: f"Rp {int(x):,.0f}".replace(",", ".") if pd.notna(x) else "-",
        "Kontribusi Omset (%)": lambda x: f"{x:.1f}%" if pd.notna(x) else "-",
        "Untung per Porsi (Rp)": lambda x: f"Rp {int(x):,.0f}".replace(",", ".") if pd.notna(x) else "-",
        "Kontribusi Untung (Rp)": lambda x: f"Rp {int(x):,.0f}".replace(",", ".") if pd.notna(x) else "-",
        "Kontribusi Untung (%)": lambda x: f"{x:.1f}%" if pd.notna(x) else "-",
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
        st.markdown(f"<p style='font-size:0.8rem; color:#64748B; margin-top:0.5rem;'>*Catatan: {retur_str} (retur) tidak dihitung dalam persentase kontribusi produk lain, namun tetap mengurangi Total Terjual dan omset produk tersebut.</p>", unsafe_allow_html=True)
    
    st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)
    
    # 3. CHART PERBANDINGAN OMSET
    st.markdown("<h5>Perbandingan Kontribusi Omset</h5>", unsafe_allow_html=True)
    
    if has_any_jual:
        # TODO: BE - Gunakan template chart yang konsisten dengan halaman lain
        df_chart = df_prod[df_prod["omset"] > 0].sort_values("omset", ascending=True)
        if not df_chart.empty:
            fig = px.bar(
                df_chart, 
                x="omset", 
                y="nama_produk", 
                orientation='h',
                text_auto='.2s',
                title="",
                labels={"omset": "Omset (Rp)", "nama_produk": "Produk"}
            )
            fig.update_traces(marker_color='#3B82F6', textfont_size=12, textangle=0, textposition="outside", cliponaxis=False)
            fig.update_layout(
                margin=dict(l=0, r=0, t=10, b=0),
                height=max(300, len(df_chart) * 40),
                xaxis=dict(showgrid=True, gridcolor='#E2E8F0'),
                yaxis=dict(showgrid=False),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
            )
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        else:
            st.info("Seluruh produk saat ini memiliki harga jual 0 sehingga tidak ada omset yang bisa dibandingkan.")
    else:
        st.info("Isi harga jual produk di halaman Data Management untuk melihat perbandingan kontribusi omset di sini.")
        
except Exception as e:
    st.error("Terjadi masalah saat memproses data Anda. Silakan periksa kembali data di halaman Data Management, atau upload ulang jika perlu.")
    if st.button("Ke Halaman Data Management", type="primary", key="err_btn_product_analysis"):
        st.switch_page(st.Page("pages/3_Data_Management.py", title="Data Management", icon=":material/upload_file:"))
    st.stop()
