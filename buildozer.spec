[app]
title = Video Metadata Spoofer
package.name = videospoofer
package.domain = org.spoofer

source.dir = .
source.include_exts = py,png,jpg,kv,atlas

version = 1.0

# Kunci agar FFmpeg dan Kivy terbundel offline di dalam APK
requirements = python3,kivy,ffmpeg

orientation = portrait
android.permissions = WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# Setelan API Android & Arsitektur agar build stabil dan tidak timeout
android.api = 33
android.minapi = 21
android.archs = arm64-v8a

[buildozer]
log_level = 2
warn_on_root = 1
