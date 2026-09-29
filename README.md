# SmartBizz AI

Demand Forecasting & Business Assistant untuk UMKM Kuliner. Dibangun untuk kebutuhan Lomba USB 2026.

SmartBizz AI membantu pemilik usaha kuliner skala kecil menengah membaca data penjualan mereka sendiri — mengunggah data, melihat tren, memperkirakan permintaan ke depan, dan mendapat rekomendasi aksi — tanpa perlu memahami istilah statistik atau akuntansi.

## Fitur

Aplikasi terdiri dari 8 halaman:

| Halaman | Fungsi |
|---|---|
| **Login / Register** | Autentikasi pengguna, satu file dengan toggle antara masuk dan daftar |
| **Dashboard** | Ringkasan bisnis: total produk, perkiraan penjualan hari ini, status risiko stok, estimasi omset & keuntungan, tren penjualan, grafik aktual vs perkiraan |
| **Data Management** | Unggah data penjualan (CSV), validasi otomatis dengan pesan error ramah pengguna, isi harga jual & modal per produk, isi biaya operasional bulanan |
| **Forecast** | Perkiraan penjualan 7/14/30 hari ke depan per produk, grafik aktual vs prediksi, insight otomatis dalam Bahasa Indonesia |
| **Rekomendasi** | Saran aksi otomatis per produk: Perlu Tambah Stok, Pantau/Kurangi Produksi, Tinjau Harga/Margin, Produk Andalan |
| **Analisis Produk** | Ranking produk berdasarkan kontribusi omset & keuntungan, produk penyumbang terbesar, grafik perbandingan |
| **Asisten AI** | Chat tanya-jawab seputar data penjualan, stok, dan keuntungan usaha (lihat catatan di bagian Status & Keterbatasan) |
| **Settings** | Pengaturan akun dan preferensi aplikasi |

## Cara Menjalankan

### Prasyarat
- Python 3.11 atau lebih baru
- pip

### Instalasi

```bash
# clone repository
git clone <url-repo-ini>
cd SmartBizz-app

# buat virtual environment
python -m venv .venv

# aktifkan virtual environment
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# install dependency
pip install -r requirements.txt
```

### Menjalankan aplikasi

```bash
streamlit run app.py
```

Aplikasi akan terbuka otomatis di browser, biasanya di `http://localhost:8501`.

### Akun demo

```
Email    : demo@smartbizz.ai
Password : demo123
```

### Mencoba dengan data sendiri

1. Login, lalu buka halaman **Data Management**
2. Unggah file CSV dengan 3 kolom: `Tanggal`, `Nama Produk`, `Jumlah Terjual` (nama kolom tidak harus persis sama, kapitalisasi dan spasi akan dinormalisasi otomatis)
3. Isi harga jual (dan harga modal jika ingin melihat estimasi keuntungan) untuk tiap produk yang terdeteksi
4. Opsional: isi biaya operasional bulanan untuk melihat estimasi keuntungan bersih
5. Jelajahi halaman Dashboard, Forecast, Rekomendasi, Analisis Produk, dan Asisten AI — semuanya otomatis mengikuti data yang diunggah

## Struktur Proyek

```
SmartBizz-app/
├── app.py                      # Entry point, mendaftarkan semua halaman ke st.navigation()
├── auth.py                     # Logic autentikasi
├── layout.py                   # Sidebar & CSS global (apply_global_css, render_sidebar)
├── styles.py                   # Definisi style/CSS
├── pages/
│   ├── 2_Dashboard.py
│   ├── 3_Data_Management.py
│   ├── 4_Forecast.py
│   ├── 5_Recommendation.py
│   ├── 6_Product_Analysis.py
│   ├── 7_AI_Assistant.py
│   └── 8_Settings.py
├── utils/
│   ├── forecasting.py          # Logic dummy forecast (generate_dummy_forecast, generate_dummy_historical_forecast)
│   ├── recommendations.py      # Logic kategori rekomendasi (get_product_recommendations)
│   ├── analysis.py             # Logic ringkasan omset/keuntungan (get_pricing_summary) — dipakai Dashboard & Asisten AI
│   └── assistant.py            # Logic jawaban chat (get_assistant_reply)
└── requirements.txt
```

## Konvensi Kode

Dua aturan yang dipegang konsisten di seluruh proyek ini:

1. **Penanda kode sementara.** Setiap bagian yang masih memakai data atau logika dummy (bukan hasil model/backend sungguhan) ditandai komentar `# TODO: BE - <penjelasan>`, supaya mudah ditemukan saat integrasi backend.
2. **Pesan error ramah pengguna.** Karena pengguna aplikasi ini mengelola data lewat Excel (yang sering menghasilkan format tidak konsisten secara wajar, bukan kesalahan pengguna), setiap error yang berpotensi terlihat pengguna ditampilkan dalam bahasa manusia yang jelas — bukan traceback Python atau istilah teknis.

## Status & Keterbatasan (Catatan untuk Tim Backend)

Seluruh data prediksi, rekomendasi, dan jawaban chat pada versi ini adalah **dummy**, dibangun untuk menunjukkan alur dan tampilan produk sebelum model/backend sesungguhnya terpasang. Titik-titik yang perlu diganti:

- **`utils/forecasting.py`** — prediksi saat ini berbasis rolling average + variasi acak. Ganti dengan model sesungguhnya (moving average/regresi/Prophet sesuai rencana tim).
- **`utils/assistant.py`** — jawaban saat ini berbasis pencocokan kata kunci sederhana, bukan LLM. Fungsi `get_assistant_reply()` adalah satu-satunya titik yang perlu diganti dengan pemanggilan LLM API; docstring di dalamnya menjelaskan kontrak input/output yang diharapkan.
  - Keterbatasan yang sudah diketahui: pencocokan kata kunci bisa salah arah untuk kalimat yang mengandung kata dari beberapa kategori sekaligus (misalnya "stok yang perlu dikurangi" pernah salah tertangkap sebagai "perlu tambah stok"), dan pencocokan nama produk parsial bisa salah kena ungkapan sehari-hari (misalnya kata "manis" dalam "laris manis" pernah tertangkap sebagai nama produk "Es Teh Manis"). Ini adalah batas wajar dari pendekatan kata kunci, dan akan hilang dengan sendirinya begitu diganti LLM sungguhan.
- **Penyimpanan data** — seluruh data (penjualan, harga produk, biaya operasional, riwayat chat) saat ini hanya berada di `st.session_state`, hilang saat sesi berakhir atau browser di-refresh. Perlu dipindahkan ke database (SQLite sesuai rencana tim).
- Titik lain yang lebih spesifik ditandai langsung di kode dengan komentar `# TODO: BE`.

## Tim

Dikerjakan untuk Lomba USB 2026. Pembagian kerja: UI/UX & frontend (Streamlit) terpisah dari data/model AI & backend.
