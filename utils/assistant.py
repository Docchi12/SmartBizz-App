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
        for w in q_words:
            if len(w) > 2 and w in p_lower:
                matched_products.append(p)
                break
                
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
        
    # Aturan 1: Laris
    if any(k in q for k in ["laris", "terlaris", "paling banyak"]):
        df_jual = df[df['jumlah_terjual'] > 0]
        if df_jual.empty:
            return "Belum ada penjualan positif di data Anda."
        top_prod = df_jual.groupby("nama_produk")["jumlah_terjual"].sum().idxmax()
        top_qty = df_jual.groupby("nama_produk")["jumlah_terjual"].sum().max()
        return f"Produk yang paling laris manis adalah **{top_prod}**, dengan total penjualan sebanyak {int(top_qty):,} porsi!".replace(",", ".")
        
    # Aturan 2: Omset
    if any(k in q for k in ["omset", "pendapatan", "penjualan total"]):
        df_jual = df[df['jumlah_terjual'] > 0]
        total_omset = 0
        unpriced = []
        for p in df_jual['nama_produk'].unique():
            hj = prices.get(p, {}).get("harga_jual", 0)
            if hj > 0:
                qty = df_jual[df_jual['nama_produk'] == p]['jumlah_terjual'].sum()
                total_omset += (qty * hj)
            else:
                unpriced.append(p)
                
        if total_omset == 0 and len(unpriced) > 0:
            return "Saya belum bisa menghitung omset Anda karena harga jual belum diisi sama sekali. Yuk isi dulu harganya di halaman Data Management!"
            
        resp = f"Total omset Anda yang berhasil saya hitung adalah Rp {int(total_omset):,.0f}.\n\n".replace(",", ".")
        if unpriced:
            resp += "Tapi ingat, angka ini belum termasuk penjualan beberapa produk yang belum diatur harga jualnya (seperti " + ", ".join([f"**{x}**" for x in unpriced[:3]]) + (", dll" if len(unpriced)>3 else "") + ")."
        return resp
        
    # Aturan 3: Untung
    if any(k in q for k in ["untung", "keuntungan", "laba", "profit"]):
        df_jual = df[df['jumlah_terjual'] > 0]
        total_untung_kotor = 0
        has_modal = False
        for p in df_jual['nama_produk'].unique():
            hj = prices.get(p, {}).get("harga_jual", 0)
            hm = prices.get(p, {}).get("harga_modal", 0)
            if hj > 0 and hm > 0:
                has_modal = True
                qty = df_jual[df_jual['nama_produk'] == p]['jumlah_terjual'].sum()
                total_untung_kotor += (qty * (hj - hm))
                
        if not has_modal:
            return "Saya tidak bisa menghitung keuntungan karena kolom 'Harga Modal' belum diisi. Silakan mampir ke Data Management untuk mengisinya ya."
            
        resp = f"Keuntungan kotor Anda (omset dikurangi biaya bahan) adalah sekitar Rp {int(total_untung_kotor):,.0f}.\n\n".replace(",", ".")
        if monthly_operational_cost > 0:
            jml_hari = df_jual['tanggal'].nunique()
            biaya_ops = (monthly_operational_cost / 30) * jml_hari
            bersih = total_untung_kotor - biaya_ops
            resp += f"Nah, kalau dipotong biaya operasional harian, keuntungan bersih Anda di periode ini diperkirakan menjadi Rp {int(bersih):,.0f}.".replace(",", ".")
        return resp
        
    # Aturan 4, 5, 6 reuse rekomendasi
    recs = get_product_recommendations(df_sales, prices)
    
    # Aturan 4: Stok
    if any(k in q for k in ["stok", "restok", "tambah", "siapkan"]):
        items = recs.get("perlu_tambah_stok", [])
        if not items:
            return "Dari data yang ada, sepertinya belum ada produk yang trennya naik tajam sampai perlu segera ditambah stoknya."
        resp = "Ini produk yang sedang naik daun dan mungkin stok bahannya perlu Anda perbanyak:\n"
        for i in items:
            resp += f"- **{i['nama']}**: {i['alasan']}\n"
        return resp
        
    # Aturan 5: Turun
    if any(k in q for k in ["turun", "sepi", "kurangi", "menurun"]):
        items = recs.get("pantau_kurangi", [])
        if not items:
            return "Bagus! Saat ini tidak ada produk yang menunjukkan tanda-tanda sepi. Semuanya cukup stabil atau naik."
        resp = "Ada beberapa produk yang kelihatannya mulai sepi dan porsinya mungkin perlu dikurangi agar bahan tidak mubazir:\n"
        for i in items:
            resp += f"- **{i['nama']}**: {i['alasan']}\n"
        return resp
        
    # Aturan 6: Harga/Tipis
    if any(k in q for k in ["harga", "tipis", "rugi", "kecil"]):
        items = recs.get("tinjau_harga", [])
        if not items:
            return "Semua produk yang sudah ada harga jual & modalnya punya untung per porsi yang lumayan sehat. Tidak ada yang terdeteksi rugi."
        resp = "Perhatian! Produk-produk ini terdeteksi punya untung per porsi yang tipis atau malah bikin tekor:\n"
        for i in items:
            resp += f"- **{i['nama']}**: {i['alasan']}\n"
        return resp
        
    # Aturan 7: Prediksi global
    if any(k in q for k in ["prediksi", "perkiraan", "ramalan", "minggu", "besok"]):
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
        
        resp = f"Secara keseluruhan, perkiraan penjualan untuk 7 hari ke depan adalah sekitar {int(total_pred):,} porsi. "
        if arah == "naik":
            resp += f"Ini artinya ada potensi kenaikan sekitar {abs(trend_pct):.0f}% dibanding minggu lalu. Usaha Anda lagi bagus!"
        elif arah == "turun":
            resp += f"Sepertinya ada sedikit penurunan tren sekitar {abs(trend_pct):.0f}%. Mari pikirkan strategi promosi baru."
        else:
            resp += "Kelihatannya penjualan ke depan akan berjalan stabil seperti biasa."
        return resp.replace(",", ".")
        
    # Aturan 9: Sapaan
    if any(k in q for k in ["halo", "hai", "bisa apa", "bantu apa", "tolong", "hei"]):
        return "Halo! Saya Asisten AI SmartBiz Anda. Saya bisa bantu cek omset, produk terlaris, barang apa yang perlu direstok, sampai memperkirakan penjualan minggu depan. Ada yang ingin ditanyakan?"
        
    # Aturan 10: Fallback
    return ("Maaf, dari data yang saya punya saat ini, saya belum bisa menjawab pertanyaan itu. "
            "Namun, Anda bisa coba tanyakan hal-hal seperti:\n"
            "- 'Produk apa yang paling laris?'\n"
            "- 'Berapa total omset saya?'\n"
            "- 'Apa yang harus saya siapkan untuk minggu depan?'")
