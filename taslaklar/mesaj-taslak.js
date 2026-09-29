// TASLAK — Danışmanlara WhatsApp mesajları
//  1) Çarşamba akşamı: hafta ortası hatırlatma + motivasyon + listedeki durum
//  2) Pazartesi sabahı: haftalık karne + broker yorumu + bu haftanın planı
// Girdi: Apps Script "haftalik" çıktısı ({siralama:[...]}) — dogusportal/veri/hXXXX.json ile aynı yapı.

// Haftalık hedefler (toplanti-rapor.html'deki aylık eşiklerin haftaya bölünmüş hali)
const HEDEF = { aktifGun: 4, fzbo: 3, etki: 5, gosterim: 2, sunum: 1, sosyal_medya: 3 };
const ETIKET = { fzbo: 'FZBO araması', etki: 'etki çevresi araması', gosterim: 'gösterim', sunum: 'sunum', sosyal_medya: 'sosyal medya paylaşımı' };

const MOTIVASYON = [
  'Haftanın yarısı geride, sonucu belirleyecek yarısı önünde.',
  'Bugün attığın bir telefon, gelecek ayın kapanışı olabilir.',
  'Portföy sabırla büyür, ama her gün bir adımla.',
  'Kazanan hafta, çarşamba akşamı verilen kararla başlar.',
  'Listede yer değiştirmek için 3 gün fazlasıyla yeter.',
  'Müşteri seni hatırlasın diye bugün bir kez daha görün.',
  'Disiplin motivasyonun bittiği yerde devreye girer.',
  'Küçük ama her gün yapılan iş, büyük ama bir kez yapılan işi yener.',
  'Kapanışlar tesadüf değil; arama, sunum ve takip toplamıdır.',
  'Fikirtepe’de her gün yeni bir kapı açılıyor, bir tanesi senin olsun.',
  'Bu hafta kendinle yarış: geçen haftaki seni geç.',
  'Bir sunum daha, bir gösterim daha. Fark buradan çıkar.',
];

// Kişiye özel ayarlar
//  mod 'destek': sıralama/puan/eksik yok; sadece destek mesajı gider, ofis ortalamasına katılmaz
//  takim: birlikte çalıştığı takım arkadaşı (mesajda takdir satırı çıkar)
const OZEL = {
  aysun: { mod: 'destek', takim: 'orhan' },
  orhan: { takim: 'aysun' },
};
const DESTEK_CUMLE = [
  'Önce sen, sonra her şey. Biz buradayız.',
  'Her gün biraz daha güçlü, adım adım.',
  'Uzakta olsan da ofisin bir köşesi hep senin.',
  'Bazen en büyük başarı, kendine iyi bakmaktır.',
];

const sayi = (c, k) => k === 'sunum' ? (c.sunum1 || 0) + (c.sunum2 || 0) : (c[k] || 0);
const haftaNo = t => Math.floor((t - new Date(t.getFullYear(), 0, 1)) / 6048e5);
const ozel = d => OZEL[d.id] || {};
const adi = (L, id) => (L.find(x => x.id === id) || {}).first || '';
const toplamAkt = c => Object.values(c || {}).reduce((s, v) => s + (v || 0), 0);

function destekMesaji(d, L, gun, cumle) {
  const ark = adi(L, ozel(d).takim), akt = toplamAkt(d.counts);
  const selam = gun === 'carsamba' ? `Merhaba ${d.first} 🌿\nHafta ortasına geldik, seni düşündük.` : `Günaydın ${d.first} ☀️\nYeni bir hafta başladı.`;
  const katki = akt ? `\nBu hafta uygulamada ${akt} aktiviten görünüyor. Uzaktan bile işin içinde olman hepimize güç veriyor, emeğine sağlık. 👏\n` : `\nUzaktan da olsa ekibin bir parçası olman hepimize güç veriyor.\n`;
  const takim = ark ? `\n🤝 ${ark} ile paslaştığınız işler emin ellerde, ihtiyacın olan her şey için bir mesaj uzağındayız.\n` : '';
  const kapanis = gun === 'carsamba' ? 'Güzel bir akşam dileriz, RE/MAX Doğuş 💙' : 'Bir telefon kadar yakınız, haftan güzel geçsin. 💙\n— {BROKER}';
  return `${selam}\n\n_"${cumle}"_\n${katki}${takim}\n${kapanis}`;
}

