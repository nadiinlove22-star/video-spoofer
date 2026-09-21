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
    
    # 1. Otomatis Jalankan Analisis Forensik Mendalam
    st.subheader("🔍 Hasil Analisis & Keaslian Video")
    
    cmd_probe = [
        "ffprobe", "-v", "quiet", "-print_format", "json",
        "-show_format", "-show_streams", tfile.name
    ]
    
    try:
        result = subprocess.run(cmd_probe, capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
        
        format_data = data.get("format", {})
        format_tags = format_data.get("format_tags", format_data.get("tags", {}))
        streams = data.get("streams", [])
        
        # Fungsi pembantu untuk mencari tag dari berbagai kemungkinan lokasi
        def find_tag(keys):
            # Cek di format tags utama
            for k in keys:
                if k in format_tags:
                    return format_tags[k]
            # Cek di setiap stream tags (video/audio stream)
            for stream in streams:
                st_tags = stream.get("tags", {})
                for k in keys:
                    if k in st_tags:
                        return st_tags[k]
            return "Tidak ada data"

        # Pencarian multi-lapis untuk akurasi tinggi
        make = find_tag(["com.apple.quicktime.make", "make", "manufacturer", "brand"])
        model = find_tag(["com.apple.quicktime.model", "model", "device_model"])
        encoder = find_tag(["com.apple.quicktime.software", "encoder", "HANDLER_NAME", "handler_name", "software", "creation_tool"])
        
        # Tampilan Metrik Data Asli
        col1, col2, col3 = st.columns(3)
        col1.metric("Pabrikan (Make)", str(make))
        col2.metric("Model Perangkat", str(model))
        col3.metric("Encoder / Software", str(encoder))
        
        st.markdown("---")
        st.markdown("### 📋 Kesimpulan Analisis Probabilitas Objektif")
        
        # Logika Deteksi Cerdas Berbasis Data Mendalam
        make_lower = str(make).lower()
        model_lower = str(model).lower()
        encoder_lower = str(encoder).lower()
        
        if "apple" in make_lower or "iphone" in model_lower or "ios" in encoder_lower:
            st.info("🟢 **Probabilitas Tinggi:** Rekaman asli berasal dari perangkat atau ekosistem iOS (Apple).")
        elif "google" in encoder_lower or "veo" in encoder_lower or "imagen" in encoder_lower:
            st.error("🤖 **Indikasi Kuat Buatan AI / Cloud:** Terdeteksi tanda tangan 'Google' atau layanan cloud AI pada metadata file.")
        elif "openai" in encoder_lower or "runway" in encoder_lower or "kling" in encoder_lower or "sora" in encoder_lower:
            st.error("🤖 **Indikasi Kuat Buatan AI:** Terdeteksi tanda tangan generator video AI pada metadata file.")
        elif "tiktok" in encoder_lower or "instagram" in encoder_lower or "facebook" in encoder_lower or "threads" in encoder_lower:
            st.warning("🟡 **Probabilitas Sedang:** Terdeteksi jejak atau string platform media sosial pada bagian encoder/tags.")
        elif make == "Tidak ada data" and model == "Tidak ada data" and encoder == "Tidak ada data":
            st.info("⚪ **Data Bersih / Kosong:** Tidak ditemukan tag metadata pabrikan atau encoder. Kemungkinan besar video unduhan bersih, hasil render editor video PC (Premiere/CapCut), atau file yang metadatanya telah dihapus.")
        else:
            st.warning(f"🔍 **Terdeteksi Software/Encoder Lain:** [{encoder}] - File diproses menggunakan software atau perangkat non-standar.")
            
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
        
