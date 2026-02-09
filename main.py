from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from adb_utils import ADBUtils
from streamer import TurboStreamer
import asyncio

app = FastAPI()
adb = ADBUtils()
streamer = TurboStreamer()
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def index():
    with open("static/index.html", encoding='utf-8') as f: return HTMLResponse(f.read())

@app.get("/stream-ui")
async def stream_ui(res: str = "540x960", bit: str = "3M"):
    with open("static/stream.html", encoding='utf-8') as f:
        return HTMLResponse(f.read().replace("{res}", res).replace("{bit}", bit))

@app.get("/config")
async def config(): return adb.load_config()

@app.get("/size")
async def size():
    w, h = adb.get_size()
    return {"width": w, "height": h}

@app.post("/pair")
async def pair(d: dict): return {"msg": await adb.pair(d['ip'], d['port'], d['code'])}

@app.post("/connect")
async def connect(d: dict):
    ok, msg = await adb.connect(d['ip'], d['port'])
    return {"ok": ok, "msg": msg}

@app.websocket("/ws-video")
async def video_ws(ws: WebSocket):
    await ws.accept()
    res = ws.query_params.get("res", "540x960")
    bit = ws.query_params.get("bit", "3M")
    try:
        for chunk in streamer.generate_mpegts(res, bit):
            await ws.send_bytes(chunk)
            await asyncio.sleep(0)
    except: pass
    finally: streamer.stop()

@app.websocket("/ws-input")
async def input_ws(ws: WebSocket):
    await ws.accept()
    while True:
        try:
            d = await ws.receive_json()
            t = d['type']
            if t == 'tap': adb.tap(d['x'], d['y'])
            elif t == 'swipe': adb.swipe(d['x1'], d['y1'], d['x2'], d['y2'], d['ms'])
            elif t == 'key': adb.key(d['code'])
            elif t == 'text': adb.type_text(d['val'])
        except: break