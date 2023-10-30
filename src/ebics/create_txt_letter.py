import json
from pypdf import PdfReader
from jinja2 import Environment, FileSystemLoader
import datetime
import pytz
import textwrap
from fpdf import FPDF
from math import floor
versions = ['A005', 'X002', 'E002']
versionName_t1 = ['Signature', "Authentification", 'Chiffrement']
versionName_t2 = ['de signature', "d'authentification", 'de chiffrement']
check_bold = ['HostID:', 'PartnerID:', 'UserID:', 'Version:', 'Type:']

with open('test', 'r') as file:
    data = file.read()

certificates = json.loads(data)
A005 = ''
X002 = ''
E002 = ''

for cert_id, cert_list in certificates.items():
    for cert_data in cert_list:
        # crt = cert_data.replace("-----BEGIN CERTIFICATE-----", "").replace("-----END CERTIFICATE-----", "").strip()
        if cert_id == 'A005':
            A005 = cert_data
        elif cert_id == 'E002':
            E002 = cert_data
        else:
            X002 = cert_data


# Opening templates
TplEnv = Environment(loader=FileSystemLoader('letter/'))
Tpl_letter = TplEnv.get_template('letter.txt')
reader = PdfReader("./letter/ini_letter2110.pdf")
number_of_pages = len(reader.pages)
# print(number_of_pages)

a4_width_mm = 210
pt_to_mm = 0.26
fontsize_pt = 12
fontsize_mm = fontsize_pt * pt_to_mm # 3.5
margin_bottom_mm = 1
character_width_mm = 7 * pt_to_mm # 2.45
width_text = a4_width_mm / character_width_mm # 514.5

for page in range(number_of_pages):
    page_txt = reader.pages[page]
    text = page_txt.extract_text()
    # print(text)
    lines = text.split("\n")

    hash = []

    for line in lines:
        if "Hash (SHA-256)" in line:
            Date = datetime.datetime.now(tz=pytz.timezone('Europe/Paris')).strftime("%d/%m/%Y %H:%M")
            txt_letter = Tpl_letter.render(
                HostID = "BNPAFRPPXXX",
                PartnerID = "30004BNPP",
                UserID = "83SN7W",
                BankName = "BNP Paribas",
                Certificate = A005 if versions[page] == 'A005' else (X002 if versions[page] == 'X002' else E002),
                Version = versions[page],
                VersionName_t1 = versionName_t1[page],
                VersionName_t2 = versionName_t2[page],
                Date = Date,
                Digest1 = lines[lines.index(line)+1],
                Digest2 = lines[lines.index(line)+2])   
            
            pdf = FPDF(orientation='P', unit='mm', format='A4')
            pdf.set_auto_page_break(auto=True, margin=margin_bottom_mm)
            pdf.add_page()
            pdf.set_font(family='Courier', size=fontsize_pt, style = 'I')
            pdf.set_left_margin(20)
            splitted = txt_letter.split('\n')

            for line in splitted:
                # lines = textwrap.wrap(line, ceil(width_text))
                lines = textwrap.wrap(line, floor(width_text))
                pdf.set_font(family='Courier', size=fontsize_pt, style = 'I')
                if len(lines) == 0:
                    pdf.ln()  # If a blank line exists then create an empty line
                else:
                    for wrap in lines:
                        temp = 0
                        # for checkBold in check_bold:
                        #     if checkBold in wrap:
                        #         parts = wrap.split(':')
                        #         pdf.cell(pdf.get_string_width(checkBold), fontsize_mm, parts[0] + ': ', ln=0) 
                        #         pdf.set_font(family='Courier', size=fontsize_pt, style = 'BI')
                        #         pdf.cell(0, fontsize_mm, parts[1], ln=1)
                        #         pdf.ln()
                        #         temp = 1
                        #         break
                        if temp == 0:
                            pdf.cell(0, fontsize_mm, wrap, ln=1)
                            pdf.ln()  # Add empty line below each line

            pdf.output(f'letter/{versions[page]}.pdf', 'F')

            # Xuất PDF ra chuỗi
            # pdf_output = pdf.output(dest='S')
            # # Chuyển chuỗi thành bytes
            # pdf_bytes = pdf_output.encode('latin1')

            # with open(f'{versions[page]}.txt', 'w') as fh:
            #     fh.write(txt_letter)