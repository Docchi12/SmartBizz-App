# utils/mock_data.py
# Semua sumber data dummy/mock untuk SmartBizz AI
# -------------------------------------------------------
# PENTING: File ini adalah satu-satunya tempat data dummy dibuat.
# Ketika backend siap, cukup ganti fungsi-fungsi di sini
# dengan implementasi asli tanpa harus mengubah UI.
#
# TODO: BACKEND - Setiap fungsi di file ini perlu diganti
#   dengan implementasi asli dari tim Software Engineer
#   (query database, panggil API, dsb.)
# -------------------------------------------------------

import numpy as np
import pandas as pd
from datetime import date, timedelta

# ── Seed agar data dummy konsisten ───────────────────────────────────────────
_RNG = np.random.default_rng(seed=42)

# ── Daftar produk dummy ───────────────────────────────────────────────────────
PRODUCT_LIST = [
    "Es Kopi Susu",
    "Nasi Goreng Spesial",
    "Ayam Geprek",
    "Mie Ayam Bakso",
    "Jus Alpukat",
    "Soto Betawi",
    "Gado-Gado",
    "Pisang Goreng",
]


# ── Fungsi helper internal ────────────────────────────────────────────────────

def _make_date_range(days_back: int = 30, from_today: bool = True) -> list[date]:
    """Buat list tanggal sejumlah `days_back` hari ke belakang dari hari ini."""
    today = date.today()
    return [today - timedelta(days=i) for i in range(days_back - 1, -1, -1)]


# ═══════════════════════════════════════════════════════════════════════════════
# DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════

def get_dashboard_summary() -> dict:
    """
    Kembalikan ringkasan bisnis untuk card di Dashboard.

    # TODO: BACKEND - ganti dengan query agregat dari database transaksi asli
    """
    return {
        "total_produk": len(PRODUCT_LIST),
        "forecast_hari_ini": int(_RNG.integers(150, 300)),
        "rekomendasi_aktif": int(_RNG.integers(3, 7)),
        "risk_status": _RNG.choice(["Rendah 🟢", "Sedang 🟡", "Tinggi 🔴"],
                                    p=[0.5, 0.35, 0.15]),
    }


def get_sales_trend(days: int = 30) -> pd.DataFrame:
    """
    Data trend penjualan harian (dummy) untuk line chart.

    # TODO: BACKEND - ganti dengan query tabel transaksi harian dari database
    """
    dates = _make_date_range(days)
    base = 200
    noise = _RNG.integers(-30, 50, size=days)
    trend = np.linspace(0, 40, days).astype(int)
    sales = base + trend + noise
    return pd.DataFrame({"Tanggal": dates, "Total Penjualan": sales.clip(0)})


def get_actual_vs_forecast(days: int = 14) -> pd.DataFrame:
    """
    Data Actual vs Forecast untuk line chart Dashboard.

    # TODO: BACKEND - ganti dengan data prediksi model ML asli vs aktual dari database
    """
    dates = _make_date_range(days)
    actual = 180 + _RNG.integers(-25, 40, size=days)
    forecast = actual + _RNG.integers(-15, 20, size=days)
    return pd.DataFrame({
        "Tanggal": dates,
        "Aktual": actual.clip(0),
        "Forecast": forecast.clip(0),
    })


# ═══════════════════════════════════════════════════════════════════════════════
# FORECAST
# ═══════════════════════════════════════════════════════════════════════════════

def get_forecast_7days(product: str) -> pd.DataFrame:
    """
    Forecast 7 hari ke depan untuk produk tertentu.

    # TODO: BACKEND - ganti dengan output model forecasting (ARIMA/Prophet/dsb.)
                     dari tim Software Engineer
    """
    today = date.today()
    dates = [today + timedelta(days=i) for i in range(1, 8)]
    base = _RNG.integers(80, 180)
    preds = base + _RNG.integers(-20, 30, size=7)
    lower = preds - _RNG.integers(5, 15, size=7)
    upper = preds + _RNG.integers(5, 20, size=7)
    return pd.DataFrame({
        "Tanggal": dates,
        "Prediksi Demand": preds.clip(0),
        "Batas Bawah (CI 80%)": lower.clip(0),
        "Batas Atas (CI 80%)": upper.clip(0),
    })


def get_historical_vs_prediction(product: str, days: int = 30) -> pd.DataFrame:
    """
    Data historis + prediksi untuk satu produk.

    # TODO: BACKEND - ganti dengan data historis dari database +
                     prediksi in-sample dari model ML
    """
    dates = _make_date_range(days)
    historical = 120 + _RNG.integers(-30, 50, size=days)
    prediction = historical + _RNG.integers(-18, 18, size=days)
    return pd.DataFrame({
        "Tanggal": dates,
        "Historis": historical.clip(0),
        "Prediksi": prediction.clip(0),
    })


# ═══════════════════════════════════════════════════════════════════════════════
# RECOMMENDATION
# ═══════════════════════════════════════════════════════════════════════════════

