import sys
import pptx

prs = pptx.Presentation("C:\\Users\\harini\\.gemini\\antigravity\\brain\\c788c5c0-c2d6-4368-89fb-fb5804766273\\.user_uploaded\\media_1793801318515_b9946fe2.pptx")
print(f"Total slides: {len(prs.slides)}")

for idx, slide in enumerate(prs.slides):
    title = slide.shapes.title.text if slide.shapes.title else "No Title"
    print(f"\n--- Slide {idx+1}: {title} ---")
    for shape in slide.shapes:
        if shape.has_text_frame:
            for p in shape.text_frame.paragraphs:
                txt = p.text.strip()
                if txt and txt != title:
                    print(f"  * {txt.encode('ascii', errors='backslashreplace').decode('ascii')}")
