import streamlit as st
import google.generativeai as genai
from huggingface_hub import InferenceClient
import requests
from PIL import Image

# --- KONFIGURASI ---
# Pastiin baris di bawah ini nempel di pinggir kiri (Gak ada spasi)
GEMINI_KEY = st.secrets["GEMINI_KEY"]
HF_TOKEN = st.secrets["HF_TOKEN"]

genai.configure(api_key=GEMINI_KEY)
gemini = genai.GenerativeModel("gemini-1.5-flash")
client = InferenceClient(token=HF_TOKEN)

st.title("🎥 Affiliate Video Pro")
st.write("Bikin video promosi otomatis!")

# --- INPUT USER ---
prod_name = st.text_input("Nama Produk", placeholder="Contoh: Piring Estetik")
uploaded_files = st.file_uploader("Upload Foto Produk", type=['jpg', 'png', 'jpeg'], accept_multiple_files=True)

if st.button("🚀 MULAI BUAT VIDEO"):
    if not prod_name or not uploaded_files:
        st.error("Isi nama produk & upload foto dulu, Bro!")
    else:
        try:
            with st.spinner("Lagi nulis naskah..."):
                prompt_script = f"Buat naskah video TikTok pendek jualan {prod_name}. Bahasa gaul Indonesia. Output teks saja."
                res = gemini.generate_content(prompt_script)
                naskah = res.text
                st.info(f"📜 **Naskah AI:** {naskah}")

            with st.spinner("Lagi ngerakit video..."):
                first_img = uploaded_files[0].getvalue()
                video_res = client.post(
                    data=first_img,
                    model="stabilityai/stable-video-diffusion-img2vid-xt",
                    parameters={"prompt": f"Professional product showcase of {prod_name}, cinematic lighting"}
                )
                st.success("✅ Video Jadi!")
                st.video(video_res)
        except Exception as e:
            st.error(f"Ada masalah nih: {str(e)}")
