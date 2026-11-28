"""Alat bersama untuk timeline gaya sinematik (dipakai build_sigra.py & build_ayla.py).

Hasil JSON dibaca oleh komponen Sinematik di src/SigraSinematik.tsx.
"""
import json
import sys

FPS = 30


# ---- lampu. Posisi (0-1) di dalam frame video asli.
# L(x, y, warna, ukuran px, nyala_di, terang_akhir, ground)
#   nyala_di: None = selalu menyala; ("b", k) = menyala tepat di ketukan k; angka = frame setelah shot mulai
#   ground: jarak (0-1) ke pantulan cahaya di lantai, None = tanpa pantulan
def L(x, y, c="white", size=60, at=None, hold=0.85, ground=None):
    return dict(x=x, y=y, c=c, size=size, at=at, hold=hold, ground=ground)


# ---- transisi masuk: (jenis, panjang frame, arah)
#   push  = layar lama terdorong keluar, baru masuk (whip blur searah), arah: l r u d
#   zoom  = zoom-through: lama membesar + blur, baru mengecil ke posisi
#   spin  = putar + zoom + blur (arah r = putar ke kanan)
#   slice = bilah-bilah vertikal naik bergantian (wipe bertangga)
#   leak  = light leak hangat menyapu layar, crossfade terang
#   blur  = blur dissolve lembut
#   mask  = shot baru muncul kecil di dalam lampu depan lalu membesar (selesai tepat di ketukan)
#   cut   = potong biasa
def T(kind="cut", n=0, d="l"):
    return dict(kind=kind, n=n, dir=d)


def build(*, bt, shots, texts, segs, dur, clip, music, out, drop):
    """bt: waktu ketukan (dtk). shots: (k0, k1, clip|None, detik, rate, opsi). texts: (k0, k1|None, judul, sub, pos, besar).
    segs: {clip: [(mulai, selesai), ...]} bagian bersih di video sumber (dtk) -> transisi tidak boleh keluar dari situ."""
    total = round(dur * FPS)

    def fr(k):
        return 0 if k is None else round(bt[k] * FPS)

    res = []
    for a, b, c, t, rate, o in shots:
        f = fr(a)
        e = total if b is None else fr(b)
        s = dict(f=f, d=e - f, clip=c or clip, t=t, rate=rate, tin=o.get("tin", T()), fx=o.get("fx", []),
                 zoom=o.get("zoom", [1.03, 1.07]), pan=o.get("pan", 0))
        if "mask" in o:
            s["mask"] = list(o["mask"])
        if "shade" in o:  # gelapkan bagian atas (mis. bekas teks bawaan)
            s["shade"] = o["shade"]
        if "lights" in o:
            s["lights"] = [dict(l, at=(fr(l["at"][1]) - f) if isinstance(l["at"], tuple) else l["at"]) for l in o["lights"]]
        res.append(s)

    # frame tambahan sebelum/sesudah potongan untuk transisi yang tumpang tindih
    bad = []
    for i, s in enumerate(res):
        n = s["tin"]["n"]
        s["pre"] = n if s["tin"]["kind"] == "mask" else n // 2
        nxt = res[i + 1]["tin"] if i + 1 < len(res) else T()
        s["post"] = 0 if nxt["kind"] in ("mask", "cut") else nxt["n"] - nxt["n"] // 2
        lo = s["t"] - s["pre"] / FPS * s["rate"]
        hi = s["t"] + (s["d"] + s["post"]) / FPS * s["rate"]
        seg = next((sg for sg in segs[s["clip"]] if sg[0] - 0.02 <= s["t"] < sg[1]), None)
        if seg is None:
            bad.append(f"shot {i} (f={s['f']}): detik {s['t']} di luar bagian bersih {s['clip']}")
        elif lo < seg[0] - 0.02 or hi > seg[1] + 0.02:
            bad.append(f"shot {i} (f={s['f']}): butuh {lo:.2f}-{hi:.2f} dtk, bagian bersih {seg[0]:.2f}-{seg[1]:.2f}")
    if bad:
        print("\n".join(bad))
        sys.exit(1)

    txt = [dict(f=fr(a), d=(total if b is None else fr(b)) - fr(a), main=m, sub=sb, pos=p, big=big) for a, b, m, sb, p, big in texts]
    data = dict(fps=FPS, durationInFrames=total, clip=clip, music=music, shots=res, texts=txt,
                beats=[fr(k) for k in range(len(bt))], drop=fr(drop))
    with open(out, "w") as fh:
        json.dump(data, fh, indent=1)
    print(f"{len(res)} shot, {len(txt)} teks, {total} frame -> {out}")
