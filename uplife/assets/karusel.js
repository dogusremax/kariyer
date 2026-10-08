// Karusel teması: sahne numarası, Doğuş logosu ve ilerleme çubuğu
(function () {
  const ids = SC.map(s => s[0]);
  ids.forEach((id, i) => {
    const sec = document.getElementById(id);
    const n = document.createElement('div'); n.className = 'bignum'; n.textContent = i + 1;
    sec.insertBefore(n, sec.firstChild);
  });
  const st = document.getElementById('stage');
  const logo = document.createElement('img'); logo.id = 'klogo'; logo.src = 'assets/dogus-logo.png'; st.appendChild(logo);
  const pr = document.createElement('div'); pr.id = 'kprog';
  pr.innerHTML = '<div class="tr"><div class="fl"></div></div><div class="nm"></div>'; st.appendChild(pr);
  const base = window.render;
  window.render = function (t) {
    base(t);
    const i = Math.max(0, SC.filter(s => t >= s[1] + WIPE * .5).length - 1), last = i === SC.length - 1;
    pr.querySelector('.fl').style.width = ((i + 1) / SC.length * 100) + '%';
    pr.querySelector('.nm').textContent = (i + 1) + '/' + SC.length;
    pr.style.opacity = (last || i === 0) ? 0 : 1;
    logo.style.opacity = last ? 0 : 1;
  };
})();
