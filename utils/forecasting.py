import pandas as pd
import random

def generate_dummy_forecast(df_prod: pd.DataFrame, horizon_days: int) -> pd.DataFrame:
    """
    TODO: BE - Ganti logic dummy di bawah ini dengan model forecasting asli (Prophet/ARIMA/dll)
    Logic Dummy Prediksi: Rata-rata bergerak dari 7 data terakhir + variasi acak
    """
    if df_prod.empty:
        return pd.DataFrame({'tanggal': [], 'prediksi': []})
        
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
    return df_pred

def generate_dummy_historical_forecast(df_actual: pd.DataFrame) -> pd.DataFrame:
    """
    TODO: BE - Ganti logic dummy di bawah ini dengan output model forecasting historis asli
    Logic Dummy: Prediksi historis = Aktual historis ± 5% variasi acak.
    """
    if df_actual.empty:
        return pd.DataFrame({'tanggal': [], 'forecast': []})
        
    df_hist = df_actual.copy()
    # Forecast historis dibuat agar sedikit berbeda dari aktual
    df_hist['forecast'] = df_hist['aktual'].apply(lambda x: int(max(0, x + (x * random.uniform(-0.05, 0.05)))))
    return df_hist
