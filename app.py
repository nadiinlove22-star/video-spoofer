import streamlit as st
import os
import subprocess
import json
import tempfile

# Konfigurasi Halaman Utama
st.set_page_config(
    page_title="Video Metadata Suite",
    page_icon="🎬",
    layout="wide"
)

# Custom Styling CSS agar UI menarik dan tidak kosongan
st.markdown("""
    <style>
    .main-header {
        font-size: 2rem;
        color: #FF4B4B;
        font-weight: 700;
        margin-bottom: 0.1rem;
    }
    .sub-header {
        font-size: 1rem;
        color: #6c757d;
        margin-bottom: 1.5rem;
    }
    </style>
""", unsafe_allow_html=True)

# Header Aplikasi
st.markdown('<div class="main-header">🎬 Video Metadata & Forensic Suite</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Upload satu kali: Analisis keaslian video secara objektif dan langsung suntik metadata ala iPhone jika diperlukan.</div>', unsafe_allow_html=True)

# Sidebar untuk Pengaturan Target Metadata iPhone
st.sidebar.header("⚙️ Pengaturan Spoofer iPhone")
device_make = st.sidebar.text_input("Device Make", "Apple")
device_model = st.sidebar.text_input("Device Model", "iPhone 11")
software_ver = st.sidebar.text_input("Software / iOS Version", "18.6.2 (Build 22G90)")
creation_time = st.sidebar.text_input("Creation Time (UTC)", "2026-09-22T06:00:00Z")

# Area Unggah Utama (Hanya 1 kali upload)
uploaded_file = st.file_uploader("📂 Pilih atau Seret File Video (.mp4 / .mov)", type=["mp4", "mov", "mkv", "avi"])

if uploaded_file is not None:
    st.video(uploaded_file)
    st.markdown("---")
    
    # Simpan ke file sementara untuk diproses ffprobe & ffmpeg
    tfile = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
    tfile.write(uploaded_file.read())
    tfile.close()
    
    # 1. Otomatis Jalankan Analisis Forensik di awal
    st.subheader("🔍 Hasil Analisis & Keaslian Video")
    
    cmd_probe = [
        "ffprobe", "-v", "quiet", "-print_format", "json",
        "-show_format", "-show_streams", tfile.name
    ]
    
    try:
        result = subprocess.run(cmd_probe, capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
        
        format_data = data.get("format", {})
        format_tags = format_data.get("tags", {})
        
        make = format_tags.get("com.apple.quicktime.make", format_tags.get("make", "Tidak ada data"))
        model = format_tags.get("com.apple.quicktime.model", format_tags.get("model", "Tidak ada data"))
        encoder = format_tags.get("com.apple.quicktime.software", format_tags.get("encoder", format_tags.get("HANDLER_NAME", "Tidak diketahui")))
        
        # Tampilan Metrik Data Asli
        col1, col2, col3 = st.columns(3)
        col1.metric("Pabrikan (Make)", make)
        col2.metric("Model Perangkat", model)
        col3.metric("Encoder / Software", encoder)
        
        # Kesimpulan Probabilitas Objektif
        make_lower = make.lower()
        model_lower = model.lower()
        encoder_lower = encoder.lower()
        
        if "apple" in make_lower or "iphone" in model_lower:
            st.info("🟢 **Probabilitas Tinggi:** Rekaman asli berasal dari perangkat ekosistem iOS (Apple).")
        elif "tiktok" in encoder_lower or "instagram" in encoder_lower or "fb" in encoder_lower:
            st.warning("🟡 **Probabilitas Sedang:** Terdeteksi string platform media sosial pada bagian encoder/tags.")
        elif make == "Tidak ada data" and model == "Tidak ada data":
            st.info("⚪ **Data Kosong:** Metadata pabrikan tidak ditemukan. Kemungkinan besar video suntingan editor PC, unduhan web bersih, atau file yang dibersihkan metadatanya. *(Tidak cukup bukti untuk melabeli sebagai AI).*")
        else:
            st.info("🔵 **Netral:** Format standar / Tidak ditemukan tanda tangan khusus perangkat atau platform tertentu.")
            
    except Exception as e:
        st.error(f"Gagal membaca struktur file: {e}")

    st.markdown("---")
    
    # 2. Bagian Aksi Penyuntikan Metadata (Tanpa Upload Ulang)
    st.subheader("🚀 Tindakan Penyuntikan Metadata (Spoofing)")
    st.write("Jika ingin mengubah atau menyamarkan metadata video di atas menjadi ala iPhone, klik tombol di bawah ini.")
    
    if st.button("Jalankan Suntik Metadata Sekarang", type="primary"):
        with st.spinner("Sedang memproses penyuntikan metadata..."):
            output_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
            output_file.close()
            
            cmd_spoof = [
                "ffmpeg", "-y", "-i", tfile.name,
                "-metadata", f"com.apple.quicktime.make={device_make}",
                "-metadata", f"com.apple.quicktime.model={device_model}",
                "-metadata", f"com.apple.quicktime.software={software_ver}",
                "-metadata", f"com.apple.quicktime.creationdate={creation_time}",
                "-metadata", f"encoder={software_ver}",
                "-codec", "copy", output_file.name
            ]
            
            try:
                subprocess.run(cmd_spoof, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                st.success("Metadata berhasil disuntikkan!")
                
                with open(output_file.name, "rb") as f:
                    st.download_button(
                        label="📥 Unduh Video Hasil Spoofer",
                        data=f,
                        file_name="video_spoofed_iphone.mp4",
                        mime="video/mp4"
                    )
            except Exception as e:
                st.error(f"Terjadi kesalahan saat memproses video: {e}")
                
    # Bersihkan file temp utama
    if os.path.exists(tfile.name): 
        os.unlink(tfile.name)
    
