# İki Yaka Fikirtepe — Durum Raporu (bilgilendirici reklam filmi)

`ikiyaka-fikirtepe.mp4` · 1080×1920 (9:16) · 57 sn · 30 fps · müzik altlığı (seslendirme eklenecek)

Seslendirme metni: [`seslendirme-metni.md`](seslendirme-metni.md) · Araştırma ve kaynaklar: [`arastirma-notu.md`](arastirma-notu.md)

## Seslendirmeyi değiştirmek için

1. Seslendirme `ses/seslendirme.mp3`; wav'a çevirip `build/vo.wav` olarak koyun (`ffmpeg -i ses/seslendirme.mp3 -ar 44100 -ac 2 build/vo.wav`).
2. Her cümlenin başladığı saniyeye göre `film.html` içindeki `STARTS` dizisini güncelleyin (6 sahne başlangıcı) ve gerekirse `DURATION`'ı uzatın.
3. `music.py` içindeki `DUR` ve `TRANSITIONS` değerlerini aynı saniyelere çekip yeniden üretin.
4. Render + miks (müzik sesin altında kalır):

```sh
python3 music.py && node render.mjs
ffmpeg -y -i build/frames.mp4 -i build/vo.wav -i build/music.wav \
  -filter_complex "[2]volume=0.3[m];[1]apad[v];[v][m]amix=inputs=2:duration=shortest:normalize=0,alimiter=limit=0.95[a]" \
  -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k -t 57 -movflags +faststart ikiyaka-fikirtepe.mp4
```

Gerekenler: Node + Playwright (Chromium), ffmpeg (libx264), Python 3 + numpy + scipy.
