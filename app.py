import streamlit as st
import google.generativeai as genai
from huggingface_hub import InferenceClient

# 1. Ambil Key
GEMINI_KEY = st.secrets["GEMINI_KEY"]
HF_TOKEN = st.secrets["HF_TOKEN"]

# 2. Setup Google AI
genai.configure(api_key=GEMINI_KEY)

# --- JURUS ANTI 404 (Auto-Select Model) ---
try:
    # Cari model yang beneran aktif di akun lu
    models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    # Prioritas: Flash (cepet), kalau gak ada ambil Pro, kalau gak ada ambil apa aja yang tersedia
    target_model = next((m for m in models if 'flash' in m), 
                        next((m for m in models if 'pro' in m), models[0]))
    gemini = genai.GenerativeModel(target_model)
except Exception as e:
    st.error(f"Gagal konek: {e}")
    st.stop()

# 3. Setup HuggingFace
client = InferenceClient(token=HF_TOKEN)

st.title("🎥 Affiliate Video Pro")
st.write(f"✅ Sistem Aktif: `{target_model}`")

prod_name = st.text_input("Nama Produk")
uploaded_files = st.file_uploader("Upload Foto", type=['jpg', 'png', 'jpeg'], accept_multiple_files=True)

if st.button("🚀 MULAI BUAT VIDEO"):
    if prod_name and uploaded_files:
        try:
            with st.spinner("Nulis naskah..."):
                res = gemini.generate_content(f"Naskah TikTok pendek jualan {prod_name}. Bahasa gaul.")
                st.info(f"📜 Naskah: {res.text}")
            
            with st.spinner("Bikin video..."):
                img_bytes = uploaded_files[0].getvalue()
                video_res = client.post(data=img_bytes, model="stabilityai/stable-video-diffusion-img2vid-xt")
                st.video(video_res)
        except Exception as e:
            st.error(f"Eror eksekusi: {e}")
