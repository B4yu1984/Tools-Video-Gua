import streamlit as st
import google.generativeai as genai
import requests

# --- 1. AMBIL KUNCI ---
GEMINI_KEY = st.secrets["GEMINI_KEY"]
HF_TOKEN = st.secrets["HF_TOKEN"]

# --- 2. SETUP GEMINI (Pake versi paling senior anti-404) ---
genai.configure(api_key=GEMINI_KEY)
# Kita kunci di gemini-pro, gak usah pake flash biar server jadul tetep bisa baca
model_gemini = genai.GenerativeModel('gemini-pro')

# --- 3. UI APLIKASI ---
st.set_page_config(page_title="Affiliate Video Pro", page_icon="🎥")
st.title("🎥 Affiliate Video Pro")
st.write("✅ Sistem Naskah Aktif: `gemini-pro`")
st.write("---")

prod_name = st.text_input("Nama Produk", placeholder="Contoh: Piring Marmer")
uploaded_files = st.file_uploader("Upload Foto Produk", type=['jpg', 'png', 'jpeg'], accept_multiple_files=True)

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
            with st.spinner("Hugging Face lagi ngerakit video..."):
                img_bytes = uploaded_files[0].getvalue()
                
                # Model Ali-Vilab yang stabil
                API_URL = "https://api-inference.huggingface.co/models/ali-vilab/i2vgen-xl"
                headers = {"Authorization": f"Bearer {HF_TOKEN}"}
                
                response = requests.post(API_URL, headers=headers, data=img_bytes, timeout=120)
                
                if response.status_code == 200:
                    st.success("✅ Video Berhasil Dibuat!")
                    st.video(response.content)
                    st.balloons()
                elif response.status_code == 503:
                    st.warning("⚠️ Server lagi loading. Sabar Bro, klik tombolnya lagi dalam 30 detik!")
                else:
                    st.error(f"Gagal generate video. Kode: {response.status_code}")
                    st.write("Server video lagi nolak. Coba upload foto yang sizenya kecil aja.")

        except Exception as e:
            st.error(f"Ada masalah sistem: {e}")

# Galeri Preview
if uploaded_files:
    st.write("---")
    st.write(f"🖼️ {len(uploaded_files)} Foto terpilih:")
    cols = st.columns(3)
    for i, file in enumerate(uploaded_files):
        cols[i % 3].image(file, use_column_width=True)
