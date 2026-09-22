import streamlit as st
import os
import subprocess
import json
import tempfile

# Konfigurasi Halaman Utama
st.set_page_config(
    page_title="Video Metadata & Forensic Suite Pro",
    page_icon="🎬",
    layout="wide"
)

PRESET_FILE = "metadata_presets_lossless.json"

def load_presets():
    if os.path.exists(PRESET_FILE):
        try:
            with open(PRESET_FILE, "r") as f:
                return json.load(f)
        except:
            pass
    return {}

def save_presets(presets):
    with open(PRESET_FILE, "w") as f:
        json.dump(presets, f, indent=4)

if "preset_list" not in st.session_state:
    st.session_state.preset_list = load_presets()

# Header Aplikasi
st.markdown("<h2>🎬 Video Forensic & iPhone Re-Encoder Suite</h2>", unsafe_allow_html=True)
st.markdown("<p style='color: #adb5bd;'>Ekstraksi metadata total, analisis visual, & Transcoding replika forensik identik ala iPhone.</p>", unsafe_allow_html=True)

# --- UPLOAD VIDEO SUMBER (TEMPLATE & ANALISIS) ---
st.subheader("1️⃣ Ekstraksi & Analisis Total dari Video Sumber (iPhone Asli)")
uploaded_source = st.file_uploader("📂 Unggah Video Sumber (Template iPhone Asli)", type=["mp4", "mov", "mkv", "avi"], key="source_uploader")

if uploaded_source is not None:
    col_vsrc1, col_vsrc2 = st.columns([1, 1])
    with col_vsrc1:
        st.video(uploaded_source)
        
    src_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
    src_file.write(uploaded_source.read())
    src_file.close()
    
    cmd_probe = [
        "ffprobe", "-v", "quiet", "-print_format", "json",
        "-show_format", "-show_streams", src_file.name
    ]
    
    try:
        res = subprocess.run(cmd_probe, capture_output=True, text=True, check=True)
        probe_data = json.loads(res.stdout)
        
        format_data = probe_data.get("format", {})
        format_tags = format_data.get("tags", {})
        streams_data = probe_data.get("streams", [])
        
        master_metadata = format_tags.copy()
        for idx, s in enumerate(streams_data):
            s_tags = s.get("tags", {})
            for k, v in s_tags.items():
                master_metadata[f"stream_{idx}_{k}"] = v

        with col_vsrc2:
            st.markdown("### 📊 Ringkasan Analisis File Sumber")
            st.write(f"**Format Kontainer:** {format_data.get('format_long_name', 'N/A')}")
            st.write(f"**Durasi:** {float(format_data.get('duration', 0)):.2f} detik")
            st.write(f"**Total Atribut Metadata:** {len(master_metadata)} ditemukan")
            
            st.markdown("---")
            preset_name_input = st.text_input("Nama Preset Master", value="iPhone_Identical_Profile", key="preset_input_name")
            
            if st.button("📥 Simpan Profil Ini ke List Preset", type="secondary"):
                st.session_state.preset_list[preset_name_input] = {
                    "format_tags": format_tags,
                    "streams_tags": [s.get("tags", {}) for s in streams_data],
                    "raw_dump": master_metadata
                }
                save_presets(st.session_state.preset_list)
                st.success(f"Profil '{preset_name_input}' berhasil disimpan!")
                st.rerun()
                
        with st.expander("🔍 Lihat Seluruh Raw Metadata Master (JSON)"):
            st.json(master_metadata)
            
        if os.path.exists(src_file.name):
            os.unlink(src_file.name)
            
    except Exception as e:
        st.error(f"Gagal memproses ekstraksi: {e}")

st.markdown("---")

# --- UPLOAD VIDEO TARGET & RE-ENCODE IDENTIK ---
st.subheader("2️⃣ Re-Encode & Suntik Identik ke Video Target")
st.write("Video target akan di-transcode ulang agar struktur stream, codec, dan metadatanya menyerupai karakteristik rekam hardware iPhone.")

