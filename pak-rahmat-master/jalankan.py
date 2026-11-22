#!/usr/bin/env python3
"""KODE MASTER PAK RAHMAT - satu pintu untuk semua langkah episode.

  python3 jalankan.py <N> siap <file_audio>     audio -> kerja/ep<N>/ (audio_mentah.wav, audio.wav) + transkrip
                                                 (faster-whisper small, id) -> words_mentah.json, words.json, teks polos
  python3 jalankan.py <N> cek <dtk> [<dtk> ...]  1 gambar gabungan lebar 540 px -> kerja/ep<N>/cek.png
  python3 jalankan.py <N> render [--seg 1,3] [--n 4]
                                                 suara (mix_pro.wav) + render segmen paralel + gabung
                                                 -> kerja/ep<N>/PakRahmat_GranMax_ep<N>_PROPLUS.mp4
                                                 --seg: render ulang segmen tertentu saja (revisi), sisanya dipakai ulang
  python3 jalankan.py <N> arsip                  kerja/ep<N>/arsip/: narasi MP3 + words.json + ep<N>.py ber-awalan arsip

Adegan episode ada di episode/ep<N>.py (salin episode/TEMPLATE.py untuk episode baru; contoh lengkap episode/ep4.py).
"""
import os, sys, json, shutil, subprocess, importlib

ROOT = os.path.dirname(os.path.abspath(__file__))
PREFIX = "PakRahmat_GranMax_ep{n}__"
FINAL = "PakRahmat_GranMax_ep{n}_PROPLUS.mp4"

# koreksi nama/merek yang sering salah dari transkrip otomatis (kata -> kata)
KOREKSI = {"Grand": "Gran", "grand": "Gran", "Diyo": "Dio", "Diyo,": "Dio,", "Celes": "sales", "Seles": "sales",
           "Bersampung.": "Bersambung.", "Bersampung": "Bersambung", "Wala,": "Walah,", "Wala": "Walah",
           "Daihatzu": "Daihatsu", "Dayhatsu": "Daihatsu", "Rahmad": "Rahmat", "Rahmad,": "Rahmat,"}


def kerja(n):
    d = os.path.join(ROOT, "kerja", f"ep{n}")
    os.makedirs(d, exist_ok=True)
    return d


def ff(*args):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *args], check=True)


def muat_episode(n):
    os.chdir(kerja(n))
    sys.path[:0] = [ROOT, os.path.join(ROOT, "episode")]
    import gaya
    ep = importlib.import_module(f"ep{n}")
    gaya.pasang(ep)
    return gaya, ep


# ------------------------------------------------------------ siap: audio + transkrip
def siap(n, src):
    d = kerja(n)
    ext = os.path.splitext(src)[1].lower() or ".wav"
    raw = os.path.join(d, "audio_mentah" + ext)
    if os.path.abspath(src) != raw: shutil.copy(src, raw)
    if ext != ".wav": ff("-i", raw, os.path.join(d, "audio_mentah.wav"))
    ff("-i", os.path.join(d, "audio_mentah.wav"), "-ac", "1", "-ar", "24000", os.path.join(d, "audio.wav"))
    import numpy as np
    from faster_whisper import WhisperModel
    pcm = subprocess.run(["ffmpeg", "-v", "quiet", "-i", os.path.join(d, "audio_mentah.wav"), "-ac", "1", "-ar", "16000",
                          "-f", "f32le", "-"], capture_output=True).stdout
    audio = np.frombuffer(pcm, np.float32)        # array, bukan path (PyAV kadang gagal membaca file langsung)
    model = WhisperModel("small", device="cpu", compute_type="int8")
    segs, _ = model.transcribe(audio, language="id", word_timestamps=True, beam_size=5)
    words = []
    for s in segs:
        for w in s.words:
            k = w.word.strip()
            if k: words.append([KOREKSI.get(k, k), round(w.start, 2), round(w.end, 2)])
    json.dump(words, open(os.path.join(d, "words_mentah.json"), "w"), ensure_ascii=False)
    if not os.path.exists(os.path.join(d, "words.json")):
        json.dump(words, open(os.path.join(d, "words.json"), "w"), ensure_ascii=False)
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                os.path.join(d, "audio.wav")], capture_output=True, text=True).stdout)
    print(" ".join(w[0] for w in words))
    print(f"\n[{len(words)} kata, narasi {dur:.2f} dtk] koreksi di kerja/ep{n}/words.json (format [kata, mulai, selesai])")


