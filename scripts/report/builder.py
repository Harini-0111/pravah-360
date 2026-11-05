import os
import sys
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

from scripts.report.content_ch3 import CH3_COMPLETION
from scripts.report.content_ch4 import CH4_CONTENT
from scripts.report.content_ch5 import CH5_CONTENT
from scripts.report.content_ch6 import CH6_CONTENT
from scripts.report.content_ch7 import CH7_CONTENT
from scripts.report.content_ch8 import CH8_CONTENT
from scripts.report.content_ch9 import CH9_CONTENT
from scripts.report.content_ch10 import CH10_CONTENT
from scripts.report.content_ch11 import CH11_CONTENT
from scripts.report.content_refs_appendices import REFERENCES, APPENDICES
from scripts.report.toc_structure import TOC_ENTRIES

ARTIFACT_DIR = "C:\\Users\\harini\\.gemini\\antigravity\\brain\\c788c5c0-c2d6-4368-89fb-fb5804766273"
PROJECT_DIR = "C:\\major project"

IMAGE_MAP = {
    "landing_header_english": os.path.join(ARTIFACT_DIR, "landing_header_english.png"),
    "telugu_voice_assistant_verified": os.path.join(ARTIFACT_DIR, "telugu_voice_assistant_verified.png"),
    "header_desktop_1536x864": os.path.join(ARTIFACT_DIR, "header_desktop_1536x864.png"),
    "sentinel1_flood_candidates": os.path.join(PROJECT_DIR, "frontend", "overlays", "sentinel1_flood_candidates_track129.png"),
    "notification_drawer_verified": os.path.join(ARTIFACT_DIR, "notification_drawer_verified.png"),
    "cyclone_murasu_replay_modal": os.path.join(ARTIFACT_DIR, "cyclone_murasu_replay_modal.png"),
    "model_validation_modal": os.path.join(ARTIFACT_DIR, "model_validation_modal.png"),
}

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('w:top', top), ('w:bottom', bottom), ('w:left', left), ('w:right', right)]:
        node = OxmlElement(m)
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def set_cell_shading(cell, color_hex):
    shading_elm = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{color_hex}"/>')
    cell._tc.get_or_add_tcPr().append(shading_elm)

def add_styled_heading(doc, text, level):
    p = doc.add_paragraph()
    p.paragraph_format.keep_with_next = True
    p.paragraph_format.space_before = Pt(14)
    p.paragraph_format.space_after = Pt(6)
    run = p.add_run(text)
    run.font.name = "Times New Roman"
    run.bold = True
    if level == 1:
        run.font.size = Pt(18)
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    elif level == 2:
        run.font.size = Pt(14)
        run.font.color.rgb = RGBColor(0, 32, 96) # Academic Navy
    elif level == 3:
        run.font.size = Pt(12)
        run.bold = True
    return p