uploaded_target = st.file_uploader("📂 Unggah Video Target yang Mau Dipalsukan", type=["mp4", "mov", "mkv", "avi"], key="target_uploader")

if uploaded_target is not None:
    current_presets = list(st.session_state.preset_list.keys())
    
    if not current_presets:
        st.warning("⚠️ Belum ada profil master. Silakan unggah video sumber iPhone asli di langkah 1 terlebih dahulu.")
    else:
        chosen_profile = st.selectbox("🎯 Pilih Profil Master Rujukan", current_presets)
        
        render_mode = st.radio(
            "⚙️ Pilih Mode Pemrosesan Target:",
            [
                "Identik Forensik (Re-Encode H.264 High Profile ala Apple - Menghilangkan jejak editor/PC)",
                "Salin Cepat (Hanya Suntik Tag / Tanpa Re-encode - Cepat tapi jejak stream asli tetap tertinggal)"
            ]
        )
        
        tgt_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
        tgt_file.write(uploaded_target.read())
        tgt_file.close()
        
        if st.button("🚀 Mulai Proses Pembuatan Video Identik", type="primary"):
            # Menggunakan spinner dengan status yang jelas agar pengguna tahu proses sedang berjalan
            with st.spinner("⏳ Sedang melakukan transcoding video & menyuntikkan metadata... Mohon tunggu, proses ini memakan waktu beberapa saat tergantung ukuran video."):
                output_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mov')
                output_file.close()
                
                profile_data = st.session_state.preset_list[chosen_profile]
                f_tags = profile_data.get("format_tags", {})
                s_tags_list = profile_data.get("streams_tags", [])
                
                if "Identik Forensik" in render_mode:
                    ffmpeg_cmd = [
                        "ffmpeg", "-y", "-i", tgt_file.name,
                        "-c:v", "libx264", "-profile:v", "high", "-level", "4.2",
                        "-pix_fmt", "yuv420p", "-crf", "18", "-preset", "medium",
                        "-c:a", "aac", "-b:a", "192k",
                        "-movflags", "+use_metadata_tags+faststart",
                        "-map_metadata", "0"
                    ]
                else:
                    ffmpeg_cmd = [
                        "ffmpeg", "-y", "-i", tgt_file.name,
                        "-movflags", "+use_metadata_tags",
                        "-map_metadata", "0",
                        "-codec", "copy"
                    ]
                
                for k, v in f_tags.items():
                    ffmpeg_cmd.extend(["-metadata", f"{k}={v}"])
                    
                for idx, st_tags in enumerate(s_tags_list):
                    for sk, sv in st_tags.items():
                        ffmpeg_cmd.extend([f"-metadata:s:{idx}", f"{sk}={sv}"])
                
                ffmpeg_cmd.append(output_file.name)
                
                try:
                    subprocess.run(ffmpeg_cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    st.success("✅ Pembuatan video identik selesai!")
                    
                    cmd_verify = [
                        "ffprobe", "-v", "quiet", "-print_format", "json",
                        "-show_format", "-show_streams", output_file.name
                    ]
                    v_res = subprocess.run(cmd_verify, capture_output=True, text=True, check=True)
                    v_data = json.loads(v_res.stdout)
                    
                    st.markdown("### 🔍 Verifikasi Metadata Final")
                    v_format_tags = v_data.get("format", {}).get("tags", {})
                    st.json(v_format_tags)
                    
                    with open(output_file.name, "rb") as f:
                        st.download_button(
                            label="📥 Unduh Video Hasil Re-Encode Identik (.mov)",
                            data=f,
                            file_name="video_forensic_identical.mov",
                            mime="video/quicktime",
                            type="primary"
                        )
                        
                except Exception as e:
                    st.error(f"Gagal menjalankan FFmpeg: {e}")
                    
        if os.path.exists(tgt_file.name):
            os.unlink(tgt_file.name)
            
