import re
import zlib

pdf_path = r"C:\Users\harini\Downloads\drive-download-20261101T162443Z-1-001\cGodavari_Flood_Hazard_Map_Report_20260408.pdf"

with open(pdf_path, "rb") as f:
    data = f.read()

obj_pattern = re.compile(rb'(\d+)\s+(\d+)\s+obj(.*?)endobj', re.DOTALL)
objects = {int(m.group(1)): m.group(3) for m in obj_pattern.finditer(data)}

def is_page(node):
    return bool(re.search(rb'/Type\s*/Page\b(?![sS])', node))

def is_pages(node):
    return bool(re.search(rb'/Type\s*/Pages\b', node))

root_id = int(re.search(rb'/Root\s+(\d+)\s+0\s+R', data).group(1))
pages_id = int(re.search(rb'/Pages\s+(\d+)\s+0\s+R', objects[root_id]).group(1))

ordered_pages = []
def traverse(nid):
    node = objects.get(nid, b'')
    if is_page(node):
        ordered_pages.append(nid)
    elif is_pages(node):
        kids = re.findall(rb'(\d+)\s+0\s+R', re.search(rb'/Kids\s*\[(.*?)\]', node, re.DOTALL).group(1))
        for k in kids:
            traverse(int(k))

traverse(pages_id)
print(f"Found ordered pages: {len(ordered_pages)}")

def get_stream_data(obj_body):
    s_idx = obj_body.find(b"stream")
    if s_idx == -1:
        return b""
    start_data = s_idx + 6
    if obj_body[start_data:start_data+2] == b"\r\n":
        start_data += 2
    elif obj_body[start_data:start_data+1] in (b"\r", b"\n"):
        start_data += 1
    
    e_idx = obj_body.find(b"endstream", start_data)
    if e_idx == -1:
        return b""
    raw = obj_body[start_data:e_idx].strip()
    try:
        return zlib.decompress(raw)
    except Exception:
        return raw

def parse_text_from_stream(stream):
    bt_et = re.findall(rb'BT(.*?)ET', stream, re.DOTALL)
    page_text_lines = []
    
    for block in bt_et:
        # Match TJ arrays or Tj strings
        # Look for tokens in block
        # In PDF: [ (str1) offset (str2) ... ] TJ
        # or (str) Tj
        # or (str) '
        for match in re.finditer(rb'(\[(?:[^\[\]]*)\]\s*TJ|\((?:[^()\\]|\\.)*\)\s*(?:Tj|\'|\"))', block, re.DOTALL):
            cmd = match.group(0).strip()
            if cmd.endswith(b'TJ'):
                inner = cmd[1:cmd.rfind(b']')]
                tokens = re.findall(rb'\(((?:[^()\\]|\\.)*)\)|(-?\d+(?:\.\d+)?)', inner)
                line_parts = []
                for s, num in tokens:
                    if s:
                        decoded = s.replace(rb'\(', b'(').replace(rb'\)', b')').replace(rb'\\', b'\\')
                        try:
                            line_parts.append(decoded.decode('utf-8', errors='ignore'))
                        except Exception:
                            line_parts.append(decoded.decode('latin1', errors='ignore'))
                    elif num:
                        val = float(num)
                        if val < -100:  # kerning threshold for space
                            line_parts.append(' ')
                line = "".join(line_parts).strip()
                if line:
                    page_text_lines.append(line)
            else:
                # Tj or '
                s_match = re.search(rb'\(((?:[^()\\]|\\.)*)\)', cmd)
                if s_match:
                    s = s_match.group(1)
                    decoded = s.replace(rb'\(', b'(').replace(rb'\)', b')').replace(rb'\\', b'\\')
                    try:
                        line = decoded.decode('utf-8', errors='ignore').strip()
                    except Exception:
                        line = decoded.decode('latin1', errors='ignore').strip()
                    if line:
                        page_text_lines.append(line)

    return "\n".join(page_text_lines)

page_contents = {}
for idx, page_id in enumerate(ordered_pages):
    page_num = idx + 1
    page_obj = objects.get(page_id, b"")
    contents_match = re.search(rb'/Contents\s+(\d+)\s+0\s+R', page_obj)
    contents_arr_match = re.search(rb'/Contents\s*\[(.*?)\]', page_obj, re.DOTALL)
    stream_data = b""
    if contents_match:
        c_id = int(contents_match.group(1))
        stream_data = get_stream_data(objects.get(c_id, b""))
    elif contents_arr_match:
        c_ids = re.findall(rb'(\d+)\s+0\s+R', contents_arr_match.group(1))
        for c_id in c_ids:
            stream_data += get_stream_data(objects.get(int(c_id), b""))
    
    txt = parse_text_from_stream(stream_data)
    page_contents[page_num] = txt

print("Successfully parsed 50 pages!")
with open("data/reference_extracted_text.txt", "w", encoding="utf-8") as out:
    for p_num in range(1, 51):
        p_txt = page_contents.get(p_num, "")
        out.write(f"=== PAGE {p_num} ===\n")
        out.write(p_txt + "\n\n")

print("Output written to data/reference_extracted_text.txt")
