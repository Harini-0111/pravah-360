import zlib
import re

pdf_path = r"C:\Users\harini\Downloads\drive-download-20261101T162443Z-1-001\cGodavari_Flood_Hazard_Map_Report_20260408.pdf"

with open(pdf_path, "rb") as f:
    data = f.read()

pos = 0
decompressed_chunks = []
while True:
    s_idx = data.find(b"stream", pos)
    if s_idx == -1:
        break
    # Skip \r\n
    start_data = s_idx + 6
    if data[start_data:start_data+2] == b"\r\n":
        start_data += 2
    elif data[start_data:start_data+1] in (b"\r", b"\n"):
        start_data += 1
    
    e_idx = data.find(b"endstream", start_data)
    if e_idx == -1:
        break
    
    stream_bytes = data[start_data:e_idx].strip()
    try:
        decomp = zlib.decompress(stream_bytes)
        # Check if text is present
        if b"BT" in decomp and b"ET" in decomp:
            decompressed_chunks.append(decomp)
    except Exception:
        pass
    pos = e_idx + 9

print(f"Extracted text streams: {len(decompressed_chunks)}")
text_all = []
for chunk in decompressed_chunks:
    # Extract string literals in parens
    matches = re.findall(rb"\((.*?)\)", chunk)
    for m in matches:
        try:
            s = m.decode("utf-8", errors="ignore").strip()
            if len(s) > 3 and not s.startswith("http"):
                text_all.append(s)
        except Exception:
            pass

print(f"Total extracted text fragments: {len(text_all)}")
full_text = " ".join(text_all)
print("Sample extracted text:")
print(full_text[:2000])

# Search for keywords
for kw in ["Godavari", "Flood", "Hazard", "Dowleswaram", "Sentinel", "HEC-RAS", "DEM", "2022", "2026", "Abstract", "Methodology"]:
    cnt = len(re.findall(re.escape(kw), full_text, re.IGNORECASE))
    print(f"Keyword '{kw}': {cnt} matches")
