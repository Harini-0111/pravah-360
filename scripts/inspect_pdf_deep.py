import zlib
import re

pdf_path = r"C:\Users\harini\Downloads\drive-download-20261101T162443Z-1-001\cGodavari_Flood_Hazard_Map_Report_20260408.pdf"

with open(pdf_path, "rb") as f:
    data = f.read()

pos = 0
decompressed_chunks = []
while True:
    s_idx = data.find(b"stream", pos)
    if s_idx == -1: break
    start_data = s_idx + 6
    if data[start_data:start_data+2] == b"\r\n": start_data += 2
    elif data[start_data:start_data+1] in (b"\r", b"\n"): start_data += 1
    e_idx = data.find(b"endstream", start_data)
    if e_idx == -1: break
    stream_bytes = data[start_data:e_idx].strip()
    try:
        decomp = zlib.decompress(stream_bytes)
        if b"BT" in decomp and b"ET" in decomp:
            decompressed_chunks.append(decomp)
    except Exception:
        pass
    pos = e_idx + 9

lines = []
for chunk in decompressed_chunks:
    for m in re.findall(rb"\((.*?)\)", chunk):
        try:
            s = m.decode("utf-8", errors="ignore").strip()
            if len(s) > 1:
                lines.append(s)
        except Exception:
            pass

full_text = " ".join(lines)
# Find mentions of districts or return periods
print("--- PDF CONTENT ANALYSIS ---")
for kw in ["return period", "inundation", "hazard", "risk", "East Godavari", "West Godavari", "Kakinada", "Konaseema", "Polavaram", "Dowleswaram", "barrage", "cusecs", "cumecs", "HEC", "MIKE", "hydrodynamic", "10-year", "25-year", "50-year", "100-year"]:
    matches = re.findall(re.escape(kw), full_text, re.IGNORECASE)
    print(f"Keyword '{kw}': {len(matches)} matches")

# Print paragraphs containing 'Godavari' and 'Flood'
paras = full_text.split("  ")
sample_paras = [p for p in paras if "Godavari" in p and "Flood" in p and len(p) > 50]
print(f"\nMatching paragraphs count: {len(sample_paras)}")
for i, p in enumerate(sample_paras[:5]):
    print(f"\n[Paragraph {i+1}]: {p[:250]}...")
