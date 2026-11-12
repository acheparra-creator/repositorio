"""Arma un video con paneo y zoom suaves sobre los renders (requiere ffmpeg)."""
import subprocess, os
import numpy as np
from PIL import Image

D = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'renders')
W, H, FPS, FADE = 1440, 960, 30, 0.9
# (archivo, segundos, encuadre inicial, encuadre final) -- encuadre = (centro_x, centro_y, ancho) en fracciones de la imagen
SHOTS = [
    ('0_planta.png',          7.0, (0.50, 0.21, 1.00), (0.50, 0.79, 1.00)),
    ('1_desde_entrada.png',   5.0, (0.50, 0.50, 1.00), (0.52, 0.47, 0.82)),
    ('3_escritorio.png',      5.0, (0.45, 0.52, 0.84), (0.55, 0.50, 0.96)),
    ('5_tv_cuadro.png',       5.0, (0.42, 0.52, 0.86), (0.56, 0.50, 0.80)),
    ('4_barra_tarja.png',     5.0, (0.50, 0.50, 1.00), (0.47, 0.50, 0.80)),
    ('2_desde_ventanal.png',  5.5, (0.56, 0.50, 0.84), (0.50, 0.50, 1.00)),
]
ims = [Image.open(os.path.join(D, s[0])).convert('RGB') for s in SHOTS]

def ease(t): return t * t * (3 - 2 * t)

def frame(i, t):
    im = ims[i]; _, dur, a, b = SHOTS[i]
    k = ease(min(max(t / dur, 0), 1))
    cx, cy, w = (a[j] + (b[j] - a[j]) * k for j in range(3))
    bw = w * im.width; bh = bw * H / W
    x0 = min(max(cx * im.width - bw / 2, 0), im.width - bw); y0 = min(max(cy * im.height - bh / 2, 0), im.height - bh)
    return np.asarray(im.resize((W, H), Image.LANCZOS, box=(x0, y0, x0 + bw, y0 + bh)), dtype=np.float32)

starts = []; t0 = 0.0
for s in SHOTS: starts.append(t0); t0 += s[1] - FADE
total = t0 + FADE
out = os.path.join(os.path.dirname(D), 'consultorio_recorrido.mp4')
ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '%dx%d' % (W, H), '-r', str(FPS),
                       '-i', '-', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '18', '-preset', 'medium', '-movflags', '+faststart', out],
                      stdin=subprocess.PIPE)
n = int(total * FPS)
for f in range(n):
    t = f / FPS; acc = None; wsum = 0
    for i, s in enumerate(SHOTS):
        lt = t - starts[i]
        if 0 <= lt <= s[1]:
            w = 1.0
            if i > 0 and lt < FADE: w = ease(lt / FADE)
            if acc is None: acc = frame(i, lt)
            else: acc = acc * (1 - w) + frame(i, lt) * w
    g = min(1.0, t / 0.6, (total - t) / 0.8)          # entrada y salida desde negro
    ff.stdin.write(np.clip(acc * max(g, 0), 0, 255).astype(np.uint8).tobytes())
ff.stdin.close(); ff.wait()
print(out, '%.1f s' % total)
