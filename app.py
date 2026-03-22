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

# --- 2. SETUP STATE MANAGEMENT ---
if 'step' not in st.session_state:
    st.session_state.step = 1
if 'naskah' not in st.session_state:
    st.session_state.naskah = ""
if 'prompt_data' not in st.session_state:
    st.session_state.prompt_data = []
if 'vo_gender' not in st.session_state:
    st.session_state.vo_gender = ""
if 'pilihan_bg' not in st.session_state:
    st.session_state.pilihan_bg = ""
if 'aktivitas' not in st.session_state:
    st.session_state.aktivitas = ""

# --- 3. UI APLIKASI ---
st.set_page_config(page_title="Sutradara Affiliate Pro v4", page_icon="🎬", layout="wide")
st.title("🎬 Sutradara Affiliate Pro v4 (Smart Editor)")
st.write(f"✅ Sistem Aktif: `{target_model}`")
st.write("Flow Pro: Naskah -> Review & Revisi AI -> Foto di Gemini Chat -> Animasikan di Veo")
st.write("---")

# === STEP 1: FORM INPUT ===
if st.session_state.step == 1:
    st.subheader("📝 1. Persiapan Syuting")
    prod_name = st.text_input("Nama Produk", placeholder="Contoh: Smartwatch Pro")

    col1, col2 = st.columns(2)
    with col1:
        foto_produk = st.file_uploader("📸 Foto Produk Polos (WAJIB)", type=['jpg', 'png', 'jpeg'])
        if foto_produk: st.image(foto_produk, caption="Produk Asli", width=200)
    with col2:
        foto_model = st.file_uploader("🧍‍♂️ Foto Model/Talent (OPSIONAL)", type=['jpg', 'png', 'jpeg'])
        if foto_model: st.image(foto_model, caption="Talent Asli", width=200)

    pilihan_bg_user = st.selectbox("🖼️ Pilihan Background", ["Dapur", "Pinggir Jalan Kota", "Taman", "Studio", "Kamar Tidur"])
    aktivitas_user = st.text_input("🏃‍♂️ Aktivitas Talent", placeholder="Contoh: lari atau joging / sedang memasak")
    vo_gender = st.selectbox("🎙️ Pilihan Voice Over (VO)", ["Suara Wanita (Ceria/Warm)", "Suara Pria (Enerjik/Wibawa)"])

    if st.button("📝 GENERATE NASKAH (SCENE BY SCENE)"):
        if not prod_name or not foto_produk or not pilihan_bg_user or not aktivitas_user:
            st.error("Nama Produk, Foto Produk, Background, dan Aktivitas WAJIB diisi, Bro!")
        else:
            with st.spinner("Gemini lagi nulis naskah yang nyatu sama konteks..."):
                try:
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
                       **VO:** (Apa yang diucapkan, sesuaikan tone dengan aktivitas)
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

# === STEP 2: VALIDASI & SMART EDITOR ===
if st.session_state.step == 2:
    st.write("---")
    st.subheader("🧐 2. Review & Validasi Naskah")
    
    # Text area buat edit manual
    new_naskah = st.text_area("Validasi Naskah Anda (Edit manual jika perlu):", st.session_state.naskah, height=300)
    st.session_state.naskah = new_naskah 
    
    st.markdown("💡 **Smart Editor AI:** Ada adegan yang kurang pas? Kasih instruksi ke AI buat ngerevisi khusus di bagian itu aja.")
    # Input Free Text buat koreksi parsial
    koreksi_adegan = st.text_input("✏️ Koreksi Adegan AI (Opsional)", placeholder="Contoh: Tolong Scene 2 ganti VO-nya jadi lebih ngegas, scene lain biarin aja")
    
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("🔁 REVISI / GENERATE ULANG (AI)"):
            if koreksi_adegan:
                # KONDISI 1: User ngisi field koreksi -> Revisi Parsial pakai AI
                with st.spinner("Gemini lagi ngedit adegan yang lu minta..."):
                    try:
                        prompt_koreksi = f"""
                        Ini adalah naskah video saat ini:
                        {st.session_state.naskah}
                        
                        Tolong revisi naskah tersebut berdasarkan instruksi berikut:
                        "{koreksi_adegan}"
                        
                        Aturan:
                        1. HANYA ubah adegan atau teks yang diminta pada instruksi.
                        2. Pertahankan scene lainnya sama persis seperti naskah aslinya.
                        3. Tampilkan kembali SELURUH naskah (dari Scene awal sampai akhir) dengan format yang sama.
                        """
                        res_koreksi = model_gemini.generate_content(prompt_koreksi)
                        st.session_state.naskah = res_koreksi.text
                        st.rerun()
                    except Exception as e:
                        st.error(f"Gagal revisi naskah: {e}")
            else:
                # KONDISI 2: Kosong -> Reset total ke Step 1
                st.session_state.step = 1
                st.session_state.naskah = ""
                st.rerun()
            
    with col_btn2:
        if st.button("✨ VALIDASI NASKAH & RACIK MASTER PROMPT"):
            with st.spinner("Meracik Master Prompt Video & Gambar (Veo/Nano Banana 2)..."):
                try:
                    prompt_structure = f"""
                    Berdasarkan naskah draf ini:
                    {st.session_state.naskah}
                    
                    Pecah menjadi data prompt.
                    Format output wajib menggunakan format LIST JSON (Hanya JSON, tanpa teks lain):
                    [
                      {{
                        "scene": "1",
                        "image_prompt": "A highly detailed, cinematic studio photograph of [produk polos description] being held/worn by [model description if any] while performing '{st.session_state.aktivitas}' on a '{st.session_state.pilihan_bg}' background, realistic cinematic lighting, 8k resolution, photorealistic",
                        "video_prompt": "Ultra realistic commercial video, vertical 9:16.\\n\\nScene: (Deskripsikan visual scene secara presisi bahasa Inggris, sebutkan background '{st.session_state.pilihan_bg}' dan aktivitas '{st.session_state.aktivitas}')\\n\\nTalent Motion: (The talent smiles naturally, makes subtle expressive hand gestures while talking, slight head tilt, natural breathing, and relaxed body language. NOT a static pose.)\\n\\nCamera movement: (Deskripsikan pergerakan kamera misal: Start from right, slowly slide left while zooming in. Smooth cinematic motion, shallow depth of field)\\n\\nLighting & FX: (Deskripsikan lighting)\\n\\nAudio & Ambient: (Deskripsikan background misal: Realistic ambient room tone)\\n\\nVoice over: (Contoh: {st.session_state.vo_gender}, natural Indonesian accent. She/He says calmly/energetically: '(Masukkan kalimat VO dari naskah di sini)')\\n\\nHigh detail, 4K realism, No subtitles, No watermark."
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
