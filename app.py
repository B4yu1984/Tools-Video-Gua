import streamlit as st
import google.generativeai as genai
from PIL import Image
import json
import re

# --- 1. SETUP KUNCI & GEMINI ---
try:
    GEMINI_KEY = st.secrets["GEMINI_KEY"]
    genai.configure(api_key=GEMINI_KEY)
    
    # Cari model Flash yang aktif secara dinamis
    models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    target_model = next((m for m in models if 'flash' in m), models[0])
    model_gemini = genai.GenerativeModel(target_model)
except Exception as e:
    st.error(f"Gagal Setup Kunci: {e}")
    st.stop()

# --- FUNGSI PENDUKUNG ---
def clean_json_string(json_string):
    """Membersihkan respon AI agar menjadi JSON murni yang bisa diparse"""
    json_string = json_string.strip()
    if json_string.startswith("```json"):
        json_string = json_string[7:]
    if json_string.endswith("```"):
        json_string = json_string[:-3]
    return json_string.strip()

def get_background_details(background_name):
    """Mengunci detail interior agar background tetap konsisten di setiap scene"""
    details = {
        "Dapur": "modern, warm kitchen interior with dark oak wood kitchen set, white marble countertop, and a large silver French door refrigerator visible in the corner.",
        "Pinggir Jalan Kota": "busy, modern city sidewalk with bustling traffic, glass buildings in the background, neon signs, and a green bus stop bench.",
        "Taman": "lush green public park with manicured grass, blooming flowers, tall oak trees, and a wooden bench under soft sunlight.",
        "Studio": "professional photo studio with a clean, smooth grey cyclical background, professional softbox lighting setup visible.",
        "Kamar Tidur": "cozy, clean bedroom interior with a white bed, beige linen, a wooden bedside table with a lamp, and a large window with soft curtains.",
        "Ruang Tamu": "comfortable modern living room with a beige fabric sofa, a dark wood coffee table, a grey rug, and a large bookshelf against a white wall."
    }
    return details.get(background_name, "clean and nice background.")

# --- 2. SETUP STATE MANAGEMENT ---
# Inisialisasi semua memori agar tidak "pikun" saat pindah halaman/step
if 'step' not in st.session_state: st.session_state.step = 1
if 'naskah' not in st.session_state: st.session_state.naskah = ""
if 'prompt_data' not in st.session_state: st.session_state.prompt_data = []

keys = [
    'prod_name', 'merk_produk', 'kelebihan_produk', 'pilihan_bg', 
    'aktivitas', 'gaya_video', 'vo_gender', 'vo_style', 'bg_details'
]
for k in keys:
    if k not in st.session_state: st.session_state[k] = ""

# --- 3. UI APLIKASI ---
st.set_page_config(page_title="Sutradara Affiliate Pro Ultimate", page_icon="🎬", layout="wide")
st.title("🎬 Sutradara Affiliate Pro Ultimate")
st.write(f"✅ Sistem Aktif: `{target_model}` | 💸 Ultimate Cuan Factory")
st.write("---")

