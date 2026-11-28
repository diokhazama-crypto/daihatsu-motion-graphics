#!/usr/bin/env python3
"""Timeline SigraSinematik / SigraTerang -> src/sigra.json

Gaya editan meniru video referensi:
- tiap shot 2 ketukan (kadang 4), gerak kamera pelan (push-in / pull-back)
- lampu menyala (inti putih, bloom, flare, pantulan), rack focus, flash di drop
- transisi bervariasi & berpusat tepat di ketukan: push (whip blur), zoom, spin,
  slice (bilah bergantian), lightleak, blur dissolve, mask lewat lampu depan
- teks gaya judul "NEW SIGRA" di beberapa bagian
- shot terakhir = shot pembuka, jadi videonya nyambung saat di-loop

Lagu: audio asli video Sigra (152 BPM). Ketukan diukur dengan librosa;
bagian tenang sampai ~18 dtk, riser 18-20 dtk, DROP di ketukan 51 (20.13 dtk).
Potongan selalu di ketukan ganjil (= awal/tengah bar).
"""
import json
import sys

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

# batas shot di video asli (frame @38fps) -> transisi tidak boleh "bocor" ke shot sebelah
SRC_CUTS = [0, 94, 155, 192, 219, 278, 311, 342, 396, 455, 517, 574, 637, 697, 813, 870, 941, 998, 1061, 1117, 1140]
SRC_SEG = [(a / 38, b / 38) for a, b in zip(SRC_CUTS, SRC_CUTS[1:])]
SRC_SEG[0] = (0.56, SRC_SEG[0][1])  # awal video hitam + teks


# ---- lampu. Posisi (0-1) di dalam frame video asli.
# L(x, y, warna, ukuran px, nyala_di, terang_akhir, ground)
#   nyala_di: None = selalu menyala; ("b", k) = menyala tepat di ketukan k; angka = frame setelah shot mulai
#   ground: jarak (0-1) ke pantulan cahaya di lantai, None = tanpa pantulan
def L(x, y, c="white", size=60, at=None, hold=0.85, ground=None):
    return dict(x=x, y=y, c=c, size=size, at=at, hold=hold, ground=ground)


HEADLIGHT = (0.50, 0.46)                              # tengah lampu depan (dipakai transisi mask)
HEAD_ON = [L(0.47, 0.44, size=80, at=3, hold=0.9)]    # lampu depan menyala (shot detik 4.1-5.0)
HERO_ON = [L(0.42, 0.635, size=34, at=0, hold=0.9, ground=0.17), L(0.81, 0.62, size=26, at=0, hold=0.9, ground=0.16)]
TAIL_ON = [L(0.40, 0.47, "red", size=110, hold=0.75)]                     # close-up lampu belakang
REAR_ON = [L(0.51, 0.575, "red", size=46, hold=0.8), L(0.80, 0.745, "red", size=24, hold=0.7)]  # rear 3/4


# ---- transisi masuk: (jenis, panjang frame, arah)
#   push  = layar lama terdorong keluar, baru masuk (whip blur searah), arah: l r u d
#   zoom  = zoom-through: lama membesar + blur, baru mengecil ke posisi
#   spin  = putar + zoom + blur
#   slice = bilah-bilah vertikal masuk bergantian atas/bawah
#   leak  = light leak hangat menyapu layar, crossfade terang
#   blur  = blur dissolve lembut
#   mask  = shot baru muncul kecil di dalam lampu depan lalu membesar (selesai tepat di ketukan)
#   cut   = potong biasa
def T(kind="cut", n=0, d="l"):
    return dict(kind=kind, n=n, dir=d)


