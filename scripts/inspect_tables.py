import docx

doc = docx.Document("C:\\major project\\mp.docx")
print(f"Total tables: {len(doc.tables)}")

for t_idx, table in enumerate(doc.tables):
    print(f"\n=== TABLE {t_idx} (rows: {len(table.rows)}, cols: {len(table.columns)}) ===")
    for r_idx, row in enumerate(table.rows[:15]):
        row_text = [cell.text.strip().replace('\n', ' ') for cell in row.cells]
        print(f"  Row {r_idx}: {' | '.join(row_text[:5])}")
    if len(table.rows) > 15:
        print(f"  ... and {len(table.rows) - 15} more rows")
