import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- 1. SETUP KUNCI & GEMINI ---
try:
    GEMINI_KEY = st.secrets["GEMINI_KEY"]
    genai.configure(api_key=GEMINI_KEY)
    # Pake Flash karena kita butuh dia buat "ngeliat" banyak foto (Multimodal)
    model_gemini = genai.GenerativeModel('gemini-1.5-flash')
except Exception:
    st.error("Kunci GEMINI_KEY belum bener di Secrets, Bro!")
    st.stop()

# --- 2. SETUP "INGATAN" APLIKASI (STATE MANAGEMENT) ---
# Ini biar aplikasi gak reset pas lu klik tombol
if 'step' not in st.session_state:
    st.session_state.step = 1 # Step 1: Input form
if 'naskah' not in st.session_state:
    st.session_state.naskah = ""
if 'prompt_veo' not in st.session_state:
    st.session_state.prompt_veo = ""

# --- 3. UI APLIKASI ---
st.set_page_config(page_title="Sutradara Affiliate Pro", page_icon="🎬")
st.title("🎬 Sutradara Affiliate Pro")
st.write("Kendali Penuh: Naskah -> Validasi -> Prompt Veo/Labs Flow")
st.write("---")

# === STEP 1: FORM INPUT ===
st.subheader("📝 1. Persiapan Syuting")
prod_name = st.text_input("Nama Produk", placeholder="Contoh: Wadah Saji Emas")

col1, col2 = st.columns(2)
with col1:
    foto_produk = st.file_uploader("📸 Foto Produk (WAJIB)", type=['jpg', 'png', 'jpeg'])
with col2:
    foto_model = st.file_uploader("🧍‍♂️ Foto Model (OPSIONAL)", type=['jpg', 'png', 'jpeg'])

vo_gender = st.selectbox("🎙️ Pilihan Voice Over (VO)", ["Suara Wanita (Ceria/Elegan)", "Suara Pria (Enerjik/Wibawa)"])

# Tombol Eksekusi Step 1
if st.button("📝 GENERATE NASKAH (SCENE BY SCENE)"):
    if not prod_name or not foto_produk:
        st.error("Nama Produk dan Foto Produk WAJIB diisi, Bro!")
    else:
        with st.spinner("Gemini lagi nulis naskah..."):
            try:
                # Siapin bahan visual buat Gemini
                content_parts = []
                
                # Cek apakah pakai model atau nggak
                instruksi_model = ""
                if foto_model:
                    instruksi_model = "VIDEO MENGGUNAKAN TALENT/MODEL. Gabungkan interaksi model dengan produk di naskah."
                    img_model = Image.open(foto_model)
                    content_parts.append(img_model) # Kasih liat foto model ke Gemini
                else:
                    instruksi_model = "VIDEO TANPA TALENT. Fokus 100% pada keindahan dan detail produk secara sinematik (B-Roll style)."
                
                img_produk = Image.open(foto_produk)
                content_parts.append(img_produk) # Kasih liat foto produk ke Gemini
                
                # Instruksi Naskah
                prompt_naskah = f"""
                Buat naskah video TikTok pendek jualan produk '{prod_name}'.
                Aturan:
                1. {instruksi_model}
                2. Voice Over menggunakan: {vo_gender}.
                3. Pecah menjadi 3-4 Scene. Format wajib per scene:
                   [SCENE X]
                   Visual: (Jelaskan adegan visualnya)
                   VO: (Apa yang diucapkan)
                   Teks di Layar: (Teks hook)
                """
                content_parts.append(prompt_naskah)
                
                # Panggil Gemini
                res = model_gemini.generate_content(content_parts)
                st.session_state.naskah = res.text
                st.session_state.step = 2 # Lanjut ke mode validasi
                st.rerun() # Refresh layar buat nampilin Step 2
            except Exception as e:
                st.error(f"Gagal bikin naskah: {e}")

# === STEP 2: VALIDASI NASKAH ===
if st.session_state.step >= 2:
    st.write("---")
    st.subheader("🧐 2. Review Naskah")
    st.info(st.session_state.naskah)
    
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        # Tombol Generate Ulang (Ngereset step)
        if st.button("🔁 GENERATE ULANG NASKAH"):
            st.session_state.step = 1
            st.rerun()
            
    with col_btn2:
        # Tombol Lanjut ke Prompt Veo
        if st.button("✨ GENERATE TO PROMPT (VEO / LABS FLOW)"):
            with st.spinner("Meracik Prompt Image & Video..."):
                try:
                    prompt_veo = f"""
                    Berdasarkan naskah ini:
                    {st.session_state.naskah}
                    
                    Buat instruksi teknis (PROMPT) per Scene untuk AI Video Generator (Veo / Labs Flow).
                    Untuk setiap Scene, berikan format ini:
                    
                    **🎬 SCENE X**
                    - **Image Prompt (Bahasa Inggris):** (Prompt sangat detail untuk generate foto awal. Pencahayaan sinematik, kualitas 8k, photorealistic).
                    - **Motion Prompt (Bahasa Inggris):** (Instruksi pergerakan kamera atau objek untuk Veo/Labs. Contoh: Slow pan to left, cinematic zoom in).
                    - **Voice Over & BGM:** (Catatan untuk editor: Kalimat VO '{vo_gender}' dan rekomendasi musik background yang cocok).
                    """
                    res_veo = model_gemini.generate_content(prompt_veo)
                    st.session_state.prompt_veo = res_veo.text
                    st.session_state.step = 3
                    st.rerun()
                except Exception as e:
                    st.error(f"Gagal bikin prompt: {e}")

# === STEP 3: HASIL PROMPT VEO ===
if st.session_state.step == 3:
    st.write("---")
    st.subheader("🚀 3. Prompt Siap Eksekusi (Copy-Paste ke Veo/Labs Flow)")
    st.success(st.session_state.prompt_veo)
    
    if st.button("🔄 Mulai Proyek Baru"):
        st.session_state.step = 1
        st.session_state.naskah = ""
        st.session_state.prompt_veo = ""
        st.rerun()
