from __future__ import annotations

from pathlib import Path
from typing import Dict, Any

from reporting.report_generator import generate_markdown_report, generate_text_report
from reporting.docx_exporter import export_report_to_docx
from reporting.pdf_exporter import export_report_to_pdf


def export_full_report_bundle(
    output_dir: str | Path,
    cfg: Dict[str, Any],
    network_bundle: Dict[str, Any],
    result: Dict[str, Any],
) -> Dict[str, Any]:
    """
    一次性导出报告包：
    - TXT
    - Markdown
    - DOCX（若可用）
    - PDF（若可用）
    """
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    txt_path = out / "analysis_report.txt"
    md_path = out / "analysis_report.md"
    docx_path = out / "analysis_report.docx"
    pdf_path = out / "analysis_report.pdf"

    generate_text_report(txt_path, cfg, network_bundle, result)
    generate_markdown_report(md_path, cfg, network_bundle, result)

    md_text = md_path.read_text(encoding="utf-8")
    txt_text = txt_path.read_text(encoding="utf-8")

    docx_ok = export_report_to_docx(md_text, docx_path)
    pdf_ok = export_report_to_pdf(txt_text, pdf_path)

    return {
        "txt": str(txt_path),
        "md": str(md_path),
        "docx": str(docx_path) if docx_ok else None,
        "pdf": str(pdf_path) if pdf_ok else None,
    }
