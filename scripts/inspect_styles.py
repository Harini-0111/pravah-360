import docx

doc = docx.Document("C:\\major project\\mp.docx")

print("=== SECTIONS & MARGINS ===")
for s_idx, section in enumerate(doc.sections):
    print(f"Section {s_idx}: top={section.top_margin.inches}in, bottom={section.bottom_margin.inches}in, left={section.left_margin.inches}in, right={section.right_margin.inches}in, page_width={section.page_width.inches}in, page_height={section.page_height.inches}in")

print("\n=== STYLES AVAILABLE ===")
for style in doc.styles:
    if style.type == docx.enum.style.WD_STYLE_TYPE.PARAGRAPH:
        font_name = style.font.name if style.font else "Default"
        font_size = style.font.size.pt if style.font and style.font.size else "Default"
        print(f"  Paragraph Style: '{style.name}' (font: {font_name}, size: {font_size})")

print("\n=== SAMPLE RUNS FROM CHAPTER 1 ===")
for p in doc.paragraphs[130:145]:
    if p.text.strip():
        runs_info = []
        for r in p.runs[:3]:
            r_font = r.font.name or "inherited"
            r_size = r.font.size.pt if r.font.size else "inherited"
            r_bold = r.bold
            runs_info.append(f"'{r.text[:20]}' [{r_font}, {r_size}pt, bold={r_bold}]")
        print(f"P ({p.style.name}): {' | '.join(runs_info)}")
