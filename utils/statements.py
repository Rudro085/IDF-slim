from utils.transactions import Transaction
import csv

class Statement:
    def __init__(self,pdf_name:str,
                 bank_name:str,acc_no:str='-',
                 acc_type:str = '-',
                 opening_balance:str = '-', 
                 closing_balance:str = '-',
                 pdf_location = 'uploaded_pdf',
                 page_count = None
                 ):
        
        # Bank meta data
        self.bank_name = bank_name
        self.acc_no = acc_no
        self.acc_type = acc_type
        self.opening_balance = opening_balance 
        self.closing_balance = closing_balance
        
        # PDF data
        self.pdf_name = pdf_name
        self.pdf_location = pdf_location
        self.page_count = page_count

        # User data
        self.owner = None
        
        # list of Transaction object
        self.data = []  
    def add(self,transaction:Transaction):
        self.data.append(transaction)


    def show(self):
        """ Displays extracted data """

        tab ="\t"
        if len(self.data) == 0:
            print("No transaction found")
        else:
            

            print("date"+tab+ "transaction_code"+tab+ "details"+tab+ "ref"+tab+ "cheque"+tab+ "debit"+tab+ "credit"+tab+ "balance")
            for data in self.data:
                date= data.date
                transaction_code= data.transaction_code 
                details = data.details 
                ref = data.ref  
                cheque = data.cheque  
                debit = data.debit  
                credit = data.credit  
                balance = data.balance  
                print(str(date)+tab+ str(transaction_code)+tab+ str(details) + tab+tab+ str(ref)+tab+ str(cheque)
                      +tab+ str(debit)+tab+ str(credit)+tab+ str(balance))

                #print(details)
            print("Acc. no : " + self.acc_no)
            print("Acc. type : " + self.acc_type)
            print("Opening Balance : " + str(self.opening_balance))
            print("Closing Balance : " + str(self.closing_balance))


    def save_to_csv(self, file_path: str):
        """Saves the transaction data to a CSV file."""
        
        headers = [
            "Date", "Transaction_code", "Details", "Ref",
            "Cheque", "Debit", "Credit", "Balance", "Cat1", "Cat2", "Cat3"
        ]
        with open(file_path, mode='w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(headers)
            for data in self.data:
                writer.writerow([
                    data.date,
                    data.transaction_code,
                    data.details,
                    data.ref,
                    data.cheque,
                    float('0' if data.debit == '-' or data.debit == ''  else data.debit),
                    float('0' if data.credit  == '-' or data.credit  == '' else data.credit),
                    float('0' if data.balance == '-' or data.balance == '' else data.balance),
                    data.result['type1'],
                    data.result['type2'],
                    data.result['type3'],


                ])
    def validate(self):
        if self.acc_no == '-':
            return False
        elif self.acc_type == '-':
            return False
        elif self.opening_balance == '-':
            return False
        elif self.closing_balance == '-':
            return False
        elif len(self.data) == 0:
            return False
        else:
            return True



