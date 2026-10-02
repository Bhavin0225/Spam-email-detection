from markdown_pdf import MarkdownPdf, Section
import sys

try:
    with open("analysis_results.md", "r", encoding="utf-8") as f:
        text = f.read()

    pdf = MarkdownPdf(toc_level=2)
    pdf.add_section(Section(text))
    pdf.save("analysis_results.pdf")
    print("PDF converted successfully.")
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
