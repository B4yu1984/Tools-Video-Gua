import streamlit as st
import google.generativeai as genai
from PIL import Image
import json

# --- 1. SETUP KUNCI & GEMINI ---
try:
    GEMINI_KEY = st.secrets["GEMINI_KEY"]
    genai.configure(api_key=GEMINI_KEY)
    
    # JURUS DETEKTIF: Cari nama model Flash yang bener-bener aktif
    models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    # Gak boleh pake teks manual gemini-1.5-flash, biar gak 404 lagi Bro!
    target_model = next((m for m in models if 'flash' in m), models[0])
    model_gemini = genai.GenerativeModel(target_model)
except Exception as e:
    st.error(f"Gagal Setup Kunci: {e}")
    st.stop()

# --- 2. SETUP STATE MANAGEMENT ---
# Ini kotak memori permanen aplikasi kita
if 'step' not in st.session_state:
    st.session_state.step = 1
if 'naskah' not in st.session_state:
    st.session_state.naskah = ""
if 'prompt_data' not in st.session_state:
    st.session_state.prompt_data = []
# Kita tambahin memori buat VO, BG, dan Aktivitas
if 'vo_gender' not in st.session_state:
    st.session_state.vo_gender = ""
if 'pilihan_bg' not in st.session_state:
    st.session_state.pilihan_bg = ""
if 'aktivitas' not in st.session_state:
    st.session_state.aktivitas = ""

# --- 3. UI APLIKASI ---
# Pake layout wide biar lega
st.set_page_config(page_title="Sutradara Affiliate Pro v3", page_icon="🎬", layout="wide")
st.title("🎬 Sutradara Affiliate Pro v3 (Veo Master + Konteks Pro)")
st.write(f"✅ Sistem Aktif: `{target_model}`")
st.write("Flow Pro: Naskah -> Validasi Teks -> Foto di Gemini Chat -> Animasikan di Veo")
st.write("---")

