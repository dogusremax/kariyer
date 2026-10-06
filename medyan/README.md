# Medyan Kadıköy — Durum Raporu (bilgilendirici reklam filmi)

`medyan-kadikoy.mp4` · 1080×1920 (9:16) · 48 sn · 30 fps · müzik altlığı (seslendirme sonra eklenecek)

Seslendirme metni ve sahne süreleri: [`seslendirme-metni.md`](seslendirme-metni.md)

## Seslendirme gelince

1. Ses dosyasını `build/vo.wav` olarak koyun.
2. Her cümlenin başladığı saniyeye göre `film.html` içindeki `STARTS` dizisini güncelleyin (6 sahne başlangıcı) ve gerekirse `DURATION`'ı uzatın.
3. `music.py` içindeki `DUR` ve `TRANSITIONS` değerlerini aynı saniyelere çekip yeniden üretin.
4. Render + miks (müzik sesin altında kalır):

```sh
python3 music.py && node render.mjs
ffmpeg -y -i build/frames.mp4 -i build/vo.wav -i build/music.wav \
  -filter_complex "[2]volume=0.25[m];[1][m]amix=inputs=2:duration=longest:normalize=0[a]" \
  -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart medyan-kadikoy.mp4
```

Gerekenler: Node + Playwright (Chromium), ffmpeg (libx264), Python 3 + numpy + scipy.
