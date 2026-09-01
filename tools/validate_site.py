from pathlib import Path
import re, sys

errors = []

index = Path('index.html')
cityhall = Path('cityhall.html')

if not index.exists():
    errors.append('index.html が存在しません')
else:
    s = index.read_text(encoding='utf-8')
    required = [
        '<!doctype html>', 'data-view="admin"', 'data-view="needs"', 'data-view="dx"',
        'id="adminView"', 'id="needsView"', 'id="dxView"', 'id="siteSearch"',
        'id="aiInput"', 'id="future"', 'id="kpi"', 'id="voice"', 'id="quest"',
        'Sodegau-Ride', 'Digital Twin', '2035年の袖ケ浦を見る', 'AI市政コンシェルジュ',
        'Accessibility Mode', '非公式プロトタイプ', 'v0.3.1', 'Updated 2026-09-01'
    ]
    for token in required:
        if token not in s:
            errors.append(f'index必須要素不足: {token}')
    if 'http-equiv="refresh"' in s.lower():
        errors.append('indexに意図しないmeta refreshがあります')
    if 'target="_blank"' in s and 'noopener' not in s:
        errors.append('index外部リンクのnoopenerが不足しています')
    if s.count('id="siteSearch"') != 1:
        errors.append('siteSearch IDが一意ではありません')
    if s.count('role="tab"') != 3:
        errors.append('固定3タブの数が3ではありません')
    subs = re.findall(r'\bsubs\s*:\s*\[(.*?)\]', s, re.S)
    if len(subs) != 8:
        errors.append(f'行政大分類が8件ではありません: {len(subs)}')
    for phrase in ['市民入力','AI整理','担当課','行政処理','KPI更新','政策改善','Twin更新']:
        if phrase not in s:
            errors.append(f'都市OS循環の要素不足: {phrase}')
    for year in ['2026','2030','2035','2040']:
        if f'data-year="{year}"' not in s:
            errors.append(f'未来時間軸不足: {year}')
    if 'localStorage' not in s:
        errors.append('Phase 1端末内設定がありません')
    if 'prefers-reduced-motion' not in s:
        errors.append('reduced motion対応がありません')

if not cityhall.exists():
    errors.append('cityhall.html が存在しません')
else:
    c = cityhall.read_text(encoding='utf-8')
    cityhall_required = [
        '袖ケ浦市庁舎 Digital Twin', '目的から庁舎を歩く', 'data-purpose="転入"',
        'data-purpose="住民票"', 'data-purpose="子育て"', 'data-purpose="福祉"',
        'data-floor="1F"', 'data-floor="2F"', 'data-floor="3F"', 'data-floor="全館"',
        '必要書類', '館内ルート', '庁舎AI案内', 'バリアフリー', 'DEMO / API未接続',
        'prefers-reduced-motion'
    ]
    for token in cityhall_required:
        if token not in c:
            errors.append(f'cityhall必須要素不足: {token}')
    if c.count('id="q"') != 1:
        errors.append('cityhall AI入力ID qが一意ではありません')
    if c.count('data-pin=') < 4:
        errors.append('cityhall地点ピンが4件未満です')
    if '正式確認必須' not in c and '正式要件' not in c:
        errors.append('cityhallに正式情報確認の注意書きがありません')

if errors:
    print('VALIDATION FAILED')
    for e in errors:
        print('-', e)
    sys.exit(1)
print('VALIDATION PASSED: Sodegau-Ride v0.3.1 + City Hall Twin module invariants are satisfied')