# ------------------------------------------------------------ cek gambar
def cek(n, times):
    gaya, ep = muat_episode(n)
    from PIL import Image
    tw, th = 180, 320
    cols = min(3, len(times)); rows = (len(times) + cols - 1) // cols
    sheet = Image.new("RGB", (tw * cols, th * rows), (0, 0, 0))
    for i, ts in enumerate(times):
        data = gaya.render(int(float(ts) * gaya.FPS))
        im = Image.frombuffer("RGBA", (gaya.W, gaya.H), data, "raw", "BGRA", 0, 1).convert("RGB").resize((tw, th), Image.LANCZOS)
        sheet.paste(im, ((i % cols) * tw, (i // cols) * th))
    if sheet.width < 540:
        sheet = sheet.resize((540, int(sheet.height * 540 / sheet.width)), Image.LANCZOS)
    out = os.path.join(kerja(n), "cek.png"); sheet.save(out)
    print(out)


# ------------------------------------------------------------ render
def _seg(n, i, k):
    gaya, ep = muat_episode(n)
    W, H, FPS = gaya.W, gaya.H, gaya.FPS
    NF = int(ep.DUR * FPS)
    a, b = NF * i // k, NF * (i + 1) // k
    p = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{W}x{H}", "-r", str(FPS),
                          "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "15", "-pix_fmt", "yuv420p", "-threads", "1",
                          f"xseg{i}.mp4"], stdin=subprocess.PIPE)
    for f in range(a, b):
        p.stdin.write(gaya.render(f))
        if (f - a) % 150 == 0: open(f"xprog{i}.txt", "w").write(f"{(f - a) / (b - a) * 100:.0f}")
    p.stdin.close(); p.wait()
    open(f"xprog{i}.txt", "w").write("100")


def suara(n):
    gaya, ep = muat_episode(n)
    if not hasattr(ep, 'suara'):          # audio final dari pengguna: pakai apa adanya
        ff("-i", "audio_mentah.wav", "-af", f"apad=whole_dur={ep.DUR}", "-ar", "44100", "mix_pro.wav")
        return
    import sfx_alat as S
    S.mulai(ep.DUR)
    ep.suara(S)
    S.campur("audio_mentah.wav", "mix_pro.wav")


def render(n, segs=None, k=None):
    d = kerja(n)
    k = k or os.cpu_count() or 4
    me = os.path.abspath(__file__)
    jobs = [subprocess.Popen([sys.executable, me, str(n), "_suara"])]
    todo = segs if segs is not None else list(range(k))
    for i in todo:
        jobs.append(subprocess.Popen([sys.executable, me, str(n), "_seg", str(i), str(k)]))
    if any(j.wait() for j in jobs): sys.exit("render gagal (lihat error di atas)")
    with open(os.path.join(d, "list.txt"), "w") as f:
        for i in range(k): f.write(f"file 'xseg{i}.mp4'\n")
    out = os.path.join(d, FINAL.format(n=n))
    ff("-f", "concat", "-safe", "0", "-i", os.path.join(d, "list.txt"), "-i", os.path.join(d, "mix_pro.wav"),
       "-c:v", "libx264", "-b:v", "11M", "-maxrate", "14M", "-bufsize", "22M", "-pix_fmt", "yuv420p",
       "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", out)
    print(out, f"{os.path.getsize(out) / 1e6:.1f} MB")


# ------------------------------------------------------------ arsip
def arsip(n):
    d = kerja(n); a = os.path.join(d, "arsip"); os.makedirs(a, exist_ok=True)
    pre = PREFIX.format(n=n)
    ff("-i", os.path.join(d, "audio_mentah.wav"), "-codec:a", "libmp3lame", "-b:a", "128k", os.path.join(a, pre + "narasi.mp3"))
    shutil.copy(os.path.join(d, "words.json"), os.path.join(a, pre + "words.json"))
    shutil.copy(os.path.join(ROOT, "episode", f"ep{n}.py"), os.path.join(a, pre + f"ep{n}.py"))
    for f in sorted(os.listdir(a)): print(os.path.join(a, f))


if __name__ == "__main__":
    if len(sys.argv) < 3: sys.exit(__doc__)
    n, cmd, rest = int(sys.argv[1]), sys.argv[2], sys.argv[3:]
    if cmd == "siap": siap(n, rest[0])
    elif cmd == "cek": cek(n, rest)
    elif cmd == "render":
        segs = k = None
        if "--seg" in rest: segs = [int(x) for x in rest[rest.index("--seg") + 1].split(",")]
        if "--n" in rest: k = int(rest[rest.index("--n") + 1])
        render(n, segs, k)
    elif cmd == "arsip": arsip(n)
    elif cmd == "_seg": _seg(n, int(rest[0]), int(rest[1]))
    elif cmd == "_suara": suara(n)
    else: sys.exit(__doc__)
