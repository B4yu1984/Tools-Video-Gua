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

# --- Fungsi Pendukung: Bersihkan JSON dari Markdown ---
def clean_json_string(json_string):
    """Membersihkan teks respon AI dari markdown json ```json ... ```"""
    json_string = json_string.strip()
    if json_string.startswith("```json"):
        json_string = json_string[7:]
    if json_string.endswith("```"):
        json_string = json_string[:-3]
    return json_string.strip()

# --- Fungsi Pendukung: Perbaiki Tanda Kutip JSON ---
def fix_json_quotes(json_string):
    """Memperbaiki tanda kutip ganda yang rusak di dalam teks JSON."""
    return json_string.replace('"',"'")

# --- Fungsi Pendukung: Ekstrak JSON dari Teks Raw ---
def extract_json_from_raw(raw_text):
    """Mencoba mengekstrak list JSON valid dari teks acak."""
    try:
        match = re.search(r'\[.*\]', raw_text, re.DOTALL)
        if match:
            return match.group(0)
    except:
        return None
    return None

# --- Fungsi Pendukung: Setup Instruksi Background Spesifik (PENTING!) ---
def get_background_details(background_name):
    """Mengembalikan detail spesifik untuk setiap pilihan background agar konsisten."""
    details = {
        "Dapur": "modern, warm kitchen interior with dark oak wood kitchen set, white marble countertop, and a large silver French door refrigerator visible in the left corner.",
        "Pinggir Jalan Kota": "busy, modern city sidewalk with bustling traffic, glass buildings in the background, neon signs, and a green bus stop bench.",
        "Taman": "lush green public park with manicured grass, blooming flowers, tall oak trees, and a wooden bench under soft sunlight.",
        "Studio": "professional photo studio with a clean, smooth grey cyclical background, professional softbox lighting setup visible.",
        "Kamar Tidur": "cozy, clean bedroom interior with a white bed, beige linen, a wooden bedside table with a lamp, and a large window with soft curtains.",
        "Ruang Tamu": "comfortable modern living room with a beige fabric sofa, a dark wood coffee table, a grey rug, and a large bookshelf against a white wall."
    }
    return details.get(background_name, "clean and nice background.")

# --- 2. SETUP STATE MANAGEMENT (Memori Aplikasi) ---
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
# Tambahin memori buat detail background
if 'bg_details' not in st.session_state: st.session_state.bg_details = ""

# --- 3. UI APLIKASI ---
st.set_page_config(page_title="Sutradara Affiliate Pro Ultimate", page_icon="🎬", layout="wide")
st.title("🎬 Sutradara Affiliate Pro Ultimate")
st.write(f"✅ Sistem Aktif: `{target_model}` | 🎧 Audio Optimizer + 🖼️ Background Locker")
st.write("---")

