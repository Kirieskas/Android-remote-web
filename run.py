import os, sys, zipfile, requests, subprocess, asyncio
from tqdm import tqdm

ADB_URL = "https://dl.google.com/android/repository/platform-tools-latest-windows.zip"
FFMPEG_URL = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
JSMPEG_URL = "https://raw.githubusercontent.com/phoboslab/jsmpeg/master/jsmpeg.min.js"

def download(url, filename):
    if os.path.exists(filename): return
    print(f"Скачивание {filename}...")
    r = requests.get(url, stream=True)
    with open(filename, 'wb') as f:
        for data in r.iter_content(1024): f.write(data)

def setup():
    for d in ['bin', 'static']:
        if not os.path.exists(d): os.makedirs(d)
    
    if not os.path.exists('bin/adb.exe'):
        download(ADB_URL, "adb.zip")
        with zipfile.ZipFile("adb.zip", 'r') as z:
            for f in z.namelist():
                if 'adb.exe' in f or 'AdbWin' in f:
                    with z.open(f) as src, open(f"bin/{os.path.basename(f)}", "wb") as dst: dst.write(src.read())
        os.remove("adb.zip")

    if not os.path.exists('bin/ffmpeg.exe'):
        download(FFMPEG_URL, "ffmpeg.zip")
        with zipfile.ZipFile("ffmpeg.zip", 'r') as z:
            for f in z.namelist():
                if f.endswith('ffmpeg.exe'):
                    with z.open(f) as src, open("bin/ffmpeg.exe", "wb") as dst: dst.write(src.read())
        os.remove("ffmpeg.zip")
    
    if not os.path.exists('static/jsmpeg.min.js'):
        download(JSMPEG_URL, 'static/jsmpeg.min.js')
    print("✅ Система готова!")

if __name__ == "__main__":
    setup()
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8888, reload=True)