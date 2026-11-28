#!/usr/bin/env python3
"""Timeline AylaTerang -> src/ayla.json (gaya sama dengan SigraTerang).

Footage (sudah di-grade dengan prep_sigra.py --terang):
  ayla_a = Ayla 1.2 R CVT Ultra Black Solid di gedung parkir (video A, 58 dtk, sudah berisi transisi bawaan)
  ayla_b = Ayla merah di showroom (video B, 20 dtk)
Lagu: SSSTopTop mp3, 14.37 dtk, 152 BPM. Hentakan 0-1.6 dtk, bagian tenang 1.6-6.4 dtk, DROP 6.46 dtk (ketukan 16).
Potongan di ketukan genap (tiap 2 ketukan ~0.8 dtk).
"""
from timeline import L, T, build

DUR = 14.37
BT = [0.07, 0.44, 0.84, 1.25, 1.65, 2.04, 2.44, 2.86, 3.25, 3.65, 4.04, 4.44, 4.85, 5.25, 5.64, 6.06, 6.46, 6.85,
      7.24, 7.66, 8.06, 8.45, 8.85, 9.26, 9.66, 10.05, 10.45, 10.84, 11.24, 11.66, 12.05, 12.45, 12.84, 13.24, 13.63]
DROP = 16

# bagian bersih di video sumber (dtk). Dilewati: frame noise warna-warni (A 6.9), layar kamera HP (A 26),
# tangan membuka bagasi (A 41-44), transisi bawaan video A di antara shot.
SEGS = {
    "ayla_a": [(0.5, 3.3), (3.7, 6.85), (7.05, 10.1), (10.5, 13.65), (14.0, 17.0), (17.3, 20.5), (21.0, 24.1),
               (24.25, 25.8), (27.65, 29.25), (33.0, 34.35), (34.6, 37.85), (38.0, 40.9), (45.0, 48.1),
               (48.3, 51.35), (51.6, 54.98), (55.1, 57.5)],
    "ayla_b": [(0.6, 5.75), (5.95, 8.65), (9.15, 11.75), (11.9, 14.45), (15.2, 17.75), (17.9, 20.4)],
}

HEADLIGHT = (0.52, 0.46)  # lampu depan di close-up (video A 3.7-6.8 dtk)
HEAD_ON = [L(0.52, 0.46, size=80, at=3, hold=0.9)]
FRONT_ON = [L(0.16, 0.64, size=30, at=0, hold=0.9, ground=0.13), L(0.81, 0.645, size=30, at=0, hold=0.9, ground=0.13)]

# (ketukan mulai, ketukan selesai, klip, detik di video sumber, playbackRate, opsi)
SHOTS = [
    # ---- hentakan pembuka
    (None, 2, "ayla_a", 55.20, 0.8, dict(zoom=[1.02, 1.08])),                                   # hero hitam sudut rendah (= penutup)
    (2, 4, "ayla_a", 3.85, 0.8, dict(tin=T("zoom", 8), fx=["lightOn"], lights=HEAD_ON, zoom=[1.03, 1.08])),  # lampu depan MENYALA
    # ---- bagian tenang: detail
    (4, 6, "ayla_a", 7.30, 0.8, dict(tin=T("push", 8, "l"), zoom=[1.03, 1.07])),                # grille sudut rendah
    (6, 8, "ayla_a", 10.70, 0.8, dict(tin=T("spin", 8), zoom=[1.08, 1.02])),                    # velg
    (8, 10, "ayla_b", 6.10, 0.8, dict(tin=T("slice", 10), zoom=[1.03, 1.08])),                  # depan merah + emblem AYLA
    (10, 12, "ayla_a", 24.35, 0.8, dict(tin=T("push", 8, "u"), zoom=[1.03, 1.07])),             # tuas CVT
    (12, 14, "ayla_a", 27.78, 0.8, dict(tin=T("zoom", 8), zoom=[1.02, 1.07])),                  # setir
    (14, DROP, "ayla_a", 4.60, 0.6, dict(fx=["focus"], lights=[L(0.52, 0.46, size=80, at=("b", 15), hold=1.0)], zoom=[1.2, 1.04])),  # lampu blur -> tajam -> menyala
    # ---- DROP: masuk lewat lampu depan
    (DROP, 20, "ayla_a", 51.90, 0.85, dict(tin=T("mask", 9), mask=HEADLIGHT, fx=["flash"], lights=FRONT_ON, zoom=[1.0, 1.06])),  # tampak depan hitam
    (20, 22, "ayla_a", 34.80, 0.8, dict(tin=T("push", 6, "l"), zoom=[1.03, 1.08])),             # lampu belakang + badge CVT
    (22, 24, "ayla_b", 1.20, 0.8, dict(tin=T("leak", 10), zoom=[1.03, 1.08])),                  # Ayla merah di showroom
    (24, 26, "ayla_b", 9.40, 0.8, dict(tin=T("spin", 8, "r"), zoom=[1.04, 1.08])),              # belakang merah
    (26, 28, "ayla_a", 38.20, 0.8, dict(tin=T("push", 6, "r"), zoom=[1.03, 1.08])),             # emblem AYLA hitam
    (28, 30, "ayla_b", 18.10, 0.8, dict(tin=T("slice", 8), zoom=[1.03, 1.08])),                 # dashboard
    (30, 32, "ayla_b", 15.40, 0.8, dict(tin=T("push", 6, "l"), zoom=[1.04, 1.08])),             # kabin dari pintu
    (32, None, "ayla_a", 56.00, 0.8, dict(tin=T("blur", 8), zoom=[1.04, 1.10])),                # hero hitam (= pembuka)
]

# (ketukan mulai, ketukan selesai, judul, sub, posisi top|bottom, besar)
TEXTS = [
    (0, 4, "SIAP TAMPIL BEDA?", "ALL NEW AYLA", "bottom", False),
    (4, 8, "DESAIN SPORTY", "TAMPANG BARU YANG LEBIH BERANI", "top", False),
    (10, 14, "TRANSMISI CVT", "NYAMAN TANPA KOPLING", "top", False),
    (DROP, 20, "ALL NEW AYLA", "1.2 R CVT", "top", True),
    (22, 26, "PILIH WARNAMU", "HITAM ATAU MERAH", "top", False),
    (28, 32, "KABIN MODERN", "NYAMAN DI SETIAP PERJALANAN", "top", False),
    (32, None, "TEST DRIVE SEKARANG", "HUBUNGI KAMI", "bottom", False),
]

if __name__ == "__main__":
    build(bt=BT, shots=SHOTS, texts=TEXTS, segs=SEGS, dur=DUR, clip="ayla_a", music="ayla_music.wav",
          out="src/ayla.json", drop=DROP)
