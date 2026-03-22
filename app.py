import streamlit as st
import google.generativeai as genai
import requests
import time

# --- KONFIGURASI ---
try:
    GEMINI_KEY = st.secrets["GEMINI_KEY"]
    HF_TOKEN = st.secrets["HF_TOKEN"]
except Exception:
    st.error("Kunci API belum diset di Secrets, Bro!")
    st.stop()

# --- SETUP GOOGLE AI ---
genai.configure(api_key=GEMINI_KEY)
try:
    models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    target_model = next((m for m in models if 'flash' in m), next((m for m in models if 'pro' in m), models[0]))
    gemini = genai.GenerativeModel(target_model)
except Exception as e:
    st.error(f"Gagal konek ke Gemini: {e}")
    st.stop()

# --- UI APLIKASI ---
st.title("🎥 Affiliate Video Pro")
st.write(f"✅ Sistem Naskah Aktif (`{target_model}`)")
st.write("---")

prod_name = st.text_input("Nama Produk", placeholder="Contoh: Piring Keramik Gold")
uploaded_files = st.file_uploader("Upload Foto Produk (Bisa banyak)", type=['jpg', 'png', 'jpeg'], accept_multiple_files=True)

# --- EKSEKUSI ---
if st.button("🚀 MULAI BUAT KONTEN"):
    if not prod_name or not uploaded_files:
        st.error("Isi nama produk & upload foto dulu, Bro!")
    else:
        try:
            # 1. GENERATE NASKAH
            with st.spinner("Gemini lagi mikir naskah..."):
                prompt_script = f"Buat naskah video TikTok pendek untuk jualan {prod_name}. Bahasa gaul Indonesia yang menarik."
                res = gemini.generate_content(prompt_script)
                naskah = res.text
                st.info(f"📜 **Naskah AI:**\n{naskah}")

            # 2. GENERATE VIDEO (VERSI ANTI-PUTUS)
            with st.spinner("Hugging Face lagi ngerakit video (Sabar, jangan di-refresh)..."):
                img_bytes = uploaded_files[0].getvalue()
                
                # Kita coba model paling bandel
                API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-video-diffusion-img2vid-xt"
                headers = {"Authorization": f"Bearer {HF_TOKEN}"}
                
                # Kita kasih timeout 120 detik (2 menit) biar dia gak gampang mutusin koneksi
                response = requests.post(API_URL, headers=headers, data=img_bytes, timeout=120, stream=True)
                
                if response.status_code == 200:
                    # Ambil data secara utuh
                    video_content = response.raw.read()
                    st.success("✅ Video Berhasil Dibuat!")
                    st.video(video_content)
                    st.balloons()
                elif response.status_code == 503:
                    st.warning("⚠️ Server lagi penuh (Overload). Klik lagi tombolnya dalam 30 detik ya!")
                else:
                    st.error(f"Gagal generate video. Kode: {response.status_code}")

        except requests.exceptions.RequestException as e:
            st.error(f"Koneksi lemot nih, Bro! Coba lagi ya. Detail: {str(e)}")
        except Exception as e:
            st.error(f"Eror sistem: {str(e)}")

# Tampilan Galeri
if uploaded_files:
    st.write("---")
    st.write(f"🖼️ {len(uploaded_files)} Foto dipilih:")
    cols = st.columns(3)
    for i, file in enumerate(uploaded_files):
        cols[i % 3].image(file, use_column_width=True)
