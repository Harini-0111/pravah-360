with open('frontend/index.html', 'r', encoding='utf-8') as f:
    c = f.read()

import re
c = re.sub(r'https://unpkg\.com/leaflet@1\.9\.4/dist/leaflet\.css[^"]*', '/static/leaflet/leaflet.css', c)
c = re.sub(r'https://unpkg\.com/leaflet@1\.9\.4/dist/leaflet\.js[^"]*', '/static/leaflet/leaflet.js', c)
# remove leftover integrity/crossorigin attributes
c = c.replace(' integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=" crossorigin=""', '')
c = c.replace(' integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo=" crossorigin=""', '')

with open('frontend/index.html', 'w', encoding='utf-8') as f:
    f.write(c)

print("Updated index.html to use local leaflet successfully.")
