import docx

doc = docx.Document("C:\\major project\\mp.docx")

for i in range(135):
    text = doc.paragraphs[i].text.strip()
    if text:
        print(f"[{i}] {text}")
