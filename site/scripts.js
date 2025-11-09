
// Простая SPA — все данные хранятся в localStorage под ключом 'educards_decks'
const STORAGE_KEY = 'educards_decks_v1';

// Утилиты
const $ = id => document.getElementById(id);
const now = () => new Date().toISOString();

// State
let decks = loadDecks();
let activeDeckId = null;

// Инициализация UI
const decksList = $('decksList');
const deckTitle = $('deckTitle');
const deckInfo = $('deckInfo');
const visibilityTag = $('visibilityTag');
const deckEditor = $('deckEditor');
const emptyState = $('emptyState');

renderDecksList();

// --- Events ---
$('newDeckBtn').addEventListener('click', ()=>{
  const id = createDeck({title:'Новая колода', description:'', visibility:'private', tags:[], cards:[]});
  selectDeck(id);
});

$('saveDeckBtn').addEventListener('click', ()=>{
  if(!activeDeckId) return;
  const d = getActiveDeck();
  d.title = $('titleInput').value.trim() || 'Без названия';
  d.description = $('descInput').value.trim();
  d.visibility = $('visibilitySelect').value;
  d.tags = $('tagsInput').value.split(',').map(t=>t.trim()).filter(Boolean);
  d.updated_at = now();
  saveDecks(); renderDecksList(); renderActive();
  alert('Сохранено');
});

$('addCardBtn').addEventListener('click', ()=>{
  if(!activeDeckId) return alert('Выберите колоду');
  const term = $('termInput').value.trim();
  const answer = $('answerInput').value.trim();
  if(!term || !answer) return alert('Заполните слово и значение');
  const d = getActiveDeck();
  d.cards.unshift({id: 'c_'+Date.now(), term, answer, created_at: now()});
  d.updated_at = now();
  $('termInput').value=''; $('answerInput').value='';
  saveDecks(); renderActive(); renderDecksList();
});

$('clearCardsBtn').addEventListener('click', ()=>{
  if(!activeDeckId) return;
  if(!confirm('Очистить все карточки в этой колоде?')) return;
  const d = getActiveDeck(); d.cards = []; d.updated_at = now(); saveDecks(); renderActive(); renderDecksList();
});

$('deleteDeckBtn').addEventListener('click', ()=>{
  if(!activeDeckId) return;
  if(!confirm('Удалить колоду?')) return;
  decks = decks.filter(x=>x.id!==activeDeckId);
  saveDecks(); activeDeckId=null; renderDecksList(); renderActive();
});

$('exportBtn').addEventListener('click', ()=>{
  const data = JSON.stringify(decks, null, 2);
  const blob = new Blob([data], {type:'application/json'});
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a'); a.href = url; a.download = 'educards_export.json'; a.click(); URL.revokeObjectURL(url);
});

$('importBtn').addEventListener('click', ()=>{ $('fileInput').click(); });
$('fileInput').addEventListener('change', async (e)=>{
  const f = e.target.files[0]; if(!f) return;
  const txt = await f.text(); try{ const imported = JSON.parse(txt); if(!Array.isArray(imported)) throw 0; decks = decks.concat(imported.map(normalizeDeck)); saveDecks(); renderDecksList(); alert('Импортировано'); }catch(err){alert('Неверный формат JSON')}
  e.target.value='';
});

$('shareBtn').addEventListener('click', ()=>{
  if(!activeDeckId) return alert('Выберите колоду');
  const d = getActiveDeck();
  const blob = btoa(unescape(encodeURIComponent(JSON.stringify(d))));
  const link = location.origin + location.pathname + '?deck=' + encodeURIComponent(blob);
  navigator.clipboard.writeText(link).then(()=> alert('Ссылка скопирована'))
});

$('searchInput').addEventListener('input', (e)=>{ renderDecksList(e.target.value) });

// --- Helpers ---
function createDeck({title,description,visibility,tags,cards}){
  const id = 'd_'+Date.now();
  const deck = {id, title, description, visibility, tags, cards, created_at: now(), updated_at: now()};
  decks.unshift(deck); saveDecks(); renderDecksList(); return id;
}
function getActiveDeck(){ return decks.find(x=>x.id===activeDeckId); }
function saveDecks(){ localStorage.setItem(STORAGE_KEY, JSON.stringify(decks)); }
function loadDecks(){ try{ const raw = localStorage.getItem(STORAGE_KEY); if(!raw) return sampleDecks(); return JSON.parse(raw).map(normalizeDeck); }catch(e){return sampleDecks()} }
function normalizeDeck(d){ return {...{id:'d_'+Date.now(),title:'Без названия',description:'',visibility:'private',tags:[],cards:[],created_at:now(),updated_at:now()}, ...d} }

