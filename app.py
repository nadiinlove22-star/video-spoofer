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

# Custom Styling CSS agar tampilannya elegan ala software profesional
st.markdown("""
    <style>
    .main-header {
        font-size: 2.2rem;
        color: #FF4B4B;
        font-weight: 800;
        margin-bottom: 0.1rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #adb5bd;
        margin-bottom: 1.5rem;
    }
    .stMetric {
        background-color: #1e1e1e;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    </style>
""", unsafe_allow_html=True)

# Header Aplikasi
st.markdown('<div class="main-header">🎬 Video Metadata & Forensic Suite Pro</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Analisis forensik mendalam untuk mengekstrak seluruh parameter QuickTime/EXIF secara komprehensif.</div>', unsafe_allow_html=True)

# Sidebar untuk Pengaturan Target Metadata iPhone (Spoofer)
st.sidebar.header("⚙️ Pengaturan Spoofer iPhone")
device_make = st.sidebar.text_input("Device Make", "Apple")
device_model = st.sidebar.text_input("Device Model", "iPhone 11")
software_ver = st.sidebar.text_input("Software / iOS Version", "18.6.2")
creation_time = st.sidebar.text_input("Creation Time (UTC)", "2026-02-28T04:54:17Z")

# Area Unggah Utama
uploaded_file = st.file_uploader("📂 Pilih atau Seret File Video (.mp4 / .mov / .mkv)", type=["mp4", "mov", "mkv", "avi"])