# === STEP 1: FORM INPUT (PRA-PRODUKSI) ===
if st.session_state.step == 1:
    st.subheader("📝 1. Persiapan Syuting (Detail Produk & Konteks)")
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.session_state.prod_name = st.text_input("📦 Nama Produk (Wajib)", value=st.session_state.prod_name, placeholder="Contoh: Smartwatch Pro / Air Fryer")
    with col_b:
        st.session_state.merk_produk = st.text_input("🏷️ Merk Produk (Opsional)", value=st.session_state.merk_produk, placeholder="Contoh: Samsung / Gaabor")

    st.session_state.kelebihan_produk = st.text_area("✨ Kelebihan/Fitur Produk (Opsional)", value=st.session_state.kelebihan_produk, placeholder="Tuliskan data valid kelebihan produk di sini...")

    st.subheader("🎥 2. Setup Visual & Talent")
    col1, col2 = st.columns(2)
    with col1:
        # Multiple Upload diaktifkan
        foto_produk = st.file_uploader("📸 Foto Produk (WAJIB, BISA BANYAK)", type=['jpg', 'png', 'jpeg'], accept_multiple_files=True)
        if foto_produk: st.success(f"{len(foto_produk)} Foto produk siap digunakan!")
    with col2:
        foto_model = st.file_uploader("🧍‍♂️ Foto Model/Talent (OPSIONAL)", type=['jpg', 'png', 'jpeg'])
        if foto_model: st.image(foto_model, caption="Talent Asli", width=150)

    col3, col4 = st.columns(2)
    with col3:
        st.session_state.pilihan_bg = st.selectbox("🖼️ Pilihan Background", ["Dapur", "Pinggir Jalan Kota", "Taman", "Studio", "Kamar Tidur", "Ruang Tamu"])
    with col4:
        st.session_state.aktivitas = st.text_input("🏃‍♂️ Aktivitas Talent", value=st.session_state.aktivitas, placeholder="Contoh: sedang joging / sedang unboxing")

    st.subheader("🎙️ 3. Setup Gaya & Audio")
    col5, col6, col7 = st.columns(3)
    with col5:
        st.session_state.gaya_video = st.selectbox("🎬 Gaya Video", ["Normal (Hook -> Soft Selling -> CTA)", "Review Produk (Fokus Cara Pakai & Manfaat)"])
    with col6:
        st.session_state.vo_gender = st.selectbox("👤 Suara VO", ["Wanita (Ceria/Warm)", "Pria (Enerjik/Wibawa)"])
    with col7:
        st.session_state.vo_style = st.selectbox("🎭 Style Penyampaian VO", ["Normal (Lugas/Promosi)", "Story Telling (Bercerita/Mengalir)"])

    if st.button("🚀 GENERATE NASKAH (SCENE BY SCENE)"):
        if not st.session_state.prod_name or not foto_produk or not st.session_state.aktivitas:
            st.error("Nama Produk, Foto Produk, dan Aktivitas WAJIB diisi, Bro!")
        else:
            with st.spinner("Sutradara AI lagi ngeracik naskah ultimate lu..."):
                try:
                    # Kunci detail background berdasarkan pilihan
                    st.session_state.bg_details = get_background_details(st.session_state.pilihan_bg)
                    
                    content_parts = []
                    # Masukkan foto model jika ada
                    if foto_model: content_parts.append(Image.open(foto_model))
                    # Masukkan semua foto produk
                    for img_file in foto_produk: content_parts.append(Image.open(img_file))
                    
                    # Logika instruksi dinamis
                    instruksi_merk = f"Pastikan menyebutkan merk '{st.session_state.merk_produk}' secara natural dalam naskah." if st.session_state.merk_produk else ""
                    instruksi_kelebihan = f"Gunakan data keunggulan produk ini: {st.session_state.kelebihan_produk}" if st.session_state.kelebihan_produk else ""
                    
                    prompt_naskah = f"""
                    Buat naskah video TikTok jualan produk '{st.session_state.prod_name}'.
                    Instruksi Khusus:
                    - {instruksi_merk}
                    - {instruksi_kelebihan}
                    - Gaya Video: {st.session_state.gaya_video}.
                    - Voice Over: {st.session_state.vo_gender} ({st.session_state.vo_style}).
                    - Konteks Visual: Aktivitas '{st.session_state.aktivitas}' di background '{st.session_state.pilihan_bg}'.
                    
                    Aturan Produksi:
                    1. Kalimat VO per scene WAJIB PENDEK (Maksimal 15 KATA per scene).
                    2. Gunakan bahasa lisan natural. WAJIB tambahkan koma (,) atau elipsis (...) untuk jeda napas AI.
                    3. Hindari adegan fisik rumit (seperti buka tutup). Fokus pada kamera sinematik.
                    4. Pecah naskah menjadi 4 hingga 8 Scene jika informasinya padat.
                    
                    Format output wajib (Pisah per scene dengan '---'):
                    [SCENE X]
                    **Visual Description:** (Detail visual scene)
                    **VO:** (Teks yang diucapkan)
                    **Teks di Layar:** (Hook teks)
                    ---
                    """
                    content_parts.append(prompt_naskah)
                    
                    res = model_gemini.generate_content(content_parts)
                    st.session_state.naskah = res.text
                    st.session_state.step = 2 
                    st.rerun() 
                except Exception as e:
                    st.error(f"Gagal bikin naskah: {e}")

