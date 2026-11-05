import docx

doc = docx.Document("C:\\major project\\mp.docx")

print(f"Total paragraphs: {len(doc.paragraphs)}")
print(f"Total tables: {len(doc.tables)}")

print("\n--- FIRST 30 PARAGRAPHS ---")
for i, p in enumerate(doc.paragraphs[:30]):
    if p.text.strip():
        print(f"[{i}] ({p.style.name}): {p.text.strip()[:100]}")

print("\n--- LAST 30 PARAGRAPHS ---")
for i, p in enumerate(doc.paragraphs[-30:], start=len(doc.paragraphs)-30):
    if p.text.strip():
        print(f"[{i}] ({p.style.name}): {p.text.strip()[:100]}")

print("\n--- ALL HEADINGS ---")
for i, p in enumerate(doc.paragraphs):
    if "Heading" in p.style.name or p.text.strip().startswith("CHAPTER") or p.text.strip().startswith("Chapter"):
        print(f"[{i}] ({p.style.name}): {p.text.strip()}")
