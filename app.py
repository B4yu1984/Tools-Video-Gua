import streamlit as st
import google.generativeai as genai
from PIL import Image
import json
import re

# --- 1. SETUP KUNCI & GEMINI ---
try:
    GEMINI_KEY = st.secrets["GEMINI_KEY"]
    genai.configure(api_key=GEMINI_KEY)
    
    models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    target_model = next((m for m in models if 'flash' in m), models[0])
    model_gemini = genai.GenerativeModel(target_model)
except Exception as e:
    st.error(f"Gagal Setup Kunci: {e}")
    st.stop()

# --- Fungsi Pendukung ---
def clean_json_string(json_string):
    json_string = json_string.strip()
    if json_string.startswith("```json"):
        json_string = json_string[7:]
    if json_string.endswith("```"):
        json_string = json_string[:-3]
    return json_string.strip()

def get_background_details(background_name):
    details = {
        "Dapur": "modern, warm kitchen interior with dark oak wood kitchen set, white marble countertop, and a large silver French door refrigerator visible in the left corner.",
        "Pinggir Jalan Kota": "busy, modern city sidewalk with bustling traffic, glass buildings in the background, neon signs, and a green bus stop bench.",
        "Taman": "lush green public park with manicured grass, blooming flowers, tall oak trees, and a wooden bench under soft sunlight.",
        "Studio": "professional photo studio with a clean, smooth grey cyclical background, professional softbox lighting setup visible.",
        "Kamar Tidur": "cozy, clean bedroom interior with a white bed, beige linen, a wooden bedside table with a lamp, and a large window with soft curtains.",
        "Ruang Tamu": "comfortable modern living room with a beige fabric sofa, a dark wood coffee table, a grey rug, and a large bookshelf against a white wall."
    }
    return details.get(background_name, "clean and nice background.")

# --- 2. SETUP STATE MANAGEMENT ---
if 'step' not in st.session_state: st.session_state.step = 1
if 'naskah' not in st.session_state: st.session_state.naskah = ""
if 'prompt_data' not in st.session_state: st.session_state.prompt_data = []
if 'prod_name' not in st.session_state: st.session_state.prod_name = ""
if 'vo_gender' not in st.session_state: st.session_state.vo_gender = ""
if 'pilihan_bg' not in st.session_state: st.session_state.pilihan_bg = ""
if 'aktivitas' not in st.session_state: st.session_state.aktivitas = ""
if 'merk_produk' not in st.session_state: st.session_state.merk_produk = ""
if 'kelebihan_produk' not in st.session_state: st.session_state.kelebihan_produk = ""
if 'gaya_video' not in st.session_state: st.session_state.gaya_video = ""
if 'vo_style' not in st.session_state: st.session_state.vo_style = ""
if 'bg_details' not in st.session_state: st.session_state.bg_details = ""

# --- 3. UI APLIKASI ---
st.set_page_config(page_title="Sutradara Affiliate Pro Ultimate", page_icon="🎬", layout="wide")
st.title("🎬 Sutradara Affiliate Pro Ultimate")
st.write(f"✅ Sistem Aktif: `{target_model}` | 🎧 Fixed Gender & Quote System")
st.write("---")

