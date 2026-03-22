import streamlit as st
import google.generativeai as genai
import requests

# --- 1. AMBIL KUNCI ---
GEMINI_KEY = st.secrets["GEMINI_KEY"]
HF_TOKEN = st.secrets["HF_TOKEN"]

# --- 2. SETUP GEMINI (Balik ke versi Flash yang sukses kemarin!) ---
genai.configure(api_key=GEMINI_KEY)
try:
    # Kita pake jurus detektif lagi yang udah terbukti nembus di akun lu
    models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    target_model = next((m for m in models if 'flash' in m), models[0])
    model_gemini = genai.GenerativeModel(target_model)
except Exception as e:
    st.error(f"Gagal setup Gemini: {e}")
    st.stop()

# --- 3. UI APLIKASI ---
st.set_page_config(page_title="Affiliate Video Pro", page_icon="🎥")
st.title("🎥 Affiliate Video Pro")
st.write(f"✅ Sistem Naskah Aktif: `{target_model}`")
st.write("---")

prod_name = st.text_input("Nama Produk", placeholder="Contoh: Piring Marmer")
uploaded_files = st.file_uploader("Upload Foto Produk (Bisa banyak)", type=['jpg', 'png', 'jpeg'], accept_multiple_files=True)

if st.button("🚀 MULAI BUAT KONTEN"):
    if not prod_name or not uploaded_files:
        st.error("Isi nama produk & upload foto dulu, Bro!")
    else:
        # STEP 1: NASKAH (UDAH PASTI JALAN)
        with st.spinner("Gemini lagi nulis naskah..."):
            try:
                res = model_gemini.generate_content(f"Buat naskah TikTok pendek jualan {prod_name}. Bahasa gaul Indonesia yang asik.")
                st.info(f"📜 **Naskah AI:**\n{res.text}")
            except Exception as e:
                st.error(f"Eror naskah: {e}")
                st.stop()

        # STEP 2: VIDEO (ANTI 410 GONE)
        with st.spinner("Hugging Face lagi ngerakit video (Sabar, bisa 1-2 menit)..."):
            try:
                img_bytes = uploaded_files[0].getvalue()
                
                # Kita pake model video Ali-Vilab yang aman dari eror 410
                API_URL = "https://api-inference.huggingface.co/models/ali-vilab/i2vgen-xl"
                headers = {"Authorization": f"Bearer {HF_TOKEN}"}
                
                response = requests.post(API_URL, headers=headers, data=img_bytes, timeout=120)
                
                if response.status_code == 200:
                    st.success("✅ Video Berhasil Dibuat!")
                    st.video(response.content)
                    st.balloons()
                elif response.status_code == 503:
                    st.warning("⚠️ Server video lagi loading. Sabar Bro, klik tombolnya lagi dalam 30 detik!")
                else:
                    st.error(f"Gagal generate video. Kode: {response.status_code}")
                    st.write("Saran: Coba pake foto yang ukurannya kecil aja (di bawah 500KB).")
            except Exception as e:
                st.error(f"Eror sistem video: {e}")

# Galeri Preview
if uploaded_files:
    st.write("---")
    st.write(f"🖼️ {len(uploaded_files)} Foto terpilih:")
    cols = st.columns(3)
    for i, file in enumerate(uploaded_files):
        cols[i % 3].image(file, use_column_width=True)
