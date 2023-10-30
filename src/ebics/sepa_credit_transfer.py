import os
import json
import xml.etree.ElementTree as ET
import fintech
import requests
fintech.register()
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

# keyring = EbicsKeyRing(keys='./keys/mykeyspostfinance', passphrase='mysecret')
# bank = EbicsBank(keyring=keyring, hostid='PFEBICS', url='https://isotest.postfinance.ch/ebicsweb/ebicsweb')
# user = EbicsUser(keyring=keyring, partnerid='PFC00532', userid='PFC00532')

client = EbicsClient(bank, user, version = 'H003')

# Create the debtor account from an IBAN // con nợ
debtor = Account(('FR7600002000105555555555521','BNPAFRPPXXX'), 'HAOAO')
# Create the creditor account from a tuple (IBAN, BIC) // chủ nợ
creditor = Account('FR7600002000106666666666652', 'Long')
# creditor2 = Account('FR7617515900000497026130714', 'Hung')
# Create a SEPACreditTransfer instance
sct = SEPACreditTransfer(debtor, scheme = 'pain.001.001.03')
# sct = SEPATransaction(debtor, type = 'HIGH', cat_purpose = 'SALA')
# Add the transaction

trans = sct.add_transaction(creditor, 10.00, 'tien dien') 
# Render the SEPA document
data = sct.render()
uploadId = client.FUL(filetype = 'XML', data = data)
print(uploadId)

# with open('./letter/C001.xml') as file:
#     data2 = file.read()
#     print(data2)
# uploadId = client.XE2(data2)
# print(uploadId)
root = ET.fromstring(data)
tree = ET.ElementTree(root)
tree.write('./letter/sct_long_test.xml', encoding='utf-8', xml_declaration=True)
