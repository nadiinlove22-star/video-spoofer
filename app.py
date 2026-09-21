import streamlit as st
import os
import subprocess
import json
import tempfile

# Konfigurasi Halaman Utama
st.set_page_config(
    page_title="Video Metadata Spoofer & Forensic",
    page_icon="🎬",
    layout="wide"
)

# Custom Styling CSS agar UI tidak kosongan dan lebih menarik
st.markdown("""
    <style>
    .main-header {
        font-size: 2.2rem;
        color: #FF4B4B;
        font-weight: 700;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #6c757d;
        margin-bottom: 2rem;
    }
    .stAlert {
        border-radius: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# Header Aplikasi
st.markdown('<div class="main-header">🎬 Video Metadata Spoofer & Forensic Suite</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Suntik metadata super detail ala iPhone secara presisi dan analisis keaslian video berbasis data objektif.</div>', unsafe_allow_html=True)

# Sidebar untuk Pengaturan Metadata iPhone
st.sidebar.header("⚙️ Konfigurasi Metadata iPhone")
st.sidebar.info("Atur parameter perangkat di bawah ini untuk disuntikkan ke dalam video target.")

device_make = st.sidebar.text_input("Device Make", "Apple")
device_model = st.sidebar.text_input("Device Model", "iPhone 11")
software_ver = st.sidebar.text_input("Software / iOS Version", "18.6.2 (Build 22G90)")
creation_time = st.sidebar.text_input("Creation Time (UTC)", "2026-09-22T06:00:00Z")

# Tab Utama
tab1, tab2 = st.tabs(["🚀 Suntik Metadata (Spoofer)", "🔍 Analisis Forensik Video"])

with tab1:
    st.subheader("Penyuntikan Metadata Video")
    st.write("Unggah video target, lalu jalankan proses penyuntikan metadata perangkat secara instan.")
    
    uploaded_file_spoof = st.file_uploader("Pilih file video (.mp4 / .mov)", type=["mp4", "mov"], key="spoof")
    
    if uploaded_file_spoof is not None:
        st.video(uploaded_file_spoof)
        
        if st.button("Jalankan Penyuntikan Metadata", type="primary"):
            with st.spinner("Sedang memproses metadata video..."):
                # Simpan file sementara
                tfile = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
                tfile.write(uploaded_file_spoof.read())
                tfile.close()
                
                output_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
                output_file.close()
                
                # Perintah FFmpeg untuk menyuntikkan metadata
                cmd = [
                    "ffmpeg", "-y", "-i", tfile.name,
                    "-metadata", f"com.apple.quicktime.make={device_make}",
                    "-metadata", f"com.apple.quicktime.model={device_model}",
                    "-metadata", f"com.apple.quicktime.software={software_ver}",
                    "-metadata", f"com.apple.quicktime.creationdate={creation_time}",
                    "-metadata", f"encoder={software_ver}",
                    "-codec", "copy", output_file.name
                ]
                
                try:
                    subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    st.success("Metadata berhasil disuntikkan dengan sukses!")
                    
                    with open(output_file.name, "rb") as f:
                        st.download_button(
                            label="📥 Unduh Video Hasil Spoofer",
                            data=f,
                            file_name="video_spoofed_iphone.mp4",
                            mime="video/mp4"
                        )
                except Exception as e:
                    st.error(f"Terjadi kesalahan saat memproses video: {e}")
                finally:
                    # Bersihkan file temp
                    if os.path.exists(tfile.name): os.unlink(tfile.name)

with tab2:
    st.subheader("Analisis Asal-Usul & Keaslian Video (Data-Driven)")
    st.write("Periksa struktur metadata file secara objektif tanpa asumsi atau tebakan liar.")
    
    uploaded_file_forensic = st.file_uploader("Pilih file video untuk dianalisis", type=["mp4", "mov", "mkv", "avi"], key="forensic")
    
    if uploaded_file_forensic is not None:
        st.video(uploaded_file_forensic)
        
        if st.button("Mulai Analisis Forensik", type="primary"):
            with st.spinner("Mengekstrak struktur stream dan format tags..."):
                tfile = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
                tfile.write(uploaded_file_forensic.read())
                tfile.close()
                
                cmd_probe = [
                    "ffprobe", "-v", "quiet", "-print_format", "json",
                    "-show_format", "-show_streams", tfile.name
                ]
                
                try:
                    result = subprocess.run(cmd_probe, capture_output=True, text=True, check=True)
                    data = json.loads(result.stdout)
                    
                    format_data = data.get("format", {})
                    format_tags = format_data.get("tags", {})
                    
                    # Ekstraksi informasi penting
                    make = format_tags.get("com.apple.quicktime.make", format_tags.get("make", "Tidak ada data"))
                    model = format_tags.get("com.apple.quicktime.model", format_tags.get("model", "Tidak ada data"))
                    encoder = format_tags.get("com.apple.quicktime.software", format_tags.get("encoder", format_tags.get("HANDLER_NAME", "Tidak diketahui")))
                    
                    # Tampilan Metrik Hasil
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Pabrikan (Make)", make)
                    col2.metric("Model Perangkat", model)
                    col3.metric("Encoder / Software", encoder)
                    
                    st.markdown("---")
                    st.markdown("### 📋 Kesimpulan Analisis Probabilitas Objektif")
                    
                    # Logika Probabilitas Jujur Berbasis Data
                    make_lower = make.lower()
                    model_lower = model.lower()
                    encoder_lower = encoder.lower()
                    
                    if "apple" in make_lower or "iphone" in model_lower:
                        st.info("🟢 **Probabilitas Tinggi:** Rekaman asli berasal dari perangkat ekosistem iOS (Apple).")
                    elif "tiktok" in encoder_lower or "instagram" in encoder_lower or "fb" in encoder_lower:
                        st.warning("🟡 **Probabilitas Sedang:** Terdeteksi string platform media sosial pada bagian encoder/tags.")
                    elif make == "Tidak ada data" and model == "Tidak ada data":
                        st.info("⚪ **Data Kosong:** Metadata pabrikan tidak ditemukan. Kemungkinan besar video suntingan editor PC, unduhan web bersih, atau file yang telah dibersihkan metadatanya. *(Tidak cukup bukti untuk melabeli sebagai AI).*")
                    else:
                        st.info("🔵 **Netral:** Format standar / Tidak ditemukan tanda tangan khusus perangkat atau platform tertentu.")
                        
                except Exception as e:
                    st.error(f"Gagal membaca struktur file: {e}")
                finally:
                    if os.path.exists(tfile.name): os.unlink(tfile.name)
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
