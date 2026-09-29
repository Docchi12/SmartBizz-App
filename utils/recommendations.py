import pandas as pd
import random
from utils.forecasting import generate_dummy_forecast

def get_product_recommendations(df_sales: pd.DataFrame) -> dict:
    """
    Menghasilkan rekomendasi per produk berdasarkan gap stok dan prediksi demand.
    Returns:
    {
        "kurang_stok": [ {"nama": "...", "prediksi_demand": 100, "stok_saat_ini": 50, "rekomendasi_produksi": "Tambah 50", "alasan": "..."} ],
        "stok_aman": [ {"nama": "...", "prediksi_demand": 20, "stok_saat_ini": 50, "rekomendasi_produksi": "Cukup", "alasan": "..."} ]
    }
    """
    rekomendasi = {
        "kurang_stok": [],
        "stok_aman": []
    }
    
    if df_sales is None or df_sales.empty:
        return rekomendasi
        
    df = df_sales.copy()
    if not pd.api.types.is_datetime64_any_dtype(df['tanggal']):
        df['tanggal'] = pd.to_datetime(df['tanggal'], format='mixed', dayfirst=True, errors='coerce')
        
    df = df.dropna(subset=['tanggal'])
    df_daily = df.groupby(['tanggal', 'nama_produk'])['jumlah_terjual'].sum().reset_index()
    unique_products = df_daily['nama_produk'].unique()
    
    for prod in unique_products:
        df_prod = df_daily[df_daily['nama_produk'] == prod].sort_values('tanggal')
        if len(df_prod) == 0: continue
            
        recent_actual = df_prod['jumlah_terjual'].tail(7).mean()
        df_pred = generate_dummy_forecast(df_prod, horizon_days=7)
        
        # Prediksi demand 7 hari ke depan
        if not df_pred.empty:
            total_prediksi = int(df_pred['prediksi'].sum())
            avg_pred = df_pred['prediksi'].mean()
        else:
            total_prediksi = int(recent_actual * 7)
            avg_pred = recent_actual
            
        if recent_actual > 0:
            trend_pct = ((avg_pred - recent_actual) / recent_actual) * 100
        else:
            trend_pct = 0
            
        # Generate stok saat ini secara dummy statis per nama produk
        random.seed(hash(prod))
        stok_saat_ini = random.randint(0, int(total_prediksi * 1.5) if total_prediksi > 0 else 50)
        
        selisih = total_prediksi - stok_saat_ini
        
        if selisih > 0:
            rekomendasi_produksi = f"Tambah {selisih} unit"
            if trend_pct > 5:
                alasan = f"Permintaan {prod} diperkirakan naik sekitar {trend_pct:.0f}% dalam seminggu ke depan. Stok Anda ({stok_saat_ini} unit) tidak akan cukup untuk memenuhi prediksi sebanyak {total_prediksi} unit."
            elif trend_pct < -5:
                alasan = f"Walaupun penjualannya agak turun {abs(trend_pct):.0f}%, tapi diprediksi Anda masih butuh {total_prediksi} unit minggu ini. Stok saat ini kurang {selisih} unit."
            else:
                alasan = f"Penjualannya cukup stabil. Untuk seminggu ke depan butuh sekitar {total_prediksi} unit, jadi stok Anda saat ini ({stok_saat_ini} unit) masih kurang."
            
            rekomendasi["kurang_stok"].append({
                "nama": prod,
                "prediksi_demand": total_prediksi,
                "stok_saat_ini": stok_saat_ini,
                "rekomendasi_produksi": rekomendasi_produksi,
                "alasan": alasan
            })
        else:
            rekomendasi_produksi = "Cukup, tidak perlu tambah"
            if trend_pct < -5:
                alasan = f"Penjualannya agak turun sekitar {abs(trend_pct):.0f}%. Stok saat ini ({stok_saat_ini} unit) sudah lebih dari cukup untuk memenuhi prediksi permintaan ({total_prediksi} unit)."
            else:
                alasan = f"Stok Anda saat ini ({stok_saat_ini} unit) sangat aman dan berlebih dari perkiraan permintaan ({total_prediksi} unit) untuk 7 hari ke depan."
                
            rekomendasi["stok_aman"].append({
                "nama": prod,
                "prediksi_demand": total_prediksi,
                "stok_saat_ini": stok_saat_ini,
                "rekomendasi_produksi": rekomendasi_produksi,
                "alasan": alasan
            })
            
    # Sort descending berdasarkan demand tertinggi
    rekomendasi["kurang_stok"].sort(key=lambda x: x["prediksi_demand"], reverse=True)
    rekomendasi["stok_aman"].sort(key=lambda x: x["prediksi_demand"], reverse=True)
    
    return rekomendasi
