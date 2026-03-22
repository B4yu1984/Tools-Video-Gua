import streamlit as st
import requests

# --- 1. AMBIL KUNCI ---
GEMINI_KEY = st.secrets["GEMINI_KEY"]
HF_TOKEN = st.secrets["HF_TOKEN"]

# --- 2. UI APLIKASI ---
st.set_page_config(page_title="Affiliate Video Pro", page_icon="🎥")
st.title("🎥 Affiliate Video Pro")
st.write("✅ Sistem Naskah Aktif: `Jalur Langsung (Direct API)`")
st.write("---")

prod_name = st.text_input("Nama Produk", placeholder="Contoh: Piring Marmer")
uploaded_files = st.file_uploader("Upload Foto Produk (Bisa banyak)", type=['jpg', 'png', 'jpeg'], accept_multiple_files=True)

if st.button("🚀 MULAI BUAT KONTEN"):
    if not prod_name or not uploaded_files:
        st.error("Isi nama produk & upload foto dulu, Bro!")
    else:
        # STEP 1: NASKAH (TEMBAK LANGSUNG KE PUSAT GEMINI)
        with st.spinner("Gemini lagi nulis naskah..."):
            try:
                gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
                prompt = f"Buat naskah TikTok pendek jualan {prod_name}. Bahasa gaul Indonesia yang asik dan viral."
                
                payload = {
                    "contents": [{"parts": [{"text": prompt}]}]
                }
                headers = {"Content-Type": "application/json"}
                
                res = requests.post(gemini_url, json=payload, headers=headers)
                
                if res.status_code == 200:
                    data = res.json()
                    naskah = data['candidates'][0]['content']['parts'][0]['text']
                    st.info(f"📜 **Naskah AI:**\n{naskah}")
                else:
                    st.error(f"Gagal narik naskah. Kode: {res.status_code}")
                    st.write(res.text)
                    st.stop() # Berhenti di sini kalau naskah gagal
            except Exception as e:
                st.error(f"Eror sistem naskah: {e}")
                st.stop()

        # STEP 2: VIDEO (HUGGING FACE)
        with st.spinner("Hugging Face lagi ngerakit video (Sabar, ini agak lama)..."):
            try:
                img_bytes = uploaded_files[0].getvalue()
                
                # Model Ali-Vilab
                API_URL = "https://api-inference.huggingface.co/models/ali-vilab/i2vgen-xl"
                hf_headers = {"Authorization": f"Bearer {HF_TOKEN}"}
                
                response = requests.post(API_URL, headers=hf_headers, data=img_bytes, timeout=120)
                
                if response.status_code == 200:
                    st.success("✅ Video Berhasil Dibuat!")
                    st.video(response.content)
                    st.balloons()
                elif response.status_code == 503:
                    st.warning("⚠️ Server video lagi loading model. Sabar Bro, klik tombolnya lagi dalam 30 detik!")
                else:
                    st.error(f"Gagal generate video. Kode: {response.status_code}")
                    st.write("Server video gratisan lagi sibuk/nolak. Coba upload foto yang ukurannya di bawah 500KB.")
            except Exception as e:
                st.error(f"Eror sistem video: {e}")

# Galeri Preview
if uploaded_files:
    st.write("---")
    st.write(f"🖼️ {len(uploaded_files)} Foto terpilih:")
    cols = st.columns(3)
    for i, file in enumerate(uploaded_files):
        cols[i % 3].image(file, use_column_width=True)