# === STEP 1: FORM INPUT ===
if st.session_state.step == 1:
    st.subheader("📝 1. Persiapan Syuting (Detail Produk)")
    
    col_a, col_b = st.columns(2)
    with col_a:
        prod_name = st.text_input("📦 Nama Produk (Wajib)", placeholder="Contoh: Smartwatch / Wadah Saji")
    with col_b:
        merk_user = st.text_input("🏷️ Merk Produk (Opsional)", placeholder="Contoh: Samsung / Goto")

    kelebihan_user = st.text_area("✨ Kelebihan/Fitur Produk (Opsional)", placeholder="Tuliskan data valid kelebihan produk di sini...")

    st.subheader("🎥 2. Setup Visual & Talent")
    col1, col2 = st.columns(2)
    with col1:
        foto_produk = st.file_uploader("📸 Foto Produk (WAJIB, BISA BANYAK)", type=['jpg', 'png', 'jpeg'], accept_multiple_files=True)
        if foto_produk: st.success(f"{len(foto_produk)} Foto produk siap!")
    with col2:
        foto_model = st.file_uploader("🧍‍♂️ Foto Model/Talent (OPSIONAL)", type=['jpg', 'png', 'jpeg'])
        if foto_model: st.image(foto_model, caption="Talent Asli", width=150)

    col3, col4 = st.columns(2)
    with col3:
        pilihan_bg_user = st.selectbox("🖼️ Pilihan Background", ["Dapur", "Pinggir Jalan Kota", "Taman", "Studio", "Kamar Tidur", "Ruang Tamu"])
    with col4:
        aktivitas_user = st.text_input("🏃‍♂️ Aktivitas Talent", placeholder="Contoh: joging / sedang memasak / unboxing")

    st.subheader("🎙️ 3. Setup Gaya & Audio")
    col5, col6, col7 = st.columns(3)
    with col5:
        gaya_video_user = st.selectbox("🎬 Gaya Video", ["Normal (Hook -> Soft Selling -> CTA)", "Review Produk (Fokus Cara Pakai & Manfaat)"])
    with col6:
        vo_gender_user = st.selectbox("👤 Suara VO", ["Wanita (Ceria/Warm)", "Pria (Enerjik/Wibawa)"])
    with col7:
        vo_style_user = st.selectbox("🎭 Style Penyampaian VO", ["Normal (Lugas/Promosi)", "Story Telling (Bercerita/Mengalir)"])

    if st.button("🚀 GENERATE NASKAH (SCENE BY SCENE)"):
        if not prod_name or not foto_produk or not pilihan_bg_user or not aktivitas_user:
            st.error("Nama Produk, Foto Produk (minimal 1), Background, dan Aktivitas WAJIB diisi, Bro!")
        else:
            with st.spinner("Sutradara AI lagi ngeracik naskah ultimate lu..."):
                try:
                    st.session_state.prod_name = prod_name
                    st.session_state.vo_gender = vo_gender_user
                    st.session_state.pilihan_bg = pilihan_bg_user
                    st.session_state.aktivitas = aktivitas_user
                    st.session_state.merk_produk = merk_user
                    st.session_state.kelebihan_produk = kelebihan_user
                    st.session_state.gaya_video = gaya_video_user
                    st.session_state.vo_style = vo_style_user
                    # Kunci detail background di memori
                    st.session_state.bg_details = get_background_details(pilihan_bg_user)
                    
                    content_parts = []
                    
                    if foto_model:
                        instruksi_model = f"VIDEO MENGGUNAKAN TALENT. Model akan melakukan aktivitas '{st.session_state.aktivitas}' di background '{st.session_state.pilihan_bg}'."
                        content_parts.append(Image.open(foto_model))
                    else:
                        instruksi_model = f"VIDEO TANPA TALENT. Fokus 100% pada keindahan dan detail produk secara sinematik di background '{st.session_state.pilihan_bg}'."
                    
                    for img_file in foto_produk:
                        content_parts.append(Image.open(img_file))
                        
                    instruksi_merk = f"Pastikan menyebutkan merk '{st.session_state.merk_produk}' secara natural dalam naskah." if st.session_state.merk_produk else "Sebutkan nama produk secara umum."
                    instruksi_kelebihan = f"Gunakan data/fakta berikut sebagai keunggulan utama produk agar tidak berlebihan: {st.session_state.kelebihan_produk}" if st.session_state.kelebihan_produk else "Jelaskan kelebihan produk secara menarik berdasarkan pengamatan visual."
                    
                    if "Review Produk" in st.session_state.gaya_video:
                        struktur_scene = """
                       - SCENE AWAL: Gunakan HOOK yang kuat.
                       - SCENE TENGAH (Fokus Review): Tunjukkan cara pemakaian, demonstrasi, dan tonjolkan manfaat spesifik.
                       - SCENE AKHIR: Call to Action (CTA) yang jelas.
                        """
                    else:
                        struktur_scene = """
                       - SCENE AWAL: Gunakan HOOK yang kuat.
                       - SCENE TENGAH: Basa-basi asik, jelaskan kelebihan produk secara ringan (Soft Selling).
                       - SCENE AKHIR: Call to Action (CTA) yang jelas.
                        """

                    prompt_naskah = f"""
                    Buat naskah video TikTok jualan produk '{prod_name}'.
                    Aturan:
                    1. {instruksi_model}
                    2. {instruksi_merk}
                    3. {instruksi_kelebihan}
                    4. Voice Over menggunakan suara: {st.session_state.vo_gender} dengan gaya penyampaian {st.session_state.vo_style}.
                    5. STRUKTUR NASKAH WAJIB ({st.session_state.gaya_video}):
                       {struktur_scene}
                    6. ATURAN DURASI & SUARA AI (SANGAT PENTING):
                       - Kalimat VO per scene WAJIB PENDEK! Maksimal HANYA 10 hingga 15 KATA per scene.
                       - Jika informasi panjang, PECAH naskah menjadi lebih banyak scene (Bisa 4 hingga 8 Scene). 
                       - Gunakan bahasa lisan yang sangat natural (contoh: tambahkan "Wah", "Eits", "Jujur ya").
                       - WAJIB gunakan tanda elipsis ("...") atau koma (",") di tengah kalimat agar AI pengisi suara mengambil nafas.
                    7. Format wajib per scene (Pisahkan dengan garis '---'):
                       
                       [SCENE X]
                       **Visual Description:** (Jelaskan visualnya, sebutkan background '{st.session_state.pilihan_bg}' & aktivitas '{st.session_state.aktivitas}')
                       **VO:** (Tuliskan kalimat VO maksimal 15 KATA)
                       **Teks di Layar:** (Teks hook/highlight)
                       ---
                    8. ATURAN VISUAL/VIDEO: Hindari adegan interaksi fisik yang rumit pada produk (seperti membuka tutup). Fokus pada pergerakan kamera sinematik, ekspresi, atau gestur menunjuk.
                    """
                    content_parts.append(prompt_naskah)
                    
                    res = model_gemini.generate_content(content_parts)
                    st.session_state.naskah = res.text
                    st.session_state.step = 2 
                    st.rerun() 
                except Exception as e:
                    st.error(f"Gagal bikin naskah: {e}")

