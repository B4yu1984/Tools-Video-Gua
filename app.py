import streamlit as st
import google.generativeai as genai
from huggingface_hub import InferenceClient

# 1. Ambil Key
GEMINI_KEY = st.secrets["GEMINI_KEY"]
HF_TOKEN = st.secrets["HF_TOKEN"]

# 2. Setup Google AI
genai.configure(api_key=GEMINI_KEY)

# --- TRIK AUTO-DETECT MODEL ---
try:
    # Kita cari model yang support 'generateContent' secara otomatis
    available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    # Kita cari yang ada nama 'flash', kalau gak ada kita ambil yang paling atas
    target_model = next((m for m in available_models if 'flash' in m), available_models[0])
    gemini = genai.GenerativeModel(target_model)
except Exception as e:
    st.error(f"Waduh, gagal narik daftar model: {e}")
    st.stop()

# 3. Setup HuggingFace
client = InferenceClient(token=HF_TOKEN)

st.title("🎥 Affiliate Video Pro")
st.write(f"Sistem menggunakan model: `{target_model}`") # Biar kita tau dia pake apa

prod_name = st.text_input("Nama Produk")
uploaded_files = st.file_uploader("Upload Foto", type=['jpg', 'png', 'jpeg'], accept_multiple_files=True)

if st.button("🚀 MULAI BUAT VIDEO"):
    if prod_name and uploaded_files:
        try:
            # Step 1: Naskah
            res = gemini.generate_content(f"Buat naskah TikTok pendek jualan {prod_name}. Bahasa gaul Indonesia.")
            st.info(f"📜 Naskah: {res.text}")
            
            # Step 2: Video
            img_bytes = uploaded_files[0].getvalue()
            video_res = client.post(
                data=img_bytes, 
                model="stabilityai/stable-video-diffusion-img2vid-xt"
            )
            st.video(video_res)
        except Exception as e:
            st.error(f"Eror pas eksekusi: {e}")
