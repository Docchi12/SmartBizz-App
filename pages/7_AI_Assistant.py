import streamlit as st
import time

try:
    df_sales_raw = st.session_state.get("uploaded_sales_data")
    if df_sales_raw is None or len(df_sales_raw) == 0:
        st.info("Anda belum mengupload data penjualan. Silakan upload data terlebih dahulu di halaman Data Management.")
        if st.button("Ke Halaman Data Management", type="primary", key="ai_to_dm"):
            st.switch_page(st.Page("pages/3_Data_Management.py", title="Data Management", icon=":material/upload_file:"))
        st.stop()
        
    from utils.assistant import get_assistant_reply
    prices_dict = st.session_state.get("product_prices", {})
    monthly_op_cost = st.session_state.get("monthly_operational_cost", 0)
    
    st.markdown("<h2 style='margin-bottom:0.1rem;'>Asisten AI</h2>", unsafe_allow_html=True)
    st.markdown("<p style='font-size:0.85rem; color:#64748B;'>Tanya apa saja soal penjualan, stok, dan untung usaha Anda.</p>", unsafe_allow_html=True)
    st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)
    
    # 8. DATA BERUBAH: Penanda unik data (jumlah baris + tanggal awal + tanggal akhir)
    df_jual = df_sales_raw.dropna(subset=['tanggal'])
    if len(df_jual) > 0:
        sig_data = f"{len(df_sales_raw)}_{df_jual['tanggal'].min()}_{df_jual['tanggal'].max()}"
    else:
        sig_data = "nodata"
        
    # Inisialisasi riwayat
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
        st.session_state.chat_sig = sig_data
        
    # Peringatan jika data berubah sejak chat terakhir (hanya jika ada riwayat)
    data_changed = (st.session_state.get("chat_sig") != sig_data)
    if data_changed and len(st.session_state.chat_history) > 0:
        st.info("Data Anda berubah sejak percakapan terakhir, jawaban sebelumnya mungkin sudah tidak berlaku.")
        
    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("Mulai Percakapan Baru", key="new_chat_btn"):
            st.session_state.chat_history = []
            st.session_state.chat_sig = sig_data
            st.rerun()
            
    st.divider()
    
    # TODO: BE - Riwayat percakapan saat ini hanya di session_state dan hilang saat sesi berakhir; pindahkan ke penyimpanan permanen.
    
    # Tampilkan riwayat chat dengan format native Streamlit
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.write(message["content"])
            
    # Generator untuk stream kata per kata (efek mengetik)
    def stream_data(text):
        # TODO: BE - Ganti generator simulasi ini dengan streaming asli dari LLM API.
        words = text.split(" ")
        # Jeda disesuaikan agar total waktu ~1.5 detik (max 0.1 detik per kata)
        sleep_time = min(1.5 / max(len(words), 1), 0.1)
        for word in words:
            yield word + " "
            time.sleep(sleep_time)

    # 4. CHIP PERTANYAAN AWAL (Hanya muncul jika riwayat kosong)
    user_q = None
    if len(st.session_state.chat_history) == 0:
        st.markdown("<p style='font-size:0.85rem; font-weight:600;'>💡 Coba tanyakan ini:</p>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Apa produk saya yang terlaris?", use_container_width=True): user_q = "Apa produk saya yang terlaris?"
            if st.button("Produk apa yang perlu ditambah stoknya?", use_container_width=True): user_q = "Produk apa yang perlu ditambah stoknya?"
            if st.button("Berapa omset saya?", use_container_width=True): user_q = "Berapa omset saya?"
        with c2:
            if st.button("Perkiraan penjualan minggu depan?", use_container_width=True): user_q = "Perkiraan penjualan minggu depan?"
            if st.button("Produk apa yang untungnya tipis?", use_container_width=True): user_q = "Produk apa yang untungnya tipis?"
    
    # Input utama (selalu di bawah)
    typed_q = st.chat_input("Tanya soal penjualan Anda...")
    if typed_q:
        user_q = typed_q
        
    # Proses pertanyaan (dari input maupun klik chip)
    if user_q:
        # Jika data berubah, update signature agar tidak terus-terusan muncul notifikasi data berubah
        if data_changed:
            st.session_state.chat_sig = sig_data
            
        st.session_state.chat_history.append({"role": "user", "content": user_q})
        with st.chat_message("user"):
            st.write(user_q)
            
        with st.chat_message("assistant"):
            try:
                # Titik sambung ke logika jawaban (nantinya ke BE/LLM)
                raw_reply = get_assistant_reply(user_q, df_sales_raw, prices_dict, monthly_op_cost)
                
                # Render jawaban dengan efek mengetik
                st.write_stream(stream_data(raw_reply))
                st.session_state.chat_history.append({"role": "assistant", "content": raw_reply})
            except Exception as e:
                # 10. ERROR: Tangkap error agar tidak merusak halaman atau riwayat
                err_msg = "Maaf, saya sedang kesulitan menjawab. Coba pertanyaan lain atau periksa data Anda di Data Management."
                st.write(err_msg)
                st.session_state.chat_history.append({"role": "assistant", "content": err_msg})
                
        st.rerun()

    st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)
    st.caption("Jawaban dibuat otomatis dari data yang Anda unggah. Angka perkiraan bukan jaminan.")
        
except Exception as e:
    # Fail-safe terluar untuk halaman
    st.error("Terjadi masalah saat memuat Asisten AI. Silakan periksa kembali data di Data Management.")