# === STEP 1: FORM INPUT ===
if st.session_state.step == 1:
    st.subheader("📝 1. Persiapan Syuting")
    prod_name = st.text_input("Nama Produk", placeholder="Contoh: Wadah Saji Emas / Smartwatch Pro")

    col1, col2 = st.columns(2)
    with col1:
        foto_produk = st.file_uploader("📸 Foto Produk Polos (WAJIB)", type=['jpg', 'png', 'jpeg'])
        if foto_produk: st.image(foto_produk, caption="Produk Asli", width=200)
    with col2:
        foto_model = st.file_uploader("🧍‍♂️ Foto Model/Talent (OPSIONAL)", type=['jpg', 'png', 'jpeg'])
        if foto_model: st.image(foto_model, caption="Talent Asli", width=200)

    # BARU: Pilihan Background
    pilihan_bg_user = st.selectbox("🖼️ Pilihan Background", ["Dapur", "Pinggir Jalan Kota", "Taman", "Studio", "Kamar Tidur"])
    
    # BARU: Input Free Text Aktivitas
    aktivitas_user = st.text_input("🏃‍♂️ Aktivitas Talent", placeholder="Contoh: lari atau joging / sedang memasak")

    vo_gender = st.selectbox("🎙️ Pilihan Voice Over (VO)", ["Suara Wanita (Ceria/Warm)", "Suara Pria (Enerjik/Wibawa)"])

    if st.button("📝 GENERATE NASKAH (SCENE BY SCENE)"):
        # Validasi input wajib
        if not prod_name or not foto_produk or not pilihan_bg_user or not aktivitas_user:
            st.error("Nama Produk, Foto Produk, Background, dan Aktivitas WAJIB diisi, Bro!")
        else:
            with st.spinner("Gemini lagi nulis naskah yang nyatu sama konteks..."):
                try:
                    # Simpan pilihan ke dalam memori
                    st.session_state.vo_gender = vo_gender
                    st.session_state.pilihan_bg = pilihan_bg_user
                    st.session_state.aktivitas = aktivitas_user
                    
                    content_parts = []
                    
                    if foto_model:
                        instruksi_model = f"VIDEO MENGGUNAKAN TALENT/MODEL. Gabungkan interaksi model dengan produk. Model akan melakukan aktivitas '{st.session_state.aktivitas}' di background '{st.session_state.pilihan_bg}'."
                        img_model = Image.open(foto_model)
                        content_parts.append(img_model)
                    else:
                        instruksi_model = f"VIDEO TANPA TALENT. Fokus 100% pada keindahan dan detail produk secara sinematik (B-Roll style) di background '{st.session_state.pilihan_bg}'."
                    
                    img_produk = Image.open(foto_produk)
                    content_parts.append(img_produk)
                    
                    # UPDATE Prompt Naskah buat masukin konteks BG & Aktivitas
                    prompt_naskah = f"""
                    Buat naskah video TikTok pendek jualan produk '{prod_name}'.
                    Aturan:
                    1. {instruksi_model}
                    2. Voice Over menggunakan: {st.session_state.vo_gender}.
                    3. STRUKTUR NASKAH WAJIB:
                       - SCENE AWAL: Gunakan HOOK yang kuat (pertanyaan atau pernyataan yang bikin penasaran/relate).
                       - SCENE TENGAH: Basa-basi asik, ceritakan kelebihan produk atau pengalaman menggunakan produk.
                       - SCENE AKHIR: Call to Action (CTA) yang jelas agar penonton segera beli/klik keranjang.
                    4. Pecah menjadi 3-4 Scene. Format wajib per scene (Pisahkan dengan garis '---'):
                       
                       [SCENE X]
                       **Visual Description:** (Jelaskan visualnya detail, sebutkan background '{st.session_state.pilihan_bg}' dan aktivitas '{st.session_state.aktivitas}')
                       **VO:** (Apa yang diucapkan, sesuaikan tone dengan aktivitas. Misal: Ceria saat lari di taman)
                       **Teks di Layar:** (Teks hook/highlight)
                       ---
                    5. ATURAN VISUAL/VIDEO: Hindari adegan interaksi fisik yang rumit pada produk (seperti membuka tutup, menuangkan air, atau mengangkat barang). Fokuskan visual pada: pergerakan kamera sinematik, senyuman/ekspresi talent, atau gestur tangan yang HANYA menunjuk ke arah produk tanpa merubah/menyentuh bentuk fisiknya.
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
        if st.button("🔁 GENERATE ULANG NASKAH (AI)"):
            st.session_state.step = 1
            st.session_state.naskah = ""
            st.rerun()
            
    with col_btn2:
        if st.button("✨ VALIDE NASKAH & RACIK MASTER PROMPT"):
            with st.spinner("Meracik Master Prompt Video & Gambar (SDXL/Veo/Nano Banana 2)..."):
                try:
                    # UPDATE Prompt JSON buat masukin konteks BG & Aktivitas secara mandiri
                    prompt_structure = f"""
                    Berdasarkan naskah draf ini:
                    {st.session_state.naskah}
                    
                    Pecah menjadi data prompt.
                    Format output wajib menggunakan format LIST JSON (Hanya JSON, tanpa teks lain):
                    [
                      {{
                        "scene": "1",
                        "image_prompt": "A highly detailed, cinematic studio photograph of [produk polos description] being held/worn by [model description if any] while performing '{st.session_state.aktivitas}' on a '{st.session_state.pilihan_bg}' background, realistic cinematic lighting (e.g., natural sun for park, softbox for studio), 8k resolution, photorealistic",
                        "video_prompt": "Ultra realistic commercial video, vertical 9:16.\\n\\nScene: (Deskripsikan visual scene secara presisi bahasa Inggris, sebutkan background '{st.session_state.pilihan_bg}' dan aktivitas '{st.session_state.aktivitas}')\\n\\nTalent Motion: (The talent smiles naturally, makes subtle expressive hand gestures while talking, slight head tilt, natural breathing, and relaxed body language. NOT a static pose.)\\n\\nCamera movement: (Deskripsikan pergerakan kamera misal: Start from right, slowly slide left while zooming in. Smooth cinematic motion, shallow depth of field)\\n\\nLighting & FX: (Deskripsikan lighting misal: Natural daylight reflection for park, soft warm light for bedroom)\\n\\nAudio & Ambient: (Deskripsikan background misal: Realistic ambient room tone with park sounds, city noise, or quiet room)\\n\\nVoice over: (Contoh: {st.session_state.vo_gender}, natural Indonesian accent. She/He says calmly/energetically: '(Masukkan kalimat VO dari naskah di sini)')\\n\\nHigh detail, 4K realism, No subtitles, No watermark."
                      }}
                    ]
                    """
                    # JURUS DETEKTIF: Panggil model yang terdeteksi
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
    st.subheader("🚀 3. Prompt Siap Eksekusi (The Masterplan)")
    
    for scene_data in st.session_state.prompt_data:
        s_num = scene_data['scene']
        
        with st.container():
            st.write(f"### 🎬 SCENE {s_num}")
            
            # PROMPT 1: Buat ke Gemini Chat
            st.write("**1️⃣ Copy Image Prompt Ini ke Chat Gemini (Buat Bikin Foto):**")
            st.code(scene_data['image_prompt'], language="text")
            
            # PROMPT 2: Buat ke Veo / Labs Flow
            st.write("**2️⃣ Copy Master Video Prompt Ini ke Veo/Labs Flow:**")
            st.code(scene_data['video_prompt'], language="text")
            
            st.write("---")

    if st.button("🔄 Mulai Proyek Baru"):
        st.session_state.step = 1
        st.session_state.naskah = ""
        st.session_state.prompt_data = []
        st.rerun()
