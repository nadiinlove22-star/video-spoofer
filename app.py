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

# File lokal untuk menyimpan preset agar permanen
PRESET_FILE = "metadata_presets.json"

def load_presets():
    if os.path.exists(PRESET_FILE):
        try:
            with open(PRESET_FILE, "r") as f:
                return json.load(f)
        except:
            pass
    return {
        "iPhone 11 (iOS 18.6)": {
            "make": "Apple",
            "model": "iPhone 11",
            "software": "18.6.2",
            "creation_date": "2026-02-28T04:54:17Z",
            "encoder": "Lavf60.3.100"
        }
    }

def save_presets(presets):
    with open(PRESET_FILE, "w") as f:
        json.dump(presets, f, indent=4)

if "preset_list" not in st.session_state:
    st.session_state.preset_list = load_presets()

# Header Aplikasi
st.markdown("<h2>🎬 Video Metadata & Forensic Suite Pro</h2>", unsafe_allow_html=True)
st.markdown("<p style='color: #adb5bd;'>Analisis forensik, salin/simpan template metadata permanen, dan verifikasi hasil suntikan.</p>", unsafe_allow_html=True)

# --- SIDEBAR: MANAJEMEN LIST PRESET ---
st.sidebar.header("📋 Manajemen List Preset")

preset_names = list(st.session_state.preset_list.keys())
selected_preset_sidebar = st.sidebar.selectbox("Pilih Preset untuk Diedit", ["-- Buat Baru / Manual --"] + preset_names, key="sb_select")

with st.sidebar.expander("🛠️ Edit / Hapus Preset Terpilih", expanded=False):
    if selected_preset_sidebar != "-- Buat Baru / Manual --":
        curr_data = st.session_state.preset_list[selected_preset_sidebar]
        p_name_input = st.text_input("Nama Preset", value=selected_preset_sidebar, key="edit_p_name")
        p_make = st.text_input("Make", value=curr_data.get("make", "Apple"), key="edit_make")
        p_model = st.text_input("Model", value=curr_data.get("model", "iPhone"), key="edit_model")
        p_sw = st.text_input("Software", value=curr_data.get("software", "18.0"), key="edit_sw")
        p_date = st.text_input("Creation Date", value=curr_data.get("creation_date", ""), key="edit_date")
        p_enc = st.text_input("Encoder", value=curr_data.get("encoder", ""), key="edit_enc")
        
        col_s1, col_s2 = st.columns(2)
        if col_s1.button("💾 Update Preset"):
            if p_name_input != selected_preset_sidebar:
                del st.session_state.preset_list[selected_preset_sidebar]
            st.session_state.preset_list[p_name_input] = {
                "make": p_make, "model": p_model, "software": p_sw, "creation_date": p_date, "encoder": p_enc
            }
            save_presets(st.session_state.preset_list)
            st.sidebar.success("Berhasil diupdate!")
            st.rerun()
            
        if col_s2.button("🗑️ Hapus Preset", type="primary"):
            del st.session_state.preset_list[selected_preset_sidebar]
            save_presets(st.session_state.preset_list)
            st.sidebar.warning("Berhasil dihapus!")
            st.rerun()
    else:
        new_p_name = st.text_input("Nama Preset Baru", "Preset Baru 1", key="new_p_name")
        new_make = st.text_input("Make", "Apple", key="new_make")
        new_model = st.text_input("Model", "iPhone 11", key="new_model")
        new_sw = st.text_input("Software", "18.6.2", key="new_sw")
        new_date = st.text_input("Creation Date", "2026-02-28T04:54:17Z", key="new_date")
        new_enc = st.text_input("Encoder", "Lavf60.3.100", key="new_enc")
        
        if st.button("➕ Tambah ke List"):
            st.session_state.preset_list[new_p_name] = {
                "make": new_make, "model": new_model, "software": new_sw, "creation_date": new_date, "encoder": new_enc
            }
            save_presets(st.session_state.preset_list)
            st.sidebar.success("Preset baru ditambahkan!")
            st.rerun()


# --- AREA UTAMA APLIKASI ---
uploaded_file = st.file_uploader("📂 Pilih atau Seret File Video (.mp4 / .mov / .mkv)", type=["mp4", "mov", "mkv", "avi"])

