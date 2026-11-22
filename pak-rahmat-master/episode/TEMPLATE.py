"""TEMPLATE EPISODE BARU. Salin jadi episode/ep<N>.py, lalu isi adegan sesuai narasi (words.json).
Contoh lengkap semua teknik: episode/ep4.py (grep -n "def sc_" episode/ep4.py untuk melihat adegannya).
Fungsi gambar tetap: lihat README.md bagian "Daftar aset" (jangan menggambar ulang tokoh/toko/mobil).
"""
from aset_dio import *          # W, H, hx, CH, street, rahmat_po, dio_po, SERIUS, pose_seq, card, bubble, ... + modul E, P, G, lib
import gaya

N = 0                                   # nomor episode
VDUR = gaya.durasi_suara()              # panjang narasi (otomatis dari audio.wav)
DUR = round(VDUR + 2.7, 2)              # + kartu penutup
HOOK = ("HOOK 1-3 KATA?!", 2.2)         # teks besar di detik pertama, hilang di detik ke-2,2
PUNCH = (0.12,)                         # zoom hentak, MAKS 2 (kamera tenang)
BERSAMBUNG = VDUR - 1.0                 # kartu "BERSAMBUNG..." (None = tanpa)
CTA = dict(baris1="PERTANYAAN BARIS 1", baris2="BARIS 2?",
           pilihan=[("PILIHAN A", '#2E6BD6'), ("PILIHAN B", '#D7141A')])
SUASANA = []                            # [(t0, t1, 'tense'|'warm'|'morning'|'freeze')], selain itu 'day'

RAHMAT_SPEAK = []                       # [(t0, t1)] saat Pak Rahmat bicara (mulut ikut suara)
DIO_SPEAK = []


# ------------------------------------------------------------ adegan: fungsi(c, t, t0)
def sc_depan_toko(c, t, t0):
    m_r = talk(t, RAHMAT_SPEAK); m_d = talk(t, DIO_SPEAK)
    street(c, t, [rahmat_po(**SERIUS, mouth=m_r),
                  dio_po(aF=(30, 0), aB=(10, 0), eyes='open', expr='smile', mouth=m_d)])


SCENES = [
    # (mulai, selesai, fungsi, kamera)  kamera = [(detik, cx, cy, zoom), ...] (zoom > 1,3 = latar blur otomatis)
    (0.0, DUR + 1, sc_depan_toko, [(0, 1190, 1170, 1.3), (DUR, 1190, 1170, 1.35)]),
]


# ------------------------------------------------------------ opsional
def akting(who, t, po):                 # ubah pose tokoh per waktu (po = dict pose)
    pass

def efek_bawah(c, t):                   # sebelum grading: garis fokus, hujan, kilat
    E.focus_lines(c, t, 0.1, 0.9, cy=H * .45)

def efek_atas(c, t):                    # sesudah grading: label/pill, confetti
    pass


def suara(S):
    S.musik([(0.0, S.DUR, S.section(S.DUR + .5, 108, S.C, S.CB, S.FULL, .95))])
    S.put(S.thud(), 0.15, .5); S.put(S.boing(), 0.2, .22)
    S.put_amb(S.birds(min(30, S.DUR), 18), 0.0, .06)
    t_cta = VDUR + .25
    S.put(S.pop(), t_cta, .4); S.put(S.chime(), t_cta + .05, .35)
