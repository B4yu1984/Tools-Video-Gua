import streamlit as st
import google.generativeai as genai
from huggingface_hub import InferenceClient
import requests
from PIL import Image
import time

# --- AMBIL KUNCI RAHASIA ---
try:
    GEMINI_KEY = st.secrets["GEMINI_KEY"]
    HF_TOKEN = st.secrets["HF_TOKEN"]
except:
    st.error("Waduh, kuncinya belum bener di Secrets, Bro!")
    st.stop()

genai.configure(api_key=GEMINI_KEY)
gemini = genai.GenerativeModel("gemini-1.5-flash")
client = InferenceClient(token=HF_TOKEN)

st.set_page_config(page_title="Affiliate Video Pro", page_icon="🎥")
st.title("🎥 Affiliate Video Pro")
st.write("Sekarang bisa banyak foto sekaligus, Bro!")

# --- INPUT USER ---
prod_name = st.text_input("Nama Produk", placeholder="Contoh: Piring Marmer Estetik")
uploaded_files = st.file_uploader("Upload Foto Produk (Bisa banyak)", type=['jpg', 'png', 'jpeg'], accept_multiple_files=True)

if st.button("🚀 MULAI BUAT VIDEO"):
    if not prod_name or not uploaded_files:
        st.error("Isi nama produk & upload foto dulu, Bro!")
    else:
        with st.spinner("Sabar Bro, lagi diracik..."):
            # 1. Bikin Naskah Pake Gemini
            try:
                prompt_script = f"Buat naskah pendek TikTok jualan {prod_name}. Bahasa gaul, to the point, maksimal 15 detik. Output teks saja."
                res = gemini.generate_content(prompt_script)
                naskah = res.text
                st.info(f"📜 **Naskah AI:** {naskah}")
            except:
                st.error("Gagal konek ke Gemini, cek API Key lu.")

            # 2. Proses Foto Pertama jadi Video (Model Lebih Stabil)
            try:
                # Ambil foto pertama buat dijadiin video
                first_img = uploaded_files[0].getvalue()
                
                # Kita pake model Stable Video Diffusion (Lebih Bandel)
                video_res = client.post(
                    data=first_img,
                    model="stabilityai/stable-video-diffusion-img2vid-xt",
                    parameters={"prompt": f"Professional product showcase of {prod_name}, cinematic lighting, slow motion movement"}
                )
                
                st.success("✅ Video Berhasil Dibuat!")
                st.video(video_res)
                st.balloons()
            except Exception as e:
                st.warning("⚠️ Server video lagi penuh. Coba klik lagi tombolnya 2-3 kali ya!")
                st.write("Saran: Kalau gagal terus, coba upload file foto yang ukurannya lebih kecil (dibawah 1MB).")

# Tampilan Galeri Foto yang diupload
if uploaded_files:
    st.write("---")
    st.write(f"🖼️ {len(uploaded_files)} Foto siap diproses:")
    cols = st.columns(3)
    for i, file in enumerate(uploaded_files):
        cols[i % 3].image(file, use_column_width=True)
