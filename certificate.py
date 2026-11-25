from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib import colors
from pathlib import Path
import os

def make_certificate(path, full_name, school, grade, subject,
                     fan_correct, iq_correct, date_text):
    page = landscape(A4)
    c = canvas.Canvas(str(path), pagesize=page)
    w, h = page

    # Soddalashtirilgan, chop etishga mos A4 sertifikat.
    c.setFillColor(colors.HexColor("#10233F"))
    c.rect(0, h-82, w, 82, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 23)
    c.drawCentredString(w/2, h-48, "TEST NATIJALARI SERTIFIKATI")
    c.setFont("Helvetica", 10)
    c.drawCentredString(w/2, h-66, "O'QUVCHINING BILIM DARAJASI")

    c.setFillColor(colors.HexColor("#172B4D"))
    c.setFont("Helvetica-Bold", 17)
    c.drawCentredString(w/2, h-125, full_name)
    c.setFont("Helvetica", 10)
    c.setFillColor(colors.HexColor("#526174"))
    c.drawCentredString(w/2, h-145, f"{school}  |  {grade}-sinf  |  {date_text}")
    c.drawCentredString(w/2, h-162, f"Tanlangan fan: {subject}")

    # Markazdagi ajratuvchi chiziq
    mid = w / 2
    c.setStrokeColor(colors.HexColor("#AAB6C5"))
    c.setLineWidth(1.6)
    c.line(mid, 90, mid, h-190)

    left_x = 55
    right_x = mid + 35
    top_y = h - 225

    c.setFillColor(colors.HexColor("#176B87"))
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(w*0.25, top_y, "FAN TESTI NATIJASI")
    c.setFillColor(colors.HexColor("#16805D"))
    c.setFont("Helvetica-Bold", 29)
    c.drawCentredString(w*0.25, top_y-58, f"{fan_correct}/18")
    c.setFillColor(colors.HexColor("#26364A"))
    c.setFont("Helvetica", 12)
    c.drawString(left_x, top_y-100, f"To'g'ri javoblar: {fan_correct}")
    c.drawString(left_x, top_y-123, f"Noto'g'ri javoblar: {18-fan_correct}")
    c.drawString(left_x, top_y-146, f"Natija: {round(fan_correct/18*100)}%")

    c.setFillColor(colors.HexColor("#176B87"))
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(w*0.75, top_y, "IQ TESTI NATIJASI")
    c.setFillColor(colors.HexColor("#16805D"))
    c.setFont("Helvetica-Bold", 29)
    c.drawCentredString(w*0.75, top_y-58, f"{iq_correct}/7")
    c.setFillColor(colors.HexColor("#26364A"))
    c.setFont("Helvetica", 12)
    c.drawString(right_x, top_y-100, f"To'g'ri javoblar: {iq_correct}")
    c.drawString(right_x, top_y-123, f"Noto'g'ri javoblar: {7-iq_correct}")
    c.drawString(right_x, top_y-146, f"Natija: {round(iq_correct/7*100)}%")

    c.setStrokeColor(colors.HexColor("#D6DEE8"))
    c.line(45, 65, w-45, 65)
    c.setFillColor(colors.HexColor("#66758A"))
    c.setFont("Helvetica", 9)
    c.drawCentredString(w/2, 45, "Ushbu sertifikat Telegram test botida avtomatik shakllantirildi.")
    c.save()