# === STEP 2: VALIDASI & SMART EDITOR ===
if st.session_state.step == 2:
    st.write("---")
    st.subheader("🧐 2. Review & Validasi Naskah")
    
    new_naskah = st.text_area("Validasi Naskah Anda (Edit manual jika perlu):", st.session_state.naskah, height=300)
    st.session_state.naskah = new_naskah 
    
    st.markdown("💡 **Smart Editor AI:** Ada adegan yang kurang pas? Kasih instruksi ke AI buat ngerevisi khusus di bagian itu aja.")
    koreksi_adegan = st.text_input("✏️ Koreksi Adegan AI (Opsional)", placeholder="Contoh: Tolong Scene 2 ganti VO-nya jadi lebih ngegas, scene lain biarin aja")
    
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("🔁 REVISI / GENERATE ULANG (AI)"):
            if koreksi_adegan:
                with st.spinner("Gemini lagi ngedit adegan yang lu minta..."):
                    try:
                        prompt_koreksi = f"""
                        Ini adalah naskah video saat ini:
                        {st.session_state.naskah}
                        
                        Tolong revisi naskah tersebut berdasarkan instruksi berikut:
                        "{koreksi_adegan}"
                        
                        Aturan:
                        1. HANYA ubah adegan atau teks yang diminta pada instruksi.
                        2. Pertahankan scene lainnya sama persis.
                        3. PASTIKAN kalimat VO di scene yang direvisi tetap PENDEK (Maksimal 15 kata).
                        4. Tampilkan kembali SELURUH naskah.
                        """
                        res_koreksi = model_gemini.generate_content(prompt_koreksi)
                        st.session_state.naskah = res_koreksi.text
                        st.rerun()
                    except Exception as e:
                        st.error(f"Gagal revisi naskah: {e}")
            else:
                st.session_state.step = 1
                st.session_state.naskah = ""
                st.rerun()
            
    with col_btn2:
        if st.button("✨ VALIDASI NASKAH & RACIK MASTER PROMPT"):
            with st.spinner("Mengekstrak data untuk Master Prompt..."):
                try:
                    # UPDATE PROMPT JSON: Pake Single Quote buat Teks Kalimat biar aman dari error JSON
                    prompt_structure = f"""
                    Berdasarkan naskah draf ini:
                    {st.session_state.naskah}
                    
                    Pecah menjadi data prompt terstruktur.
                    Format output WAJIB berupa LIST JSON yang valid (Tanpa kutip ganda/double quotes di dalam teks kalimat, ganti dengan single quote (') jika perlu).
                    [
                      {{
                        "scene": "1",
                        "image_prompt": "A highly detailed, cinematic studio photograph of {st.session_state.merk_produk} [produk polos description] being held/worn by [model description if any] while performing '{st.session_state.aktivitas}' on a '{st.session_state.bg_details}' background, realistic cinematic lighting, 8k resolution, photorealistic",
                        "v_scene": "Deskripsi singkat visual scene dalam bahasa Inggris, sebutkan detail background '{st.session_state.bg_details}'",
                        "v_camera": "Slow cinematic zoom in towards the product details, smooth motion.",
                        "v_lighting": "Realistic cinematic lighting, bright kitchen interior.",
                        "v_audio": "Realistic ambient room tone",
                        "v_vo": "Masukkan teks VO bahasa Indonesia di sini persis dari naskah"
                      }}
                    ]
                    """
                    res_structure = model_gemini.generate_content(prompt_structure)
                    
                    # Bersihkan markdown json kalau ada
                    clean_json = res_structure.text.strip()
                    if clean_json.startswith("```json"):
                        clean_json = clean_json[7:]
                    if clean_json.endswith("```"):
                        clean_json = clean_json[:-3]
                    
                    st.session_state.prompt_data = json.loads(clean_json.strip())
                    st.session_state.step = 3
                    st.rerun()
                except Exception as e:
                    st.error(f"Gagal bikin prompt terstruktur. Data JSON tidak valid. Silakan klik tombol '✨ VALIDASI NASKAH' sekali lagi.")
                    st.code(res_structure.text)