// ---------- 1) ÇARŞAMBA ----------
function carsamba(veri, tarih = new Date()) {
  const L = veri.siralama, n = L.length;
  const mot = MOTIVASYON[haftaNo(tarih) % MOTIVASYON.length];
  return L.map((d, i) => {
    if (ozel(d).mod === 'destek') return { id: d.id, ad: d.name, metin: destekMesaji(d, L, 'carsamba', DESTEK_CUMLE[haftaNo(tarih) % DESTEK_CUMLE.length]) };
    const sira = i + 1, ust = L[i - 1];
    let durum;
    if (d.puan === 0 && d.aktifGun === 0) {
      durum = `Bu hafta henüz aktivite girişin görünmüyor. Girmeyi unuttuğun bir şey varsa bu akşam ekle; yoksa yarın *tek bir etki araması* bile seni listeye taşır. 📲`;
    } else if (sira === 1) {
      durum = `Şu an *1. sıradasın* (${d.puan} puan) 🏆 Arkandaki fark ${d.puan - L[1].puan} puan. Tempoyu koru, hafta sonuna kadar bırakma!`;
    } else {
      const fark = ust.puan - d.puan + 1, alt = L.slice(i + 1).find(x => ozel(x).mod !== 'destek');
      if (fark <= 60) {
        const arama = Math.ceil(fark / 10);
        durum = `Şu an *${sira}. sıradasın* (${d.puan} puan). ${ust.first} ile aranda ${fark} puan var, *${arama} etki araması* bu farkı kapatır! 🎯`;
      } else if (alt && alt.puan > 0) {
        durum = `Şu an *${sira}. sıradasın* (${d.puan} puan). Arkandaki ${alt.first} ile farkın ${d.puan - alt.puan} puan, yerini sağlamlaştır ve kendi rekorunu kovala! 💪`;
      } else {
        durum = `Şu an *${sira}. sıradasın* (${d.puan} puan). Haftanın geri kalanında her gün bir aktivite, seni bir üst lige taşır! 💪`;
      }
    }
    const eksik = Object.keys(ETIKET).filter(k => sayi(d.counts, k) < HEDEF[k]).slice(0, 2)
      .map(k => `• ${ETIKET[k]}: ${sayi(d.counts, k)}/${HEDEF[k]}`);
    const metin =
`Merhaba ${d.first} 👋
Hafta ortasına geldik, *Çarşamba* akşamı! 🗓️

_"${mot}"_

📊 ${durum}
${ozel(d).takim ? `\n🤝 Takım arkadaşın ${adi(L, ozel(d).takim)} ile paslaştığınız işler de bu emeğin parçası, birlikte güçlüsünüz.\n` : ''}${d.aktifGun === 0 && d.puan === 0 ? '' : eksik.length ? `\nHafta sonuna kadar yetiştirebileceklerin:\n${eksik.join('\n')}\n` : '\nHaftalık hedeflerinin hepsini tutturmuşsun, harikasın! 👏\n'}
Aktivitelerini uygulamaya girmeyi unutma 👉 dogusportal.com
İyi akşamlar, RE/MAX Doğuş`;
    return { id: d.id, ad: d.name, metin };
  });
}

