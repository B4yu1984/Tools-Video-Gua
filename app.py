import streamlit as st
import google.generativeai as genai
import requests

# --- 1. AMBIL KUNCI ---
GEMINI_KEY = st.secrets["GEMINI_KEY"]
HF_TOKEN = st.secrets["HF_TOKEN"]

# --- 2. SETUP GEMINI ---
genai.configure(api_key=GEMINI_KEY)
model_gemini = genai.GenerativeModel('gemini-1.5-flash')

# --- 3. TAMPILAN ---
st.set_page_config(page_title="Affiliate Video Pro", page_icon="🎥")
st.title("🎥 Affiliate Video Pro")
st.write("---")

prod_name = st.text_input("Nama Produk", placeholder="Contoh: Piring Keramik Mewah")
uploaded_files = st.file_uploader("Upload Foto Produk (Bisa banyak)", type=['jpg', 'png', 'jpeg'], accept_multiple_files=True)

if st.button("🚀 MULAI BUAT KONTEN"):
    if not prod_name or not uploaded_files:
        st.error("Isi nama produk & upload foto dulu, Bro!")
    else:
        try:
            # STEP 1: NASKAH
            with st.spinner("Gemini lagi nulis naskah..."):
                res = model_gemini.generate_content(f"Buat naskah TikTok pendek jualan {prod_name}. Bahasa gaul.")
                st.info(f"📜 **Naskah AI:**\n{res.text}")

            # STEP 2: VIDEO
            with st.spinner("Lagi ngerakit video (Bisa 1-2 menit)..."):
                img_bytes = uploaded_files[0].getvalue()
                
                # ALAMAT BARU YANG DIMINTA HUGGING FACE
                API_URL = "https://router.huggingface.co/models/stabilityai/stable-video-diffusion-img2vid-xt"
                headers = {"Authorization": f"Bearer {HF_TOKEN}"}
                
                # Kirim data
                response = requests.post(API_URL, headers=headers, data=img_bytes, timeout=180)
                
                if response.status_code == 200:
                    st.success("✅ Video Berhasil Dibuat!")
                    st.video(response.content)
                    st.balloons()
                elif response.status_code == 503:
                    st.warning("⚠️ Server lagi 'pemanasan'. Tunggu 30 detik terus klik tombol lagi ya!")
                else:
                    st.error(f"Gagal generate video. Kode: {response.status_code}")
                    st.write(f"Detail: {response.text[:200]}") # Biar kita tau eror aslinya apa

        except Exception as e:
            st.error(f"Ada masalah sistem: {e}")

# Galeri Preview
if uploaded_files:
    st.write("---")
    st.write(f"🖼️ {len(uploaded_files)} Foto terpilih:")
    cols = st.columns(3)
    for i, file in enumerate(uploaded_files):
        cols[i % 3].image(file, use_column_width=True)
