import streamlit as st
import google.generativeai as genai
from PIL import Image
import json

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

# --- 2. SETUP STATE MANAGEMENT (Memori Aplikasi) ---
if 'step' not in st.session_state: st.session_state.step = 1
if 'naskah' not in st.session_state: st.session_state.naskah = ""
if 'prompt_data' not in st.session_state: st.session_state.prompt_data = []

if 'vo_gender' not in st.session_state: st.session_state.vo_gender = ""
if 'pilihan_bg' not in st.session_state: st.session_state.pilihan_bg = ""
if 'aktivitas' not in st.session_state: st.session_state.aktivitas = ""
if 'merk_produk' not in st.session_state: st.session_state.merk_produk = ""
if 'kelebihan_produk' not in st.session_state: st.session_state.kelebihan_produk = ""
if 'gaya_video' not in st.session_state: st.session_state.gaya_video = ""
if 'vo_style' not in st.session_state: st.session_state.vo_style = ""

# --- 3. UI APLIKASI ---
st.set_page_config(page_title="Sutradara Affiliate Pro Ultimate", page_icon="🎬", layout="wide")
st.title("🎬 Sutradara Affiliate Pro Ultimate")
st.write(f"✅ Sistem Aktif: `{target_model}` | 🎧 Audio Optimizer (Anti-Robot)")
st.write("---")

# === STEP 1: FORM INPUT ===
if st.session_state.step == 1:
    st.subheader("📝 1. Persiapan Syuting (Detail Produk)")
    
    col_a, col_b = st.columns(2)
    with col_a:
        prod_name = st.text_input("📦 Nama Produk (Wajib)", placeholder="Contoh: Smartwatch / Wadah Saji")
    with col_b:
        merk_user = st.text_input("🏷️ Merk Produk (Opsional)", placeholder="Contoh: Samsung / Goto (Biar disebut di naskah)")

    kelebihan_user = st.text_area("✨ Kelebihan/Fitur Produk (Opsional)", placeholder="Tuliskan data valid kelebihan produk di sini agar naskah tidak lebay/halu...")

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
                    st.session_state.vo_gender = vo_gender_user
                    st.session_state.pilihan_bg = pilihan_bg_user
                    st.session_state.aktivitas = aktivitas_user
                    st.session_state.merk_produk = merk_user
                    st.session_state.kelebihan_produk = kelebihan_user
                    st.session_state.gaya_video = gaya_video_user
                    st.session_state.vo_style = vo_style_user
                    
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

                    # PERUBAHAN BESAR DI SINI (ATURAN 6: VO & DURASI)
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
                       - AI Video (Veo) HANYA BISA render 8 detik per scene.
                       - Kalimat VO per scene WAJIB PENDEK! Maksimal HANYA 10 hingga 15 KATA per scene (sekitar 5 detik diucapkan).
                       - Jika informasi panjang, PECAH naskah menjadi lebih banyak scene (Bisa 4 hingga 8 Scene). Jangan tumpuk teks di 1 scene!
                       - Gunakan bahasa lisan yang sangat natural (contoh: tambahkan "Wah", "Eits", "Jujur ya").
                       - WAJIB gunakan tanda elipsis ("...") atau koma (",") di tengah kalimat agar AI pengisi suara mengambil nafas dan tidak terdengar seperti robot monoton.
                    7. Format wajib per scene (Pisahkan dengan garis '---'):
                       
                       [SCENE X]
                       **Visual Description:** (Jelaskan visualnya, sebutkan background '{st.session_state.pilihan_bg}' & aktivitas '{st.session_state.aktivitas}')
                       **VO:** (Tuliskan kalimat VO maksimal 15 KATA. Sesuaikan dengan gaya {st.session_state.vo_style})
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
            with st.spinner("Meracik Master Prompt Video & Gambar..."):
                try:
                    # PERUBAHAN PADA INSTRUKSI VEO AUDIO (Lebih Manusiawi)
                    prompt_structure = f"""
                    Berdasarkan naskah draf ini:
                    {st.session_state.naskah}
                    
                    Pecah menjadi data prompt.
                    Format output wajib menggunakan format LIST JSON (Hanya JSON, tanpa teks lain):
                    [
                      {{
                        "scene": "1",
                        "image_prompt": "A highly detailed, cinematic studio photograph of {st.session_state.merk_produk} [produk polos description] being held/worn by [model description if any] while performing '{st.session_state.aktivitas}' on a '{st.session_state.pilihan_bg}' background, realistic cinematic lighting, 8k resolution, photorealistic",
                        "video_prompt": "Ultra realistic commercial video, vertical 9:16.\\n\\nScene: (Deskripsikan visual scene secara presisi bahasa Inggris, sebutkan background '{st.session_state.pilihan_bg}' dan aktivitas '{st.session_state.aktivitas}')\\n\\nTalent Motion: (The talent smiles naturally, makes subtle expressive hand gestures while talking, slight head tilt, natural breathing, and relaxed body language. NOT a static pose.)\\n\\nCamera movement: (Deskripsikan pergerakan kamera misal: Start from right, slowly slide left while zooming in. Smooth cinematic motion, shallow depth of field)\\n\\nLighting & FX: (Deskripsikan lighting)\\n\\nAudio & Ambient: (Deskripsikan background misal: Realistic ambient room tone)\\n\\nVoice over: (Extremely realistic human voice, {st.session_state.vo_gender}, {st.session_state.vo_style} style, natural Indonesian accent. Emotionally expressive, dynamic intonation, natural pauses and breaths. NOT robotic or monotonous. She/He says: '(Masukkan kalimat VO dari naskah di sini. PASTIKAN MASUKKAN TANDA BACA seperti elipsis (...) dan koma (,) agar AI mengambil nafas secara natural)')\\n\\nHigh detail, 4K realism, No subtitles, No watermark."
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

# === STEP 3: PROMPT FINAL ===
if st.session_state.step == 3:
    st.write("---")
    st.subheader("🚀 3. Prompt Siap Eksekusi (The Masterplan)")
    
    for scene_data in st.session_state.prompt_data:
        s_num = scene_data['scene']
        
        with st.container():
            st.write(f"### 🎬 SCENE {s_num}")
            st.write("**1️⃣ Copy Image Prompt Ini ke Chat Gemini (Buat Bikin Foto):**")
            st.code(scene_data['image_prompt'], language="text")
            st.write("**2️⃣ Copy Master Video Prompt Ini ke Veo/Labs Flow:**")
            st.code(scene_data['video_prompt'], language="text")
            st.write("---")

    if st.button("🔄 Mulai Proyek Baru"):
        st.session_state.step = 1
        st.session_state.naskah = ""
        st.session_state.prompt_data = []
        st.rerun()
