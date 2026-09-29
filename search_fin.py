import os
import re
import json

keywords = re.compile(r'(harga_jual|harga_modal|omset|keuntungan|untung|Rp\s)', re.IGNORECASE)
res = []

for r, d, files in os.walk('.'):
    for f in files:
        if f.endswith('.py') and ('pages' in r or 'utils' in r):
            file_path = os.path.join(r, f)
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    for i, l in enumerate(file):
                        if keywords.search(l):
                            res.append(f"{os.path.relpath(file_path)}:{i+1}: {l.strip()}")
            except Exception as e:
                pass

with open('grep_results.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(res))
