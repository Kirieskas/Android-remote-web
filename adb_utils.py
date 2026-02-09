import subprocess, os, re, asyncio, json

class ADBUtils:
    def __init__(self):
        self.adb = os.path.abspath("bin/adb.exe")
        self.config_file = "config.json"
        self._shell = None

    def _get_shell(self):
        if self._shell is None or self._shell.poll() is not None:
            self._shell = subprocess.Popen([self.adb, 'shell'], stdin=subprocess.PIPE, text=True, encoding='utf-8')
        return self._shell

    def fast_cmd(self, cmd):
        try:
            s = self._get_shell()
            s.stdin.write(cmd + "\n")
            s.stdin.flush()
        except: self._shell = None

    def load_config(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f: return json.load(f)
        return {"ip": "192.168.1.50", "port": "40057"}

    async def pair(self, ip, port, code):
        addr = f"{ip.strip()}:{port.strip()}"
        return await asyncio.to_thread(lambda: subprocess.run([self.adb, 'pair', addr, code.strip()], capture_output=True, text=True).stdout)

    async def connect(self, ip, port):
        addr = f"{ip.strip()}:{port.strip()}"
        subprocess.run([self.adb, 'disconnect'])
        res = await asyncio.to_thread(lambda: subprocess.run([self.adb, 'connect', addr], capture_output=True, text=True).stdout)
        if "connected" in res.lower():
            with open(self.config_file, 'w') as f: json.dump({'ip':ip,'port':port}, f)
            self.fast_cmd("pkill screenrecord")
            return True, res
        return False, res

    def tap(self, x, y): self.fast_cmd(f"input tap {x} {y}")
    def swipe(self, x1, y1, x2, y2, ms=200): self.fast_cmd(f"input swipe {x1} {y1} {x2} {y2} {ms}")
    def key(self, code): self.fast_cmd(f"input keyevent {code}")
    def type_text(self, text): self.fast_cmd(f"input text '{text.replace(' ', '%s')}'")
    def get_size(self):
        res = subprocess.run([self.adb, 'shell', 'wm', 'size'], capture_output=True, text=True).stdout
        m = re.search(r'(\d+)x(\d+)', res)
        return (int(m.group(1)), int(m.group(2))) if m else (1080, 1920)