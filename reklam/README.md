# RE/MAX Doğuş — Kariyer Reklam Filmi

`reklam-filmi.mp4` · 1080×1920 (9:16, Reels/Story/TikTok) · 34 sn · 30 fps · müzikli

Kariyer sayfasındaki (`../index.html`) içerik, renkler (RE/MAX lacivert/kırmızı), fontlar (Archivo + Manrope), logo, balon ve hero videosuyla hazırlandı.

| Süre | Sahne |
|---|---|
| 0–5 sn | Hero videosu · "Kariyerin tam burada yükseliyor." |
| 5–10 sn | Sayaçlar: 11.729 konut · 110+ ülke · 11 ders · 2 pazar |
| 10–15 sn | Neden RE/MAX Doğuş? Bölge · Eğitim · Teknoloji · Global |
| 15–21 sn | Doğuşla 1. Vites: 11 basamak (DOĞ → ZİRVE), balon yükselir |
| 21–26 sn | Maaş tavanı yok: grafik tavanı kırar · Fikirtepe, K. Kıbrıs, Golden Visa, Dubai, Londra |
| 26–30 sn | Deneyim aramıyoruz. Karakter arıyoruz. |
| 30–34 sn | Masanız hazır. Sıra sizde. · Hemen Başvur · yenifikirtepeburada.com |

## Yeniden üretme

Gerekenler: Node + Playwright (Chromium), ffmpeg (libx264), Python 3 + numpy + scipy.

```sh
cd reklam
mkdir -p build/hero
ffmpeg -i ../hero.mp4 -t 5.5 -vf "scale=2560:1920,crop=1080:1920:420:0" -q:v 4 build/hero/%03d.jpg
python3 music.py                 # build/music.wav
node render.mjs                  # build/frames.mp4 (kare kare, deterministik)
ffmpeg -y -i build/frames.mp4 -i build/music.wav -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart reklam-filmi.mp4
```

Metin/zamanlama düzenlemek için `film.html`'i değiştirin; tarayıcıda açınca canlı önizleme döngüsü oynar (hero kareleri `build/hero` altında olmalı).
