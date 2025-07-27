from markdown2 import markdown
from pathlib import Path

sections = []

def add_section(title, content):
    sections.append(f"## {title}\n\n{content}\n")

def export_report(format="html", output_path="audit_report"):
    full = "\n".join(sections)
    if format == "html":
        html = markdown(full)
        Path(f"{output_path}.html").write_text(html)
    else:
        Path(f"{output_path}.md").write_text(full)
