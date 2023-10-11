import os
import json
import fintech
import xml.etree.ElementTree as ET
fintech.register()
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
    
keyring = EbicsKeyRing(keys='./keys/mykeys', passphrase='mysecret')
bank = EbicsBank(keyring=keyring, hostid='BLBANK', url='https://www.bankrechner.org/ebics/EbicsServlet')
user = EbicsUser(keyring=keyring, partnerid='DEMO12870', userid='DEMO12870')

client = EbicsClient(bank, user, version='H005')

btf = BusinessTransactionFormat(
    service='SCT',
    msg_name='pain.001',
    variant = '001',
    version = '03',
    scope = 'FR',
    format = 'XML'
)
data = BTU(btf, data)
# btf = BusinessTransactionFormat(
#     service='EOP',
#     msg_name='pain.008',
#     format='XML',
# )

# data = client.BTD(btf, start='2023-09-29', end='2023-09-30')
# data = client.STA()
# data = client.FDL(filetype='camt.xxx.cfonb120.stm', start='2023-10-01', end='2023-10-03')
# data = client.download('A013')
# data = client.HEV()
# bank._next_order_id()
data = client.HTD()
root = ET.fromstring(data)
tree = ET.ElementTree(root)
tree.write('./letter/info.xml', encoding='utf-8', xml_declaration=True)
print(data)