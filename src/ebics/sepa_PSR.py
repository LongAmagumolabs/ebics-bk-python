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

client = EbicsClient(bank, user, version = 'H003')

# xml = client.CRZ(start='2023-10-16', end='2023-10-17')
xml = client.Z01(start='2023-10-16', end='2023-10-17')
print(xml)