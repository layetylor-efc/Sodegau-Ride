from pathlib import Path
from html.parser import HTMLParser
import json,re,sys,subprocess,shutil
errors=[]
required_files=['index.html','app.js','cityhall.html','cityhall.js','offline.html','manifest.webmanifest','sw.js','icon.svg','.nojekyll']
for f in required_files:
    if not Path(f).exists(): errors.append(f'必須ファイル不足: {f}')
class Audit(HTMLParser):
    def __init__(self,path): super().__init__();self.path=path;self.ids=[];self.links=[];self.blank=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'id' in a:self.ids.append(a['id'])
        if tag=='a' and a.get('href'):
            h=a['href'];self.links.append(h)
            if a.get('target')=='_blank':self.blank.append((h,a.get('rel','')))
def audit_html(path):
    text=Path(path).read_text(encoding='utf-8');p=Audit(path);p.feed(text)
    dup=sorted({x for x in p.ids if p.ids.count(x)>1})
    if dup:errors.append(f'{path} 重複ID: {dup}')
    for href in p.links:
        if href.startswith('./') and not href.startswith('./#'):
            target=href[2:].split('#')[0].split('?')[0]
            if target and not Path(target).exists():errors.append(f'{path} ローカルリンク切れ: {href}')
    for href,rel in p.blank:
        if 'noopener' not in rel:errors.append(f'{path} target=_blank noopener不足: {href}')
    if 'http-equiv="refresh"' in text.lower():errors.append(f'{path} meta refresh禁止')
    return text
if Path('index.html').exists():
    s=audit_html('index.html')
    tokens=['v0.5.0','data-view="admin"','data-view="needs"','data-view="dx"','role="tabpanel"','id="siteSearch"','id="emptyState"','id="aiInput"','AI市政コンシェルジュ','AIルーター','SodeMap Digital Twin','2035年の袖ケ浦を見る','未来予測の注意','市民入力','AI整理','担当課','行政処理','KPI更新','市民へ回答','政策改善','Twin更新','Accessibility Mode','低速回線モード','災害時モード','id="emergencyPanel"','id="networkStatus"','id="layerReset"','id="updateNotice"','./cityhall.html','./app.js','Updated 2026-09-02']
    for t in tokens:
        if t not in s:errors.append(f'index必須要素不足: {t}')
    if s.count('role="tab"')!=3:errors.append('固定3タブが3件ではありません')
    for y in ['2026','2030','2035','2040']:
        if f'data-year="{y}"' not in s:errors.append(f'未来時間軸不足: {y}')
    for layer in ['避難所','浸水','医療','交通','高齢化','市民の声']:
        if f'data-layer="{layer}"' not in s:errors.append(f'Twinレイヤー不足: {layer}')
if Path('app.js').exists():
    a=Path('app.js').read_text(encoding='utf-8')
    tokens=['safeStore','normalize(\'NFKC\')' if False else "normalize('NFKC')",'expandTerms','synonymGroups','routeMatches','alternatives','searchMatch','arrowGroup','setEmergency','emergencyPanel','localDateKey','getFullYear()','sr-layers','sr-zone','sr-year','sr-scenario','syncStateUrl','URLSearchParams','history.replaceState','showUpdate','reg.waiting','SKIP_WAITING','controllerchange','navigator.onLine','escapeHtml','serviceWorker']
    for t in tokens:
        if t not in a:errors.append(f'app.js 改善機能不足: {t}')
    subs=re.findall(r'\bsubs\s*:\s*\[(.*?)\]',a,re.S)
    if len(subs)!=8:errors.append(f'行政大分類が8件ではありません: {len(subs)}')
    if "toISOString().slice(0,10)" in a:errors.append('クエスト日付にUTC判定が残っています')
if Path('cityhall.html').exists():
    c=audit_html('cityhall.html')
    for t in ['v0.5.0','中庁舎1F','北庁舎1F','北庁舎5F','2～4階','data-purpose="転入・住民票"','data-purpose="税"','data-purpose="福祉"','data-purpose="議会"','data-floor="5F"','data-building="北庁舎"','状態リンクをコピー','正式要件','庁舎AI案内','./cityhall.js','Updated 2026-09-02']:
        if t not in c:errors.append(f'cityhall必須要素不足: {t}')
    if c.count('data-pin=')<4:errors.append('cityhall地点ピンが4件未満')
if Path('cityhall.js').exists():
    cj=Path('cityhall.js').read_text(encoding='utf-8')
    for t in ['URLSearchParams','history.replaceState','buildings.includes','floors.includes','navigator.share','navigator.clipboard','document.execCommand','aria-pressed','bindArrow','mismatch()','推奨位置と現在の選択が異なります','esc']:
        if t not in cj:errors.append(f'cityhall.js 状態共有/防御不足: {t}')
if Path('manifest.webmanifest').exists():
    try:
        m=json.loads(Path('manifest.webmanifest').read_text(encoding='utf-8'))
        for k in ['name','short_name','id','start_url','scope','display','icons','shortcuts']:
            if k not in m:errors.append(f'manifest必須キー不足: {k}')
        if len(m.get('shortcuts',[]))<3:errors.append('manifest shortcutsが3件未満')
        if not m.get('icons') or m['icons'][0].get('src')!='./icon.svg':errors.append('manifest icon不正')
    except Exception as e:errors.append(f'manifest JSON不正: {e}')
if Path('sw.js').exists():
    sw=Path('sw.js').read_text(encoding='utf-8')
    for t in ['./index.html','./app.js','./cityhall.html','./cityhall.js','./offline.html','./manifest.webmanifest','./icon.svg']:
        if t not in sw:errors.append(f'SW shell不足: {t}')
    for t in ["url.origin!==self.location.origin","req.mode==='navigate'","caches.match('./offline.html')","sodegau-ride-v051",'CACHEABLE_PATHS','normalizedNavigationRequest',"u.search=''",'SKIP_WAITING','event.waitUntil']:
        if t not in sw:errors.append(f'SW安全要件不足: {t}')
    if "caches.match('./index.html')" in sw:errors.append('旧index誤フォールバックが残っています')
    if 'c.put(req' in sw:errors.append('クエリ付きrequestを直接キャッシュする旧処理が残っています')
if Path('offline.html').exists():
    o=audit_html('offline.html')
    for t in ['オフラインです','災害時','保存済み市庁舎Twin','再接続を試す']:
        if t not in o:errors.append(f'offline案内不足: {t}')
node=shutil.which('node')
if node:
    for js in ['app.js','cityhall.js','sw.js']:
        if Path(js).exists():
            p=subprocess.run([node,'--check',js],capture_output=True,text=True)
            if p.returncode:errors.append(f'{js} JavaScript構文エラー: {p.stderr.strip()}')
else:
    errors.append('node が見つからずJavaScript構文検査を実行できません')
if errors:
    print('VALIDATION FAILED')
    for e in errors:print('-',e)
    sys.exit(1)
print('VALIDATION PASSED: v0.5 hardening gate; local-date quest, fuzzy search, shared twin/future state, bounded PWA cache, cityhall consistency and JS syntax are satisfied')