// ---------- 2) PAZARTESİ KARNE ----------
function pazartesi(veri, onceki, broker = 'U.T / M.T') {
  const L = veri.siralama, n = L.length;
  const say = L.filter(x => ozel(x).mod !== 'destek'), ort = Math.round(say.reduce((s, x) => s + x.puan, 0) / say.length);
  const eski = {}; (onceki ? onceki.siralama : []).forEach((x, i) => eski[x.id] = { sira: i + 1, puan: x.puan });
  return L.map((d, i) => {
    if (ozel(d).mod === 'destek') return { id: d.id, ad: d.name, metin: destekMesaji(d, L, 'pazartesi', DESTEK_CUMLE[(haftaNo(new Date()) + 1) % DESTEK_CUMLE.length]).replace('{BROKER}', broker) };
    const sira = i + 1, c = d.counts, e = eski[d.id];
    const trend = (!e || d.puan === 0) ? '' : e.sira > sira ? ` ⬆️ (geçen hafta ${e.sira}.)` : e.sira < sira ? ` ⬇️ (geçen hafta ${e.sira}.)` : ' ➡️ (sıranı korudun)';

    const iyi = [], eksik = [];
    if (d.kapanis) iyi.push(`${d.kapanis} kapanış 🤝`);
    if (d.aktifGun >= HEDEF.aktifGun) iyi.push(`${d.aktifGun} gün aktif, istikrar tam`);
    Object.keys(ETIKET).forEach(k => {
      const v = sayi(c, k);
      if (v >= HEDEF[k]) iyi.push(`${v} ${ETIKET[k]}`);
      else eksik.push({ k, v, h: HEDEF[k] });
    });
    if (e && d.puan > e.puan && e.puan > 0) iyi.push(`puanını %${Math.round((d.puan / e.puan - 1) * 100)} artırdın`);
    if (d.aktifGun < HEDEF.aktifGun) eksik.unshift({ k: 'aktifGun', v: d.aktifGun, h: HEDEF.aktifGun });

    const eksikYaz = x => x.k === 'aktifGun' ? `aktif gün ${x.v}/${x.h}` : `${ETIKET[x.k]} ${x.v}/${x.h}`;

    // Broker yorumu: profile göre
    let yorum;
    if (d.aktifGun === 0 && d.puan === 0) yorum = `${d.first}, geçen hafta seni listede göremedik. Her şey yolunda mı? Bir kahve içip konuşalım, bu hafta birlikte planlayalım.`;
    else if (sira === 1) yorum = `Haftanın lideri sensin ${d.first}! Ekibe örnek oluyorsun. Bu hafta da çıtayı sen belirliyorsun, emeğine sağlık.`;
    else if (d.kapanis) yorum = `Kapanış yapmak her şeyin özeti, tebrikler ${d.first}! Şimdi yeni portföy ve aramalarla gelecek kapanışların zeminini hazırlayalım.`;
    else if (d.aktivitePuan >= ort) yorum = `Sahada emek veriyorsun ${d.first}, bu çok değerli. Bu emeği sonuca çevirmek için gösterim ve teklif aşamasına ağırlık verelim; kapanış yakın.`;
    else if (e && d.puan > e.puan) yorum = `Yükselişin gözümüzden kaçmadı ${d.first}! Doğru yoldasın, istikrarı koruyalım.`;
    else yorum = `${d.first}, potansiyelin bu listenin çok üstünde. Küçük ama her gün yapılan adımlarla bu hafta farkı birlikte göreceğiz.`;

    if (ozel(d).takim) yorum += ` ${adi(L, ozel(d).takim)} ile takım çalışman için de ayrıca teşekkürler, birbirinize verdiğiniz destek çok kıymetli.`;

    // Bu haftanın planı: en kritik 3 eksik → somut görev
    const GOREV = {
      aktifGun: 'Her gün en az 1 aktivite gir (etki araması bile sayılır)',
      fzbo: 'Salı ve Perşembe 09:30–11:00 arası sahibinden ilanlara 3 FZBO araması',
      etki: 'Her sabah çevrenden 1 kişiyi ara (haftada 5 etki araması)',
      gosterim: 'Ilık müşterilerine 2 gösterim randevusu planla',
      sunum: 'En az 1 mal sahibiyle sunum randevusu al',
      sosyal_medya: 'Pzt-Çar-Cuma birer paylaşım (bilgi, portföy, reels)',
    };
    const plan = (eksik.length ? eksik : [{ k: 'sunum' }, { k: 'fzbo' }]).slice(0, 3).map((x, j) => `${j + 1}. ${GOREV[x.k]}`);

    const metin =
`Günaydın ${d.first} ☀️
*${veri.ayAdi} haftalık karnen* 📋

🏅 Sıralama: *${sira}/${n}*${trend}
⭐ Puan: *${d.puan}* (ofis ortalaması ${ort})
📅 Aktif gün: ${d.aktifGun}

✅ *İyi yaptıkların*
${iyi.length ? iyi.map(x => '• ' + x).join('\n') : '• Bu hafta yeni bir sayfa açıyoruz'}

⚠️ *Geliştirmen gerekenler*
${eksik.length ? eksik.slice(0, 3).map(x => '• ' + eksikYaz(x)).join('\n') : '• Tüm haftalık hedeflerini tutturdun 👏'}

💬 *Broker yorumu*
_${yorum}_
— ${broker}

🎯 *Bu haftanın planı*
${plan.join('\n')}

Haftalık sıralama story’si Instagram’da 📸 Hadi bu hafta bir basamak yukarı! 🚀`;
    return { id: d.id, ad: d.name, metin };
  });
}

module.exports = { carsamba, pazartesi, MOTIVASYON, HEDEF };

if (require.main === module) {
  const fs = require('fs'), P = '/home/user/dogusremax/dogusportal/veri/';
  const h = JSON.parse(fs.readFileSync(P + 'h0824.json')), o = JSON.parse(fs.readFileSync(P + 'h0817.json'));
  const out = { carsamba: carsamba(h, new Date('2026-08-26')), pazartesi: pazartesi(h, o) };
  fs.writeFileSync(__dirname + '/ornekler.json', JSON.stringify(out, null, 1));
  for (const t of ['carsamba', 'pazartesi']) for (const i of [0, 2, 6]) console.log(`\n===== ${t} / ${out[t][i].ad}\n${out[t][i].metin}`);
}