# === STEP 2: REVIEW & SMART EDITOR ===
if st.session_state.step == 2:
    st.write("---")
    st.subheader("🧐 2. Review & Smart Editor")
    
    st.session_state.naskah = st.text_area("Validasi Naskah Anda (Edit manual jika perlu):", st.session_state.naskah, height=300)
    
    st.markdown("💡 **Smart Editor AI:** Masukkan instruksi revisi untuk adegan tertentu di sini.")
    koreksi_user = st.text_input("✏️ Koreksi Adegan AI (Opsional)", placeholder="Contoh: Tolong Scene 3 diganti visualnya jadi lebih dramatis...")
    
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("🔁 REVISI / RESET TOTAL"):
            if koreksi_user:
                with st.spinner("Gemini lagi ngedit adegan..."):
                    try:
                        prompt_rev = f"Naskah saat ini:\n{st.session_state.naskah}\n\nInstruksi Revisi: {koreksi_user}. Tampilkan kembali seluruh naskah secara lengkap."
                        res_rev = model_gemini.generate_content(prompt_rev)
                        st.session_state.naskah = res_rev.text
                        st.rerun()
                    except Exception as e:
                        st.error(f"Gagal revisi: {e}")
            else:
                st.session_state.step = 1
                st.rerun()
                
    with col_btn2:
        if st.button("✨ VALIDASI & RACIK MASTER PROMPT"):
            with st.spinner("Mengekstrak data untuk Master Prompt..."):
                try:
                    # Kita minta data potongan agar aman dari JSON Error
                    prompt_struk = f"""
                    Ekstrak naskah berikut menjadi format LIST JSON.
                    Naskah:
                    {st.session_state.naskah}
                    
                    Gunakan format (Hanya JSON, ganti tanda kutip ganda dalam teks dengan single quote):
                    [
                      {{
                        "scene": "X",
                        "image_p": "Detailed studio photo of [product] on {st.session_state.bg_details} background, 8k",
                        "v_desc": "Visual description in English",
                        "v_cam": "Camera movement instruction in English",
                        "v_vo": "Teks VO bahasa Indonesia"
                      }}
                    ]
                    """
                    res_struk = model_gemini.generate_content(prompt_struk)
                    clean_json = clean_json_string(res_struk.text)
                    st.session_state.prompt_data = json.loads(clean_json)
                    st.session_state.step = 3
                    st.rerun()
                except Exception as e:
                    st.error(f"JSON Error: Klik tombol VALIDASI lagi Bro!")
                    st.code(res_struk.text)

# === STEP 3: MASTER PROMPT & EXPORT ===
if st.session_state.step == 3:
    st.write("---")
    st.subheader("🚀 3. Master Prompt Siap Eksekusi")
    
    # Logika Pronoun (She/He)
    gender_tag = "She" if "Wanita" in st.session_state.vo_gender else "He"
    
    # Siapkan data export
    export_content = f"🎬 PROJECT: {st.session_state.prod_name}\n"
    export_content += f"🏷️ BRAND: {st.session_state.merk_produk}\n"
    export_content += "=========================================\n\n"
    export_content += f"📜 NASKAH FULL:\n\n{st.session_state.naskah}\n\n"
    export_content += "=========================================\n"
    export_content += "🚀 MASTER PROMPTS:\n\n"
    
    for d in st.session_state.prompt_data:
        s_idx = d.get('scene', 'X')
        vo_clean = d.get('v_vo', '').replace('"', "'") # Pastikan tidak ada kutip ganda di dalam naskah
        
        # Rakit Image Prompt
        img_prompt_final = f"{d.get('image_p', '')}"
        
        # Rakit Master Video Prompt (Lego System - Anti Crash)
        vid_prompt_final = f"Ultra realistic commercial video, vertical 9:16.\n\n"
        vid_prompt_final += f"Scene: {d.get('v_desc', '')} in {st.session_state.bg_details}\n\n"
        vid_prompt_final += f"Talent Motion: The talent smiles naturally, makes subtle expressive hand gestures while talking, {st.session_state.aktivitas}.\n\n"
        vid_prompt_final += f"Camera movement: {d.get('v_cam', '')}\n\n"
        vid_prompt_final += f"Voice over: (Extremely realistic human voice, {st.session_state.vo_gender}, {st.session_state.vo_style} style. {gender_tag} says: \"{vo_clean}\")\n\n"
        vid_prompt_final += "High detail, 4K realism, No subtitles, No watermark."

        with st.container():
            st.write(f"### 🎬 SCENE {s_idx}")
            st.write("**1️⃣ Copy Image Prompt (Buat Gemini Chat):**")
            st.code(img_prompt_final, language="text")
            st.write("**2️⃣ Copy Master Video Prompt (Buat Veo/Labs Flow):**")
            st.code(vid_prompt_final, language="text")
            st.write("---")
            
            export_content += f"--- SCENE {s_idx} ---\n[IMG]: {img_prompt_final}\n[VID]: {vid_prompt_final}\n\n"

    # Tombol Download & New Project
    c_dl, c_new = st.columns(2)
    with c_dl:
        file_clean = re.sub(r'[^a-zA-Z0-9]', '_', st.session_state.prod_name)
        st.download_button(
            label="💾 DOWNLOAD PROJECT (.txt)",
            data=export_content,
            file_name=f"Project_{file_clean}.txt",
            mime="text/plain"
        )
    with c_new:
        if st.button("🔄 Mulai Proyek Baru"):
            st.session_state.step = 1
            st.session_state.naskah = ""
            st.session_state.prompt_data = []
            st.rerun()
