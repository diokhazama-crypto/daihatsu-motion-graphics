#!/usr/bin/env python3
"""Timeline SigraSinematik -> src/sigra.json

Gaya editan meniru video referensi (mobil di parkiran malam):
- grading gelap, hanya merah yang menyala (lihat prep_sigra.py)
- tiap shot 2 ketukan (kadang 4), gerak kamera pelan (push-in / pull-back)
- efek: lampu menyala, meredup ke gelap, whip blur, glitch pixel-stretch,
  rack focus, transisi "masuk lewat lampu" (mask), flash + bloom di drop
- shot terakhir = shot pembuka, jadi videonya nyambung saat di-loop

Lagu: audio asli video Sigra (152 BPM). Ketukan diukur dengan librosa;
bagian tenang sampai ~18 dtk, riser 18-20 dtk, DROP di ketukan 51 (20.13 dtk).
Potongan selalu di ketukan ganjil (= awal/tengah bar).
"""
import json

FPS = 30
DUR = 30.0
CLIP = "sigra"

# waktu ketukan (detik) hasil librosa.beat.beat_track pada audio video Sigra
BT = [0.60, 1.04, 1.44, 1.83, 2.23, 2.62, 3.02, 3.41, 3.81, 4.20, 4.62, 4.99, 5.36, 5.78, 6.20, 6.57, 6.94,
      7.34, 7.73, 8.13, 8.52, 8.92, 9.33, 9.73, 10.10, 10.50, 10.84, 11.19, 11.59, 11.98, 12.35, 12.72, 13.10,
      13.47, 13.86, 14.23, 14.63, 15.02, 15.42, 15.79, 16.18, 16.58, 16.97, 17.37, 17.76, 18.16, 18.55, 18.95,
      19.34, 19.74, 20.13, 20.50, 20.90, 21.29, 21.71, 22.11, 22.48, 22.89, 23.29, 23.68, 24.06, 24.45, 24.85,
      25.24, 25.63, 26.03, 26.42, 26.82, 27.21, 27.61, 27.98, 28.37, 28.79, 29.19, 29.58, 29.95]
DROP = 51

# posisi (0-1) lampu di dalam frame, dipakai untuk efek lampu menyala / mask / bloom
HEADLIGHT = (0.50, 0.46)      # shot lampu depan (detik 4.1-5.0 di video asli)
HERO_LAMPS = [(0.42, 0.63), (0.82, 0.62)]
TAIL = (0.52, 0.50)           # close-up lampu belakang
TAIL_34 = (0.43, 0.58)        # rear 3/4

