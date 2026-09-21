import streamlit as st
import os
import subprocess
import json
import tempfile

st.set_page_config(page_title="Video Metadata Spoofer", page_icon="🎬", layout="centered")

st.title("🎬 Video Metadata Spoofer & Inspector")
st.markdown("Ubah metadata video agar aman dari deteksi algoritma TikTok/Shopee!")

menu = st.tabs(["🔍 1. Inspector (Cek Metadata)", "🛠️ 2. Spoofer (Ubah Metadata)"])

with menu[0]:
    st.subheader("Pemeriksa Metadata Video")
    uploaded_file_inspect = st.file_uploader("Upload video untuk dicek:", type=["mp4", "mov", "avi", "mkv"], key="inspect")

    if uploaded_file_inspect is not None:
        tfile = tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file_inspect.name)[1])
        tfile.write(uploaded_file_inspect.read())
        video_path = tfile.name

        if st.button("Mulai Analisis"):
            with st.spinner("Membongkar metadata..."):
                cmd = ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", "-show_streams", video_path]
                try:
                    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                    data = json.loads(result.stdout)
                    format_info = data.get("format", {})
                    st.success("Selesai!")
                    st.write(f"- **Format:** {format_info.get('format_long_name', 'N/A')}")
                    tags = format_info.get("tags", {})
                    if tags:
                        st.json(tags)
                    else:
                        st.info("Global tags kosong/bersih.")
                except Exception as e:
                    st.error(f"Error: {e}")

with menu[1]:
    st.subheader("Penyuntik Metadata (Apple QuickTime Spoofer)")
    uploaded_file_spoof = st.file_uploader("Upload video target:", type=["mp4", "mov", "avi", "mkv"], key="spoof")

    if uploaded_file_spoof is not None:
        tfile = tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file_spoof.name)[1])
        tfile.write(uploaded_file_spoof.read())
        input_path = tfile.name
        output_path = input_path + "_original_like.mp4"

        if st.button("Proses & Suntik Metadata"):
            with st.spinner("Sedang memproses video..."):
                cmd = [
                    "ffmpeg", "-y", "-i", input_path,
                    "-metadata", "major_brand=qt  ",
                    "-metadata", "minor_version=512",
                    "-metadata", "compatible_brands=qt  isom",
                    "-metadata", "artist=Mobile User",
                    "-metadata", "encoder=Apple QuickTime",
                    "-metadata", "comment=Captured via Smartphone",
                    "-c:v", "libx264", "-crf", "22", "-preset", "medium",
                    "-c:a", "aac", "-b:a", "192k",
                    output_path
                ]
                try:
                    subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    st.success("Berhasil! Silakan download video hasil modifikasi:")
                    with open(output_path, "rb") as f:
                        st.download_button(
                            label="📥 Download Video Aman",
                            data=f,
                            file_name="video_aman.mp4",
                            mime="video/mp4"
                        )
                except Exception as e:
                    st.error(f"Gagal: {e}")
                  
