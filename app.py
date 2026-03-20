import streamlit as st
import google.generativeai as genai
from huggingface_hub import InferenceClient

GEMINI_KEY = st.secrets["GEMINI_KEY"]
HF_TOKEN = st.secrets["HF_TOKEN"]

genai.configure(api_key=GEMINI_KEY)
gemini = genai.GenerativeModel("gemini-1.5-flash")
client = InferenceClient(token=HF_TOKEN)

st.title("🎥 Affiliate Video Pro")
prod_name = st.text_input("Nama Produk")
uploaded_files = st.file_uploader("Upload Foto", type=['jpg', 'png', 'jpeg'], accept_multiple_files=True)

if st.button("🚀 MULAI BUAT VIDEO"):
 if prod_name and uploaded_files:
  try:
   res = gemini.generate_content(f"Naskah TikTok pendek jualan {prod_name}")
   st.info(f"📜 Naskah: {res.text}")
   img_bytes = uploaded_files[0].getvalue()
   video_res = client.post(data=img_bytes, model="stabilityai/stable-video-diffusion-img2vid-xt")
   st.video(video_res)
  except Exception as e:
   st.error(f"Eror: {e}")
