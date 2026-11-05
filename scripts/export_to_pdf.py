import os
import sys
import win32com.client

def export_docx_to_pdf(docx_path, pdf_path):
    abs_docx = os.path.abspath(docx_path)
    abs_pdf = os.path.abspath(pdf_path)
    print(f"Opening Word to convert {abs_docx} -> {abs_pdf}...")
    
    word = win32com.client.Dispatch("Word.Application")
    word.Visible = False
    word.DisplayAlerts = 0 # wdAlertsNone
    
    try:
        doc = word.Documents.Open(abs_docx)
        print("Document opened. Updating fields and Table of Contents...")
        
        # Update Table of Contents and all fields
        try:
            for toc in doc.TablesOfContents:
                toc.Update()
        except Exception as e:
            print(f"Note on TOC update: {e}")
            
        try:
            for f in doc.Fields:
                f.Update()
        except Exception as e:
            print(f"Note on Fields update: {e}")
            
        # Export as PDF (wdFormatPDF = 17)
        # wdExportFormatPDF = 17
        print("Exporting as PDF...")
        doc.ExportAsFixedFormat(
            OutputFileName=abs_pdf,
            ExportFormat=17, # wdExportFormatPDF
            OpenAfterExport=False,
            OptimizeFor=0, # wdExportOptimizeForPrint
            CreateBookmarks=1, # wdExportCreateHeadingBookmarks
            DocStructureTags=True
        )
        print(f"Successfully exported PDF to: {abs_pdf}")
        
        # Save back the docx with updated fields/page numbers
        doc.Save()
        doc.Close()
    finally:
        word.Quit()

if __name__ == "__main__":
    docx_file = "C:\\major project\\mp_final_completed.docx"
    pdf_file = "C:\\major project\\mp_final_completed.pdf"
    export_docx_to_pdf(docx_file, pdf_file)
    # Also sync mp.docx and mp.pdf
    export_docx_to_pdf("C:\\major project\\mp.docx", "C:\\major project\\mp.pdf")