# (ketukan mulai, ketukan selesai, detik di video asli, playbackRate, opsi)
# None = awal / akhir video. rate 0.8 = kecepatan asli sebelum dipercepat 1.25x.
# opsi: in = cut|lightOn|fromBlack|whip|focus|mask, out = cut|dim|whip|stretch,
#       zoom = [awal, akhir], pan = geser %, light = (x, y), flash = True,
#       bloom = [(ketukan, x, y, warna)]
SHOTS = [
    # ---- eksterior: detail, gelap, pelan
    (None, 1, 5.78, 0.8, dict(zoom=[1.02, 1.08])),                       # grille + lis merah (pembuka = penutup)
    (1, 3, 2.55, 0.8, dict(zoom=[1.10, 1.02])),                           # velg, pull-back
    (3, 5, 7.36, 0.8, dict(zoom=[1.03, 1.07], pan=-1.5)),                 # spion, siluet gelap
    (5, 7, 4.12, 0.8, dict(inn="lightOn", light=HEADLIGHT, zoom=[1.02, 1.06])),  # lampu depan MENYALA
    (7, 11, 27.95, 0.8, dict(out="dim", zoom=[1.03, 1.09])),              # rear 3/4, lalu meredup ke gelap
    (11, 13, 29.39, 0.75, dict(inn="fromBlack", light=TAIL, glow="red", zoom=[1.08, 1.03])),  # lampu belakang dari gelap
    (13, 15, 5.06, 0.85, dict(out="whip", zoom=[1.03, 1.07])),            # grille miring -> whip
    (15, 17, 8.20, 0.8, dict(inn="whip", zoom=[1.04, 1.08])),             # handle pintu
    # ---- interior: aksen merah
    (17, 21, 9.05, 0.8, dict(out="stretch", zoom=[1.02, 1.08])),          # panel pintu merah -> glitch stretch
    (21, 23, 10.50, 0.8, dict(zoom=[1.06, 1.02])),                        # kabin + dashboard merah
    (23, 27, 12.00, 0.8, dict(zoom=[1.02, 1.06])),                        # dashboard lewat pilar (wipe alami)
    (27, 29, 13.65, 0.8, dict(zoom=[1.03, 1.07])),                        # head unit
    (29, 31, 15.15, 0.8, dict(inn="lightOn", zoom=[1.02, 1.06])),         # panel instrumen menyala
    (31, 35, 16.80, 0.8, dict(zoom=[1.02, 1.07], pan=1.5)),               # setir + ventilasi merah
    (35, 37, 21.42, 0.8, dict(zoom=[1.04, 1.08])),                        # jok depan
    (37, 39, 22.95, 0.8, dict(out="stretch", zoom=[1.03, 1.07])),         # jok belakang -> glitch
    (39, 43, 18.40, 0.8, dict(zoom=[1.02, 1.07])),                        # kabin dari belakang (gelap)
    (43, 45, 26.30, 0.8, dict(out="dim", zoom=[1.03, 1.06])),             # baris ke-3, meredup (riser mulai)
    # ---- riser: gelap, lalu potongan rapat
    (45, 47, 24.80, 0.8, dict(zoom=[1.04, 1.08])),                        # shot gelap
    (47, 48, 17.60, 1.0, dict(zoom=[1.10, 1.14])),                        # ventilasi, kilat
    (48, DROP, 4.30, 0.6, dict(inn="focus", zoom=[1.22, 1.04])),          # lampu depan blur -> tajam, pull-back
    # ---- DROP: masuk lewat lampu depan, flash
    (DROP, 55, 0.90, 0.95, dict(inn="mask", ov=9, mask=HEADLIGHT, flash=True, lamps=HERO_LAMPS, zoom=[1.0, 1.07])),  # hero
    (55, 57, 3.25, 0.8, dict(zoom=[1.0, 1.30])),                          # velg, push-in kuat
    (57, 59, 15.90, 0.8, dict(zoom=[1.03, 1.08])),                        # instrumen
    (59, 61, 11.20, 0.8, dict(inn="whip", zoom=[1.04, 1.08])),            # kabin
    (61, 63, 14.30, 0.8, dict(zoom=[1.03, 1.08])),                        # head unit
    (63, 67, 28.00, 0.8, dict(zoom=[1.03, 1.09], bloom=[(65, *TAIL_34, "fire")])),  # rear 3/4 + semburan cahaya
    (67, 69, 29.39, 0.75, dict(light=TAIL, glow="red", zoom=[1.04, 1.0])), # lampu belakang
    (69, 71, 17.00, 0.8, dict(out="stretch", zoom=[1.03, 1.07])),         # setir -> glitch
    (71, 73, 5.06, 0.85, dict(zoom=[1.03, 1.07])),                        # grille miring
    (73, None, 6.33, 0.8, dict(zoom=[1.04, 1.08])),                       # grille + lis merah (sama dgn pembuka)
]

TITLE = dict(beat=DROP, until=55, main="NEW SIGRA", sub="1.2 R MT  ·  BRONZE METALLIC")


def fr(k):
    if k is None:
        return 0
    return round(BT[k] * FPS)


def main():
    total = round(DUR * FPS)
    shots = []
    for a, b, t, rate, o in SHOTS:
        f = fr(a)
        e = total if b is None else fr(b)
        s = dict(f=f, d=e - f, t=t, rate=rate, inn=o.get("inn", "cut"), out=o.get("out", "cut"),
                 ov=o.get("ov", 0), zoom=o.get("zoom", [1.03, 1.07]), pan=o.get("pan", 0))
        for k in ("light", "mask"):
            if k in o:
                s[k] = list(o[k])
        if "glow" in o:
            s["glow"] = o["glow"]
        if o.get("flash"):
            s["flash"] = True
            s["lamps"] = [list(p) for p in o.get("lamps", [])]
        if "bloom" in o:
            s["bloom"] = [dict(at=fr(k) - f, x=x, y=y, color=c) for k, x, y, c in o["bloom"]]
        # cek sumber cukup panjang (video asli 30 dtk, 38 fps)
        need = t - s["ov"] / FPS * rate, t + s["d"] / FPS * rate
        assert need[0] >= 0 and need[1] <= DUR + 0.01, (a, b, need)
        shots.append(s)

    title = dict(f=fr(TITLE["beat"]), d=fr(TITLE["until"]) - fr(TITLE["beat"]), main=TITLE["main"], sub=TITLE["sub"])
    data = dict(fps=FPS, durationInFrames=total, clip=CLIP, music="sigra_music.wav", shots=shots, title=title,
                beats=[fr(k) for k in range(len(BT))], drop=fr(DROP))
    with open("src/sigra.json", "w") as fh:
        json.dump(data, fh, indent=1)
    print(f"{len(shots)} shot, {total} frame -> src/sigra.json")


if __name__ == "__main__":
    main()
