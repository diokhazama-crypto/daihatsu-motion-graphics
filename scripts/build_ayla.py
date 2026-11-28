#!/usr/bin/env python3
"""Timeline AylaTerang -> src/ayla.json (gaya sama dengan SigraTerang).

Footage (sudah di-grade dengan prep_sigra.py --terang):
  ayla_a = Ayla 1.2 R CVT Ultra Black Solid di gedung parkir (video A, 58 dtk, sudah berisi transisi bawaan)
  ayla_b = Ayla merah di showroom (video B, 20 dtk)
Lagu: mp3 14.34 dtk (152 BPM) diputar 2x (scripts/prep_ayla_music.sh) -> 28.71 dtk.
Tiap putaran: hentakan 0-1.6 dtk, bagian tenang 1.6-6.4 dtk, DROP di ketukan 16.
Putaran 1 = Ayla hitam, putaran 2 = Ayla merah + kabin, penutup = shot pembuka (bisa di-loop).
Potongan di ketukan genap (tiap 2 ketukan ~0.8 dtk).
"""
from timeline import L, T, build

LOOP = 14.37  # putaran kedua mulai di sini
DUR = 28.71
BT1 = [0.07, 0.44, 0.84, 1.25, 1.65, 2.04, 2.44, 2.86, 3.25, 3.65, 4.04, 4.44, 4.85, 5.25, 5.64, 6.06, 6.46, 6.85,
       7.24, 7.66, 8.06, 8.45, 8.85, 9.26, 9.66, 10.05, 10.45, 10.84, 11.24, 11.66, 12.05, 12.45, 12.84, 13.24, 13.63]
BT = BT1 + [round(b + LOOP, 2) for b in BT1]
N = len(BT1)  # ketukan putaran 2 = P(k)


def P(k):
    return N + k


DROP = 16
DROP2 = P(16)

