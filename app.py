import streamlit as st
import google.generativeai as genai
import requests
import time

# --- KONFIGURASI ---
try:
    GEMINI_KEY = st.secrets["GEMINI_KEY"]
    HF_TOKEN = st.secrets["HF_TOKEN"]
except Exception:
    st.error("Kunci API belum diset di Secrets, Bro!")
    st.stop()

# --- SETUP GOOGLE AI ---
genai.configure(api_key=GEMINI_KEY)
try:
    models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    target_model = next((m for m in models if 'flash' in m), next((m for m in models if 'pro' in m), models[0]))
    gemini = genai.GenerativeModel(target_model)
except Exception as e:
    st.error(f"Gagal konek ke Gemini: {e}")
    st.stop()

# --- UI APLIKASI ---
st.title("🎥 Affiliate Video Pro")
st.write(f"✅ Sistem Naskah Aktif (`{target_model}`)")
st.write("---")

prod_name = st.text_input("Nama Produk", placeholder="Contoh: Piring Keramik Gold")

# FITUR MULTIPLE UPLOAD BALIK LAGI!
uploaded_files = st.file_uploader("Upload Foto Produk (Bisa pilih banyak)", type=['jpg', 'png', 'jpeg'], accept_multiple_files=True)

# --- EKSEKUSI ---
if st.button("🚀 MULAI BUAT KONTEN"):
    if not prod_name or not uploaded_files:
        st.error("Isi nama produk & upload foto dulu, Bro!")
    else:
        try:
            # 1. GENERATE NASKAH
            with st.spinner("Gemini lagi mikir naskah..."):
                prompt_script = f"Buat naskah video TikTok pendek untuk jualan {prod_name}. Bahasa gaul Indonesia yang menarik."
                res = gemini.generate_content(prompt_script)
                naskah = res.text
                st.info(f"📜 **Naskah AI:**\n{naskah}")

            # 2. GENERATE VIDEO (PAKE JALUR BARU YANG BENER)
            with st.spinner("Hugging Face lagi ngerakit video..."):
                # Kita ambil foto pertama untuk dijadikan video
                img_bytes = uploaded_files[0].getvalue()
                
                # JALUR BARU: Kita pake model yang lebih stabil buat video gratisan
                API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-video-diffusion-img2vid-xt"
                headers = {"Authorization": f"Bearer {HF_TOKEN}"}
                
                response = requests.post(API_URL, headers=headers, data=img_bytes)
                
                if response.status_code == 200:
                    st.success("✅ Video Berhasil Dibuat!")
                    st.video(response.content)
                    st.balloons()
                elif response.status_code == 503:
                    st.warning("⚠️ Server lagi penuh/loading. Tunggu 1 menit terus klik lagi tombolnya ya!")
                elif response.status_code == 404:
                    # Kalau model utama 404, kita coba model alternatif
                    st.warning("Model utama lagi offline, mencoba jalur alternatif...")
                    API_URL_ALT = "https://api-inference.huggingface.co/models/ali-vilab/i2vgen-xl"
                    response = requests.post(API_URL_ALT, headers=headers, data=img_bytes)
                    if response.status_code == 200:
                        st.video(response.content)
                    else:
                        st.error("Semua server video lagi penuh, Bro. Coba lagi nanti ya.")
                else:
                    st.error(f"Gagal generate video. Kode: {response.status_code}")

        except Exception as e:
            st.error(f"Eror eksekusi: {str(e)}")

# Tampilan Galeri (Biar lu bisa liat foto-foto yang lu upload)
if uploaded_files:
    st.write("---")
    st.write(f"🖼️ {len(uploaded_files)} Foto dipilih:")
    cols = st.columns(3)
    for i, file in enumerate(uploaded_files):
        cols[i % 3].image(file, use_column_width=True)
