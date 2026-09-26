/*
  OPINIONES DE CLIENTES
  - Muestra 5 recomendaciones inicialmente.
  - "Ver todas" muestra el resto.
  - El formulario está preparado para conectarse a una base de datos online.
  - Mientras REVIEW_API_URL esté vacío, guarda las pruebas solo en este navegador.
  - Para publicación real entre todos los equipos, conectar REVIEW_API_URL a un backend.
*/
(() => {
  const REVIEW_API_URL = ''; // Aquí irá el endpoint online cuando configuremos el almacenamiento.
  const STORAGE_KEY = 'fred_dota_reviews_pending_demo';
  const PUBLIC_KEY = 'fred_dota_reviews_public_demo';
  const PAGE_SIZE = 5;

  const grid = document.getElementById('reviewsGrid');
  const empty = document.getElementById('reviewsEmpty');
  const more = document.getElementById('reviewsMore');
  const total = document.getElementById('reviewsTotal');
  const modal = document.getElementById('reviewModal');
  const status = document.getElementById('reviewStatus');
  const nameEl = document.getElementById('reviewName');
  const textEl = document.getElementById('reviewText');
  const starsEl = document.getElementById('starPicker');
  const open = document.getElementById('openReview');
  const close = document.getElementById('closeReview');
  const submit = document.getElementById('submitReview');
  let showAll = false;
  let rating = 5;

  const esc = s => String(s ?? '').replace(/[&<>"']/g, m => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m]));
  const stars = n => '★'.repeat(n) + '☆'.repeat(5 - n);
  const loadLocal = key => { try { return JSON.parse(localStorage.getItem(key) || '[]'); } catch { return []; } };
  const saveLocal = (key, data) => localStorage.setItem(key, JSON.stringify(data));

  function render(list) {
    total.textContent = list.length;
    const visible = showAll ? list : list.slice(0, PAGE_SIZE);
    grid.innerHTML = visible.map(r => `
      <article class="review-card">
        <div class="review-top">
          <div class="review-avatar">${esc((r.name || '?').trim().charAt(0).toUpperCase())}</div>
          <div><div class="review-name">${esc(r.name)}</div><div class="review-date">${esc(r.date || '')}</div></div>
        </div>
        <div class="review-stars" aria-label="${esc(r.rating)} de 5">${stars(Number(r.rating) || 5)}</div>
        <div class="review-text">${esc(r.text)}</div>
      </article>`).join('');
    empty.hidden = list.length !== 0;
    more.hidden = list.length <= PAGE_SIZE;
    more.innerHTML = showAll ? 'Ver menos ⌃' : `Ver todas las recomendaciones (<span id="reviewsTotal">${list.length}</span>)⌄`;
  }

  async function getReviews() {
    if (REVIEW_API_URL) {
      try {
        const r = await fetch(REVIEW_API_URL, {headers:{'Accept':'application/json'}});
        if (!r.ok) throw new Error('No se pudo cargar las recomendaciones.');
        return await r.json();
      } catch (e) { console.warn(e); }
    }
    return loadLocal(PUBLIC_KEY);
  }

  function initStars() {
    starsEl.innerHTML = [1,2,3,4,5].map(n => `<button type="button" class="star-choice ${n <= rating ? 'selected':''}" data-star="${n}" aria-label="${n} estrellas">★</button>`).join('');
    starsEl.querySelectorAll('.star-choice').forEach(b => b.addEventListener('click', () => {
      rating = Number(b.dataset.star); initStars();
    }));
  }

  function setStatus(msg, error=false) { status.textContent = msg; status.classList.toggle('error', error); }
  function openModal() { modal.hidden = false; document.body.style.overflow = 'hidden'; setStatus(''); nameEl.focus(); }
  function closeModal() { modal.hidden = true; document.body.style.overflow = ''; }

  async function submitReview() {
    const name = nameEl.value.trim();
    const text = textEl.value.trim();
    if (!name || !text) return setStatus('Completa tu nombre y tu recomendación.', true);
    const review = {name, text, rating, date:new Date().toLocaleDateString('es-PE'), status:'pending'};
    submit.disabled = true;
    try {
      if (REVIEW_API_URL) {
        const r = await fetch(REVIEW_API_URL, {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(review)});
        if (!r.ok) throw new Error('No se pudo enviar.');
      } else {
        const pending = loadLocal(STORAGE_KEY); pending.push(review); saveLocal(STORAGE_KEY, pending);
      }
      setStatus('¡Gracias! Tu recomendación quedó enviada para revisión.');
      nameEl.value = ''; textEl.value = ''; rating = 5; initStars();
    } catch (e) { setStatus('No se pudo enviar. Inténtalo nuevamente.', true); }
    submit.disabled = false;
  }

  open.addEventListener('click', openModal); close.addEventListener('click', closeModal); submit.addEventListener('click', submitReview);
  modal.querySelectorAll('[data-close-review]').forEach(x => x.addEventListener('click', closeModal));
  document.addEventListener('keydown', e => { if (e.key === 'Escape' && !modal.hidden) closeModal(); });
  more.addEventListener('click', async () => { showAll = !showAll; render(await getReviews()); });
  initStars();
  getReviews().then(render);
})();
