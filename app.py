import streamlit as st
import google.generativeai as genai
import requests

# 1. AMBIL KUNCI
GEMINI_KEY = st.secrets["GEMINI_KEY"]
HF_TOKEN = st.secrets["HF_TOKEN"]

# 2. SETUP GOOGLE AI (JURUS DETEKTIF)
genai.configure(api_key=GEMINI_KEY)
try:
    # Cari model yang aktif di akun lu secara otomatis
    available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    # Pilih flash kalau ada, kalau nggak ada pilih pro, atau yang paling atas
    target_model = next((m for m in available_models if 'flash' in m), 
                        next((m for m in available_models if 'pro' in m), available_models[0]))
    gemini = genai.GenerativeModel(target_model)
except Exception as e:
    st.error(f"Gagal konek ke Google AI: {e}")
    st.stop()

# 3. UI APLIKASI
st.title("🎥 Affiliate Video Pro")
st.write(f"✅ Sistem Naskah Aktif: `{target_model}`")

prod_name = st.text_input("Nama Produk", placeholder="Contoh: Piring Marmer")
# Fitur Multiple Upload Aktif Lagi
uploaded_files = st.file_uploader("Upload Foto Produk (Bisa banyak)", type=['jpg', 'png', 'jpeg'], accept_multiple_files=True)

if st.button("🚀 MULAI BUAT KONTEN"):
    if prod_name and uploaded_files:
        try:
            # STEP 1: NASKAH
            with st.spinner("Gemini lagi mikir naskah..."):
                res = gemini.generate_content(f"Buat naskah TikTok pendek jualan {prod_name}. Bahasa gaul.")
                st.info(f"📜 **Naskah AI:**\n{res.text}")

            # STEP 2: VIDEO
            with st.spinner("Hugging Face lagi ngerakit video..."):
                img_bytes = uploaded_files[0].getvalue()
                # Pake router terbaru
                API_URL = "https://router.huggingface.co/models/stabilityai/stable-video-diffusion-img2vid-xt"
                headers = {"Authorization": f"Bearer {HF_TOKEN}"}
                response = requests.post(API_URL, headers=headers, data=img_bytes, timeout=180)
                
                if response.status_code == 200:
                    st.success("✅ Video Jadi!")
                    st.video(response.content)
                    st.balloons()
                else:
                    st.error(f"Gagal Video (Kode {response.status_code})")
                    st.write("Saran: Klik tombol sekali lagi, biasanya server butuh pemanasan.")
        except Exception as e:
            st.error(f"Eror eksekusi: {e}")

# Galeri Preview
if uploaded_files:
    st.write("---")
    st.write(f"🖼️ {len(uploaded_files)} Foto terpilih:")
    cols = st.columns(3)
    for i, file in enumerate(uploaded_files):
        cols[i % 3].image(file, use_column_width=True)
