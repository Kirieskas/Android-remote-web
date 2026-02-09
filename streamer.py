import subprocess, os

class TurboStreamer:
    def __init__(self):
        self.adb = os.path.abspath("bin/adb.exe")
        self.ffmpeg = os.path.abspath("bin/ffmpeg.exe")
        self.proc = None
        self.ff_proc = None

    def stop(self):
        if self.proc: self.proc.kill()
        if self.ff_proc: self.ff_proc.kill()

    def generate_mpegts(self, res="540x960", bit="3M"):
        self.stop()
        # Захват h264
        adb_cmd = [self.adb, 'exec-out', 'screenrecord', '--output-format=h264', '--size', res, '--bit-rate', bit, '--time-limit', '180', '-']
        self.proc = subprocess.Popen(adb_cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        
        # Конвертация в MPEG1 (самый быстрый декодер для JS)
        ff_cmd = [
            self.ffmpeg, '-f', 'h264', '-i', 'pipe:0',
            '-f', 'mpegts', '-codec:v', 'mpeg1video', '-s', res, '-b:v', bit, 
            '-bf', '0', '-tune', 'zerolatency', '-preset', 'ultrafast', '-'
        ]
        self.ff_proc = subprocess.Popen(ff_cmd, stdin=self.proc.stdout, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)

        while True:
            chunk = self.ff_proc.stdout.read(4096)
            if not chunk: break
            yield chunk