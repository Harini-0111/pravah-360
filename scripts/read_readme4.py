with open(r"C:\Users\harini\Downloads\drive-download-20261101T162443Z-1-001\README (4).md", "r", encoding="utf-8") as f:
    text = f.read()

# Print sections
lines = text.split("\n")
for i, l in enumerate(lines):
    if l.startswith("#") or "http" in l or "parquet" in l or "bucket" in l or "blob" in l or "azure" in l or "aws" in l:
        print(f"L{i}: {l}")
