import pandas as pd
from utils.forecasting import generate_dummy_forecast
from utils.recommendations import get_product_recommendations

def get_assistant_reply(question: str, df_sales: pd.DataFrame) -> str:
    """
    Menghasilkan jawaban AI asisten.
    
    Args:
        question: Pertanyaan pengguna.
        df_sales: DataFrame penjualan mentah.
        
    Returns:
        String teks jawaban asisten.
    """
    if df_sales is None or df_sales.empty:
        return "Maaf, saya belum melihat data penjualan Anda. Silakan unggah dulu di halaman Data Management ya."
        
    q = question.lower()
    
    # Siapkan data tanggal agar valid
    df = df_sales.copy()
    if not pd.api.types.is_datetime64_any_dtype(df['tanggal']):
        df['tanggal'] = pd.to_datetime(df['tanggal'], format='mixed', dayfirst=True, errors='coerce')
    df = df.dropna(subset=['tanggal'])
    
    # Cari penyebutan nama produk secara parsial dan penuh
    unique_products = df['nama_produk'].unique()
    matched_products = []
    
    q_clean = q.replace("?", "").replace(".", "").replace(",", "")
    stopwords = ["berapa", "bagaimana", "apa", "prediksi", "ramalan", "hari", "ini", "besok", "kemarin", "minggu", "depan", "stok", "restok", "terlaris", "laris", "sepi", "turun", "naik", "produk", "saya", "yang", "buat", "dari", "ke", "di", "itu"]
    q_words = [w for w in q_clean.split() if w not in stopwords]
    
    for p in unique_products:
        p_lower = str(p).lower()
        if p_lower in q_clean:
            matched_products.append(p)
            continue
            
        p_words = p_lower.split()
        if len(p_words) == 1:
            for w in q_words:
                if len(w) > 2 and w == p_lower:
                    matched_products.append(p)
                    break
        else:
            match_count = sum(1 for w in q_words if w in p_words)
            if match_count >= 2:
                matched_products.append(p)
                
    # Jika produk disebut
    if matched_products:
        if len(matched_products) > 1:
            names = ", ".join([f"**{m}**" for m in matched_products])
            return f"Maksud Anda {names}? Mohon sebutkan nama produk yang lebih spesifik ya."
            
        mentioned_product = matched_products[0]
        df_prod = df[df['nama_produk'] == mentioned_product].copy()
        
        qty = df_prod['jumlah_terjual'].sum()
        is_prediksi = any(k in q for k in ["prediksi", "perkiraan", "ramalan", "depan", "besok"])
        
        if is_prediksi:
            df_daily = df_prod.groupby('tanggal')['jumlah_terjual'].sum().reset_index()
            recent_actual = df_daily['jumlah_terjual'].tail(7).mean() if len(df_daily) > 0 else 0
            df_pred = generate_dummy_forecast(df_daily, horizon_days=7)
            total_pred = df_pred['prediksi'].sum() if not df_pred.empty else (recent_actual * 7)
            avg_pred = df_pred['prediksi'].mean() if not df_pred.empty else recent_actual
            
            if recent_actual > 0:
                trend_pct = ((avg_pred - recent_actual) / recent_actual) * 100
            else:
                trend_pct = 0 if avg_pred == 0 else 100
                
            arah = "stabil"
            if trend_pct > 5: arah = "naik"
            elif trend_pct < -5: arah = "turun"
            
            resp = f"Perkiraan permintaan **{mentioned_product}** untuk 7 hari ke depan adalah sekitar {int(total_pred):,} porsi. "
            if arah == "naik":
                resp += f"Trennya diprediksi naik sekitar {abs(trend_pct):.0f}%. "
            elif arah == "turun":
                resp += f"Trennya agak menurun sekitar {abs(trend_pct):.0f}%. "
            else:
                resp += "Permintaannya diprediksi stabil. "
            return resp.replace(",", ".")
            
        # Jika tidak ada metrik spesifik, berikan ringkasan umum volume
        total_jual_asli = df_prod[df_prod['jumlah_terjual'] > 0]['jumlah_terjual'].sum()
        
        df_daily = df_prod.groupby('tanggal')['jumlah_terjual'].sum().reset_index()
        recent_actual = df_daily['jumlah_terjual'].tail(7).mean() if len(df_daily) > 0 else 0
        df_pred = generate_dummy_forecast(df_daily, horizon_days=7)
        avg_pred = df_pred['prediksi'].mean() if not df_pred.empty else recent_actual
        
        if recent_actual > 0:
            trend_pct = ((avg_pred - recent_actual) / recent_actual) * 100
        else:
            trend_pct = 0 if avg_pred == 0 else 100
            
        arah = "stabil"
        if trend_pct > 5: arah = "naik"
        elif trend_pct < -5: arah = "turun"
        
        resp = f"Untuk **{mentioned_product}**, total volume terjual aslinya mencapai {int(total_jual_asli):,} porsi.\n\n"
        if (df_prod['jumlah_terjual'] < 0).any():
            retur = abs(df_prod[df_prod['jumlah_terjual'] < 0]['jumlah_terjual'].sum())
            resp += f"(Ada {int(retur)} porsi retur yang tidak dihitung sebagai penjualan positif).\n\n"
            
        if arah == "naik":
            resp += f"Tren permintaannya diperkirakan akan naik sekitar {abs(trend_pct):.0f}% minggu depan."
        elif arah == "turun":
            resp += f"Permintaannya agak menurun sekitar {abs(trend_pct):.0f}% untuk seminggu ke depan."
        else:
            resp += "Permintaannya diprediksi stabil."
            
        return resp.replace(",", ".")
        
    recs = get_product_recommendations(df_sales)
    
    is_turun_sepi = any(k in q for k in ["turun", "sepi", "kurang", "menurun", "tidak perlu"])
    is_stok_tambah = any(k in q for k in ["tambah", "restok", "siapkan"])
    is_stok_umum = any(k in q for k in ["stok", "bahan"])
    is_prediksi = any(k in q for k in ["prediksi", "perkiraan", "ramalan", "minggu", "besok"])
    is_laris = any(k in q for k in ["laris", "terlaris", "paling banyak", "paling laku"])

    if is_stok_tambah or (is_stok_umum and not is_turun_sepi):
        items = recs.get("kurang_stok", [])
        if not items:
            return "Kabar baik! Dari data yang ada, semua produk kelihatannya masih punya stok yang cukup aman untuk memenuhi perkiraan permintaan."
        resp = "Ini beberapa produk yang stoknya diperkirakan kurang dan perlu segera ditambah:\n"
        for i in items[:3]:
            resp += f"- **{i['nama']}**: {i['alasan']} (Butuh tambahan {i['prediksi_demand'] - i['stok_saat_ini']} porsi)\n"
        return resp
        
    elif is_turun_sepi:
        items = recs.get("stok_aman", [])
        if not items:
            return "Bagus! Saat ini tidak ada produk yang menunjukkan tanda-tanda sepi permintaan. Semuanya cukup stabil atau naik."
        resp = "Ada beberapa produk yang kelihatannya permintaannya lagi stabil atau sedikit turun, jadi stok saat ini masih sangat cukup:\n"
        for i in items[:3]:
            resp += f"- **{i['nama']}**: {i['alasan']}\n"
        return resp
        
    elif is_prediksi:
        df_jual = df[df['jumlah_terjual'] > 0]
        df_daily = df_jual.groupby('tanggal')['jumlah_terjual'].sum().reset_index()
        df_pred = generate_dummy_forecast(df_daily, horizon_days=7)
        if df_pred.empty:
            return "Data harian Anda belum cukup stabil untuk dibuatkan prediksinya."
        
        total_pred = df_pred['prediksi'].sum()
        recent_total = df_daily['jumlah_terjual'].tail(7).sum()
        trend_pct = ((total_pred - recent_total) / recent_total * 100) if recent_total > 0 else 0
        
        arah = "stabil"
        if trend_pct > 5: arah = "naik"
        elif trend_pct < -5: arah = "turun"
        
        resp = f"Secara keseluruhan, perkiraan permintaan untuk 7 hari ke depan adalah sekitar {int(total_pred):,} porsi. "
        if arah == "naik":
            resp += f"Ini artinya ada potensi kenaikan volume sekitar {abs(trend_pct):.0f}% dibanding minggu lalu. Pastikan stok bahan aman!"
        elif arah == "turun":
            resp += f"Sepertinya ada sedikit penurunan tren sekitar {abs(trend_pct):.0f}%. Mari pikirkan strategi promosi baru."
        else:
            resp += "Kelihatannya permintaan ke depan akan berjalan stabil seperti biasa."
        return resp.replace(",", ".")
        
    elif is_laris:
        df_jual = df[df['jumlah_terjual'] > 0]
        if df_jual.empty:
            return "Belum ada penjualan positif di data Anda."
        
        top_prod = df_jual.groupby("nama_produk")["jumlah_terjual"].sum().idxmax()
        top_qty = df_jual.groupby("nama_produk")["jumlah_terjual"].sum().max()
        return f"Produk yang paling laris manis adalah **{top_prod}**, dengan total terjual sebanyak {int(top_qty):,} porsi!".replace(",", ".")
        
    if any(k in q for k in ["halo", "hai", "bisa apa", "bantu apa", "tolong", "hei"]):
        return "Halo! Saya Asisten AI SmartBiz Anda. Saya bisa bantu cek tren produk, barang apa yang laris, stok mana yang perlu ditambah, sampai memperkirakan volume permintaan minggu depan. Ada yang ingin ditanyakan?"
        
    return ("Maaf, dari data yang saya punya saat ini, saya belum bisa menjawab pertanyaan itu. "
            "Namun, Anda bisa coba tanyakan hal-hal seperti:\n"
            "- 'Produk apa yang paling laris?'\n"
            "- 'Produk apa yang stoknya perlu segera ditambah?'\n"
            "- 'Apa prediksi permintaan minggu depan?'")
