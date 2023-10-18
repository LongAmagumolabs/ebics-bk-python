import json
import fintech
fintech.register()
from fintech.sepa import Account, SEPACreditTransfer

def lambda_handler(event, context):
    print(__name__)  
    print(etree.LXML_VERSION)  
    debtor = Account(('FR7600002000105555555555521','BNPAFRPPXXX'), 'BNP Parias')
    creditor = Account('FR7600002000106666666666652', 'Long amagumo')
    sct = SEPACreditTransfer(debtor)
    trans = sct.add_transaction(creditor, 10.00, 'Purpose')
    data = sct.render()
    
    return {
        'statusCode': 200,
        'body': data
    }
