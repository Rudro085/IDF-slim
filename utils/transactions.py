import json
from utils.enums import *

class Transaction:
    def __init__(self,date:str = '',transaction_code:str = '',details:str = '',ref:str = '',
                 cheque:str = '',debit:str = '',credit:str = '',balance:str = ''
                 ):
        self.date = date
        self.transaction_code = transaction_code
        self.details = details
        self.ref = ref
        self.cheque = cheque
        self.debit = debit
        self.credit = credit
        self.balance = balance

        self.result = dict(type1 = Cat_L1.undefined,type2 = Cat_L2.undefined, type3 = Cat_L3.undefined)

    def to_json(self):
        """ Used for dumping transcaction data as a json string """

        dictionary = {
            "date":self.date,
            "transaction_code":self.transaction_code,
            "details":self.details,
            "ref":self.ref,
            "cheque":self.cheque,
            "debit":self.debit,
            "credit":self.credit,
            "balance":self.credit
        }
        return json.dumps(dictionary)
    
    def concatinate(self,other):
        # self.date = self.date 
        # self.transaction_code = self.transaction_code
        self.details = self.details + other.details
        # self.ref = self.ref + other.ref
        # self.cheque = '' # self.cheque + other.cheque
        # self.debit = '' # self.debit + other.debit
        # self.credit = '' # self.credit + other.credit
        # self.balance = '' # self.balance + other.balance