def get_recommendations() -> pd.DataFrame:
    """
    Tabel rekomendasi produksi per produk.

    # TODO: BACKEND - ganti dengan output recommendation engine asli
                     berdasarkan forecast + stok aktual dari database
    """
    alasan_pool = [
        "Permintaan diprediksi naik 15% minggu depan.",
        "Stok mendekati batas minimum, perlu penambahan segera.",
        "Tren musiman menunjukkan lonjakan demand.",
        "Permintaan stabil, produksi cukup dijaga di level saat ini.",
        "Demand diprediksi turun, kurangi produksi untuk efisiensi.",
    ]
    rng = _RNG
    demand = rng.integers(80, 200, size=len(PRODUCT_LIST))
    stok = rng.integers(30, 160, size=len(PRODUCT_LIST))
    produksi = np.where(
        stok < demand * 0.5,
        (demand - stok + rng.integers(10, 30, size=len(PRODUCT_LIST))).clip(0),
        rng.integers(5, 20, size=len(PRODUCT_LIST)),
    )
    alasan = rng.choice(alasan_pool, size=len(PRODUCT_LIST))
    return pd.DataFrame({
        "Produk": PRODUCT_LIST,
        "Prediksi Demand": demand,
        "Stok Saat Ini": stok,
        "Rekomendasi Produksi": produksi,
        "Alasan": alasan,
    })


# ═══════════════════════════════════════════════════════════════════════════════
# PRODUCT ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════════

def get_product_ranking() -> pd.DataFrame:
    """
    Ranking produk berdasarkan total penjualan.

    # TODO: BACKEND - ganti dengan query agregat penjualan dari database
    """
    total_sales = _RNG.integers(500, 3000, size=len(PRODUCT_LIST))
    df = pd.DataFrame({
        "Produk": PRODUCT_LIST,
        "Total Penjualan": total_sales,
    }).sort_values("Total Penjualan", ascending=False).reset_index(drop=True)
    df.index += 1
    df.index.name = "Rank"
    return df


def get_sales_distribution() -> pd.DataFrame:
    """
    Distribusi penjualan per produk (untuk pie/bar chart).

    # TODO: BACKEND - ganti dengan query proporsi penjualan dari database
    """
    sales = _RNG.integers(200, 2500, size=len(PRODUCT_LIST))
    return pd.DataFrame({
        "Produk": PRODUCT_LIST,
        "Penjualan": sales,
    })


def get_demand_trend_all(days: int = 30) -> pd.DataFrame:
    """
    Trend demand semua produk (long format) untuk multi-line chart.

    # TODO: BACKEND - ganti dengan query time series demand per produk dari database
    """
    dates = _make_date_range(days)
    rows = []
    for product in PRODUCT_LIST:
        base = int(_RNG.integers(50, 200))
        for i, d in enumerate(dates):
            val = max(0, base + int(_RNG.integers(-20, 30)) + i // 5)
            rows.append({"Tanggal": d, "Produk": product, "Demand": val})
    return pd.DataFrame(rows)


# ═══════════════════════════════════════════════════════════════════════════════
# AI ASSISTANT
# ═══════════════════════════════════════════════════════════════════════════════

# Template jawaban dummy AI Assistant
_AI_TEMPLATES = [
    (
        ["produksi", "tambah", "naik"],
        (
            "📈 Berdasarkan forecast terbaru, permintaan untuk produk ini diprediksi "
            "meningkat sekitar 15-20% dalam 7 hari ke depan. Stok saat ini berada di "
            "bawah ambang aman, sehingga rekomendasi sistem adalah menambah produksi "
            "sebesar {val} unit untuk menghindari kehabisan stok."
        ),
    ),
    (
        ["stok", "habis", "kurang"],
        (
            "⚠️ Sistem mendeteksi bahwa stok beberapa produk mendekati batas minimum. "
            "Rekomendasi: segera tambah produksi atau lakukan pemesanan bahan baku. "
            "Detail per produk dapat dilihat di halaman **Recommendation**."
        ),
    ),
    (
        ["tren", "trend", "penjualan"],
        (
            "📊 Berdasarkan analisis 30 hari terakhir, penjualan menunjukkan tren "
            "positif dengan rata-rata pertumbuhan ~5% per minggu. Produk dengan "
            "performa terbaik adalah **{top_product}** dengan kontribusi tertinggi "
            "terhadap total revenue."
        ),
    ),
    (
        ["forecast", "prediksi", "besok"],
        (
            "🔮 Forecast untuk 7 hari ke depan menunjukkan total demand sekitar "
            "{forecast_total} unit di seluruh produk. Hari dengan prediksi demand "
            "tertinggi adalah akhir pekan. Lihat detail di halaman **Forecast**."
        ),
    ),
]

_DEFAULT_AI_RESPONSE = (
    "🤖 Terima kasih atas pertanyaan Anda! Saat ini saya dapat membantu "
    "menganalisis data penjualan, forecast demand, dan rekomendasi produksi "
    "berdasarkan data bisnis Anda. Coba tanyakan tentang: \n"
    "- *Mengapa saya harus menambah produksi produk X?*\n"
    "- *Bagaimana tren penjualan saya?*\n"
    "- *Produk mana yang stoknya hampir habis?*"
)


def get_ai_response(user_message: str) -> str:
    """
    Hasilkan balasan dummy dari AI Assistant berdasarkan kata kunci pesan user.

    # TODO: BACKEND - ganti dengan pemanggilan LLM API asli (misal: Gemini, GPT)
                     dengan konteks data forecast + stok + rekomendasi dari database.
                     Contoh: response = llm_client.chat(prompt=user_message, context=data_context)

    Args:
        user_message: Pesan teks dari user.

    Returns:
        String balasan AI (saat ini: template dummy).
    """
    msg_lower = user_message.lower()
    top_product = PRODUCT_LIST[0]
    forecast_total = int(_RNG.integers(800, 1500))
    val = int(_RNG.integers(20, 80))

    for keywords, template in _AI_TEMPLATES:
        if any(kw in msg_lower for kw in keywords):
            return template.format(
                top_product=top_product,
                forecast_total=forecast_total,
                val=val,
            )

    return _DEFAULT_AI_RESPONSE
