from markdown2 import markdown
from pathlib import Path

report_sections = []

def generate_report_section(title, content):
    section = f"## {title}\n\n{content}\n"
    report_sections.append(section)

def finalize_report(output_format="html", output_path=None):
    full_report = "\n".join(report_sections)

    if output_format == "html":
        html = markdown(full_report)

        if not output_path:
            output_path = "audit_report.html"
        Path(output_path).write_text(html)

    elif output_format == "md":
        if not output_path:
            output_path = "audit_report.md"
        Path(output_path).write_text(full_report)

    else:
        raise ValueError("Unsupported output format. Use 'html' or 'md'.")
