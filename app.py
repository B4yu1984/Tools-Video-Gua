import streamlit as st
import google.generativeai as genai
from PIL import Image
import json

# --- 1. SETUP KUNCI & GEMINI ---
try:
    GEMINI_KEY = st.secrets["GEMINI_KEY"]
    genai.configure(api_key=GEMINI_KEY)
    
    # Deteksi model paling optimal
    models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    target_model = next((m for m in models if 'flash' in m), models[0])
    model_gemini = genai.GenerativeModel(target_model)
except Exception as e:
    st.error(f"Gagal Setup Kunci: {e}")
    st.stop()

# --- 2. SETUP STATE MANAGEMENT ---
if 'step' not in st.session_state:
    st.session_state.step = 1
if 'naskah' not in st.session_state:
    st.session_state.naskah = ""
if 'prompt_data' not in st.session_state:
    st.session_state.prompt_data = []

# --- 3. UI APLIKASI ---
st.set_page_config(page_title="Sutradara Affiliate Pro", page_icon="🎬", layout="wide")
st.title("🎬 Sutradara Affiliate Pro")
st.write("Flow: Naskah -> Validasi Teks -> Copas Prompt ke Gemini Chat -> Animasikan di Veo")
st.write("---")

# === STEP 1: FORM INPUT ===
if st.session_state.step == 1:
    st.subheader("📝 1. Persiapan Syuting")
    prod_name = st.text_input("Nama Produk", placeholder="Contoh: Wadah Saji Emas")

    col1, col2 = st.columns(2)
    with col1:
        foto_produk = st.file_uploader("📸 Foto Produk Polos (WAJIB)", type=['jpg', 'png', 'jpeg'])
        if foto_produk: st.image(foto_produk, caption="Produk Asli", width=200)
    with col2:
        foto_model = st.file_uploader("🧍‍♂️ Foto Model/Talent (OPSIONAL)", type=['jpg', 'png', 'jpeg'])
        if foto_model: st.image(foto_model, caption="Talent Asli", width=200)

    vo_gender = st.selectbox("🎙️ Pilihan Voice Over (VO)", ["Suara Wanita (Ceria/Elegan)", "Suara Pria (Enerjik/Wibawa)"])

    if st.button("📝 GENERATE NASKAH (SCENE BY SCENE)"):
        if not prod_name or not foto_produk:
            st.error("Nama Produk dan Foto Produk WAJIB diisi, Bro!")
        else:
            with st.spinner("Gemini lagi nulis naskah..."):
                try:
                    content_parts = []
                    
                    if foto_model:
                        instruksi_model = "VIDEO MENGGUNAKAN TALENT/MODEL. Gabungkan interaksi model dengan produk."
                        img_model = Image.open(foto_model)
                        content_parts.append(img_model)
                    else:
                        instruksi_model = "VIDEO TANPA TALENT. Fokus 100% pada keindahan produk (B-Roll style)."
                    
                    img_produk = Image.open(foto_produk)
                    content_parts.append(img_produk)
                    
                    prompt_naskah = f"""
                    Buat naskah video TikTok pendek jualan produk '{prod_name}'.
                    Aturan:
                    1. {instruksi_model}
                    2. Voice Over menggunakan: {vo_gender}.
                    3. Pecah menjadi 3-4 Scene. Format wajib per scene (Pisahkan dengan garis '---'):
                       
                       [SCENE X]
                       **Visual Description:** (Jelaskan visualnya sangat detail)
                       **VO:** (Apa yang diucapkan)
                       **Teks di Layar:** (Teks hook)
                       ---
                    """
                    content_parts.append(prompt_naskah)
                    
                    res = model_gemini.generate_content(content_parts)
                    st.session_state.naskah = res.text
                    st.session_state.step = 2 
                    st.rerun() 
                except Exception as e:
                    st.error(f"Gagal bikin naskah: {e}")

# === STEP 2: VALIDASI NASKAH ===
if st.session_state.step == 2:
    st.write("---")
    st.subheader("🧐 2. Review & Validasi Naskah")
    new_naskah = st.text_area("Validasi Naskah Anda (Edit jika perlu):", st.session_state.naskah, height=300)
    st.session_state.naskah = new_naskah 
    
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("🔁 GENERATE ULANG NASKAH"):
            st.session_state.step = 1
            st.session_state.naskah = ""
            st.rerun()
            
    with col_btn2:
        if st.button("✨ VALIDE NASKAH & RACIK PROMPT"):
            with st.spinner("Meracik Prompt Gambar & Gerakan..."):
                try:
                    prompt_structure = f"""
                    Berdasarkan naskah draf ini:
                    {st.session_state.naskah}
                    
                    Pecah menjadi data prompt.
                    Format output wajib menggunakan format LIST JSON (Hanya JSON, tanpa teks lain):
                    [
                      {{
                        "scene": "1",
                        "image_prompt": "A highly detailed, cinematic studio photograph of [produk] being held by [model if any] in a luxurious setting, 8k resolution, photorealistic",
                        "motion_prompt": "Cinematic slow zoom in towards the product details, soft focus background"
                      }}
                    ]
                    """
                    res_structure = model_gemini.generate_content(prompt_structure)
                    clean_json = res_structure.text.replace("```json", "").replace("```", "").strip()
                    st.session_state.prompt_data = json.loads(clean_json)
                    st.session_state.step = 3
                    st.rerun()
                except Exception as e:
                    st.error(f"Gagal bikin prompt terstruktur: {e}")

# === STEP 3: PROMPT FINAL (SIAP COPY-PASTE) ===
if st.session_state.step == 3:
    st.write("---")
    st.subheader("🚀 3. Prompt Siap Eksekusi")
    st.warning("👉 Copy 'Image Prompt' di bawah ini, lalu paste ke chat Gemini (AI Plus) lu buat generate gambarnya!")
    
    for scene_data in st.session_state.prompt_data:
        s_num = scene_data['scene']
        
        with st.container():
            st.write(f"### 🎬 SCENE {s_num}")
            st.write("**🎨 Copy Prompt Gambar Ini ke Gemini:**")
            st.code(scene_data['image_prompt'], language="text")
            
            st.write("**🎥 Prompt Gerakan buat di Veo:**")
            st.success(scene_data['motion_prompt'])
            st.write("---")

    if st.button("🔄 Mulai Proyek Baru"):
        st.session_state.step = 1
        st.session_state.naskah = ""
        st.session_state.prompt_data = []
        st.rerun()
