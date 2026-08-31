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
        'Sodegau-Ride',
        'Digital Twin',
        'Myクローン',
        '非公式プロトタイプ',
    ]
    for token in required:
        if token not in s:
            errors.append(f'必須要素不足: {token}')
    if 'http-equiv="refresh"' in s.lower():
        errors.append('意図しないmeta refreshが残っています')
    if 'target="_blank"' in s and 'noopener' not in s:
        errors.append('外部リンクのnoopenerが不足しています')
    if s.count('id="siteSearch"') != 1:
        errors.append('siteSearch IDが一意ではありません')
    if s.count('role="tab"') != 3:
        errors.append('固定3タブの数が3ではありません')
    subs = re.findall(r'"subs":\[(.*?)\]', s)
    if len(subs) != 8:
        errors.append(f'行政大分類が8件ではありません: {len(subs)}')

if errors:
    print('VALIDATION FAILED')
    for e in errors:
        print('-', e)
    sys.exit(1)
print('VALIDATION PASSED: Sodegau-Ride release invariants are satisfied')