# (ketukan mulai, ketukan selesai, detik di video asli, playbackRate, opsi)
# None = awal / akhir video. rate 0.8 = kecepatan asli sebelum dipercepat 1.25x.
# opsi: tin = T(...), fx = [lightOn|focus|flash], zoom = [awal, akhir], pan = geser %, lights = [L(...)]
SHOTS = [
    # ---- eksterior detail
    (None, 1, 5.80, 0.8, dict(zoom=[1.02, 1.08])),                                     # grille + lis merah (pembuka = penutup)
    (1, 3, 2.62, 0.8, dict(tin=T("zoom", 8), zoom=[1.10, 1.02])),                      # velg, pull-back
    (3, 5, 7.44, 0.8, dict(tin=T("push", 8, "l"), zoom=[1.03, 1.07], pan=-1.5)),       # spion
    (5, 7, 4.12, 0.8, dict(fx=["lightOn"], lights=HEAD_ON, zoom=[1.02, 1.06])),       # lampu depan MENYALA
    (7, 11, 28.06, 0.74, dict(tin=T("spin", 10), lights=REAR_ON, zoom=[1.03, 1.09])),  # rear 3/4
    (11, 13, 29.50, 0.52, dict(tin=T("leak", 12), lights=TAIL_ON, zoom=[1.08, 1.03])), # lampu belakang
    (13, 15, 5.17, 0.63, dict(tin=T("slice", 10), zoom=[1.03, 1.07])),                  # grille miring
    (15, 17, 8.30, 0.78, dict(tin=T("push", 8, "r"), zoom=[1.04, 1.08])),               # handle pintu
    # ---- interior: aksen merah
    (17, 21, 9.11, 0.75, dict(tin=T("zoom", 8), zoom=[1.02, 1.08])),                    # panel pintu merah
    (21, 23, 10.55, 0.8, dict(tin=T("blur", 8), zoom=[1.06, 1.02])),                   # kabin + dashboard merah
    (23, 27, 12.09, 0.8, dict(tin=T("push", 8, "u"), zoom=[1.02, 1.06])),              # dashboard lewat pilar
    (27, 29, 13.75, 0.8, dict(tin=T("slice", 10), zoom=[1.03, 1.07])),                 # head unit
    (29, 31, 15.20, 0.8, dict(fx=["lightOn"], zoom=[1.02, 1.06])),                    # panel instrumen menyala
    (31, 35, 16.90, 0.8, dict(tin=T("spin", 10), zoom=[1.02, 1.07], pan=1.5)),         # setir + ventilasi merah
    (35, 37, 21.50, 0.8, dict(tin=T("push", 8, "l"), zoom=[1.04, 1.08])),              # jok depan
    (37, 39, 23.05, 0.8, dict(tin=T("slice", 10), zoom=[1.03, 1.07])),                 # jok tengah
    (39, 43, 18.46, 0.8, dict(tin=T("zoom", 8), zoom=[1.02, 1.07])),                   # kabin dari belakang
    (43, 45, 26.36, 0.8, dict(tin=T("blur", 8), zoom=[1.03, 1.06])),                   # baris ke-3
    # ---- riser: potongan makin rapat
    (45, 47, 22.15, 0.8, dict(tin=T("push", 8, "r"), zoom=[1.04, 1.09])),              # jok, dari pintu
    (47, 48, 17.62, 1.0, dict(tin=T("zoom", 6), zoom=[1.10, 1.14])),                   # ventilasi, kilat
    (48, DROP, 4.32, 0.6, dict(fx=["focus"], lights=[L(0.47, 0.44, size=80, at=("b", 49), hold=1.0)], zoom=[1.22, 1.04])),  # lampu depan blur -> tajam -> menyala
    # ---- DROP: masuk lewat lampu depan, flash
    (DROP, 55, 0.90, 0.9, dict(tin=T("mask", 9), mask=HEADLIGHT, fx=["flash"], lights=HERO_ON, shade=0.75, zoom=[1.0, 1.07])),  # hero
    (55, 57, 3.30, 0.8, dict(tin=T("zoom", 6), zoom=[1.0, 1.28])),                     # velg, push-in kuat
    (57, 59, 15.95, 0.8, dict(tin=T("push", 6, "u"), zoom=[1.03, 1.08])),              # instrumen
    (59, 61, 11.15, 0.8, dict(tin=T("spin", 8), zoom=[1.04, 1.08])),                   # kabin
    (61, 63, 14.35, 0.8, dict(tin=T("slice", 8), zoom=[1.03, 1.08])),                  # head unit
    (63, 67, 28.01, 0.76, dict(tin=T("push", 6, "l"), lights=REAR_ON, zoom=[1.03, 1.09])),  # rear 3/4
    (67, 69, 29.50, 0.56, dict(tin=T("leak", 10), lights=TAIL_ON, zoom=[1.04, 1.0])),   # lampu belakang
    (69, 71, 17.05, 0.8, dict(tin=T("push", 6, "r"), zoom=[1.03, 1.07])),              # setir
    (71, 73, 5.155, 0.63, dict(tin=T("spin", 8), zoom=[1.03, 1.07])),                    # grille miring
    (73, None, 6.38, 0.8, dict(tin=T("blur", 8), zoom=[1.04, 1.08])),                  # grille + lis merah (= pembuka)
]

