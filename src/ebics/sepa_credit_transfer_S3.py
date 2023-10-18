import os
import json
import xml.etree.ElementTree as ET
import fintech
import requests
import boto3
fintech.register()

from fintech.sepa import Account, SEPACreditTransfer, SEPATransaction
from fintech.ebics import EbicsKeyRing, EbicsBank, EbicsUser, EbicsClient, BusinessTransactionFormat

s3_client = boto3.client('s3')

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
    """
    EBICS protocol version H003 requires generation of the OrderID.
    The OrderID must be a string between 'A000' and 'ZZZZ' and
    unique for each partner id.
    """
    order_ids_s3_bucket = 'ebics-test-bucket'
    order_ids_s3_key = 'order/order_ids.json'

    def _next_order_id(self, partnerid):
        # Initialize AWS S3 client
        s3 = boto3.client('s3')

        try:
            # Try to fetch 'order_ids.json' from S3
            order_ids = json.loads(s3.get_object(Bucket=self.order_ids_s3_bucket, Key=self.order_ids_s3_key)['Body'].read().decode('utf-8'))
        except s3.exceptions.NoSuchKey:
            # If the file doesn't exist on S3, create it
            order_ids = {}

        order_id = order_ids.setdefault(partnerid, "A000")
        diff = (b36decode(order_id) - 466559) % 1213056
        order_ids[partnerid] = b36encode(466560 + diff)

        # Save 'order_ids.json' back to S3
        s3.put_object(Bucket=self.order_ids_s3_bucket, Key=self.order_ids_s3_key, Body=json.dumps(order_ids, indent=4))

        return order_id

class MyKeyRing(EbicsKeyRing):
    def _write(self, keydict):
        uploadByteStream = bytes(json.dumps(keydict).encode('UTF-8'))
        print(uploadByteStream)
        s3_client.put_object(Bucket = 'ebics-test-bucket', Key = 'keys/mykeys5', Body = uploadByteStream)

s3_bucket = 'ebics-test-bucket'
passphrase = 'mysecret'
s3_key = 'keys/mykeys5'

keydict = {}
# load keys from s3
try:
    res = s3_client.get_object(Bucket=s3_bucket, Key=s3_key)
    keys = res['Body']
    keydict = json.loads(keys.read())
    print(json.dumps(keydict))
    print(keydict)
    # print(json.dumps(keydict))
except s3_client.exceptions.NoSuchKey as e:
    print(f"directory {s3_key} does not exist in S3.")
except Exception as e:
    print(f"different error: {str(e)}")
    
keyring = MyKeyRing(keydict, 'mysecret')
bank = EbicsBank(keyring=keyring, hostid='EBIXQUAL', url='https://server-ebics.webank.fr:28103/WbkPortalFileTransfert/EbicsProtocol')
user = EbicsUser(keyring=keyring, partnerid='AMAGUMOTEST243', userid='AMAGUMOTEST243', transport_only = True)

client = EbicsClient(bank, user, version = 'H003')

# Create the debtor account from an IBAN
debtor = Account(('FR7600002000105555555555521','BNPAFRPPXXX'), 'HAOAO')
# Create the creditor account from a tuple (IBAN, BIC)
creditor = Account('FR7600002000106666666666652', 'Long')
creditor2 = Account('FR7617515900000497026130714', 'Hung')
# Create a SEPACreditTransfer instance
sct = SEPACreditTransfer(debtor, scheme = 'pain.001.001.03')
# sct = SEPATransaction(debtor, type = 'HIGH', cat_purpose = 'SALA')
# Add the transaction
purpose = ('code1','landing pep')
trans = sct.add_transaction(creditor, 10.00, 'tien dien', due_date = '2023-10-15', eref  = 'FR99') 
trans = sct.add_transaction(creditor2, 10.00, 'tien nha', due_date = '2023-10-15')
# Render the SEPA document
data = sct.render()
uploadId = client.FUL(filetype = 'xml', data = sct.render(), TEST = 'True')



# btf = BusinessTransactionFormat(
#     service='SCT',
#     msg_name='pain.001',
#     variant = '001',
#     version = '03',
#     scope = 'FR',
#     format = 'XML'
# )
# btd = BusinessTransactionFormat(
#     service='PSR',
#     msg_name='pain.002'
# )
# datas = client.BTU(btf, data)
# datas = client.BTD(btd)

# response = requests.post('https://www.bankrechner.org/ebics/EbicsServlet', sct.render())

# uploadId = client.XE2(sct.render())
# response = client.BTU(btf)
# camtZ01 = client.Z01()
# print(camtZ01)
# datas = client.Z01()
# print(datas)
root = ET.fromstring(data)
tree = ET.ElementTree(root)
tree.write('./letter/sct.xml', encoding='utf-8', xml_declaration=True)
# count = fintech.iban.get_bic('FR7600002000106666666666652')
# print(count)
# print(uploadId)