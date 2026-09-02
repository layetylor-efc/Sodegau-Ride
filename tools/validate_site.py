from pathlib import Path
from html.parser import HTMLParser
import json, re, sys

errors=[]
required_files=['index.html','cityhall.html','offline.html','manifest.webmanifest','sw.js','icon.svg','.nojekyll']
for f in required_files:
    if not Path(f).exists(): errors.append(f'必須ファイル不足: {f}')

class AuditParser(HTMLParser):
    def __init__(self,name):
        super().__init__(); self.name=name; self.ids=[]; self.local_links=[]; self.blank=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'id' in a: self.ids.append(a['id'])
        if tag=='a' and 'href' in a:
            href=a['href']
            if href.startswith('./') and not href.startswith('./#'):
                self.local_links.append(href.split('#')[0].split('?')[0])
            if a.get('target')=='_blank': self.blank.append((href,a.get('rel','')))

def audit_html(path):
    text=Path(path).read_text(encoding='utf-8'); p=AuditParser(path); p.feed(text)
    dup=sorted({x for x in p.ids if p.ids.count(x)>1})
    if dup: errors.append(f'{path} 重複ID: {dup}')
    for href in p.local_links:
        target=href[2:] if href.startswith('./') else href
        if target and target!='/' and not Path(target).exists(): errors.append(f'{path} ローカルリンク切れ: {href}')
    for href,rel in p.blank:
        if 'noopener' not in rel: errors.append(f'{path} target=_blank にnoopener不足: {href}')
    if 'http-equiv="refresh"' in text.lower(): errors.append(f'{path} 意図しないmeta refresh')
    return text

if Path('index.html').exists():
    s=audit_html('index.html')
    required=['<!doctype html>','v0.4.1','data-view="admin"','data-view="needs"','data-view="dx"','role="tabpanel"','id="siteSearch"','id="emptyState"','id="aiInput"','AI市政コンシェルジュ','AIルーター','SodeMap Digital Twin','2035年の袖ケ浦を見る','未来予測の注意','市民入力','AI整理','担当課','行政処理','KPI更新','市民へ回答','政策改善','Twin更新','Accessibility Mode','低速回線モード','災害時モード','sr-emergency','resetPrefs','serviceWorker','manifest.webmanifest','icon.svg','./cityhall.html','Updated 2026-09-02']
    for t in required:
        if t not in s: errors.append(f'index必須要素不足: {t}')
    if s.count('role="tab"')!=3: errors.append('固定3タブの数が3ではありません')
    if 'ArrowLeft' not in s or 'ArrowRight' not in s: errors.append('タブの矢印キー操作がありません')
    subs=re.findall(r'\bsubs\s*:\s*\[(.*?)\]',s,re.S)
    if len(subs)!=8: errors.append(f'行政大分類が8件ではありません: {len(subs)}')
    for y in ['2026','2030','2035','2040']:
        if f'data-year="{y}"' not in s: errors.append(f'未来時間軸不足: {y}')
    for layer in ['避難所','浸水','医療','交通','高齢化','市民の声']:
        if f'data-layer="{layer}"' not in s: errors.append(f'Digital Twinレイヤー不足: {layer}')
    if 'localStorage' not in s: errors.append('端末内状態保持がありません')
    if 'prefers-reduced-motion' not in s: errors.append('reduced-motion対応がありません')
    if 'escapeHtml' not in s: errors.append('動的HTMLのエスケープ関数がありません')

if Path('cityhall.html').exists():
    c=audit_html('cityhall.html')
    req=['袖ケ浦市庁舎 Digital Twin','v0.4.1','中庁舎1F','北庁舎1F','北庁舎5F','2～4階','data-purpose="転入・住民票"','data-purpose="税"','data-purpose="福祉"','data-purpose="議会"','data-floor="1F"','data-floor="5F"','data-building="中庁舎"','data-building="北庁舎"','状態リンクをコピー','URLSearchParams','history.replaceState','正式要件','庁舎AI案内','prefers-reduced-motion','Updated 2026-09-02']
    for t in req:
        if t not in c: errors.append(f'cityhall必須要素不足: {t}')
    if c.count('data-pin=')<4: errors.append('cityhall地点ピンが4件未満です')

if Path('manifest.webmanifest').exists():
    try:
        m=json.loads(Path('manifest.webmanifest').read_text(encoding='utf-8'))
        for key in ['name','short_name','id','start_url','scope','display','icons']:
            if key not in m: errors.append(f'manifest必須キー不足: {key}')
        if not m.get('icons'): errors.append('manifestアイコンがありません')
        elif m['icons'][0].get('src')!='./icon.svg': errors.append('manifestアイコン参照がicon.svgではありません')
        if len(m.get('shortcuts',[]))<2: errors.append('manifest shortcutsが2件未満です')
    except Exception as e: errors.append(f'manifest JSON不正: {e}')

if Path('sw.js').exists():
    sw=Path('sw.js').read_text(encoding='utf-8')
    for t in ['./index.html','./cityhall.html','./offline.html','./manifest.webmanifest','./icon.svg']:
        if t not in sw: errors.append(f'オフラインキャッシュ対象不足: {t}')
    if "url.origin!==self.location.origin" not in sw: errors.append('Service Workerに同一オリジン制限がありません')
    if "req.mode==='navigate'" not in sw: errors.append('Service Workerにナビゲーション専用フォールバックがありません')
    if "caches.match('./offline.html')" not in sw: errors.append('Service Workerに専用offlineフォールバックがありません')
    if "caches.match('./index.html')" in sw: errors.append('任意失敗URLをindexへ誤フォールバックする旧処理が残っています')

if Path('offline.html').exists():
    o=audit_html('offline.html')
    if 'オフラインです' not in o or '災害時' not in o: errors.append('offline画面の案内不足')

if errors:
    print('VALIDATION FAILED')
    for e in errors: print('-',e)
    sys.exit(1)
print('VALIDATION PASSED: v0.4.1 UX, accessibility, PWA, offline resilience, twin state and local-link invariants are satisfied')