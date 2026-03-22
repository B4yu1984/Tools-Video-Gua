import streamlit as st
import google.generativeai as genai
import requests
import time

# --- KONFIGURASI API ---
try:
    GEMINI_KEY = st.secrets["GEMINI_KEY"]
    HF_TOKEN = st.secrets["HF_TOKEN"]
except Exception:
    st.error("Waduh, Kunci API belum lu pasang di Secrets, Bro!")
    st.stop()

# --- SETUP GOOGLE AI ---
genai.configure(api_key=GEMINI_KEY)
try:
    models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    target_model = next((m for m in models if 'flash' in m), next((m for m in models if 'pro' in m), models[0]))
    gemini = genai.GenerativeModel(target_model)
except Exception as e:
    st.error(f"Gemini mogok: {e}")
    st.stop()

# --- UI APLIKASI ---
st.set_page_config(page_title="Affiliate Video Pro", page_icon="🎥")
st.title("🎥 Affiliate Video Pro")
st.write(f"✅ Sistem Naskah Aktif: `{target_model}`")
st.write("---")

prod_name = st.text_input("Nama Produk", placeholder="Contoh: Piring Keramik Gold")

# FITUR MULTIPLE UPLOAD BALIK LAGI!
uploaded_files = st.file_uploader("Upload Foto Produk (Bisa banyak)", type=['jpg', 'png', 'jpeg'], accept_multiple_files=True)

# --- EKSEKUSI ---
if st.button("🚀 MULAI BUAT KONTEN"):
    if not prod_name or not uploaded_files:
        st.error("Isi nama produk & upload foto dulu, Bro!")
    else:
        try:
            # 1. GENERATE NASKAH (PROSES GEMINI)
            with st.spinner("Gemini lagi ngeracik naskah..."):
                prompt = f"Buat naskah TikTok pendek jualan {prod_name}. Bahasa gaul Indonesia yang asik."
                res = gemini.generate_content(prompt)
                st.info(f"📜 **Naskah AI:**\n{res.text}")

            # 2. GENERATE VIDEO (PROSES HUGGING FACE)
            with st.spinner("Hugging Face lagi ngerakit video (Bisa 1-2 menit)..."):
                # Kita ambil foto pertama buat dijadiin video
                img_bytes = uploaded_files[0].getvalue()
                
                # Kita coba jalur 'Router' terbaru dengan model alternatif yang lebih ringan
                # Model ini biasanya lebih ramah buat API gratisan
                API_URL = "https://router.huggingface.co/models/ali-vilab/i2vgen-xl"
                headers = {"Authorization": f"Bearer {HF_TOKEN}"}
                
                # Kirim permintaan
                response = requests.post(API_URL, headers=headers, data=img_bytes, timeout=150)
                
                if response.status_code == 200:
                    st.success("✅ Video Berhasil Dibuat!")
                    st.video(response.content)
                    st.balloons()
                elif response.status_code == 503:
                    st.warning("⚠️ Server lagi sibuk/loading model. Klik lagi tombolnya 1 menit lagi ya!")
                elif response.status_code == 410:
                    st.error("Aduh, Hugging Face bener-bener matiin jalur video ini. Harus ganti strategi, Bro!")
                else:
                    st.error(f"Gagal generate video. Kode: {response.status_code}")
                    st.write(f"Detail: {response.text[:200]}")

        except Exception as e:
            st.error(f"Eror sistem: {str(e)}")

# Tampilan Galeri Foto
if uploaded_files:
    st.write("---")
    st.write(f"🖼️ {len(uploaded_files)} Foto dipilih:")
    cols = st.columns(3)
    for i, file in enumerate(uploaded_files):
        cols[i % 3].image(file, use_column_width=True)