# ---- teks: (ketukan mulai, ketukan selesai, judul, sub, posisi top|bottom, besar)
TEXTS = [
    (1, 5, "DESAIN SPORTY", "VELG ALLOY  ·  AKSEN MERAH", "bottom", False),
    (17, 23, "INTERIOR", "SENTUHAN MERAH YANG BERANI", "top", False),
    (27, 31, "FITUR LENGKAP", "HEAD UNIT LAYAR SENTUH", "top", False),
    (35, 43, "7 PENUMPANG", "TIGA BARIS KURSI", "bottom", False),
    (DROP, 55, "NEW SIGRA", "1.2 R MT  ·  BRONZE METALLIC", "bottom", True),
]


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
        tin = o.get("tin", T())
        s = dict(f=f, d=e - f, t=t, rate=rate, tin=tin, fx=o.get("fx", []), zoom=o.get("zoom", [1.03, 1.07]), pan=o.get("pan", 0))
        if "mask" in o:
            s["mask"] = list(o["mask"])
        if "shade" in o:  # gelapkan bagian atas (bekas teks bawaan)
            s["shade"] = o["shade"]
        if "lights" in o:
            s["lights"] = [dict(l, at=(fr(l["at"][1]) - f) if isinstance(l["at"], tuple) else l["at"]) for l in o["lights"]]
        shots.append(s)

    # frame tambahan sebelum/sesudah potongan untuk transisi yang tumpang tindih
    bad = []
    for i, s in enumerate(shots):
        n = s["tin"]["n"]
        s["pre"] = n if s["tin"]["kind"] == "mask" else n // 2
        nxt = shots[i + 1]["tin"] if i + 1 < len(shots) else T()
        s["post"] = 0 if nxt["kind"] in ("mask", "cut") else nxt["n"] - nxt["n"] // 2
        lo = s["t"] - s["pre"] / FPS * s["rate"]
        hi = s["t"] + (s["d"] + s["post"]) / FPS * s["rate"]
        seg = next((sg for sg in SRC_SEG if sg[0] - 0.02 <= s["t"] < sg[1]), None)
        if seg is None or lo < seg[0] - 0.02 or hi > seg[1] + 0.02:
            bad.append(f"shot {i} (f={s['f']}): butuh {lo:.2f}-{hi:.2f} dtk, segmen {seg[0]:.2f}-{seg[1]:.2f}" if seg else f"shot {i}: t di luar segmen")
    if bad:
        print("\n".join(bad))
        sys.exit(1)

    texts = [dict(f=fr(a), d=fr(b) - fr(a), main=m, sub=sb, pos=p, big=big) for a, b, m, sb, p, big in TEXTS]
    data = dict(fps=FPS, durationInFrames=total, clip=CLIP, music="sigra_music.wav", shots=shots, texts=texts,
                beats=[fr(k) for k in range(len(BT))], drop=fr(DROP))
    with open("src/sigra.json", "w") as fh:
        json.dump(data, fh, indent=1)
    print(f"{len(shots)} shot, {len(texts)} teks, {total} frame -> src/sigra.json")


if __name__ == "__main__":
    main()
