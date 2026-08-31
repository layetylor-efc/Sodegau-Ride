from pathlib import Path
import re, sys

p = Path('index.html')
errors = []
if not p.exists():
    errors.append('index.html が存在しません')
else:
    s = p.read_text(encoding='utf-8')
    required = [
        '<!doctype html>',
        'data-view="admin"',
        'data-view="needs"',
        'data-view="dx"',
        'id="adminView"',
        'id="needsView"',
        'id="dxView"',
        'id="siteSearch"',
        'id="aiInput"',
        'id="future"',
        'id="kpi"',
        'id="voice"',
        'id="quest"',
        'id="twin"',
        'Sodegau-Ride',
        'Digital Twin',
        '市庁舎 Digital Twin',
        '2035年の袖ケ浦を見る',
        'AI市政コンシェルジュ',
        'Accessibility Mode',
        '非公式プロトタイプ',
        'v0.3.1',
        'Updated 2026-09-01',
    ]
    for token in required:
        if token not in s:
            errors.append(f'必須要素不足: {token}')
    if 'http-equiv="refresh"' in s.lower():
        errors.append('意図しないmeta refreshが残っています')
    if 'target="_blank"' in s and 'noopener' not in s:
        errors.append('外部リンクのnoopenerが不足しています')
    for ident in ['siteSearch','aiInput','future','kpi','voice','quest','twin']:
        if s.count(f'id="{ident}"') != 1:
            errors.append(f'{ident} IDが一意ではありません')
    if s.count('role="tab"') != 3:
        errors.append('固定3タブの数が3ではありません')
    # JS object literals in this release use single quotes, so accept either quote style.
    subs = re.findall(r"subs\s*:\s*\[(.*?)\]", s, flags=re.S)
    if len(subs) != 8:
        errors.append(f'行政大分類が8件ではありません: {len(subs)}')
    for phrase in ['市民入力','AI整理','担当課','行政処理','KPI更新','回答','政策改善','Twin更新']:
        if phrase not in s:
            errors.append(f'都市OS循環の要素不足: {phrase}')
    for year in ['2026','2030','2035','2040']:
        if f'data-year="{year}"' not in s:
            errors.append(f'未来時間軸不足: {year}')
    for mode in ['a11y','dark','lowdata']:
        if mode not in s:
            errors.append(f'表示モード不足: {mode}')
    if 'localStorage' not in s:
        errors.append('Phase 1端末内設定がありません')
    if 'prefers-reduced-motion' not in s:
        errors.append('reduced motion対応がありません')
    if 'DEMO / 予測ではありません' not in s:
        errors.append('未来シミュレーションのDEMO注記がありません')
    if '公式 自動運転バス' not in s:
        errors.append('公式交通情報への導線がありません')

if errors:
    print('VALIDATION FAILED')
    for e in errors:
        print('-', e)
    sys.exit(1)
print('VALIDATION PASSED: Sodegau-Ride urban OS v0.3.1 invariants are satisfied')
