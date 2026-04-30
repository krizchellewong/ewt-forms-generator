import csv
import io
import json
import calendar
import os
import re
from datetime import date
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas

TEMPLATE_PDF = "input/bir_form.pdf"
CLEANED_FILE = "output/cleaned_data.csv"
PAYER_FILE = "input/payer_info.csv"
COORDINATES_FILE = "input/coordinates.json"

def clean_digits(value):
    return "".join(ch for ch in str(value) if ch.isdigit())

def safe_filename(value):
    value = str(value).strip()
    value = re.sub(r'[\\/*?:"<>|]', "", value)
    value = re.sub(r"\s+", "_", value)
    return value[:80]

def draw_digits(c, value, positions, y, font_name="Helvetica", font_size=8):
    c.setFont(font_name, font_size)
    digits = clean_digits(value)

    for digit, x in zip(digits, positions):
        c.drawString(x, y, digit)

def get_quarter_dates(month_columns):
    first_month_name, first_year = month_columns[0].split()
    last_month_name, last_year = month_columns[-1].split()

    first_month = list(calendar.month_name).index(first_month_name.title())
    last_month = list(calendar.month_name).index(last_month_name.title())

    first_year = int(first_year)
    last_year = int(last_year)

    from_date = date(first_year, first_month, 1)

    last_day = calendar.monthrange(last_year, last_month)[1]
    to_date = date(last_year, last_month, last_day)

    return from_date.strftime("%m%d%Y"), to_date.strftime("%m%d%Y")

def get_quarter_number(month_columns):
    first_month_name, _ = month_columns[0].split()
    first_month = list(calendar.month_name).index(first_month_name.title())
    return ((first_month - 1) // 3) + 1

def get_number(record, key):
    return float(record.get(key, 0) or 0)

with open(COORDINATES_FILE, "r", encoding="utf-8") as f:
    coords = json.load(f)

def run():
    font_name = coords["font"]["name"]
    font_size = coords["font"]["size"]

    with open(PAYER_FILE, "r", encoding="utf-8-sig") as f:
        payer_reader = csv.DictReader(f)
        payer = next(payer_reader)

    with open(CLEANED_FILE, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        records = list(reader)

    if not records:
        raise ValueError("No records found in cleaned_data.csv")

    month_columns = [
        col for col in records[0].keys()
        if col not in ["COMPANY_NAME", "TIN", "ADDRESS", "ZIP", "ATC", "TOTAL", "TAX_WITHHELD"]
    ]

    quarter_number = get_quarter_number(month_columns)
    output_folder = f"output/ewt_forms_Q{quarter_number}"
    os.makedirs(output_folder, exist_ok=True)

    from_date, to_date = get_quarter_dates(month_columns)

    payer_name = payer.get("NAME", "")
    payer_tin = payer.get("TIN", "")
    payer_address = payer.get("ADDRESS", "")
    payer_zip = payer.get("ZIP", "")

    for record in records:
        template = PdfReader(TEMPLATE_PDF)
        page = template.pages[0]

        page_width = float(page.mediabox.width)
        page_height = float(page.mediabox.height)

        packet = io.BytesIO()
        c = canvas.Canvas(packet, pagesize=(page_width, page_height))
        c.setFont(font_name, font_size)

        company = record["COMPANY_NAME"]
        tin = record["TIN"]
        address = record.get("ADDRESS", "")
        zip_code = record.get("ZIP", "")
        atc = record.get("ATC", "")

        month_1 = get_number(record, month_columns[0])
        month_2 = get_number(record, month_columns[1])
        month_3 = get_number(record, month_columns[2])
        total = get_number(record, "TOTAL")
        tax = get_number(record, "TAX_WITHHELD")

        # dates
        draw_digits(c, from_date, coords["date"]["from_positions"], coords["date"]["y"], font_name, font_size)
        draw_digits(c, to_date, coords["date"]["to_positions"], coords["date"]["y"], font_name, font_size)

        # payee / company
        c.drawString(*coords["payee"]["name_xy"], company)
        c.drawString(*coords["payee"]["address_xy"], address)

        draw_digits(c, tin, coords["payee"]["tin_positions"], coords["payee"]["tin_y"], font_name, font_size)
        draw_digits(c, zip_code, coords["payee"]["zip_positions"], coords["payee"]["zip_y"], font_name, font_size)

        # payer
        c.drawString(*coords["payer"]["name_xy"], payer_name)
        c.drawString(*coords["payer"]["address_xy"], payer_address)

        draw_digits(c, payer_tin, coords["payer"]["tin_positions"], coords["payer"]["tin_y"], font_name, font_size)
        draw_digits(c, payer_zip, coords["payer"]["zip_positions"], coords["payer"]["zip_y"], font_name, font_size)

        # ATC
        c.drawString(coords["ATC"]["x"], coords["ATC"]["y"], atc)

        # amounts
        amounts = coords["amounts"]

        c.drawString(amounts["month_1_x"], amounts["y"], f"{month_1:,.2f}")
        c.drawString(amounts["month_2_x"], amounts["y"], f"{month_2:,.2f}")
        c.drawString(amounts["month_3_x"], amounts["y"], f"{month_3:,.2f}")
        c.drawString(amounts["total_x"], amounts["y"], f"{total:,.2f}")
        c.drawString(amounts["tax_x"], amounts["y"], f"{tax:,.2f}")

        c.save()
        packet.seek(0)

        overlay_pdf = PdfReader(packet)

        writer = PdfWriter()
        page.merge_page(overlay_pdf.pages[0])
        writer.add_page(page)

        filename = f"{safe_filename(company)}_{clean_digits(tin)}.pdf"
        output_path = os.path.join(output_folder, filename)

        with open(output_path, "wb") as f:
            writer.write(f)

    print(f"Created {len(records)} PDFs in {output_folder}")

if __name__ == "__main__":
    run()