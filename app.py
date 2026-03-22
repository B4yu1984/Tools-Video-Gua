import streamlit as st
import google.generativeai as genai
import requests

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
uploaded_file = st.file_uploader("Upload Foto Produk", type=['jpg', 'png', 'jpeg'])

# --- EKSEKUSI JURUS UTAMA ---
if st.button("🚀 MULAI BUAT KONTEN"):
    if not prod_name or not uploaded_file:
        st.error("Isi nama produk & upload foto dulu, Bro!")
    else:
        try:
            # STEP 1: GENERATE NASKAH
            with st.spinner("Si Gemini lagi mikir naskah..."):
                prompt_script = f"Buat naskah video TikTok pendek untuk jualan produk {prod_name}. Bahasa gaul Indonesia yang menarik."
                res = gemini.generate_content(prompt_script)
                naskah = res.text
                st.info(f"📜 **Naskah AI:**\n{naskah}")

            # STEP 2: GENERATE VIDEO
            with st.spinner("Hugging Face lagi ngerakit video (bisa 30 detik+)..."):
                img_bytes = uploaded_file.getvalue()
                API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-video-diffusion-img2vid-xt"
                headers = {"Authorization": f"Bearer {HF_TOKEN}"}
                response = requests.post(API_URL, headers=headers, data=img_bytes)
                
                if response.status_code == 200:
                    st.success("✅ Video Berhasil Dibuat!")
                    st.video(response.content)
                    st.balloons()
                elif response.status_code == 503:
                    st.warning("⚠️ Server video lagi penuh. Tunggu 1 menit terus klik tombol lagi ya!")
                else:
                    st.error(f"Gagal generate video. Kode error: {response.status_code}")
                    st.write(f"Detail error: {response.text}")

        except Exception as e:
            st.error(f"Eror eksekusi total: {str(e)}")
