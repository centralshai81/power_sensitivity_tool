from __future__ import annotations

from pathlib import Path


def export_report_to_pdf(text: str, output_path: str | Path) -> bool:
    """
    将文本导出为 PDF。
    优先尝试 reportlab；若不可用，返回 False。
    """
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
    except Exception:
        return False

    p = Path(output_path)
    p.parent.mkdir(parents=True, exist_ok=True)

    c = canvas.Canvas(str(p), pagesize=A4)
    width, height = A4
    x = 40
    y = height - 40
    line_height = 16

    # 使用内置字体，中文可能无法完美显示；主要作为工程接口预留
    c.setFont("Helvetica", 10)

    for raw in text.splitlines():
        line = raw[:110]
        c.drawString(x, y, line)
        y -= line_height
        if y < 40:
            c.showPage()
            c.setFont("Helvetica", 10)
            y = height - 40

    c.save()
    return True
