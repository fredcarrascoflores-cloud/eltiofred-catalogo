const defaultItems = [{name:'Lujanes',hero:'A pedido',price:350,currency:'S/',type:'A pedido',stock:null,variant:'',image:''}];
const catalogItems = Array.isArray(window.catalogItems) ? window.catalogItems : defaultItems;
let filter='all';
const catalog=document.getElementById('catalog'), empty=document.getElementById('empty'), count=document.getElementById('count');
const esc=s=>String(s??'').replace(/[&<>"']/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m]));
function money(x){
  const currency=x.currency==='$'?'$':'S/';
  return `${currency} ${esc(x.price)}`;
}
function render(){
 const q=document.getElementById('search').value.toLowerCase().trim();
 const list=catalogItems.filter(x=>(filter==='all'||x.type===filter)&&(!q||`${x.name} ${x.hero||''} ${x.type} ${x.variant||''}`.toLowerCase().includes(q)));
 catalog.innerHTML=list.map(x=>{
   const stock=Number.isFinite(Number(x.stock))?Number(x.stock):null;
   const available=stock===null||stock>0;
   const stockText=stock===null?'Consultar stock':(stock>0?`Stock: ${stock} disponible${stock===1?'':'s'}`:'Agotado');
   const duration=x.type==='Set'?'⏳ Duración: 30 días':'';
   const variant=x.variant?`\n📦 ${x.variant}`:'';
   const msg=encodeURIComponent(`Hola Fred, quiero consultar por este item:\n\n🎮 ${x.name}\n💰 ${x.currency==='$'?'$':'S/'} ${x.price}${variant}${stock!==null?`\n📦 Stock mostrado: ${stock}`:''}${duration?`\n${duration}`:''}\n🏷️ ${x.type}`);
   const wa=`https://wa.me/51943122544?text=${msg}`;
   const image=x.image?`<img class="item-image" src="${esc(x.image)}" alt="${esc(x.name)}" loading="lazy" onerror="this.style.display='none';this.nextElementSibling.style.display='flex'">`:'';
   const variantHtml=x.variant?`<div class="variant">📦 ${esc(x.variant)}</div>`:'';
   return `<article class="card ${available?'':'soldout'}" tabindex="0" role="button" aria-label="Consultar ${esc(x.name)}" data-wa="${wa}">
     <div class="pic">${image}<div class="pic-fallback">DOTA 2</div><span class="badge">● ${available?'Disponible':'Agotado'}</span></div>
     <div class="card-body"><h3>${esc(x.name)}</h3><div class="hero-name">${esc(x.hero||'Dota 2')} · ${esc(x.type)}</div><div class="price">${money(x)}</div>${variantHtml}<div class="stock">${esc(stockText)}</div>${duration?`<div class="duration">${duration}</div>`:''}
     <a class="buy" href="${available?wa:'#'}" ${available?'target="_blank" rel="noopener"':''} ${available?'':'aria-disabled="true"'}>${available?'💬 Consultar por WhatsApp':'🚫 Agotado'}</a></div></article>`;
 }).join('');
 catalog.querySelectorAll('.card').forEach(card=>{const go=()=>{if(!card.classList.contains('soldout'))window.open(card.dataset.wa,'_blank','noopener')};card.addEventListener('click',e=>{if(!e.target.closest('a'))go()});card.addEventListener('keydown',e=>{if((e.key==='Enter'||e.key===' ')&&!e.target.closest('a')){e.preventDefault();go()}})});
 empty.hidden=list.length>0; count.textContent=`${list.length} ${list.length===1?'item':'items'} mostrados`;
}
document.querySelectorAll('.nav-btn').forEach(b=>b.addEventListener('click',()=>{document.querySelectorAll('.nav-btn').forEach(x=>x.classList.remove('active'));b.classList.add('active');filter=b.dataset.filter;render()}));
document.getElementById('search').addEventListener('input',render);document.getElementById('year').textContent=new Date().getFullYear();render();
