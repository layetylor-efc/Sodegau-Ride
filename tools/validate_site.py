from pathlib import Path
import re, sys
errors=[]
required_files=['index.html','cityhall.html','manifest.webmanifest','sw.js','.nojekyll']
for f in required_files:
    if not Path(f).exists(): errors.append(f'必須ファイル不足: {f}')
if Path('index.html').exists():
    s=Path('index.html').read_text(encoding='utf-8')
    required=['<!doctype html>','v0.4.0','data-view="admin"','data-view="needs"','data-view="dx"','id="adminView"','id="needsView"','id="dxView"','id="siteSearch"','id="aiInput"','AI市政コンシェルジュ','AIルーター','SodeMap Digital Twin','2035年の袖ケ浦を見る','Adaptive Cities参考','上回る基準','市民入力','AI整理','担当課','行政処理','KPI更新','市民へ回答','政策改善','Twin更新','Accessibility Mode','低速回線モード','災害時モード','serviceWorker','manifest.webmanifest','./cityhall.html','Updated 2026-09-01']
    for t in required:
        if t not in s: errors.append(f'index必須要素不足: {t}')
    if s.count('role="tab"')!=3: errors.append('固定3タブの数が3ではありません')
    if s.count('id="siteSearch"')!=1: errors.append('siteSearch IDが一意ではありません')
    subs=re.findall(r'\bsubs\s*:\s*\[(.*?)\]',s,re.S)
    if len(subs)!=8: errors.append(f'行政大分類が8件ではありません: {len(subs)}')
    for y in ['2026','2030','2035','2040']:
        if f'data-year="{y}"' not in s: errors.append(f'未来時間軸不足: {y}')
    for layer in ['避難所','浸水','医療','交通','高齢化','市民の声']:
        if f'data-layer="{layer}"' not in s: errors.append(f'Digital Twinレイヤー不足: {layer}')
    if 'localStorage' not in s: errors.append('端末内状態保持がありません')
    if 'prefers-reduced-motion' not in s: errors.append('reduced-motion対応がありません')
    if 'target="_blank"' in s and 'noopener' not in s: errors.append('外部リンクnoopener不足')
    if 'http-equiv="refresh"' in s.lower(): errors.append('意図しないmeta refreshがあります')
if Path('cityhall.html').exists():
    c=Path('cityhall.html').read_text(encoding='utf-8')
    req=['袖ケ浦市庁舎 Digital Twin','v0.4','中庁舎1F','北庁舎1F','北庁舎5F','2～4階','data-purpose="転入・住民票"','data-purpose="税"','data-purpose="福祉"','data-purpose="議会"','data-floor="1F"','data-floor="5F"','data-building="中庁舎"','data-building="北庁舎"','市民課の待ち時間','正式要件','庁舎AI案内','prefers-reduced-motion']
    for t in req:
        if t not in c: errors.append(f'cityhall必須要素不足: {t}')
    if c.count('id="q"')!=1: errors.append('cityhall AI入力 q が一意ではありません')
    if c.count('data-pin=')<4: errors.append('cityhall地点ピンが4件未満です')
    if 'target="_blank"' in c and 'noopener' not in c: errors.append('cityhall外部リンクnoopener不足')
if Path('sw.js').exists():
    sw=Path('sw.js').read_text(encoding='utf-8')
    for t in ['./index.html','./cityhall.html','./manifest.webmanifest']:
        if t not in sw: errors.append(f'オフラインキャッシュ対象不足: {t}')
if errors:
    print('VALIDATION FAILED')
    for e in errors: print('-',e)
    sys.exit(1)
print('VALIDATION PASSED: Sodegau-Ride v0.4 urban OS benchmark release invariants are satisfied')