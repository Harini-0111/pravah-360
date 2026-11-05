import pypdf

reader = pypdf.PdfReader("C:\\Users\\harini\\.gemini\\antigravity\\brain\\c788c5c0-c2d6-4368-89fb-fb5804766273\\.user_uploaded\\media_1793801312578_2a466743.pdf")

def print_outline(outline, depth=0):
    for item in outline:
        if isinstance(item, list):
            print_outline(item, depth + 1)
        else:
            title = item.title if hasattr(item, 'title') else str(item)
            page = reader.get_destination_page_number(item) + 1 if hasattr(item, 'page') else '?'
            print(f"{'  '*depth}* {title} (p. {page})")

print("=== OUTLINE OF REFERENCE REPORT ===")
print_outline(reader.outline)
