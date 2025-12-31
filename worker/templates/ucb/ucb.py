from templates.ucb.ucb_parse import Ucb_parser
from utils.statements import Statement
from utils.enums import *

class Ucb(Ucb_parser):
    def __init__(self):
        super().__init__()

    def process(self,st:Statement):
        for i in range(len(st.data)):
            details = st.data[i].transaction_code
            #DebitCredit
            if st.data[i].debit == '' and not st.data[i].credit == '':
                st.data[i].result['type1'] = Cat_L1.credit
            elif not st.data[i].debit == '' and  st.data[i].credit == '':
                st.data[i].result['type1'] = Cat_L1.debit
            else:
                st.data[i].result['type1'] = Cat_L1.undefined

            #CreditInterest_SourceTax
            if 'Credit Interest' in details:
                st.data[i].result['type2'] = Cat_L2.creditInterest
            elif details == 'Tax':
                st.data[i].result['type2'] = Cat_L2.sourceTax
            else:
                st.data[i].result['type2'] = Cat_L2.usual

            #CashChequeTransfer
            if 'Cash' in details:
                st.data[i].result['type3'] = Cat_L3.cash
            elif 'Cheque' in details:
                st.data[i].result['type3'] = Cat_L3.cheque
            elif 'TRANSFER' in details:
                st.data[i].result['type3'] = Cat_L3.transfer
            else:
                st.data[i].result['type3'] = Cat_L3.other

        return st


    def run(self,pdf_path,bank_name):
        st = self.parse(pdf_path,bank_name)
        st = self.process(st)
        return st
