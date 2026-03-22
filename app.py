import streamlit as st
import google.generativeai as genai
import requests

# 1. AMBIL KUNCI
GEMINI_KEY = st.secrets["GEMINI_KEY"]
HF_TOKEN = st.secrets["HF_TOKEN"]

# 2. SETUP GOOGLE AI (Gemini udah oke!)
genai.configure(api_key=GEMINI_KEY)
try:
    # Pakai nama model yang tadi udah terbukti jalan di tempat lu
    gemini = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"Gagal konek ke Google AI: {e}")
    st.stop()

# 3. UI APLIKASI
st.title("🎥 Affiliate Video Pro")
st.write(f"✅ Sistem Naskah Aktif: `gemini-1.5-flash`")

prod_name = st.text_input("Nama Produk", placeholder="Contoh: Piring Marmer")
uploaded_files = st.file_uploader("Upload Foto Produk (Bisa banyak)", type=['jpg', 'png', 'jpeg'], accept_multiple_files=True)

if st.button("🚀 MULAI BUAT KONTEN"):
    if prod_name and uploaded_files:
        try:
            # STEP 1: NASKAH (Udah lancar jaya)
            with st.spinner("Gemini lagi mikir naskah..."):
                res = gemini.generate_content(f"Buat naskah TikTok pendek jualan {prod_name}. Bahasa gaul.")
                st.info(f"📜 **Naskah AI:**\n{res.text}")

            # STEP 2: VIDEO (Ganti Jalur & Model)
            with st.spinner("Hugging Face lagi ngerakit video (Sabar, jalur ini agak lama)..."):
                img_bytes = uploaded_files[0].getvalue()
                
                # Kita coba model Ali-Vilab yang lebih stabil dari SVD
                API_URL = "https://api-inference.huggingface.co/models/ali-vilab/i2vgen-xl"
                headers = {"Authorization": f"Bearer {HF_TOKEN}"}
                
                response = requests.post(API_URL, headers=headers, data=img_bytes, timeout=120)
                
                if response.status_code == 200:
                    st.success("✅ Video Jadi!")
                    st.video(response.content)
                    st.balloons()
                elif response.status_code == 503:
                    st.warning("⚠️ Server lagi penuh/loading. Klik lagi dalam 30 detik ya!")
                else:
                    st.error(f"Gagal Video (Kode {response.status_code})")
                    st.write("Coba upload foto yang ukurannya lebih kecil (di bawah 500KB) biar enteng.")
        except Exception as e:
            st.error(f"Eror eksekusi: {e}")

# Galeri Preview
if uploaded_files:
    st.write("---")
    st.write(f"🖼️ {len(uploaded_files)} Foto terpilih:")
    cols = st.columns(3)
    for i, file in enumerate(uploaded_files):
        cols[i % 3].image(file, use_column_width=True)
