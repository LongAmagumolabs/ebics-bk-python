import fintech
fintech.register()
from fintech.sepa import Account, SEPACreditTransfer

# Create the debtor account from an IBAN
debtor = Account('DE89370400440532013000', 'Max Mustermann')
# Create the creditor account from a tuple (IBAN, BIC)
creditor = Account(('AT611904300234573201', 'BKAUATWW'), 'Maria Musterfrau')
# Create a SEPACreditTransfer instance
sct = SEPACreditTransfer(debtor)
# Add the transaction
tx = sct.add_transaction(creditor, 10.00, 'Purpose')
# Render the SEPA document
print(sct.render())