function selectDeck(id){ activeDeckId = id; renderActive(); renderDecksList(); }

function renderDecksList(filter=''){
  const q = (filter||'').toLowerCase().trim();
  decksList.innerHTML='';
  if(!decks.length){ decksList.innerHTML='<div class="muted">Колод нет</div>'; return }
  decks.filter(d=>{
    if(!q) return true;
    return d.title.toLowerCase().includes(q) || (d.tags||[]).join(' ').toLowerCase().includes(q) || (d.description||'').toLowerCase().includes(q);
  }).forEach(d=>{
    const el = document.createElement('div'); el.className='deck-item';
    el.innerHTML = `<div class="meta"><strong>${escape(d.title)}</strong><div class="muted">${escape(d.tags?d.tags.join(', '):'')}</div></div><div class="muted small">${d.cards.length} карточек</div>`;
    el.addEventListener('click', ()=> selectDeck(d.id));
    decksList.appendChild(el);
  });
}

function renderActive(){
  if(!activeDeckId){ deckEditor.style.display='none'; emptyState.style.display='block'; deckTitle.textContent='Выберите колоду или создайте новую'; deckInfo.textContent='—'; visibilityTag.textContent='—'; return }
  const d = getActiveDeck(); deckEditor.style.display='block'; emptyState.style.display='none';
  deckTitle.textContent = d.title;
  deckInfo.textContent = d.description || `Создано: ${d.created_at.split('T')[0]} • Обновлено: ${d.updated_at.split('T')[0]}`;
  visibilityTag.textContent = d.visibility;
  $('titleInput').value = d.title; $('descInput').value = d.description; $('visibilitySelect').value = d.visibility; $('tagsInput').value = (d.tags||[]).join(', ');
  // render cards
  const grid = $('cardsGrid'); grid.innerHTML=''; if(!d.cards.length){ grid.innerHTML='<div class="muted">Пока нет карточек</div>'; return }
  d.cards.forEach(c=>{
    const ci = document.createElement('div'); ci.className='card-item';
    ci.innerHTML = `<strong>${escape(c.term)}</strong><div class="muted small" style="margin-top:6px">${escape(c.answer)}</div><div style="margin-top:8px" class="flex"><button class="ghost" data-id="${c.id}">Ред.</button><button class="ghost" data-del="${c.id}">Удал.</button></div>`;
    grid.appendChild(ci);
  });
  // attach delete/edit
  grid.querySelectorAll('[data-del]').forEach(b => b.addEventListener('click', e=>{
    const id = e.target.getAttribute('data-del'); d.cards = d.cards.filter(x=>x.id!==id); d.updated_at = now(); saveDecks(); renderActive(); renderDecksList();
  }));
  grid.querySelectorAll('[data-id]').forEach(b => b.addEventListener('click', e=>{
    const id = e.target.getAttribute('data-id'); const card = d.cards.find(x=>x.id===id); if(!card) return; const t = prompt('Термин', card.term); if(t===null) return; const a = prompt('Значение', card.answer); if(a===null) return; card.term=t; card.answer=a; d.updated_at=now(); saveDecks(); renderActive(); renderDecksList();
  }));
}

function escape(s){ return String(s||'').replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;') }

// sample data
function sampleDecks(){ return [
  {id:'d_sample_med', title:'Medical English — Anatomy', description:'Базовые термины по анатомии', visibility:'public', tags:['medical','anatomy'], cards:[
    {id:'c1',term:'heart',answer:'сердце'},
    {id:'c2',term:'lung',answer:'легкое'}
  ], created_at:now(), updated_at:now()},
  {id:'d_sample_it', title:'IT — Networking', description:'Основные термины сетей', visibility:'public', tags:['it','networking'], cards:[{id:'c3',term:'router',answer:'роутер'},{id:'c4',term:'switch',answer:'коммутатор'}], created_at:now(), updated_at:now()}
]}

// Check URL param (share link)
(function checkShare(){ const params = new URLSearchParams(location.search); if(params.has('deck')){ try{ const blob = decodeURIComponent(params.get('deck')); const json = decodeURIComponent(escape(atob(blob))); const deck = JSON.parse(json); deck.id = 'd_import_'+Date.now(); decks.unshift(normalizeDeck(deck)); saveDecks(); renderDecksList(); alert('Импортирована колода из ссылки'); }catch(e){console.warn(e)} }})();