# === STEP 1: FORM INPUT ===
if st.session_state.step == 1:
    st.subheader("📝 1. Persiapan Syuting (Detail Produk)")
    col_a, col_b = st.columns(2)
    with col_a:
        prod_name = st.text_input("📦 Nama Produk (Wajib)", placeholder="Contoh: Smartwatch")
    with col_b:
        merk_user = st.text_input("🏷️ Merk Produk (Opsional)", placeholder="Contoh: Samsung")

    kelebihan_user = st.text_area("✨ Kelebihan/Fitur Produk (Opsional)")

    st.subheader("🎥 2. Setup Visual & Talent")
    col1, col2 = st.columns(2)
    with col1:
        foto_produk = st.file_uploader("📸 Foto Produk", type=['jpg', 'png', 'jpeg'], accept_multiple_files=True)
    with col2:
        foto_model = st.file_uploader("🧍‍♂️ Foto Model (OPSIONAL)", type=['jpg', 'png', 'jpeg'])

    col3, col4 = st.columns(2)
    with col3:
        pilihan_bg_user = st.selectbox("🖼️ Pilihan Background", ["Dapur", "Pinggir Jalan Kota", "Taman", "Studio", "Kamar Tidur", "Ruang Tamu"])
    with col4:
        aktivitas_user = st.text_input("🏃‍♂️ Aktivitas Talent", placeholder="Contoh: sedang memasak")

    st.subheader("🎙️ 3. Setup Gaya & Audio")
    col5, col6, col7 = st.columns(3)
    with col5:
        gaya_video_user = st.selectbox("🎬 Gaya Video", ["Normal (Hook -> Soft Selling -> CTA)", "Review Produk"])
    with col6:
        vo_gender_user = st.selectbox("👤 Suara VO", ["Wanita (Ceria/Warm)", "Pria (Enerjik/Wibawa)"])
    with col7:
        vo_style_user = st.selectbox("🎭 Style Penyampaian VO", ["Normal", "Story Telling"])

    if st.button("🚀 GENERATE NASKAH"):
        if not prod_name or not foto_produk or not pilihan_bg_user or not aktivitas_user:
            st.error("Lengkapi data wajib!")
        else:
            with st.spinner("Meracik naskah..."):
                try:
                    st.session_state.prod_name = prod_name
                    st.session_state.vo_gender = vo_gender_user
                    st.session_state.pilihan_bg = pilihan_bg_user
                    st.session_state.aktivitas = aktivitas_user
                    st.session_state.merk_produk = merk_user
                    st.session_state.kelebihan_produk = kelebihan_user
                    st.session_state.gaya_video = gaya_video_user
                    st.session_state.vo_style = vo_style_user
                    st.session_state.bg_details = get_background_details(pilihan_bg_user)
                    
                    content_parts = []
                    if foto_model: content_parts.append(Image.open(foto_model))
                    for img_file in foto_produk: content_parts.append(Image.open(img_file))
                        
                    prompt_naskah = f"Buat naskah TikTok {prod_name}. VO {st.session_state.vo_gender}. BG {st.session_state.pilihan_bg}. Aktivitas {st.session_state.aktivitas}. Max 15 kata per scene. Format: [SCENE X], Visual Description, VO, Teks Layar. Pisah per scene dengan '---'."
                    content_parts.append(prompt_naskah)
                    
                    res = model_gemini.generate_content(content_parts)
                    st.session_state.naskah = res.text
                    st.session_state.step = 2 
                    st.rerun() 
                except Exception as e:
                    st.error(f"Error: {e}")

# === STEP 2: VALIDASI ===
if st.session_state.step == 2:
    st.subheader("🧐 2. Review Naskah")
    st.session_state.naskah = st.text_area("Edit Naskah:", st.session_state.naskah, height=300)
    
    if st.button("✨ VALIDASI & RACIK MASTER PROMPT"):
        with st.spinner("Ekstrak data..."):
            try:
                prompt_structure = f"Pecah naskah ini jadi JSON LIST. Pakai single quote untuk teks. Fields: scene, image_prompt, v_scene, v_camera, v_lighting, v_vo. Naskah: {st.session_state.naskah}"
                res_structure = model_gemini.generate_content(prompt_structure)
                st.session_state.prompt_data = json.loads(clean_json_string(res_structure.text))
                st.session_state.step = 3
                st.rerun()
            except:
                st.error("JSON Error, coba klik lagi.")

# === STEP 3: PROMPT FINAL (FIXED GENDER & QUOTE) ===
if st.session_state.step == 3:
    st.subheader("🚀 3. Master Prompt Siap Eksekusi")
    
    # Logika Penentuan Gender (Fix She/He)
    gender_pronoun = "She" if "Wanita" in st.session_state.vo_gender else "He"
    
    export_text = f"🎬 PROYEK: {st.session_state.prod_name}\n\n"
    
    for scene_data in st.session_state.prompt_data:
        s_num = scene_data.get('scene', 'X')
        img_p = scene_data.get('image_prompt', '')
        v_vo = scene_data.get('v_vo', '').replace('"', '').replace("'", "") # Bersihkan dulu
        
        # Rakit Master Prompt Video
        m_v_p = f"Ultra realistic commercial video, vertical 9:16.\n"
        m_v_p += f"Scene: {scene_data.get('v_scene', '')}\n"
        m_v_p += f"Talent Motion: Natural expressions, subtle hand gestures.\n"
        m_v_p += f"Camera: {scene_data.get('v_camera', '')}\n"
        m_v_p += f"Voice over: (Realistic human voice, {st.session_state.vo_gender}, {st.session_state.vo_style} style. {gender_pronoun} says: \"{v_vo}\")\n"
        m_v_p += "High detail, 4K, No subtitles."

        with st.container():
            st.write(f"### SCENE {s_num}")
            st.code(img_p, language="text") # Image
            st.code(m_v_p, language="text") # Video
            st.write("---")
            export_text += f"SCENE {s_num}\n[IMAGE]\n{img_p}\n[VIDEO]\n{m_v_p}\n\n"

    st.download_button("💾 DOWNLOAD (.txt)", export_text, file_name="Prompts.txt")
    if st.button("🔄 Proyek Baru"):
        st.session_state.step = 1
        st.rerun()