if uploaded_file is not None:
    col_vid1, col_vid2 = st.columns([1, 1])
    with col_vid1:
        st.video(uploaded_file)
    
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
                        return str(val)
            return "N/A"

        extracted_make = get_tag(["make", "manufacturer", "brand", "major_brand"])
        extracted_model = get_tag(["model", "device_model"])
        extracted_software = get_tag(["software", "com.apple.quicktime.software"])
        extracted_encoder = get_tag(["encoder", "handler_name", "creation_tool"])
        extracted_creation_date = get_tag(["creation_time", "date", "com.apple.quicktime.creationdate"])
        
        with col_vid2:
            st.markdown("### 📊 Ringkasan Identitas File Asli")
            st.write(f"**Pabrikan (Make):** {extracted_make}")
            st.write(f"**Model Perangkat:** {extracted_model}")
            st.write(f"**Software / iOS:** {extracted_software}")
            st.write(f"**Encoder / Tool:** {extracted_encoder}")
            st.write(f"**Creation Date:** {extracted_creation_date}")
            
            st.markdown("---")
            st.markdown("#### 📋 Salin & Simpan Metadata Ini")
            save_name_input = st.text_input("Beri Nama Preset List", value=f"Preset_{extracted_model if extracted_model != 'N/A' else 'Custom'}", key="save_preset_input")
            
            if st.button("📥 Simpan ke List Preset Sekarang", type="secondary"):
                st.session_state.preset_list[save_name_input] = {
                    "make": extracted_make if extracted_make != "N/A" else "Apple",
                    "model": extracted_model if extracted_model != "N/A" else "iPhone",
                    "software": extracted_software if extracted_software != "N/A" else "18.0",
                    "creation_date": extracted_creation_date if extracted_creation_date != "N/A" else "2026-02-28T04:54:17Z",
                    "encoder": extracted_encoder if extracted_encoder != "N/A" else "Lavf60.3.100"
                }
                save_presets(st.session_state.preset_list)
                st.success(f"Berhasil disimpan dengan nama **{save_name_input}**!")
                st.rerun()

        st.markdown("---")
        
        # Tabs Detail
        tab1, tab2, tab3 = st.tabs(["📱 Parameter File", "🎞️ Spesifikasi Media", "📜 Raw Metadata (JSON)"])
        with tab1:
            st.write(f"**Format:** {format_data.get('format_long_name', 'N/A')}")
            st.write(f"**Durasi:** {float(format_data.get('duration', 0)):.2f} detik")
            st.write(f"**Ukuran:** {int(format_data.get('size', 0)) / (1024*1024):.2f} MB")
        with tab2:
            st.write(f"**Video Codec:** {video_stream.get('codec_name', 'N/A').upper()}")
            st.write(f"**Resolusi:** {video_stream.get('width', 'N/A')} x {video_stream.get('height', 'N/A')} px")
            st.write(f"**Audio Codec:** {audio_stream.get('codec_name', 'N/A').upper() if audio_stream else 'Tidak ada'}")
        with tab3:
            st.json(all_tags)
            
    except Exception as e:
        st.error(f"Gagal membaca file: {e}")

    st.markdown("---")
    
    # --- BAGIAN EKSEKUSI SUNTIK DENGAN PILIHAN PRESET DEFAULT & OPSI HAPUS ---
    st.subheader("🚀 Eksekusi & Analisis Ulang Metadata (Paste & Verify Engine)")
    st.write("Pilih preset target, jalankan suntikan, lalu verifikasi detail metadata terbarunya.")
    
    current_preset_names = list(st.session_state.preset_list.keys())
    
    # Otomatis jadikan iPhone 11 sebagai default index pertama jika ada di list
    default_index = 0
    for idx, p_name in enumerate(current_preset_names):
        if "iPhone 11" in p_name:
            default_index = idx
            break
            
    chosen_execution_preset = st.selectbox(
        "🎯 Pilih Preset Target untuk Disuntikkan (Default: iPhone 11)", 
        current_preset_names, 
        index=default_index, 
        key="exec_preset_choice"
    )
    
    # Tombol instan untuk menghapus preset yang sedang dipilih dari list
    col_del_p1, col_del_p2 = st.columns([2, 5])
    with col_del_p1:
        if len(current_preset_names) > 1:
            if st.button("🗑️ Hapus Preset Ini dari List"):
                del st.session_state.preset_list[chosen_execution_preset]
                save_presets(st.session_state.preset_list)
                st.warning(f"Preset '{chosen_execution_preset}' berhasil dihapus!")
                st.rerun()
        else:
            st.caption("Minimal harus ada 1 preset tersimpan.")
            
    selected_data = st.session_state.preset_list[chosen_execution_preset]
    
    with st.expander(f"👁️ Lihat Detail Data yang Akan Disuntikkan dari Preset: **{chosen_execution_preset}**"):
        st.json(selected_data)
    
    if "spoofed_file_path" not in st.session_state:
        st.session_state.spoofed_file_path = None
    if "verified_metadata" not in st.session_state:
        st.session_state.verified_metadata = None

    if st.button(f"Jalankan Suntik & Analisis Ulang Menggunakan Preset '{chosen_execution_preset}'", type="primary"):
        with st.spinner("Memproses penyuntikan dan menganalisis ulang file baru..."):
            output_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
            output_file.close()
            
            cmd_spoof = [
                "ffmpeg", "-y", "-i", tfile.name,
                "-metadata", f"com.apple.quicktime.make={selected_data['make']}",
                "-metadata", f"com.apple.quicktime.model={selected_data['model']}",
                "-metadata", f"com.apple.quicktime.software={selected_data['software']}",
                "-metadata", f"com.apple.quicktime.creationdate={selected_data['creation_date']}",
                "-metadata", f"encoder={selected_data['encoder']}",
                "-metadata", f"handler_name=Core Media Video",
                "-codec", "copy", output_file.name
            ]
            
            try:
                subprocess.run(cmd_spoof, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                st.session_state.spoofed_file_path = output_file.name
                
                # RE-PROBE: Analisis ulang file hasil suntikan secara otomatis
                cmd_reprobe = [
                    "ffprobe", "-v", "quiet", "-print_format", "json",
                    "-show_format", "-show_streams", output_file.name
                ]
                reprobe_res = subprocess.run(cmd_reprobe, capture_output=True, text=True, check=True)
                reprobe_data = json.loads(reprobe_res.stdout)
                
                r_format_tags = reprobe_data.get("format", {}).get("tags", {})
                r_streams = reprobe_data.get("streams", [])
                r_all_tags = r_format_tags.copy()
                for s in r_streams:
                    r_all_tags.update(s.get("tags", {}))
                
                st.session_state.verified_metadata = r_all_tags
                st.success("Suntikan berhasil dan file telah dianalisis ulang!")
            except Exception as e:
                st.error(f"Gagal memproses ffmpeg / ffprobe: {e}")

    # Tampilkan Hasil Analisis Ulang & Keputusan Unduh
    if st.session_state.spoofed_file_path and st.session_state.verified_metadata:
        st.markdown("---")
        st.markdown("### 🔍 Hasil Verifikasi Metadata Terbaru (Setelah Disuntik)")
        st.info("Silakan periksa detail di bawah ini. Pastikan pengaturan sudah sesuai sebelum Anda memutuskan untuk mengunduhnya.")
        
        v_tags = st.session_state.verified_metadata
        def get_v_tag(keys):
            for k in keys:
                for ak, val in v_tags.items():
                    if k.lower() in ak.lower():
                        return str(val)
            return "N/A"
            
        col_v1, col_v2 = st.columns(2)
        with col_v1:
            st.write(f"**Make / Pabrikan:** {get_v_tag(['make', 'manufacturer', 'brand']) }")
            st.write(f"**Model Perangkat:** {get_v_tag(['model', 'device_model']) }")
            st.write(f"**Software / iOS:** {get_v_tag(['software']) }")
        with col_v2:
            st.write(f"**Creation Date:** {get_v_tag(['creation_date', 'creation_time', 'date']) }")
            st.write(f"**Encoder:** {get_v_tag(['encoder', 'handler_name']) }")
            
        with st.expander("📄 Lihat Seluruh Raw Metadata Hasil Suntikan"):
            st.json(v_tags)
            
        st.markdown("#### 🛑 Keputusan Anda:")
        col_btn1, col_btn2 = st.columns(2)
        
        with col_btn1:
            if os.path.exists(st.session_state.spoofed_file_path):
                with open(st.session_state.spoofed_file_path, "rb") as f:
                    st.download_button(
                        label="✅ Setuju & Lanjut Unduh Video",
                        data=f,
                        file_name=f"video_verified_{chosen_execution_preset.replace(' ', '_')}.mp4",
                        mime="video/mp4",
                        type="primary"
                    )
        with col_btn2:
            if st.button("❌ Batalkan / Ulangi Pengaturan"):
                st.session_state.spoofed_file_path = None
                st.session_state.verified_metadata = None
                st.rerun()

    if os.path.exists(tfile.name): 
        os.unlink(tfile.name)
        