# === STEP 3: PROMPT FINAL & EXPORT ===
if st.session_state.step == 3:
    st.write("---")
    st.subheader("🚀 3. Prompt Siap Eksekusi (The Masterplan)")
    
    # 1. PERSIAPKAN TEKS UNTUK DI-DOWNLOAD
    export_text = f"🎬 PROYEK: {st.session_state.prod_name}\n"
    export_text += f"🏷️ Merk: {st.session_state.merk_produk}\n"
    export_text += f"=========================================\n\n"
    export_text += f"📜 NASKAH FULL:\n\n{st.session_state.naskah}\n\n"
    export_text += f"=========================================\n"
    export_text += f"🚀 MASTER PROMPT VEO / LABS FLOW:\n\n"
    
    # 2. TAMPILKAN DI LAYAR SEKALIGUS GABUNGKAN KE EXPORT TEXT
    for scene_data in st.session_state.prompt_data:
        s_num = scene_data.get('scene', 'X')
        
        with st.container():
            st.write(f"### 🎬 SCENE {s_num}")
            
            # Image Prompt
            img_prompt = scene_data.get('image_prompt', '')
            st.write("**1️⃣ Copy Image Prompt Ini ke Chat Gemini (Buat Bikin Foto):**")
            st.code(img_prompt, language="text")
            
            # Video Prompt
            v_scene = scene_data.get('v_scene', '')
            v_camera = scene_data.get('v_camera', '')
            v_lighting = scene_data.get('v_lighting', '')
            v_audio = scene_data.get('v_audio', '')
            v_vo = scene_data.get('v_vo', '')
            
            master_video_prompt = f"Ultra realistic commercial video, vertical 9:16.\n\n"
            master_video_prompt += f"Scene: {v_scene}\n\n"
            master_video_prompt += f"Talent Motion: The talent smiles naturally, makes subtle expressive hand gestures while talking, slight head tilt, natural breathing, and relaxed body language. NOT a static pose.\n\n"
            master_video_prompt += f"Camera movement: {v_camera}\n\n"
            master_video_prompt += f"Lighting & FX: {v_lighting}\n\n"
            master_video_prompt += f"Audio & Ambient: {v_audio}\n\n"
            master_video_prompt += f"Voice over: (Extremely realistic human voice, {st.session_state.vo_gender}, {st.session_state.vo_style} style, natural Indonesian accent. Emotionally expressive, dynamic intonation, natural pauses and breaths. NOT robotic or monotonous. She/He says: '{v_vo}')\n\n"
            master_video_prompt += f"High detail, 4K realism, No subtitles, No watermark."
            
            st.write("**2️⃣ Copy Master Video Prompt Ini ke Veo/Labs Flow:**")
            st.code(master_video_prompt, language="text")
            st.write("---")
            
            # Tambahin ke teks export
            export_text += f"--- SCENE {s_num} ---\n"
            export_text += f"[IMAGE PROMPT]\n{img_prompt}\n\n"
            export_text += f"[VIDEO PROMPT]\n{master_video_prompt}\n\n\n"

    # 3. TOMBOL DOWNLOAD DAN RESTART
    col_dl, col_restart = st.columns(2)
    with col_dl:
        file_name_clean = re.sub(r'[^a-zA-Z0-9]', '_', st.session_state.prod_name)
        st.download_button(
            label="💾 DOWNLOAD PROJECT (.txt)",
            data=export_text,
            file_name=f"Project_{file_name_clean}.txt",
            mime="text/plain"
        )
        st.info("💡 Klik tombol di atas biar prompt lu aman di HP kalau aplikasinya ketutup!")
        
    with col_restart:
        if st.button("🔄 Mulai Proyek Baru"):
            st.session_state.step = 1
            st.session_state.naskah = ""
            st.session_state.prompt_data = []
            st.rerun()
