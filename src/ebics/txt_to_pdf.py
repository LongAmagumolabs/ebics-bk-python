# from fpdf import FPDF

# with open('./letter/auth_letter.txt', 'r', encoding='utf-8') as text_file:
#     text_content = text_file.read()

# # Tách đoạn văn bản thành các dòng riêng lẻ
# lines = text_content.split('\n')

# pdf = FPDF()
# pdf.add_page()

# pdf.set_font("Arial", style='I', size=12)
# pdf.set_auto_page_break(auto=True, margin=5)

# pdf.set_text_color(0, 0, 0)
# pdf.set_draw_color(128, 128, 128)

# is_inside_certificate = False 

# for line in text_content.splitlines():
#     if "-----BEGIN CERTIFICATE-----" in line:
#         is_inside_certificate = True
#     elif "-----END CERTIFICATE-----" in line:
#         is_inside_certificate = False

#     if is_inside_certificate:
#         pdf.cell(190, 5, txt=line, border=0, align='J', ln=0)
#     else:
#         pdf.cell(190, 5, txt=line, border=0, align='L', ln=1)

# pdf.output("file2.pdf")

import textwrap
from fpdf import FPDF
from math import ceil, floor
file = open('A005.txt')
text = file.read()
file.close()

a4_width_mm = 210
pt_to_mm = 0.35
fontsize_pt = 10  # Giảm giá trị font size để làm cho các dòng nhỏ hơn
fontsize_mm = fontsize_pt * pt_to_mm
margin_bottom_mm = 2  # Giảm giá trị margin để làm cho các dòng gần nhau hơn
character_width_mm = 7 * pt_to_mm
width_text = a4_width_mm / character_width_mm

pdf = FPDF(orientation='P', unit='mm', format='A4')
pdf.set_auto_page_break(auto=True, margin=margin_bottom_mm)
pdf.add_page()
pdf.set_font(family='Courier', size=fontsize_pt, style = 'I')
# pdf.set_font(family='Times', size=fontsize_pt)
splitted = text.split('\n')

for line in splitted:
    # lines = textwrap.wrap(line, ceil(width_text))
    lines = textwrap.wrap(line, floor(width_text))

    if len(lines) == 0:
        pdf.ln()  # If a blank line exists then create an empty line
    for wrap in lines:
        pdf.cell(2, fontsize_mm, wrap, ln=1)
    pdf.ln()  # Add empty line below each line

pdf.output('file3.pdf', 'F')
