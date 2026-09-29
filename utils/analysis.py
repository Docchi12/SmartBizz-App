import pandas as pd

def get_pricing_summary(df_raw: pd.DataFrame, prices_dict: dict, monthly_op_cost: int = 0) -> dict:
    # TODO: BE - Hitung omset dan profit dari database yang sudah tersimpan harga produknya.
    # Saat ini menggunakan aproksimasi karena data harian di-aggregate.
    
    # Jika harga kosong sama sekali, kembalikan state false
    if not prices_dict:
        return {"show_omset": False, "show_profit": False, "show_net_profit": False}
        
    total_omset = 0
    total_profit = 0
    
    has_any_modal = False
    unpriced_count = 0
    
    df = df_raw.copy()
    
    for prod in df['nama_produk'].unique():
        prod_data = prices_dict.get(prod, {})
        hj = prod_data.get('harga_jual') or 0
        hm = prod_data.get('harga_modal') or 0
        
        if hj == 0:
            unpriced_count += 1
            continue
            
        if hm > 0:
            has_any_modal = True
            
        qty = df[df['nama_produk'] == prod]['jumlah_terjual'].sum()
        total_omset += (qty * hj)
        
        if hm > 0:
            total_profit += (qty * (hj - hm))
            
    # TODO: BE - Proporsi 30 hari per bulan ini adalah pendekatan kasar, sebaiknya diganti perhitungan kalender yang lebih presisi (jumlah hari aktual di bulan tersebut) saat integrasi backend
    jumlah_hari = pd.to_datetime(df['tanggal']).dt.date.nunique()
    biaya_operasional_periode = (monthly_op_cost / 30) * jumlah_hari
    net_profit = total_profit - biaya_operasional_periode
            
    return {
        "show_omset": True,
        "show_profit": has_any_modal,
        "show_net_profit": (has_any_modal and monthly_op_cost > 0),
        "omset": total_omset,
        "profit": total_profit,
        "net_profit": net_profit,
        "unpriced_count": unpriced_count
    }
