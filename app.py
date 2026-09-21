import streamlit as st
import os
import subprocess
import json
import tempfile

st.set_page_config(page_title="Metadata Spoofer Simple", page_icon="📱", layout="centered")

st.title("📱 Simple Media & File Metadata Spoofer")
st.markdown("Pilih jenis file, lihat metadatuanya secara otomatis, lalu putuskan untuk menyuntikkan metadata ala iPhone!")

# Tab kategori file
tab_foto, tab_video, tab_file = st.tabs(["📸 Foto", "🎬 Video", "📁 File Lainnya"])

def process_file_workflow(uploaded_file, file_type_label):
    if uploaded_file is not None:
        tfile = tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1])
        tfile.write(uploaded_file.read())
        file_path = tfile.name
        
        st.info(f"File terpilih: **{uploaded_file.name}**")
        
        # --- 1. OTOMATIS INSPECT ---
        st.subheader("🔍 Hasil Inspeksi Metadata Otomatis")
        try:
            if "Video" in file_type_label or "Foto" in file_type_label:
                cmd_probe = ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", "-show_streams", file_path]
                result = subprocess.run(cmd_probe, capture_output=True, text=True, check=True)
                data = json.loads(result.stdout)
                format_info = data.get("format", {})
                
                st.write(f"- **Format:** {format_info.get('format_long_name', 'N/A')}")
                tags = format_info.get("tags", {})
                if tags:
                    st.json(tags)
                else:
                    st.info("Metadata bawaan bersih / kosong.")
            else:
                st.write("File umum dipilih. Siap untuk disuntik metadata.")
        except Exception as e:
            st.warning(f"Gagal membaca detail metadata mendalam: {e}")
            
        st.markdown("---")
        
        # --- 2. KEPUTUSAN / AKSI SPOOF ---
        st.subheader("🛠️ Keputusan Modifikasi")
        action_choice = st.radio(
            "Apakah Anda ingin mengubah/menyuntik metadata file ini?",
            ("Tidak (Biarkan Asli)", "Ya, Ubah Jadi Super Detail (Ala iPhone)")
        )
        
        if action_choice == "Ya, Ubah Jadi Super Detail (Ala iPhone)":
            if st.button("Jalankan Penyuntikan Metadata"):
                output_path = file_path + "_spoofed" + os.path.splitext(uploaded_file.name)[1]
                with st.spinner("Sedang memproses dan menyuntik metadata..."):
                    try:
                        cmd_spoof = [
                            "ffmpeg", "-y", "-i", file_path,
                            "-metadata", "major_brand=qt  ",
                            "-metadata", "minor_version=0",
                            "-metadata", "compatible_brands=qt  ",
                            "-metadata", "artist=Apple",
                            "-metadata", "encoder=Apple QuickTime",
                            "-metadata", "make=Apple",
                            "-metadata", "model=iPhone 11",
                            "-metadata", "software=18.6.2",
                            "-metadata", "location=-7.7956,110.3695,133.1",
                            "-c:v", "libx264", "-crf", "15", "-preset", "slow",
                            "-c:a", "copy",
                            output_path
                        ]
                        subprocess.run(cmd_spoof, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        st.success("Berhasil! Metadata berhasil disuntikkan.")
                        
                        with open(output_path, "rb") as f:
                            st.download_button(
                                label="📥 Download File Hasil Modifikasi",
                                data=f,
                                file_name=f"spoofed_{uploaded_file.name}",
                                mime="application/octet-stream"
                            )
                    except Exception as e:
                        st.error(f"Terjadi kesalahan saat memproses: {e}")

with tab_foto:
    st.subheader("Pilih File Foto")
    up_foto = st.file_uploader("Upload foto:", type=["jpg", "jpeg", "png", "heic"], key="foto")
    process_file_workflow(up_foto, "Foto")

with tab_video:
    st.subheader("Pilih File Video")
    up_video = st.file_uploader("Upload video:", type=["mp4", "mov", "avi", "mkv"], key="video")
    process_file_workflow(up_video, "Video")

with tab_file:
    st.subheader("Pilih File Lainnya")
    up_file = st.file_uploader("Upload file:", type=["zip", "pdf", "docx", "mp3"], key="file")
    process_file_workflow(up_file, "File")
