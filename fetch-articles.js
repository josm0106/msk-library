/**
 * fetch-articles.js
 * MusculoskeletalKey 사이트에서 Orthopedic 카테고리 전체 문헌을 가져와
 * articles.json 으로 저장합니다.
 * GitHub Actions 에서 매월 1일 자동 실행됩니다.
 */

const fs = require('fs');
const https = require('https');

const BASE = 'https://musculoskeletalkey.com/wp-json/wp/v2/posts';
const CATEGORY = 27;
const PER_PAGE = 100;
const FIELDS = 'id,title,link,date';

function fetchPage(page) {
  const url = `${BASE}?categories=${CATEGORY}&per_page=${PER_PAGE}&page=${page}&_fields=${FIELDS}`;
  return new Promise((resolve, reject) => {
    https.get(url, { headers: { 'User-Agent': 'MSK-Library-Bot/1.0' } }, res => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        if (res.statusCode === 400 || res.statusCode === 404) {
          resolve([]);
          return;
        }
        if (res.statusCode !== 200) {
          reject(new Error(`HTTP ${res.statusCode} on page ${page}`));
          return;
        }
        try {
          const json = JSON.parse(data);
          resolve(Array.isArray(json) ? json : []);
        } catch (e) {
          reject(new Error(`Parse error on page ${page}: ${e.message}`));
        }
      });
      res.on('error', reject);
    }).on('error', reject);
  });
}

async function fetchAll() {
  let allArticles = [];
  let page = 1;
  let emptyCount = 0;

  console.log('Starting article fetch from musculoskeletalkey.com ...');

  while (page <= 200 && emptyCount < 3) {
    try {
      const batch = await fetchPage(page);
      if (!batch.length) {
        emptyCount++;
        console.log(`Page ${page}: empty (${emptyCount}/3 consecutive empty)`);
      } else {
        emptyCount = 0;
        const mapped = batch.map(a => ({
          i: a.id,
          t: a.title?.rendered || '',
          l: a.link,
          d: a.date ? a.date.slice(0, 10) : ''
        }));
        allArticles.push(...mapped);
        console.log(`Page ${page}: +${batch.length} articles (total: ${allArticles.length})`);
      }
    } catch (e) {
      console.error(`Page ${page} error: ${e.message}`);
      emptyCount++;
    }
    page++;
    await new Promise(r => setTimeout(r, 200));
  }

  // Deduplicate by ID
  const seen = new Set();
  allArticles = allArticles.filter(a => {
    if (seen.has(a.i)) return false;
    seen.add(a.i);
    return true;
  });

  console.log(`\nTotal unique articles: ${allArticles.length}`);

  let prevCount = 0;
  try {
    const prev = JSON.parse(fs.readFileSync('articles.json', 'utf8'));
    prevCount = prev.length;
  } catch (e) { /* first run */ }

  fs.writeFileSync('articles.json', JSON.stringify(allArticles, null, 0), 'utf8');

  const diff = allArticles.length - prevCount;
  if (prevCount > 0) {
    console.log(`Previous: ${prevCount} -> New: ${allArticles.length} (${diff >= 0 ? '+' : ''}${diff})`);
  }
  console.log('Saved to articles.json');
}

fetchAll().catch(e => {
  console.error('Fatal error:', e);
  process.exit(1);
});
