"""Rebuild the synthetic demo files; requires requirements-dev.txt."""
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import reportlab

FONT_DIR = Path(reportlab.__file__).parent / "fonts"
pdfmetrics.registerFont(TTFont("DemoSans", str(FONT_DIR / "Vera.ttf")))
pdfmetrics.registerFont(TTFont("DemoSans-Bold", str(FONT_DIR / "VeraBd.ttf")))

ROOT = Path(__file__).resolve().parents[1]
HEADERS = ["Item", "Description", "Qty", "Unit price", "Amount"]
ROWS = [
    ["001", "Wi-Fi access point", "2", "79.50", "159.00"],
    ["002", "8-port network switch", "1", "48.00", "48.00"],
    ["003", "Cat6 cable - 10 m", "6", "8.25", "49.50"],
    ["004", "Wall mount kit", "3", "12.00", "36.00"],
    ["005", "USB-C adapter", "4", "19.90", "79.60"],
    ["006", "Cable labels\nPack of 100", "2", "5.50", "11.00"],
    ["007", "Patch panel", "1", "62.00", "62.00"],
    ["008", "Installation service", "2", "35.00", "70.00"],
]


def make_pdf(path, pages, headers=None):
    path.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(path), pagesize=(612, 792))
    c.setTitle("TableBridge synthetic quotation")
    c.setAuthor("TableBridge demo")
    for index, rows in enumerate(pages, 1):
        c.setFillColor(colors.HexColor("#163B40"));c.rect(0, 684, 612, 108, fill=1, stroke=0)
        c.setFillColor(colors.white);c.setFont("DemoSans-Bold", 24);c.drawString(42, 739, "NORTHLINE / QUOTATION")
        c.setFont("DemoSans", 10);c.drawString(42, 715, "SYNTHETIC SAMPLE  |  No real client or transaction")
        c.setFillColor(colors.HexColor("#163B40"));c.setFont("DemoSans-Bold", 11)
        c.drawString(42, 653, "Reference: DEMO-001");c.drawRightString(570, 653, f"PAGE {index} / {len(pages)}")
        c.setFont("DemoSans", 10);c.drawString(42, 631, "Currency: USD    /    TableBridge fixed-layout example")
        table = Table([headers or HEADERS] + rows, colWidths=[50, 220, 50, 95, 95], rowHeights=[32] + [44] * len(rows))
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E6EFE8")),
            ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#163B40")),
            ("FONTNAME", (0, 0), (-1, -1), "DemoSans"),
            ("FONTNAME", (0, 0), (-1, 0), "DemoSans-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("GRID", (0, 0), (-1, -1), .6, colors.HexColor("#ADBFB4")),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 10),
            ("ALIGN", (2, 1), (-1, -1), "RIGHT"),
            ("RIGHTPADDING", (2, 1), (-1, -1), 10),
        ]))
        _, height = table.wrap(510, 500);table.drawOn(c, 42, 596 - height)
        c.setFont("DemoSans", 9);c.setFillColor(colors.HexColor("#718779"))
        c.drawString(42, 96, "All names, quantities and prices are fictional demonstration data.")
        c.line(42, 78, 570, 78);c.drawString(42, 59, "TableBridge / PDF to Excel demo")
        c.showPage()
    c.save()


if __name__ == "__main__":
    make_pdf(ROOT / "examples/demo-quotation.pdf", [ROWS[:4], ROWS[4:]])
    altered = [row[:] for row in ROWS[:2]];altered[0][-1] = "160.00"
    make_pdf(ROOT / "examples/demo-amount-warning.pdf", [altered])
    make_pdf(ROOT / "examples/demo-wrong-layout.pdf", [ROWS[:2]], ["Code", "Product", "Count", "Price", "Total"])
    print("Created 3 synthetic demo PDFs.")
