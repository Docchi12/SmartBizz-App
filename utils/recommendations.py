import pandas as pd
from utils.forecasting import generate_dummy_forecast

def get_product_recommendations(df_sales: pd.DataFrame, prices_dict: dict) -> dict:
    """
    Menghasilkan kategori rekomendasi per produk.
    Returns:
    {
        "perlu_tambah_stok": [ {"nama": "A", "alasan": "...", "aksi": "..."} ],
        "pantau_kurangi": [...],
        "tinjau_harga": [...],
        "produk_andalan": [...]
    }
    """
    rekomendasi = {
        "perlu_tambah_stok": [],
        "pantau_kurangi": [],
        "tinjau_harga": [],
        "produk_andalan": []
    }
    
    if df_sales is None or df_sales.empty:
        return rekomendasi
        
    # Pastikan tipe data tanggal benar untuk fungsi forecast
    df = df_sales.copy()
    if not pd.api.types.is_datetime64_any_dtype(df['tanggal']):
        df['tanggal'] = pd.to_datetime(df['tanggal'], format='mixed', dayfirst=True, errors='coerce')
        
    # Buang data dengan tanggal tidak valid
    df = df.dropna(subset=['tanggal'])
        
    df_daily = df.groupby(['tanggal', 'nama_produk'])['jumlah_terjual'].sum().reset_index()
    unique_products = df_daily['nama_produk'].unique()
    
    for prod in unique_products:
        df_prod = df_daily[df_daily['nama_produk'] == prod].sort_values('tanggal')
        
        if len(df_prod) == 0:
            continue
            
        # 1. Hitung Tren Penjualan
        recent_actual = df_prod['jumlah_terjual'].tail(7).mean()
        
        # Prediksi = rata-rata dari forecast 7 hari ke depan
        df_pred = generate_dummy_forecast(df_prod, horizon_days=7)
        if not df_pred.empty:
            avg_pred = df_pred['prediksi'].mean()
        else:
            avg_pred = recent_actual
            
        # TODO: BE - ambang batas 5% ini adalah asumsi sementara, sebaiknya disesuaikan berdasarkan data riil/masukan bisnis saat integrasi backend
        if recent_actual > 0:
            trend_pct = ((avg_pred - recent_actual) / recent_actual) * 100
        else:
            trend_pct = 0 if avg_pred == 0 else 100
            
        trend_arah = "stabil"
        if trend_pct > 5:
            trend_arah = "naik"
        elif trend_pct < -5:
            trend_arah = "turun"
            
        # 2. Kesehatan Margin
        prod_data = prices_dict.get(prod, {}) if prices_dict else {}
        hj = prod_data.get("harga_jual") or 0
        hm = prod_data.get("harga_modal") or 0
        
        margin_status = "tidak diketahui"
        margin_pct = 0
        has_modal = (hm > 0)
        
        if hj > 0 and hm > 0:
            margin = hj - hm
            margin_pct = (margin / hj) * 100
            if margin_pct > 20:
                margin_status = "sehat"
            elif margin_pct >= 0:
                margin_status = "tipis"
            else:
                margin_status = "negatif"
        elif hj > 0 and hm == 0:
             margin_status = "tidak diketahui"
                
        # 3. Klasifikasi Kategori
        
        # Kategori: Perlu Tambah Stok (tren naik)
        if trend_arah == "naik":
            rekomendasi["perlu_tambah_stok"].append({
                "nama": prod,
                "alasan": f"{prod} diperkirakan makin laris (naik sekitar {trend_pct:.0f}% dalam 7 hari ke depan).",
                "aksi": "Siapkan stok bahan lebih banyak supaya tidak kehabisan."
            })
            
        # Kategori: Pantau atau Kurangi Produksi (tren turun)
        if trend_arah == "turun":
            rekomendasi["pantau_kurangi"].append({
                "nama": prod,
                "alasan": f"{prod} kelihatannya mulai sepi (turun sekitar {abs(trend_pct):.0f}% dalam 7 hari ke depan).",
                "aksi": "Coba kurangi jumlah yang dibuat dulu sementara, biar bahan tidak terbuang."
            })
            
        # Kategori: Tinjau Harga/Margin (margin tipis/negatif) - HANYA jika ada harga modal dihitung
        if margin_status in ["tipis", "negatif"] and has_modal:
            if margin_status == "negatif":
                alasan = f"Lagi rugi nih (minus sekitar {abs(margin_pct):.0f}% dari harga jual)."
                aksi = "Segera cek harga bahan baku atau naikkan harga jual biar tidak tekor."
            else:
                alasan = f"Untung per porsi {prod} terbilang tipis (cuma sekitar {margin_pct:.0f}% dari harga jual)."
                aksi = "Coba cek lagi biaya bahan atau pertimbangkan naikkan harga sedikit."
                
            rekomendasi["tinjau_harga"].append({
                "nama": prod,
                "alasan": alasan,
                "aksi": aksi
            })
            
        # Kategori: Produk Andalan (tren naik & margin sehat)
        if trend_arah == "naik" and margin_status == "sehat":
            rekomendasi["produk_andalan"].append({
                "nama": prod,
                "alasan": f"{prod} lagi laris (naik sekitar {trend_pct:.0f}%) dan untung per porsinya juga lumayan bagus (sekitar {margin_pct:.0f}% dari harga jual).",
                "aksi": "Produk ini juaranya — coba promosikan lebih sering!"
            })
            
    return rekomendasi
