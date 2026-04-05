#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fix: replace old search code with autocomplete + add articles.json loading"""
import os

fp = r'C:\xampp\htdocs\mysite\msk-library-temp\index.html'
with open(fp, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Replace old search JS (single-line format)
old_search = "let searchTimer;document.getElementById('searchInput').addEventListener('input',()=>{clearTimeout(searchTimer);searchTimer=setTimeout(()=>{pg=1;render();},300);});"

ac_js = r"""let searchTimer,acIdx=-1;
const sInput=document.getElementById('searchInput');
const acDrop=document.getElementById('acDrop');
function highlightMatch(text,query){
if(!query)return text;
const esc=query.replace(/[.*+?^${}()|[\]\\]/g,'\\$&');
return text.replace(new RegExp('('+esc+')','gi'),'<mark>$1</mark>');
}
function showAC(q){
if(!q||q.length<2||!arts.length){acDrop.classList.remove('show');acDrop.innerHTML='';acIdx=-1;return;}
const ql=q.toLowerCase();
const words=ql.split(/\s+/).filter(w=>w.length>0);
let scored=arts.map(a=>{
const tl=(a.t||'').toLowerCase();
let score=0;
if(tl.includes(ql))score+=100;
words.forEach(w=>{if(tl.includes(w))score+=10;});
words.forEach(w=>{if(tl.split(/[\s\-:,()]+/).some(tw=>tw.startsWith(w)))score+=5;});
return{a:a,score:score};
}).filter(x=>x.score>0).sort((a,b)=>b.score-a.score);
if(!scored.length){
acDrop.innerHTML='<div class="ac-empty">검색 결과가 없습니다</div>';
acDrop.classList.add('show');acIdx=-1;return;
}
const total=scored.length;
const show=scored.slice(0,10);
let h='';
show.forEach((x,i)=>{
const a=x.a;
const cats=(a.cats||[]).slice(0,2);
const subs=(a.subs||[]).slice(0,2);
h+='<div class="ac-item" data-idx="'+i+'" data-link="'+a.l+'" data-id="'+a.i+'">';
h+='<div class="ac-title">'+highlightMatch(a.t,q)+'</div>';
h+='<div class="ac-meta">'+cats.map(c=>'<span class="ac-cat">'+c+'</span>').join('')+subs.map(s=>'<span class="ac-sub">'+s+'</span>').join('')+'</div>';
h+='</div>';
});
if(total>10)h+='<div class="ac-count">총 '+total+'개 결과 중 10개 표시 · Enter로 전체 검색</div>';
acDrop.innerHTML=h;
acDrop.classList.add('show');
acIdx=-1;
acDrop.querySelectorAll('.ac-item').forEach(el=>{
el.addEventListener('mousedown',e=>{
e.preventDefault();
const id=parseInt(el.dataset.id);
markR(id);
window.open(el.dataset.link,'_blank');
acDrop.classList.remove('show');
});
});
}
function acNav(dir){
const items=acDrop.querySelectorAll('.ac-item');
if(!items.length)return;
items.forEach(x=>x.classList.remove('sel'));
acIdx+=dir;
if(acIdx<0)acIdx=items.length-1;
if(acIdx>=items.length)acIdx=0;
items[acIdx].classList.add('sel');
items[acIdx].scrollIntoView({block:'nearest'});
}
sInput.addEventListener('input',()=>{
clearTimeout(searchTimer);
searchTimer=setTimeout(()=>{
showAC(sInput.value.trim());
pg=1;render();
},200);
});
sInput.addEventListener('keydown',e=>{
if(!acDrop.classList.contains('show'))return;
if(e.key==='ArrowDown'){e.preventDefault();acNav(1);}
else if(e.key==='ArrowUp'){e.preventDefault();acNav(-1);}
else if(e.key==='Enter'&&acIdx>=0){
e.preventDefault();
const sel=acDrop.querySelectorAll('.ac-item')[acIdx];
if(sel){markR(parseInt(sel.dataset.id));window.open(sel.dataset.link,'_blank');acDrop.classList.remove('show');}
}else if(e.key==='Escape'){acDrop.classList.remove('show');}
});
document.addEventListener('click',e=>{if(!e.target.closest('.search'))acDrop.classList.remove('show');});"""

if old_search in content:
    content = content.replace(old_search, ac_js)
    print('[OK] Autocomplete JS replaced')
else:
    print('[WARN] Old search pattern not found')

# 2. Add articles.json loading to fetchAll
old_fetch = "async function fetchAll(){const bar=document.getElementById('topBar');const cached=getCache();if(cached&&cached.length>0){arts=cached;arts.forEach(a=>catArt(a));bar.style.width='100%';setTimeout(()=>bar.style.opacity='0',500);updateStats();render();bgRefresh();return;}let loaded=0;"

new_fetch = """async function fetchAll(){const bar=document.getElementById('topBar');const cached=getCache();if(cached&&cached.length>0){arts=cached;arts.forEach(a=>catArt(a));bar.style.width='100%';setTimeout(()=>bar.style.opacity='0',500);updateStats();render();bgRefresh();return;}
try{const r=await fetch('articles.json');if(r.ok){const data=await r.json();if(Array.isArray(data)&&data.length>0){arts=data;arts.forEach(a=>catArt(a));setCache(arts);bar.style.width='100%';setTimeout(()=>bar.style.opacity='0',500);updateStats();render();bgRefresh();return;}}}catch(e){console.log('articles.json not available');}
let loaded=0;"""

if old_fetch in content:
    content = content.replace(old_fetch, new_fetch)
    print('[OK] articles.json loading added')
else:
    print('[WARN] fetchAll pattern not found - may already be modified')

with open(fp, 'w', encoding='utf-8') as f:
    f.write(content)

print(f'\n[DONE] File size: {os.path.getsize(fp):,} bytes')
