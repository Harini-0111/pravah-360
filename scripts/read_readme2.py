with open(r"C:\Users\harini\Downloads\drive-download-20261101T162443Z-1-001\README (2).md", "r", encoding="utf-8") as f:
    lines = f.readlines()

for i, l in enumerate(lines[:50]):
    print(f"L{i}: {l.strip()}")
