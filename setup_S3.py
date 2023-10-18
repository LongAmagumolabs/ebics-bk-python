import os
import json
import fintech
import time
import boto3
fintech.register()
from fintech.ebics import EbicsKeyRing, EbicsBank, EbicsUser, EbicsClient

s3_client = boto3.client('s3')
s3_bucket = 'ebics-test-bucket'
passphrase = 'mysecret'
s3_key = 'keys/mykeys'

def b36encode(number):
    chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    base36 = ""
    while number:
        number, i = divmod(number, 36)
        base36 = chars[i] + base36
    return base36 or "0"


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
        s3_client.put_object(Bucket = s3_bucket, Key = s3_key, Body = uploadByteStream)

keydict = {}
# load keys from s3
try:
    res = s3_client.get_object(Bucket=s3_bucket, Key=s3_key)
    keys = res['Body']
    keydict = json.loads(keys.read())
    # print(json.dumps(keydict))
except s3_client.exceptions.NoSuchKey as e:
    print(f"directory {s3_key} does not exist in S3.")
except Exception as e:
    print(f"different error: {str(e)}")


keyring = MyKeyRing(keydict, 'mysecret')
bank = EbicsBank(
    keyring=keyring,
    hostid="EBIXQUAL",
    url="https://server-ebics.webank.fr:28103/WbkPortalFileTransfert/EbicsProtocol",
)
# print(bank)
user = EbicsUser(
    keyring=keyring,
    partnerid="AMAGUMOTEST243",
    userid="AMAGUMOTEST243",
    transport_only=True,
)

# # Create new keys for this user
# print(keyring)
user.create_keys(keyversion='A005', bitlength=2048)
# print(user)

# Create self-signed certificates
# Only if the initialization is based on certificates!
user.create_certificates(
    commonName='longtran',
    organizationName='Amaugumolabs',
    countryName='FR',
)

client = EbicsClient(bank, user, version="H003")

print(client.INI())
print(client.HIA())

public_bank_keys = client.HPB()
print(public_bank_keys)

print(bank.activate_keys())