def add_body_p(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.line_spacing = 1.15
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    run = p.add_run(text)
    run.font.name = "Times New Roman"
    run.font.size = Pt(12)
    return p

def add_code_block(doc, text):
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = table.cell(0, 0)
    set_cell_shading(cell, "F2F4F7")
    set_cell_margins(cell, top=120, bottom=120, left=200, right=200)
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.line_spacing = 1.05
    run = p.add_run(text.strip())
    run.font.name = "Consolas"
    run.font.size = Pt(9.5)
    run.font.color.rgb = RGBColor(30, 30, 30)
    doc.add_paragraph() # Spacing

def add_image_figure(doc, img_path, figure_num, caption):
    if os.path.exists(img_path):
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_before = Pt(10)
        p_img.paragraph_format.space_after = Pt(4)
        run_img = p_img.add_run()
        run_img.add_picture(img_path, width=Inches(6.0))
        
        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.space_before = Pt(2)
        p_cap.paragraph_format.space_after = Pt(12)
        run_num = p_cap.add_run(f"Figure {figure_num}: ")
        run_num.font.name = "Times New Roman"
        run_num.font.size = Pt(10.5)
        run_num.bold = True
        run_txt = p_cap.add_run(caption)
        run_txt.font.name = "Times New Roman"
        run_txt.font.size = Pt(10.5)
        run_txt.italic = True
    else:
        print(f"Warning: Image not found at {img_path}")

def fix_preliminary_pages(doc):
    print("Fixing preliminary pages (Title, Student names, Certificate, Declaration)...")
    replacements = {
        "Uncertainity-Calibrated Geospatial AI for Flood Susceptibility and Emergency Resource Allocation": "Uncertainty-Calibrated Geospatial AI for Flood Susceptibility and Emergency Resource Allocation",
        "Uncertainity-Calibrated Geospatial AI Susceptibility and Emergency Resource Allocation": "Uncertainty-Calibrated Geospatial AI for Flood Susceptibility and Emergency Resource Allocation",
        "D.J.S.L.P.Durga-23A81A4311": "D. Jnana Sri - 23A81A4311",
        "D.J.S.L.P.Durga(23A81A4311)": "D. Jnana Sri (23A81A4311)",
        "D.J.SL.P.Durga-23A81A4311": "D. Jnana Sri - 23A81A4311",
        "P.Likhtiha": "P. Likhitha",
        "P.Likhtiha(23A81A4349)": "P. Likhitha (23A81A4349)",
        "P.Likhtiha-23A81A4349": "P. Likhitha - 23A81A4349",
        "P.Harini-23A81A4348": "P. Harini - 23A81A4348",
        "P.Likhitha-23A81A4349": "P. Likhitha - 23A81A4349",
        "K.Mokshagna Sai Teja-23A81A4321": "K. Mokshagna Sai Teja - 23A81A4321",
    }
    for p in doc.paragraphs[:135]:
        for old_txt, new_txt in replacements.items():
            if old_txt in p.text:
                for run in p.runs:
                    if old_txt in run.text:
                        run.text = run.text.replace(old_txt, new_txt)
                if old_txt in p.text: # If split across runs
                    p.text = p.text.replace(old_txt, new_txt)

def rebuild_table_of_contents(doc):
    print("Replacing old FinRAG AI TOC tables with unified Flood Geospatial AI TOC...")
    # Table 1 is the main TOC table in mp.docx.
    # Table 2 and 3 are legacy continuations that must be emptied/deleted.
    t1 = doc.tables[1]
    
    # Clear Table 2 and Table 3 rows to purge FinRAG AI content
    t2 = doc.tables[2]
    t3 = doc.tables[3]
    for r in list(t2.rows)[1:]:
        t2._tbl.remove(r._tr)
    for r in list(t3.rows)[1:]:
        t3._tbl.remove(r._tr)
    # Hide t2 and t3 headers
    for cell in t2.rows[0].cells:
        cell.text = ""
    for cell in t3.rows[0].cells:
        cell.text = ""

    # Rebuild t1 with TOC_ENTRIES
    # Clear existing rows except header
    for r in list(t1.rows)[1:]:
        t1._tbl.remove(r._tr)

    # Style header row
    hdr = t1.rows[0]
    hdr.cells[0].text = "S.NO"
    hdr.cells[1].text = "TITLE"
    hdr.cells[2].text = "PAGE NO."
    for cell in hdr.cells:
        set_cell_shading(cell, "002060") # Dark Navy
        set_cell_margins(cell, top=120, bottom=120, left=150, right=150)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for r in p.runs:
            r.font.name = "Times New Roman"
            r.font.size = Pt(11)
            r.bold = True
            r.font.color.rgb = RGBColor(255, 255, 255)

    # Add TOC entries
    for s_no, title, page_no in TOC_ENTRIES:
        row = t1.add_row()
        c0, c1, c2 = row.cells[0], row.cells[1], row.cells[2]
        c0.text = s_no
        c1.text = title
        c2.text = page_no
        
        c0.width = Inches(0.8)
        c1.width = Inches(5.0)
        c2.width = Inches(1.0)
        
        set_cell_margins(c0, top=60, bottom=60, left=100, right=100)
        set_cell_margins(c1, top=60, bottom=60, left=100, right=100)
        set_cell_margins(c2, top=60, bottom=60, left=100, right=100)
        
        p0 = c0.paragraphs[0]
        p1 = c1.paragraphs[0]
        p2 = c2.paragraphs[0]
        
        p0.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p1.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p2.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        
        is_major = (s_no != "" and not s_no.startswith(" ")) or title in ["ABSTRACT", "REFERENCES"] or title.startswith("APPENDIX")
        for p, is_bold in [(p0, is_major), (p1, is_major), (p2, is_major)]:
            for r in p.runs:
                r.font.name = "Times New Roman"
                r.font.size = Pt(10)
                r.bold = is_bold
                if is_major and s_no != "":
                    r.font.color.rgb = RGBColor(0, 32, 96)

def append_chapter_sections(doc, sections):
    for sec in sections:
        level = sec.get("level", 2)
        title_text = f"{sec['num']} {sec['title']}" if sec.get('num') else sec['title']
        add_styled_heading(doc, title_text, level)
        for p_text in sec.get("paragraphs", []):
            if p_text.startswith("```"):
                continue # Handled by code blocks
            elif p_text.startswith("+--") or p_text.startswith("|") or "----+----" in p_text:
                add_code_block(doc, p_text)
            else:
                add_body_p(doc, p_text)
        if "image_key" in sec and sec["image_key"] in IMAGE_MAP:
            add_image_figure(doc, IMAGE_MAP[sec["image_key"]], sec.get("figure_num", "10.x"), sec.get("figure_caption", ""))

def build_full_report():
    doc_path = os.path.join(PROJECT_DIR, "mp.docx")
    print(f"Loading {doc_path}...")
    doc = docx.Document(doc_path)
    
    # Step 1: Fix preliminary pages
    fix_preliminary_pages(doc)
    
    # Step 2: Rebuild Table of Contents
    rebuild_table_of_contents(doc)
    
    # Step 3: Clean up empty trailing paragraphs from Chapter 3
    print("Trimming empty trailing paragraphs from Chapter 3...")
    while len(doc.paragraphs) > 315 and not doc.paragraphs[-1].text.strip():
        p = doc.paragraphs[-1]._p
        p.getparent().remove(p)
    
    # Step 4: Complete Chapter 3 (from 3.8 to 3.11)
    print("Appending Chapter 3 completion (3.8 - 3.11)...")
    append_chapter_sections(doc, CH3_COMPLETION["sections"])
    
    # Step 5: Chapters 4 through 11
    chapters = [
        CH4_CONTENT,
        CH5_CONTENT,
        CH6_CONTENT,
        CH7_CONTENT,
        CH8_CONTENT,
        CH9_CONTENT,
        CH10_CONTENT,
        CH11_CONTENT
    ]
    
    for ch in chapters:
        print(f"Appending Chapter {ch['num']}: {ch['title']}...")
        doc.add_page_break()
        ch_hdr = doc.add_paragraph()
        ch_hdr.alignment = WD_ALIGN_PARAGRAPH.CENTER
        ch_hdr.paragraph_format.space_before = Pt(24)
        ch_hdr.paragraph_format.space_after = Pt(6)
        r_num = ch_hdr.add_run(f"CHAPTER - {ch['num']}\n")
        r_num.font.name = "Times New Roman"
        r_num.font.size = Pt(18)
        r_num.bold = True
        r_num.font.color.rgb = RGBColor(0, 32, 96)
        
        r_title = ch_hdr.add_run(ch['title'])
        r_title.font.name = "Times New Roman"
        r_title.font.size = Pt(16)
        r_title.bold = True
        r_title.font.color.rgb = RGBColor(0, 32, 96)
        
        append_chapter_sections(doc, ch.get("sections", []))
    
    # Step 6: References
    print("Appending References...")
    doc.add_page_break()
    ref_hdr = add_styled_heading(doc, "REFERENCES", level=1)
    for idx, ref in enumerate(REFERENCES, 1):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.left_indent = Inches(0.5)
        p.paragraph_format.first_line_indent = Inches(-0.5)
        p.paragraph_format.line_spacing = 1.15
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        run = p.add_run(f"[{idx}]  {ref}")
        run.font.name = "Times New Roman"
        run.font.size = Pt(11)
        
    # Step 7: Appendices A through F
    print("Appending Appendices A through F...")
    for app in APPENDICES:
        doc.add_page_break()
        add_styled_heading(doc, f"APPENDIX {app['id']}: {app['title']}", level=1)
        for p_text in app["paragraphs"]:
            if p_text.startswith("```") or p_text.startswith("+--") or "| ID |" in p_text:
                add_code_block(doc, p_text)
            else:
                add_body_p(doc, p_text)
                
    # Save the completed Word document
    out_docx = os.path.join(PROJECT_DIR, "mp_final_completed.docx")
    print(f"Saving final completed document to {out_docx} and {doc_path}...")
    doc.save(out_docx)
    doc.save(doc_path)
    print("Successfully built completed Major Project Report document!")

if __name__ == "__main__":
    build_full_report()
