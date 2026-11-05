import docx

doc = docx.Document("C:\\major project\\mp.docx")

for i in range(300, len(doc.paragraphs)):
    text = doc.paragraphs[i].text.strip()
    print(f"[{i}] ({doc.paragraphs[i].style.name}): {text}")
