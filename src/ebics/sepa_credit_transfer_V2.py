import os
import json
import xml.etree.ElementTree as ET
import fintech
import requests
fintech.register()
from decimal import Decimal
from sepa_generator.core import Account, SEPACreditTransfer, Amount
from fintech.ebics import EbicsKeyRing, EbicsBank, EbicsUser, EbicsClient

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

client = EbicsClient(bank, user, version = 'H003')

debtor = Account(iban='FR7600002000105555555555521', bic='BNPAFRPPXXX', name='HAOAO',)

creditor = Account(iban='FR7600002000106666666666652', bic='', name='Long')

sepa_transfer = SEPACreditTransfer(debtor=debtor)

sepa_transfer.add_transaction(creditor=creditor, amount=Amount(Decimal('100.10')), purpose='credit transfer', eref='FR99', ext_purpose='OTHR', cref='SI0020170504058')


data = sepa_transfer.render_xml()
uploadId = client.FUL(filetype = 'xml', data = data, TEST = 'True')
print(uploadId)

root = ET.fromstring(data)
tree = ET.ElementTree(root)
tree.write('./letter/sct_long_v2.xml', encoding='utf-8', xml_declaration=True)