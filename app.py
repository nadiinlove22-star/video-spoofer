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

# Custom Styling CSS
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
    </style>
""", unsafe_allow_html=True)

# Inisialisasi Session State untuk Menyimpan List Preset Metadata yang Disalin
if "preset_list" not in st.session_state:
    st.session_state.preset_list = {
        "iPhone 11 (Default iOS 18.6)": {
            "make": "Apple",
            "model": "iPhone 11",
            "software": "18.6.2",
            "creation_date": "2026-02-28T04:54:17Z",
            "encoder": "Lavf60.3.100"
        },
        "iPhone 15 Pro Max (iOS 17.2)": {
            "make": "Apple",
            "model": "iPhone 15 Pro Max",
            "software": "17.2.1",
            "creation_date": "2026-06-15T12:00:00Z",
            "encoder": "Apple QuickTime"
        }
    }

# Header Aplikasi
st.markdown('<div class="main-header">🎬 Video Metadata & Forensic Suite Pro</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Analisis forensik, salin/simpan template metadata, dan suntikkan ke video lain dengan mudah.</div>', unsafe_allow_html=True)

# --- SIDEBAR: MANAJEMEN LIST PRESET METADATA (COPY, EDIT, HAPUS, TAMBAH) ---
st.sidebar.header("📋 Manajemen List Preset Metadata")
st.sidebar.write("Kelola daftar metadata yang tersimpan untuk dipakai kapan saja.")

# Pilihan Preset yang Tersedia di List
preset_names = list(st.session_state.preset_list.keys())
selected_preset_name = st.sidebar.selectbox("Pilih Preset Tersimpan", ["-- Buat Baru / Manual --"] + preset_names)

# Form untuk Tambah / Edit / Hapus Preset
with st.sidebar.expander("🛠️ Tambah / Edit Preset Terpilih", expanded=False):
    if selected_preset_name != "-- Buat Baru / Manual --":
        curr_data = st.session_state.preset_list[selected_preset_name]
        p_name_input = st.text_input("Nama Preset", value=selected_preset_name)
        p_make = st.text_input("Device Make", value=curr_data["make"])
        p_model = st.text_input("Device Model", value=curr_data["model"])
        p_sw = st.text_input("Software", value=curr_data["software"])
        p_date = st.text_input("Creation Date", value=curr_data["creation_date"])
        p_enc = st.text_input("Encoder", value=curr_data["encoder"])
        
        col_s1, col_s2 = st.columns(2)
        if col_s1.button("💾 Update"):
            # Jika ganti nama, hapus yang lama
            if p_name_input != selected_preset_name:
                del st.session_state.preset_list[selected_preset_name]
            st.session_state.preset_list[p_name_input] = {
                "make": p_make, "model": p_model, "software": p_sw, "creation_date": p_date, "encoder": p_enc
            }
            st.success("Preset berhasil diperbarui!")
            st.rerun()
            
        if col_s2.button("🗑️ Hapus", type="primary"):
            del st.session_state.preset_list[selected_preset_name]
            st.warning("Preset dihapus!")
            st.rerun()
    else:
        new_p_name = st.text_input("Nama Preset Baru", "Custom Preset 1")
        new_make = st.text_input("Device Make", "Apple")
        new_model = st.text_input("Device Model", "iPhone 13")
        new_sw = st.text_input("Software", "17.4")
        new_date = st.text_input("Creation Date", "2026-01-01T00:00:00Z")
        new_enc = st.text_input("Encoder", "Lavf")
        
        if st.button("➕ Simpan ke List Baru"):
            st.session_state.preset_list[new_p_name] = {
                "make": new_make, "model": new_model, "software": new_sw, "creation_date": new_date, "encoder": new_enc
            }
            st.success("Preset baru berhasil ditambahkan ke list!")
            st.rerun()

# Tentukan nilai aktif berdasarkan pilihan preset sidebar
if selected_preset_name != "-- Buat Baru / Manual --":
    active_preset = st.session_state.preset_list[selected_preset_name]
else:
    active_preset = {"make": "Apple", "model": "iPhone 11", "software": "18.6.2", "creation_date": "2026-02-28T04:54:17Z", "encoder": "Lavf60.3.100"}

st.sidebar.markdown("---")
st.sidebar.subheader("🚀 Target Spoofer Aktif")
device_make = st.sidebar.text_input("Target Make", active_preset["make"])
device_model = st.sidebar.text_input("Target Model", active_preset["model"])
software_ver = st.sidebar.text_input("Target Software", active_preset["software"])
creation_time = st.sidebar.text_input("Target Creation Time", active_preset["creation_date"])
encoder_target = st.sidebar.text_input("Target Encoder", active_preset["encoder"])


# --- AREA UTAMA APLIKASI ---
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
        
        video_stream = next((s for s in streams if s.get("codec_type") == "video"), {})
        audio_stream = next((s for s in streams if s.get("codec_type") == "audio"), {})
        
        all_tags = format_tags.copy()
        for s in streams:
            all_tags.update(s.get("tags", {}))
            
        def get_tag(possible_keys):
            for k in possible_keys:
                for actual_k, val in all_tags.items():
                    if k.lower() in actual_k.lower():
                        return val
            return "Tidak ada data"

        # Ekstraksi Parameter Video yang di-upload
        extracted_make = str(get_tag(["make", "manufacturer", "brand"]))
        extracted_model = str(get_tag(["model", "device_model"]))
        extracted_software = str(get_tag(["software", "com.apple.quicktime.software"]))
        extracted_encoder = str(get_tag(["encoder", "handler_name", "creation_tool"]))
        extracted_creation_date = str(get_tag(["creation_time", "date", "com.apple.quicktime.creationdate"]))
        
        with col_vid2:
            st.markdown("### 📊 Ringkasan Identitas File")
            st.metric("Pabrikan (Make)", extracted_make)
            st.metric("Model Perangkat", extracted_model)
            st.metric("Software / iOS", extracted_software)
            st.metric("Encoder / Tool", extracted_encoder)
            
            # --- FITUR COPY / SIMPAN KE LIST ---
            st.markdown("#### 📋 Salin Metadata Video Ini")
            new_save_name = st.text_input("Beri Nama untuk Disimpan ke List", value=f"{extracted_model if extracted_model != 'Tidak ada data' else 'Custom Video'}")
            if st.button("📥 Copy & Simpan Metadata ke List Preset"):
                st.session_state.preset_list[new_save_name] = {
                    "make": extracted_make if extracted_make != "Tidak ada data" else "Apple",
                    "model": extracted_model if extracted_model != "Tidak ada data" else "iPhone",
                    "software": extracted_software if extracted_software != "Tidak ada data" else "18.0",
                    "creation_date": extracted_creation_date if extracted_creation_date != "Tidak ada data" else "2026-01-01T00:00:00Z",
                    "encoder": extracted_encoder if extracted_encoder != "Tidak ada data" else "Lavf"
                }
                st.success(f"Berhasil menyimpan metadata ke list dengan nama **{new_save_name}**! Silakan cek sidebar.")
                st.rerun()

        st.markdown("---")
        
        # Tampilan Tab Analisis
        tab1, tab2, tab3, tab4 = st.tabs([
            "🔍 Kesimpulan & Keaslian", 
            "📱 Parameter QuickTime / File", 
            "🎞️ Spesifikasi Video & Audio", 
            "📜 Raw Metadata Tags (Lengkap)"
        ])
        
        with tab1:
            st.subheader("Evaluasi Probabilitas Keaslian File")
            make_l = extracted_make.lower()
            model_l = extracted_model.lower()
            encoder_l = extracted_encoder.lower()
            
            if "apple" in make_l or "iphone" in model_l:
                st.success("🟢 **Indikasi Asli / Ekosistem iOS:** Metadata menunjukkan perangkat Apple/iPhone secara valid.")
            elif "google" in encoder_l or "lavf" in encoder_l:
                st.warning(f"⚠️ **Indikasi Rekayasa / Render Software:** Ditemukan tanda tangan encoder pihak ketiga (`{extracted_encoder}`).")
            else:
                st.info("ℹ️ File memiliki struktur metadata standar.")

        with tab2:
            st.subheader("Detail Parameter Kontainer & File")
            col_a, col_b = st.columns(2)
            with col_a:
                st.write(f"**Format Nama File:** {format_data.get('format_long_name', 'N/A')}")
                st.write(f"**Durasi File:** {float(format_data.get('duration', 0)):.2f} detik")
                st.write(f"**Ukuran File:** {int(format_data.get('size', 0)) / (1024*1024):.2f} MB")
            with col_b:
                st.write(f"**Major Brand:** {format_tags.get('major_brand', 'N/A')}")
                st.write(f"**Waktu Pembuatan:** {extracted_creation_date}")

        with tab3:
            st.subheader("Spesifikasi Teknis Track Media")
            col_v, col_aud = st.columns(2)
            with col_v:
                st.markdown("#### 🎬 Video Stream")
                st.write(f"**Codec:** {video_stream.get('codec_name', 'N/A').upper()}")
                st.write(f"**Resolusi:** {video_stream.get('width', 'N/A')} x {video_stream.get('height', 'N/A')} px")
                st.write(f"**Frame Rate:** {video_stream.get('r_frame_rate', 'N/A')}")
            with col_aud:
                st.markdown("#### 🔊 Audio Stream")
                if audio_stream:
                    st.write(f"**Codec Audio:** {audio_stream.get('codec_name', 'N/A').upper()}")
                    st.write(f"**Sample Rate:** {audio_stream.get('sample_rate', 'N/A')} Hz")
                else:
                    st.write("Tidak ada track audio terdeteksi.")

        with tab4:
            st.subheader("Seluruh Tag Metadata Mentah (Raw Key-Value)")
            st.json(all_tags)
            
    except Exception as e:
        st.error(f"Gagal memproses struktur file: {e}")

    st.markdown("---")
    
    # 2. Bagian Aksi Penyuntikan Metadata (Paste / Spoofer Engine)
    st.subheader("🚀 Tindakan Penyuntikan Metadata (Paste Engine)")
    st.write(f"Terapkan preset aktif (**{selected_preset_name}**) atau data kustom ke video yang sedang di-upload ini.")
    
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
                "-metadata", f"encoder={encoder_target}",
                "-metadata", f"handler_name=Core Media Video",
                "-codec", "copy", output_file.name
            ]
            
            try:
                subprocess.run(cmd_spoof, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                st.success("Metadata berhasil disuntikkan dan dipaste ke video ini!")
                
                with open(output_file.name, "rb") as f:
                    st.download_button(
                        label="📥 Unduh Video Hasil Suntikan Metadata",
                        data=f,
                        file_name="video_spoofed_pasted.mp4",
                        mime="video/mp4"
                    )
            except Exception as e:
                st.error(f"Terjadi kesalahan saat proses ffmpeg: {e}")
                
    if os.path.exists(tfile.name): 
        os.unlink(tfile.name)
