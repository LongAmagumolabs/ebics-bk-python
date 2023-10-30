import os
import io
import json
import xml.etree.ElementTree as ET
import fintech
import requests
fintech.register()
from pypdf import PdfReader
from jinja2 import Environment, FileSystemLoader
from fintech.sepa import Account, SEPACreditTransfer, SEPATransaction
from fintech.ebics import EbicsKeyRing, EbicsBank, EbicsUser, EbicsClient, BusinessTransactionFormat

def b36encode(number):
    chars = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    base36 = ''
    while number:
        number, i = divmod(number, 36)
        base36 = chars[i] + base36
    return base36 or '0'

def b36decode(number):
    return int(number, 36)


class EbicsBank(EbicsBank):

    order_ids_path = './order/order_ids.json'

    def _next_order_id(self, partnerid):
        """
        Generate an order id uniquely for each partner id
        Must be a string between 'A000' and 'ZZZZ'
        """
        if not os.path.exists(self.order_ids_path):
            with open(self.order_ids_path, 'w') as fh:
                fh.write('{}')

        with open(self.order_ids_path, 'r+') as fh:
            order_ids = json.load(fh)
            order_id = order_ids.setdefault(partnerid, 'A000')
            diff = (b36decode(order_id) - 466559) % 1213056
            order_ids[partnerid] = b36encode(466560 + diff)
            fh.truncate(0)
            fh.seek(0)
            json.dump(order_ids, fh, indent=4)

        return order_id
    
keyring = EbicsKeyRing(keys='./keys/mykeys_long', passphrase='mysecret')
bank = EbicsBank(keyring=keyring, hostid='EBIXQUAL', url='https://server-ebics.webank.fr:28103/WbkPortalFileTransfert/EbicsProtocol')
user = EbicsUser(keyring=keyring, partnerid='LONG', userid='LONG', transport_only = True)

# user.create_ini_letter(bankname='AmagumoBanks', path='./letter/ini_letter21102.pdf')
# cert = user.export_certificates()
# cert_str = json.dumps(cert, indent=4) 
# with open(f'test2', 'w') as fh:
#     fh.write(cert_str)
# print(name)
client = EbicsClient(bank, user, version = 'H003')

pdf = user.create_ini_letter(bankname='AmagumoBanks')
TplEnv = Environment(loader=FileSystemLoader('letter/'))
Tpl_letter = TplEnv.get_template('letter.txt')
print(pdf)
pdf_stream = io.BytesIO(pdf)
print(pdf_stream)
reader = PdfReader(pdf_stream)
number_of_pages = len(reader.pages)
print(number_of_pages)