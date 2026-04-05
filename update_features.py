#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
update_features.py
원본 index.html (비밀번호 보호 포함)에 다음 기능을 추가:
1. 검색 자동완성/미리보기 드롭다운
2. articles.json 우선 로딩 (GitHub Actions 매월 자동 업데이트용)
"""

import re, sys, os

src = r'C:\xampp\htdocs\mysite\msk-library-temp\index.html'
dst = r'C:\xampp\htdocs\mysite\msk-library-temp\index.html'

with open(src, 'r', encoding='utf-8') as f:
    content = f.read()

# ===== 1. 자동완성 CSS 추가 =====
ac_css = """
.search{position:relative}
.ac-drop{position:absolute;top:100%;left:0;right:0;background:var(--card);border:1px solid var(--bdr);border-top:none;border-radius:0 0 10px 10px;max-height:400px;overflow-y:auto;z-index:200;display:none;box-shadow:0 8px 24px rgba(0,0,0,.4)}
.ac-drop.show{display:block}
.ac-item{padding:.75rem 1rem;cursor:pointer;border-bottom:1px solid var(--bg3);transition:background .2s}
.ac-item:last-child{border-bottom:none}
.ac-item:hover,.ac-item.sel{background:var(--bg3)}
.ac-item .ac-title{font-size:.9rem;color:var(--tx);margin-bottom:.25rem;line-height:1.3}
.ac-item .ac-title mark{background:transparent;color:var(--ac);font-weight:700}
.ac-item .ac-meta{display:flex;gap:.5rem;flex-wrap:wrap}
.ac-item .ac-cat{font-size:.7rem;padding:.15rem .4rem;background:var(--bg);border:1px solid var(--bdr);border-radius:3px;color:var(--ac)}
.ac-item .ac-sub{font-size:.7rem;color:var(--tx2)}
.ac-count{padding:.5rem 1rem;font-size:.75rem;color:var(--tx2);background:var(--bg3);border-top:1px solid var(--bdr);text-align:center}
.ac-empty{padding:1rem;text-align:center;font-size:.85rem;color:var(--tx2)}"""

# CSS 삽입: .search input:focus 뒤에
if '.ac-drop' not in content:
    content = content.replace(
        '.search input:focus{outline:none;border-color:var(--ac);box-shadow:0 0 8px rgba(0,212,255,.2)}',
        '.search input:focus{outline:none;border-color:var(--ac);box-shadow:0 0 8px rgba(0,212,255,.2)}' + ac_css
    )
    print('[OK] Autocomplete CSS added')
else:
    print('[SKIP] Autocomplete CSS already exists')

# ===== 2. 자동완성 드롭다운 HTML 추가 =====
if 'id="acDrop"' not in content:
    content = content.replace(
        '<input type="text" id="searchInput" placeholder="검색... (Search)">',
        '<input type="text" id="searchInput" placeholder="검색... (Search)" autocomplete="off">\n<div class="ac-drop" id="acDrop"></div>'
    )
    print('[OK] Autocomplete dropdown HTML added')
else:
    print('[SKIP] Autocomplete dropdown HTML already exists')

# ===== 3. fetchAll에 articles.json 로딩 추가 =====
if 'articles.json' not in content:
    old_fetch = """async function fetchAll(){
const bar=document.getElementById('topBar');
const cached=getCache();
if(cached&&cached.length>0){
arts=cached;
arts.forEach(a=>catArt(a));
bar.style.width='100%';
setTimeout(()=>bar.style.opacity='0',500);
updateStats();render();
bgRefresh();
return;
}
// Progressive load"""

    new_fetch = """async function fetchAll(){
const bar=document.getElementById('topBar');
// 1) LocalStorage cache
const cached=getCache();
if(cached&&cached.length>0){
arts=cached;
arts.forEach(a=>catArt(a));
bar.style.width='100%';
setTimeout(()=>bar.style.opacity='0',500);
updateStats();render();
bgRefresh();
return;
}
// 2) Pre-built articles.json (GitHub Actions monthly auto-update)
try{
const r=await fetch('articles.json');
if(r.ok){
const data=await r.json();
if(Array.isArray(data)&&data.length>0){
arts=data;
arts.forEach(a=>catArt(a));
setCache(arts);
bar.style.width='100%';
setTimeout(()=>bar.style.opacity='0',500);
updateStats();render();
bgRefresh();
return;
}
}
}catch(e){console.log('articles.json not available, falling back to API');}
// 3) Fallback: WordPress API progressive load"""

    content = content.replace(old_fetch, new_fetch)
    print('[OK] articles.json loading added to fetchAll')
else:
    print('[SKIP] articles.json loading already exists')

# ===== 4. 검색 자동완성 JS 교체 =====
ac_js = """// Search with Autocomplete
let searchTimer,acIdx=-1;
const sInput=document.getElementById('searchInput');
const acDrop=document.getElementById('acDrop');

function highlightMatch(text,query){
if(!query)return text;
const esc=query.replace(/[.*+?^${}()|[\\]\\\\]/g,'\\\\$&');
return text.replace(new RegExp(`(${esc})`,'gi'),'<mark>$1</mark>');
}

function showAC(q){
if(!q||q.length<2||!arts.length){acDrop.classList.remove('show');acDrop.innerHTML='';acIdx=-1;return;}
const ql=q.toLowerCase();
const words=ql.split(/\\s+/).filter(w=>w.length>0);
let scored=arts.map(a=>{
const tl=(a.t||'').toLowerCase();
let score=0;
if(tl.includes(ql))score+=100;
words.forEach(w=>{if(tl.includes(w))score+=10;});
words.forEach(w=>{if(tl.split(/[\\s\\-:,()]+/).some(tw=>tw.startsWith(w)))score+=5;});
return{a,score};
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
h+=`<div class="ac-item" data-idx="${i}" data-link="${a.l}" data-id="${a.i}">
<div class="ac-title">${highlightMatch(a.t,q)}</div>
<div class="ac-meta">${cats.map(c=>`<span class="ac-cat">${c}</span>`).join('')}${subs.map(s=>`<span class="ac-sub">${s}</span>`).join('')}</div>
</div>`;
});
if(total>10)h+=`<div class="ac-count">총 ${total}개 결과 중 10개 표시 · Enter로 전체 검색</div>`;
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

old_search = """// Search
let searchTimer;
document.getElementById('searchInput').addEventListener('input',()=>{
clearTimeout(searchTimer);
searchTimer=setTimeout(()=>{pg=1;render();},300);
});"""

if 'showAC' not in content:
    content = content.replace(old_search, ac_js)
    print('[OK] Autocomplete JS added')
else:
    print('[SKIP] Autocomplete JS already exists')

# Write
with open(dst, 'w', encoding='utf-8') as f:
    f.write(content)

print(f'\n[DONE] Updated: {dst}')
print(f'File size: {os.path.getsize(dst):,} bytes')
