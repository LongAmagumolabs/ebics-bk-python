import os
import json
import fintech
import time
import boto3
fintech.register()
from fintech.ebics import EbicsKeyRing, EbicsBank, EbicsUser, EbicsClient

s3_client = boto3.client('s3')


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
    


# tmp_dir = '/tmp'

# if os.path.exists(tmp_dir) and os.path.isdir(tmp_dir):
#     print(f"The /tmp directory exists and is a directory.")
# else:
#     print(f"The /tmp directory not exists and is a directory.")



start_time = time.time()
# keyring = EbicsKeyRing(keys='./keys/mykeys', passphrase='mysecret')
# bank = EbicsBank(keyring=keyring, hostid='BLBANK', url='https://www.bankrechner.org/ebics/EbicsServlet')
# user = EbicsUser(keyring=keyring, partnerid='DEMO12870', userid='DEMO12870')

keyring = EbicsKeyRing(keys='./keys/mykeys_long', passphrase='mysecret')
bank = EbicsBank(keyring=keyring, hostid='EBIXQUAL', url='https://server-ebics.webank.fr:28103/WbkPortalFileTransfert/EbicsProtocol')
user = EbicsUser(keyring=keyring, partnerid='LONGAMA', userid='LONGAMA', transport_only = True)


# keyring = EbicsKeyRing(keys='./keys/mykeyspostfinance', passphrase='mysecret')
# bank = EbicsBank(keyring=keyring, hostid='PFEBICS', url='https://isotest.postfinance.ch/ebicsweb/ebicsweb')
# user = EbicsUser(keyring=keyring, partnerid='PFC00532', userid='PFC00532')

# keyring = EbicsKeyRing(keys='./keys/mykeys', passphrase='mysecret')
# bank = EbicsBank(keyring=keyring, hostid='PFEBICS', url='https://localhost:8080/')
# user = EbicsUser(keyring=keyring, partnerid='PFC00532', userid='PFC00532')

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
# print(user)

end_time = time.time()
execution_time = end_time - start_time
print(f"Thời gian chạy: {execution_time} giây")
# print(user)
client = EbicsClient(bank, user, version="H003")

# print(client)
# Send the public electronic signature key to the bank.
print(client.INI())
# Send the public authentication and encryption keys to the bank.
print(client.HIA())

# Create an INI-letter which must be printed and sent to the bank.
# user.create_ini_letter(bankname='AmagumoBanks', path='./letter/ini_letter.pdf')

# After the account has been activated the public bank keys
# must be downloaded and checked for consistency.
# print(client.HTD())
public_bank_keys = client.HPB()
print(public_bank_keys)

# Finally the bank keys must be activated.
print(bank.activate_keys())

# # Retrieve bank account statements (camt.053 format)
# print(bank)
# print(client)


# ---------------------------------------------------
# Download camt.53 documents


# docs = client.C53('2023-09-18', '2023-09-21')
# # Print all received documents
# for name, xml in docs.items():
#     print(xml)
# Print the transaction id for this download process
# print(client.last_trans_id)
# # Confirm download
# client.confirm_download()



# keydict = {}
# load keys from s3
# try:
#     res = s3_client.get_object(Bucket=s3_bucket, Key=s3_key)
#     keys = res['Body']
#     keydict = json.loads(keys.read())
#     print(json.dumps(keydict))
#     print(keydict)
#     # print(json.dumps(keydict))
# except s3_client.exceptions.NoSuchKey as e:
#     print(f"directory {s3_key} does not exist in S3.")
# except Exception as e:
#     print(f"different error: {str(e)}")

# jsonToS3 = bytes(json.dumps(keydict).encode('UTF-8'))
# print('jsonToS3')
# print(jsonToS3)
# s3_client.put_object(Bucket = 'ebics-test-bucket', Key = 'keys/mykeys3', Body = jsonToS3)