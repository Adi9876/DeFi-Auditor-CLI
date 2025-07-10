from markdown2 import markdown
from pathlib import Path

report_sections = []

def generate_report_section(title, content):
    section = f"## {title}\n\n{content}\n"
    report_sections.append(section)

def finalize_report(output_format="html"):
    full_report = "\n".join(report_sections)
    if output_format == "html":
        html = markdown(full_report)
        Path("audit_report.html").write_text(html)
    else:
        Path("audit_report.md").write_text(full_report)