if uploaded_file is not None:
    col_vid1, col_vid2 = st.columns([1, 1])
    with col_vid1:
        st.video(uploaded_file)
    
    # Simpan ke file sementara untuk diproses ffprobe & ffmpeg
    tfile = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
    tfile.write(uploaded_file.read())
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
        streams = data.get("streams", [])
        
        # Ekstraksi Stream Video & Audio
        video_stream = next((s for s in streams if s.get("codec_type") == "video"), {})
        audio_stream = next((s for s in streams if s.get("codec_type") == "audio"), {})
        
        # Gabungkan semua tag dari format dan streams untuk pencarian menyeluruh
        all_tags = format_tags.copy()
        for s in streams:
            all_tags.update(s.get("tags", {}))
            
        def get_tag(possible_keys):
            for k in possible_keys:
                # Cek case-insensitive
                for actual_k, val in all_tags.items():
                    if k.lower() in actual_k.lower():
                        return val
            return "Tidak ada data"

        # Parameter Utama
        make = get_tag(["make", "manufacturer", "brand"])
        model = get_tag(["model", "device_model"])
        software = get_tag(["software", "com.apple.quicktime.software"])
        encoder = get_tag(["encoder", "handler_name", "creation_tool"])
        creation_date = get_tag(["creation_time", "date", "com.apple.quicktime.creationdate"])
        major_brand = format_data.get("format_name", get_tag(["major_brand"]))
        gps_loc = get_tag(["location", "gps", "coordinates"])
        
        with col_vid2:
            st.markdown("### 📊 Ringkasan Identitas File")
            st.metric("Pabrikan (Make)", str(make))
            st.metric("Model Perangkat", str(model))
            st.metric("Software / iOS", str(software))
            st.metric("Encoder / Tool", str(encoder))

        st.markdown("---")
        
        # Tampilan Tab untuk Analisis Super Lengkap ala EXIF Editor
        tab1, tab2, tab3, tab4 = st.tabs([
            "🔍 Kesimpulan & Keaslian", 
            "📱 Parameter QuickTime / File", 
            "🎞️ Spesifikasi Video & Audio", 
            "📜 Raw Metadata Tags (Lengkap)"
        ])
        
        with tab1:
            st.subheader("Evaluasi Probabilitas Keaslian File")
            make_l = str(make).lower()
            model_l = str(model).lower()
            encoder_l = str(encoder).lower()
            
            if "apple" in make_l or "iphone" in model_l:
                st.success("🟢 **Indikasi Asli / Ekosistem iOS:** Metadata menunjukkan perangkat Apple/iPhone secara valid.")
            elif "google" in encoder_l or "lavf" in encoder_l:
                st.warning(f"⚠️ **Indikasi Rekayasa / Render Software:** Ditemukan tanda tangan encoder pihak ketiga (`{encoder}`). File mungkin telah diproses, diunduh dari platform tertentu, atau disunting metadatanya.")
            else:
                st.info("ℹ️ File memiliki struktur metadata standar.")
                
            if gps_loc != "Tidak ada data":
                st.success(f"📍 **Data GPS Ditemukan:** `{gps_loc}`")
            else:
                st.info("📍 **Data GPS:** Tidak ada data koordinat lokasi.")

        with tab2:
            st.subheader("Detail Parameter Kontainer & File")
            col_a, col_b = st.columns(2)
            with col_a:
                st.write(f"**Format Nama File:** {format_data.get('format_long_name', 'N/A')} ")
                st.write(f"**Durasi File:** {float(format_data.get('duration', 0)):.2f} detik")
                st.write(f"**Ukuran File:** {int(format_data.get('size', 0)) / (1024*1024):.2f} MB")
                st.write(f"**Bit Rate Total:** {int(format_data.get('bit_rate', 0)):,} bps")
            with col_b:
                st.write(f"**Major Brand:** {format_tags.get('major_brand', 'N/A')}")
                st.write(f"**Compatible Brands:** {format_tags.get('compatible_brands', 'N/A')}")
                st.write(f"**Waktu Pembuatan (Creation Time):** {creation_date}")

        with tab3:
            st.subheader("Spesifikasi Teknis Track Media")
            col_v, col_aud = st.columns(2)
            with col_v:
                st.markdown("#### 🎬 Video Stream")
                st.write(f"**Codec:** {video_stream.get('codec_name', 'N/A').upper()}")
                st.write(f"**Resolusi:** {video_stream.get('width', 'N/A')} x {video_stream.get('height', 'N/A')} px")
                st.write(f"**Frame Rate (FPS):** {video_stream.get('r_frame_rate', 'N/A')}")
                st.write(f"**Pixel Format:** {video_stream.get('pix_fmt', 'N/A')} (Bit Depth: {video_stream.get('bits_per_raw_sample', 'N/A')})")
                st.write(f"**Color Space:** {video_stream.get('color_space', 'N/A')}")
            with col_aud:
                st.markdown("#### 🔊 Audio Stream")
                if audio_stream:
                    st.write(f"**Codec Audio:** {audio_stream.get('codec_name', 'N/A').upper()}")
                    st.write(f"**Sample Rate:** {audio_stream.get('sample_rate', 'N/A')} Hz")
                    st.write(f"**Channel:** {audio_stream.get('channels', 'N/A')} ({audio_stream.get('channel_layout', 'N/A')})")
                    st.write(f"**Bit Rate:** {audio_stream.get('bit_rate', 'N/A')} bps")
                else:
                    st.write("Tidak ada track audio terdeteksi.")

        with tab4:
            st.subheader("Seluruh Tag Metadata Mentah (Raw Key-Value)")
            st.write("Berikut adalah seluruh kamus metadata yang berhasil ditarik dari file video secara transparan:")
            st.json(all_tags)
            
    except Exception as e:
        st.error(f"Gagal memproses struktur file: {e}")

    st.markdown("---")
    
    # 2. Bagian Aksi Penyuntikan Metadata (Spoofing)
    st.subheader("🚀 Tindakan Penyuntikan Metadata (Spoofing Engine)")
    st.write("Ubah dan suntikkan parameter metadata video ini menjadi identik seperti rekaman asli iPhone.")
    
    if st.button("Jalankan Suntik Metadata Sekarang", type="primary"):
        with st.spinner("Sedang memproses penyuntikan metadata tingkat lanjut..."):
            output_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
            output_file.close()
            
            cmd_spoof = [
                "ffmpeg", "-y", "-i", tfile.name,
                "-metadata", f"com.apple.quicktime.make={device_make}",
                "-metadata", f"com.apple.quicktime.model={device_model}",
                "-metadata", f"com.apple.quicktime.software={software_ver}",
                "-metadata", f"com.apple.quicktime.creationdate={creation_time}",
                "-metadata", f"encoder={software_ver}",
                "-metadata", f"handler_name=Core Media Video",
                "-codec", "copy", output_file.name
            ]
            
            try:
                subprocess.run(cmd_spoof, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                st.success("Metadata berhasil disuntikkan dengan sukses!")
                
                with open(output_file.name, "rb") as f:
                    st.download_button(
                        label="📥 Unduh Video Hasil Spoofer Pro",
                        data=f,
                        file_name="video_spoofed_pro.mp4",
                        mime="video/mp4"
                    )
            except Exception as e:
                st.error(f"Terjadi kesalahan saat proses ffmpeg: {e}")
                
    # Bersihkan file temp utama
    if os.path.exists(tfile.name): 
        os.unlink(tfile.name)
        
