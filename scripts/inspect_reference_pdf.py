import pypdf

reader = pypdf.PdfReader("C:\\Users\\harini\\.gemini\\antigravity\\brain\\c788c5c0-c2d6-4368-89fb-fb5804766273\\.user_uploaded\\media_1793801312578_2a466743.pdf")
print(f"Total pages in reference PDF: {len(reader.pages)}")

# Print outline if available
try:
    outline = reader.outline
    print(f"Outline items: {len(outline)}")
except Exception as e:
    print(f"No outline: {e}")

# Inspect first 10 pages text
for i in range(min(12, len(reader.pages))):
    text = reader.pages[i].extract_text()
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    print(f"\n--- Page {i+1} ({len(lines)} lines) ---")
    for line in lines[:8]:
        print(f"  {line}")
