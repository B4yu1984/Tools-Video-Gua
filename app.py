import streamlit as st
import google.generativeai as genai
from huggingface_hub import InferenceClient
import requests
from PIL import Image

# --- AMBIL KUNCI RAHASIA ---
GEMINI_KEY = st.secrets["GEMINI_KEY"]
HF_TOKEN = st.secrets["HF_TOKEN"]

genai.configure(api_key=GEMINI_KEY)
gemini = genai.GenerativeModel("gemini-1.5-flash")
client = InferenceClient(token=HF_TOKEN)

st.title("🎥 Affiliate Video Generator")
st.write("Bikin konten promosi otomatis pake AI!")

# --- INPUT USER ---
prod_name = st.text_input("Nama Produk", placeholder="Contoh: Skincare Wardah")
uploaded_file = st.file_uploader("Upload Foto Produk/Model", type=['jpg', 'png'])

if st.button("🚀 MULAI BUAT VIDEO"):
    if not prod_name or not uploaded_file:
        st.error("Isi dulu bro datanya!")
    else:
        with st.spinner("Lagi ngeracik naskah & video..."):
            # 1. Bikin Naskah Pake Gemini
            prompt_script = f"Buat naskah video TikTok 10 detik jualan {prod_name}. Bahasa gaul Indonesia yang persuasif. Output teks saja."
            res = gemini.generate_content(prompt_script)
            naskah = res.text
            st.info(f"Naskah AI: {naskah}")

            # 2. Bikin Video Pake Hugging Face
            try:
                img_bytes = uploaded_file.getvalue()
                # Pake model i2vgen-xl (gratisan HF)
                video_res = client.post(
                    data=img_bytes,
                    model="ali-vilab/i2vgen-xl",
                    parameters={"prompt": f"Professional cinematic video, a person demonstrating {prod_name}, high quality, aesthetic background"}
                )
                st.success("Video Jadi, Bro!")
                st.video(video_res)
            except Exception as e:
                st.error("Server AI lagi sibuk, coba lagi beberapa saat ya!")
