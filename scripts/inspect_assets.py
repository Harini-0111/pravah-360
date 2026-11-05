import re
from pathlib import Path

with open('frontend/app.js', 'r', encoding='utf-8') as f:
    text = f.read()

urls = re.findall(r'(https?:)?//[^\s\'\"\)\>]+', text)
for u in sorted(set(urls)):
    print('Found URL in app.js:', u)

# Check what textures exist in frontend/
print('\nExisting files in frontend/data and frontend/overlays:')
for p in Path('frontend').glob('**/*'):
    if p.is_file():
        print(f"  {p} ({p.stat().st_size:,} bytes)")
