import pandas as pd
from utils.forecasting import generate_dummy_forecast
from utils.recommendations import get_product_recommendations

def get_assistant_reply(question: str, df_sales: pd.DataFrame, prices: dict, monthly_operational_cost: int) -> str:
    """
    Menghasilkan jawaban AI asisten.
    
    Args:
        question: Pertanyaan pengguna.
        df_sales: DataFrame penjualan mentah.
        prices: Dictionary harga jual dan harga modal per produk.
        monthly_operational_cost: Biaya operasional bulanan (0 jika tidak ada).
        
    Returns:
        String teks jawaban asisten.
    """
    # TODO: BE - Ganti isi fungsi ini dengan panggilan LLM API. Kirim ringkasan data (bukan seluruh dataframe) sebagai konteks, dan kembalikan teks jawaban (atau generator untuk streaming).
    
    if df_sales is None or df_sales.empty:
        return "Maaf, saya belum melihat data penjualan Anda. Silakan unggah dulu di halaman Data Management ya."
        
    q = question.lower()
    
    # Siapkan data tanggal agar valid
    df = df_sales.copy()
    if not pd.api.types.is_datetime64_any_dtype(df['tanggal']):
        df['tanggal'] = pd.to_datetime(df['tanggal'], format='mixed', dayfirst=True, errors='coerce')
    df = df.dropna(subset=['tanggal'])
    
    # 1. Cari penyebutan nama produk secara parsial dan penuh (Poin 2)
    unique_products = df['nama_produk'].unique()
    matched_products = []
    
    q_clean = q.replace("?", "").replace(".", "").replace(",", "")
    stopwords = ["berapa", "bagaimana", "apa", "omset", "penjualan", "untung", "laba", "margin", "prediksi", "ramalan", "hari", "ini", "besok", "kemarin", "minggu", "depan", "stok", "restok", "terlaris", "laris", "sepi", "turun", "naik", "produk", "saya", "yang", "buat", "dari", "ke", "di", "itu"]
    q_words = [w for w in q_clean.split() if w not in stopwords]
    
    for p in unique_products:
        p_lower = str(p).lower()
        if p_lower in q_clean:
            matched_products.append(p)
            continue
            
        # Pencocokan parsial berdasarkan kata signifikan
        p_words = p_lower.split()
        if len(p_words) == 1:
            for w in q_words:
                if len(w) > 2 and w == p_lower:
                    matched_products.append(p)
                    break
        else:
            # Jika nama produk > 1 kata (misal "Es Teh Manis"), butuh minimal 2 kata yang cocok
            # agar kata umum seperti "manis" di "laris manis" tidak membajak keseluruhan.
            match_count = sum(1 for w in q_words if w in p_words)
            if match_count >= 2:
                matched_products.append(p)
                
    # Aturan 8: Jika produk disebut (Poin 1)
    if matched_products:
        if len(matched_products) > 1:
            names = ", ".join([f"**{m}**" for m in matched_products])
            return f"Maksud Anda {names}? Mohon sebutkan nama produk yang lebih spesifik ya."
            
        mentioned_product = matched_products[0]
        df_prod = df[df['nama_produk'] == mentioned_product].copy()
        
        # Total keseluruhan termasuk retur (untuk omset/untung/metrik absolut)
        qty = df_prod['jumlah_terjual'].sum()
        
        is_omset = any(k in q for k in ["omset", "pendapatan"])
        is_untung = any(k in q for k in ["untung", "laba", "profit"])
        is_prediksi = any(k in q for k in ["prediksi", "perkiraan", "ramalan", "depan", "besok"])
        
        if is_omset:
            hj = prices.get(mentioned_product, {}).get("harga_jual", 0)
            if hj > 0:
                omset = qty * hj
                resp = f"Total omset untuk **{mentioned_product}** adalah Rp {int(omset):,.0f} (dari total net {int(qty):,} porsi terjual).".replace(",", ".")
                # Catatan jika ada retur
                if (df_prod['jumlah_terjual'] < 0).any():
                    retur = abs(df_prod[df_prod['jumlah_terjual'] < 0]['jumlah_terjual'].sum())
                    resp += f" Angka ini sudah dipotong {int(retur)} unit retur."
                return resp
            else:
                return f"Saya belum bisa menghitung omset **{mentioned_product}** karena harga jualnya belum diatur. Silakan isi dulu di Data Management."
                
        if is_untung:
            hj = prices.get(mentioned_product, {}).get("harga_jual", 0)
            hm = prices.get(mentioned_product, {}).get("harga_modal", 0)
            if hj > 0 and hm > 0:
                untung = qty * (hj - hm)
                resp = f"Total keuntungan kotor untuk **{mentioned_product}** adalah Rp {int(untung):,.0f}.".replace(",", ".")
                if (df_prod['jumlah_terjual'] < 0).any():
                    retur = abs(df_prod[df_prod['jumlah_terjual'] < 0]['jumlah_terjual'].sum())
                    resp += f" (Sudah dikurangi kerugian dari {int(retur)} unit retur)."
                return resp
            else:
                return f"Saya belum bisa menghitung keuntungan **{mentioned_product}** karena harga modal/jualnya belum lengkap. Silakan isi dulu di Data Management."
                
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
            
            resp = f"Perkiraan penjualan **{mentioned_product}** untuk 7 hari ke depan adalah sekitar {int(total_pred):,} porsi. "
            if arah == "naik":
                resp += f"Trennya diprediksi naik sekitar {abs(trend_pct):.0f}%. "
            elif arah == "turun":
                resp += f"Trennya agak menurun sekitar {abs(trend_pct):.0f}%. "
            else:
                resp += "Penjualannya diprediksi stabil. "
            return resp.replace(",", ".")
            
        # Jika tidak ada metrik spesifik, berikan ringkasan umum
        total_jual_asli = df_prod[df_prod['jumlah_terjual'] > 0]['jumlah_terjual'].sum()
        
        # Arah tren
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
        
        p_data = prices.get(mentioned_product, {})
        hj = p_data.get("harga_jual", 0)
        hm = p_data.get("harga_modal", 0)
        
        resp = f"Untuk **{mentioned_product}**, total penjualan aslinya mencapai {int(total_jual_asli):,} porsi.\n\n"
        if (df_prod['jumlah_terjual'] < 0).any():
            retur = abs(df_prod[df_prod['jumlah_terjual'] < 0]['jumlah_terjual'].sum())
            resp += f"(Ada {int(retur)} porsi retur yang tidak dihitung sebagai penjualan positif).\n\n"
            
        if arah == "naik":
            resp += f"Trennya diperkirakan akan naik sekitar {abs(trend_pct):.0f}% minggu depan. "
        elif arah == "turun":
            resp += f"Penjualannya agak menurun sekitar {abs(trend_pct):.0f}% untuk seminggu ke depan. "
        else:
            resp += "Penjualannya diprediksi stabil. "
            
        if hj > 0 and hm > 0:
            untung = hj - hm
            resp += f"Untung per porsinya lumayan, yaitu Rp {untung:,.0f}."
        elif hj > 0:
            resp += "Harganya sudah ada, tapi belum ada harga modal jadi saya tidak bisa hitung untungnya."
        else:
            resp += "Oh ya, Anda belum mengisi harga jual dan modal untuk produk ini di Data Management."
            
        return resp.replace(",", ".")
        
    from utils.analysis import get_pricing_summary
    recs = get_product_recommendations(df_sales, prices)
    
    # === DETEKSI INTENSI & KOMBINASI KATA ===
    # Kita menggunakan flag untuk mendeteksi kombinasi kata yang berpotensi tumpang tindih
    is_turun_sepi = any(k in q for k in ["turun", "sepi", "kurang", "menurun", "tidak perlu"])
    is_margin_buruk = any(k in q for k in ["tipis", "rugi", "kecil", "sedikit", "tekor", "harga"])
    is_stok_tambah = any(k in q for k in ["tambah", "restok", "siapkan"])
    is_stok_umum = any(k in q for k in ["stok", "bahan"])
    is_prediksi = any(k in q for k in ["prediksi", "perkiraan", "ramalan", "minggu", "besok"])
    is_laris = any(k in q for k in ["laris", "terlaris", "paling banyak", "paling laku"])
    is_omset = any(k in q for k in ["omset", "pendapatan", "penjualan total"])
    is_untung = any(k in q for k in ["untung", "keuntungan", "laba", "profit"])

    # Evaluasi aturan secara berurutan, dari yang paling spesifik ke metrik umum (hanya 1 jawaban)
    
    # Aturan 5: Turun (Pantau/Kurangi Produksi)
    if is_turun_sepi:
        items = recs.get("pantau_kurangi", [])
        if not items:
            return "Bagus! Saat ini tidak ada produk yang menunjukkan tanda-tanda sepi. Semuanya cukup stabil atau naik."
        resp = "Ada beberapa produk yang kelihatannya mulai sepi dan porsinya mungkin perlu dikurangi agar bahan tidak mubazir:\n"
        for i in items:
            resp += f"- **{i['nama']}**: {i['alasan']}\n"
        return resp
        
    # Aturan 6: Harga/Tipis (Tinjau Harga/Margin)
    elif is_margin_buruk:
        items = recs.get("tinjau_harga", [])
        if not items:
            return "Semua produk yang sudah ada harga jual & modalnya punya untung per porsi yang lumayan sehat. Tidak ada yang terdeteksi rugi."
        resp = "Perhatian! Produk-produk ini terdeteksi punya untung per porsi yang tipis atau malah bikin tekor:\n"
        for i in items:
            resp += f"- **{i['nama']}**: {i['alasan']}\n"
        return resp
        
    # Aturan 4: Stok (Perlu Tambah)
    elif is_stok_tambah or (is_stok_umum and not is_turun_sepi and not is_margin_buruk):
        items = recs.get("perlu_tambah_stok", [])
        if not items:
            return "Dari data yang ada, sepertinya belum ada produk yang trennya naik tajam sampai perlu segera ditambah stoknya."
        resp = "Ini produk yang sedang naik daun dan mungkin stok bahannya perlu Anda perbanyak:\n"
        for i in items:
            resp += f"- **{i['nama']}**: {i['alasan']}\n"
        return resp
        
    # Aturan 7: Prediksi global
    elif is_prediksi:
        is_uang = is_omset or is_untung or any(k in q for k in ["rupiah", "uang", "duit", "rp"])
        df_jual = df[df['jumlah_terjual'] > 0]
        
        if not is_uang:
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
            
            resp = f"Secara keseluruhan, perkiraan penjualan untuk 7 hari ke depan adalah sekitar {int(total_pred):,} porsi. "
            if arah == "naik":
                resp += f"Ini artinya ada potensi kenaikan sekitar {abs(trend_pct):.0f}% dibanding minggu lalu. Usaha Anda lagi bagus!"
            elif arah == "turun":
                resp += f"Sepertinya ada sedikit penurunan tren sekitar {abs(trend_pct):.0f}%. Mari pikirkan strategi promosi baru."
            else:
                resp += "Kelihatannya penjualan ke depan akan berjalan stabil seperti biasa."
            return resp.replace(",", ".")
        else:
            total_pred_rp = 0
            recent_total_rp = 0
            unpriced = []
            
            for p in df_jual['nama_produk'].unique():
                hj = prices.get(p, {}).get("harga_jual", 0)
                if hj == 0:
                    unpriced.append(p)
                    continue
                    
                df_p = df_jual[df_jual['nama_produk'] == p]
                df_daily_p = df_p.groupby('tanggal')['jumlah_terjual'].sum().reset_index()
                if df_daily_p.empty: continue
                
                df_pred_p = generate_dummy_forecast(df_daily_p, horizon_days=7)
                if not df_pred_p.empty:
                    total_pred_rp += (df_pred_p['prediksi'].sum() * hj)
                    
                recent_total_rp += (df_daily_p['jumlah_terjual'].tail(7).sum() * hj)
                
            if total_pred_rp == 0 and len(unpriced) > 0:
                return "Saya belum bisa memprediksi nilai omset ke depan karena harga jual produk belum diisi. Silakan isi dulu di Data Management ya."
            
            trend_pct = ((total_pred_rp - recent_total_rp) / recent_total_rp * 100) if recent_total_rp > 0 else 0
            arah = "stabil"
            if trend_pct > 5: arah = "naik"
            elif trend_pct < -5: arah = "turun"
            
            resp_pred = f"Secara keseluruhan, perkiraan pendapatan untuk 7 hari ke depan adalah sekitar Rp {int(total_pred_rp):,.0f}. ".replace(",", ".")
            if arah == "naik":
                resp_pred += f"Ini artinya ada potensi kenaikan sekitar {abs(trend_pct):.0f}% dibanding minggu lalu. Usaha Anda lagi bagus!"
            elif arah == "turun":
                resp_pred += f"Sepertinya ada sedikit penurunan tren sekitar {abs(trend_pct):.0f}%. Mari pikirkan strategi promosi baru."
            else:
                resp_pred += "Kelihatannya pendapatan ke depan akan berjalan stabil seperti biasa."
                
            if unpriced:
                unpriced_list = ", ".join([f"**{x}**" for x in unpriced[:3]])
                if len(unpriced) > 3: unpriced_list += ", dll"
                resp_pred += f" Oh ya, prediksi ini belum memasukkan produk yang harganya kosong (seperti {unpriced_list})."
                
            return resp_pred
        
    # Aturan 1: Laris
    elif is_laris:
        df_jual = df[df['jumlah_terjual'] > 0]
        if df_jual.empty:
            return "Belum ada penjualan positif di data Anda."
        
        top_prod = df_jual.groupby("nama_produk")["jumlah_terjual"].sum().idxmax()
        top_qty = df_jual.groupby("nama_produk")["jumlah_terjual"].sum().max()
        return f"Produk yang paling laris manis adalah **{top_prod}**, dengan total penjualan sebanyak {int(top_qty):,} porsi!".replace(",", ".")
        
    # Aturan 2: Omset (Global)
    elif is_omset:
        summary = get_pricing_summary(df, prices, monthly_operational_cost)
        
        tgl_min = df['tanggal'].min().strftime('%d %b %Y')
        tgl_max = df['tanggal'].max().strftime('%d %b %Y')
        periode = f"selama {tgl_min} hingga {tgl_max}" if tgl_min != tgl_max else f"pada {tgl_min}"
        
        unpriced = [p for p in df['nama_produk'].unique() if prices.get(p, {}).get("harga_jual", 0) == 0]
        priced_count = len(df['nama_produk'].unique()) - len(unpriced)
        
        if priced_count == 0:
            return "Saya belum bisa menghitung omset Anda karena tidak ada satu pun produk yang harga jualnya sudah diisi. Yuk isi dulu harganya di halaman Data Management!"
            
        omset = summary.get("omset", 0)
        resp = f"Total omset Anda {periode} adalah Rp {int(omset):,.0f}.\n\n".replace(",", ".")
        resp += f"Angka ini dihitung dari penjualan {priced_count} produk yang sudah memiliki harga jual."
        
        if unpriced:
            unpriced_list = ", ".join([f"**{x}**" for x in unpriced[:3]])
            if len(unpriced) > 3:
                unpriced_list += ", dll"
            resp += f" Ada beberapa produk yang belum ikut terhitung karena harganya belum diisi (seperti {unpriced_list}). Silakan lengkapi di Data Management ya."
            
        return resp
        
    # Aturan 3: Untung (Global)
    elif is_untung:
        summary = get_pricing_summary(df, prices, monthly_operational_cost)
        
        if not summary.get("show_profit"):
            return "Saya tidak bisa menghitung keuntungan karena kolom 'Harga Modal' belum diisi untuk produk mana pun. Silakan mampir ke Data Management untuk mengisinya ya."
            
        tgl_min = df['tanggal'].min().strftime('%d %b %Y')
        tgl_max = df['tanggal'].max().strftime('%d %b %Y')
        periode = f"selama {tgl_min} hingga {tgl_max}" if tgl_min != tgl_max else f"pada {tgl_min}"
        
        has_modal_count = sum(1 for p in df['nama_produk'].unique() if prices.get(p, {}).get("harga_modal", 0) > 0)
        unpriced = [p for p in df['nama_produk'].unique() if prices.get(p, {}).get("harga_modal", 0) == 0]
        
        profit = summary.get("profit", 0)
        net_profit = summary.get("net_profit", 0)
        
        resp = f"Keuntungan kotor Anda (omset dikurangi biaya bahan) {periode} adalah Rp {int(profit):,.0f}.\n\n".replace(",", ".")
        
        if summary.get("show_net_profit"):
            resp += f"Nah, setelah dipotong biaya operasional, keuntungan bersih Anda diperkirakan menjadi Rp {int(net_profit):,.0f}.\n\n".replace(",", ".")
            
        resp += f"Perhitungan ini mencakup {has_modal_count} produk."
        if unpriced:
            unpriced_list = ", ".join([f"**{x}**" for x in unpriced[:3]])
            if len(unpriced) > 3:
                unpriced_list += ", dll"
            resp += f" Produk yang harga modalnya masih kosong (seperti {unpriced_list}) belum dihitung keuntungannya."
            
        return resp
        
    # Aturan 9: Sapaan
    if any(k in q for k in ["halo", "hai", "bisa apa", "bantu apa", "tolong", "hei"]):
        return "Halo! Saya Asisten AI SmartBiz Anda. Saya bisa bantu cek omset, produk terlaris, barang apa yang perlu direstok, sampai memperkirakan penjualan minggu depan. Ada yang ingin ditanyakan?"
        
    # Aturan 10: Fallback
    return ("Maaf, dari data yang saya punya saat ini, saya belum bisa menjawab pertanyaan itu. "
            "Namun, Anda bisa coba tanyakan hal-hal seperti:\n"
            "- 'Produk apa yang paling laris?'\n"
            "- 'Berapa total omset saya?'\n"
            "- 'Apa yang harus saya siapkan untuk minggu depan?'")