# bagian bersih di video sumber (dtk). Dilewati: frame noise warna-warni (A 6.9), layar kamera HP (A 26),
# tangan membuka bagasi (A 41-44), transisi bawaan video A di antara shot.
# Tidak dipakai karena badge "CVT" terbaca: lampu belakang close-up (A 34.6-37.85) & tampak belakang lurus (A 48.3-51.35).
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
    # ===== putaran 1: Ayla hitam
    (None, 2, "ayla_a", 55.20, 0.8, dict(zoom=[1.02, 1.08])),                                   # hero sudut rendah (= penutup)
    (2, 4, "ayla_a", 3.85, 0.8, dict(tin=T("zoom", 8), fx=["lightOn"], lights=HEAD_ON, zoom=[1.03, 1.08])),  # lampu depan MENYALA
    (4, 6, "ayla_a", 7.30, 0.8, dict(tin=T("push", 8, "l"), zoom=[1.03, 1.07])),                # grille sudut rendah
    (6, 8, "ayla_a", 10.70, 0.8, dict(tin=T("spin", 8), zoom=[1.08, 1.02])),                    # velg
    (8, 10, "ayla_a", 14.20, 0.8, dict(tin=T("slice", 10), zoom=[1.03, 1.08])),                 # spion
    (10, 12, "ayla_a", 24.35, 0.8, dict(tin=T("push", 8, "u"), zoom=[1.03, 1.07])),             # tuas transmisi (tanpa teks)
    (12, 14, "ayla_a", 27.78, 0.8, dict(tin=T("zoom", 8), zoom=[1.02, 1.07])),                  # setir
    (14, DROP, "ayla_a", 4.60, 0.6, dict(fx=["focus"], lights=[L(0.52, 0.46, size=80, at=("b", 15), hold=1.0)], zoom=[1.2, 1.04])),  # lampu blur -> tajam -> menyala
    (DROP, 20, "ayla_a", 51.90, 0.85, dict(tin=T("mask", 9), mask=HEADLIGHT, fx=["flash"], lights=FRONT_ON, zoom=[1.0, 1.06])),  # DROP: tampak depan
    (20, 22, "ayla_a", 39.40, 0.8, dict(tin=T("push", 6, "l"), zoom=[1.03, 1.08])),             # emblem AYLA
    (22, 24, "ayla_a", 17.50, 0.8, dict(tin=T("spin", 8, "r"), zoom=[1.03, 1.08])),             # handle pintu
    (24, 26, "ayla_a", 33.10, 0.8, dict(tin=T("slice", 8), zoom=[1.03, 1.08])),                 # belakang 3/4
    (26, 28, "ayla_b", 13.20, 0.8, dict(tin=T("push", 6, "r"), zoom=[1.03, 1.08])),             # depan 3/4 merah (cuplikan)
    (28, 30, "ayla_a", 21.20, 0.8, dict(tin=T("zoom", 6), zoom=[1.03, 1.08])),                  # kabin
    (30, 32, "ayla_a", 16.20, 0.8, dict(tin=T("push", 6, "l"), zoom=[1.03, 1.08])),             # spion
    (32, P(0), "ayla_a", 53.50, 0.8, dict(tin=T("blur", 8), zoom=[1.02, 1.08])),                # tampak depan, menuju putaran 2
    # ===== putaran 2: Ayla merah + kabin (sambungan lagu: light leak lembut)
    (P(0), P(4), "ayla_b", 0.90, 0.8, dict(tin=T("leak", 12), zoom=[1.02, 1.08])),              # Ayla merah di showroom
    (P(4), P(6), "ayla_b", 6.10, 0.8, dict(tin=T("push", 8, "l"), zoom=[1.03, 1.08])),          # depan merah + emblem
    (P(6), P(8), "ayla_b", 9.40, 0.8, dict(tin=T("spin", 8, "r"), zoom=[1.04, 1.08])),          # belakang merah
    (P(8), P(10), "ayla_a", 12.00, 0.8, dict(tin=T("slice", 10), zoom=[1.03, 1.08])),           # velg
    (P(10), P(12), "ayla_b", 15.40, 0.8, dict(tin=T("push", 8, "r"), zoom=[1.04, 1.08])),       # kabin dari pintu
    (P(12), P(14), "ayla_b", 18.10, 0.8, dict(tin=T("zoom", 8), zoom=[1.03, 1.08])),            # dashboard
    (P(14), DROP2, "ayla_a", 5.20, 0.6, dict(fx=["focus"], lights=[L(0.52, 0.46, size=80, at=("b", P(15)), hold=1.0)], zoom=[1.2, 1.04])),  # lampu -> menyala
    (DROP2, P(20), "ayla_b", 3.20, 0.85, dict(tin=T("mask", 9), mask=HEADLIGHT, fx=["flash"], zoom=[1.0, 1.06])),  # DROP 2: Ayla merah
    (P(20), P(22), "ayla_a", 38.20, 0.8, dict(tin=T("push", 6, "l"), zoom=[1.03, 1.08])),       # emblem AYLA hitam
    (P(22), P(24), "ayla_b", 12.20, 0.8, dict(tin=T("spin", 8), zoom=[1.03, 1.08])),            # depan 3/4 merah
    (P(24), P(26), "ayla_a", 15.50, 0.8, dict(tin=T("slice", 8), zoom=[1.03, 1.08])),           # spion
    (P(26), P(28), "ayla_b", 7.30, 0.8, dict(tin=T("push", 6, "r"), zoom=[1.03, 1.08])),        # depan merah
    (P(28), P(30), "ayla_a", 9.30, 0.8, dict(tin=T("zoom", 6), zoom=[1.03, 1.08])),             # grille
    (P(30), P(32), "ayla_a", 12.85, 0.8, dict(tin=T("push", 6, "u"), zoom=[1.03, 1.08])),       # velg
    (P(32), None, "ayla_a", 55.20, 0.8, dict(tin=T("blur", 8), zoom=[1.02, 1.08])),             # hero (= pembuka)
]

# (ketukan mulai, ketukan selesai, judul, sub, posisi top|bottom, besar)
# Catatan: transmisi / CVT sengaja tidak dibahas (shot dengan badge "CVT" juga tidak dipakai).
TEXTS = [
    (0, 4, "SIAP TAMPIL BEDA?", "ALL NEW AYLA", "bottom", False),
    (4, 8, "DESAIN SPORTY", "TAMPANG BARU YANG LEBIH BERANI", "top", False),
    (DROP, 20, "ALL NEW AYLA", "1.2 R", "top", True),
    (22, 26, "ULTRA BLACK SOLID", "ELEGAN DARI SEGALA SISI", "top", False),
    (P(0), P(4), "PILIH WARNAMU", "HITAM ATAU MERAH", "top", False),
    (P(10), P(14), "KABIN MODERN", "NYAMAN DI SETIAP PERJALANAN", "top", False),
    (DROP2, P(20), "SIAP DIBAWA\nKE MANA SAJA", "LINCAH DI JALAN KOTA", "top", True),
    (P(32), None, "TEST DRIVE SEKARANG", "HUBUNGI KAMI", "bottom", False),
]

if __name__ == "__main__":
    build(bt=BT, shots=SHOTS, texts=TEXTS, segs=SEGS, dur=DUR, clip="ayla_a", music="ayla_music.wav",
          out="src/ayla.json", drop=DROP)
