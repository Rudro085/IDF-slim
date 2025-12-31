import fitz
from utils.transactions import Transaction 
from utils.statements import Statement

class Ebl_parser:
    def _date_format(self,date:str)->str:
        months = {
            'JAN': '01',
            'FEB': '02',
            'MAR': '03',
            'APR': '04',
            'MAY': '05',
            'JUN': '06',
            'JUL': '07',
            'AUG': '08',
            'SEP': '09',
            'OCT': '10',
            'NOV': '11',
            'DEC': '12'
        }
        if not len(date) == 9:
            return None
        day, month, year = date.split('-')
        year = '20'+ year
        new_date = f"{year}-{months[month]}-{day}"  
        return new_date

    def _fig_format(self,num_str:str)->str:
        for i in range(len(num_str)):
            if num_str[i]=='C':
                num_str = num_str[:i]
                break
        if num_str == '':
            return ''
        numeric_float = num_str.replace(',', '')
        return numeric_float 


    def parse(self,pdf_file_path,bank_name) -> Statement:
        if not bank_name == "EBL":
            return None
        statement = Statement(pdf_name=pdf_file_path,bank_name="EBL")
        doc = fitz.open(pdf_file_path)
        
        for page in doc:
            text = page.get_text()
            subtexts = []
            
            for i in range(len(text)):
                first_letter = 0
                if text[i] == '\n':
                    subtext = text[i-115:i]
                    subtexts.append(subtext)

            for subtext in subtexts:
                #print(subtext)
                transaction_flag = False
                transaction = Transaction()
                first_letter = 0
                for char in subtext:
                    if not char == ' ':
                        break
                    first_letter += 1
                #print(first_letter)
                # To get the acc. no. and acc. type
                if first_letter == 68: 
                    if subtext[first_letter:first_letter + 16] == "Account Number :":
                        statement.acc_no = subtext[first_letter + 16:].replace(' ', '')
                    elif subtext[first_letter:first_letter + 16] == "Product Name   :":
                        statement.acc_type = subtext[first_letter + 16:]
                # To get the transactions
                elif first_letter == 0: 
                    # with dates
                    if subtext[2] == '-' and subtext[6] == '-' and not subtext[4] == '-':
                        transaction_flag = True
                        transaction.date=self._date_format(subtext[:9])
                        transaction.details = subtext[9:].split("  ")[1]
                        #if not subtext[45:].split("  ")[0] == "":
                        transaction.ref = subtext[9+36:].split("  ")[0]

                        # debit dot at 72 
                        # credit dot at 92
                        # balance dot at 112
                        if subtext[72] == '.' and not subtext[92] == '.':
                            # debit
                            transaction.debit = self._fig_format(subtext[:75].split("  ")[-1].replace(' ', ''))

                        elif not subtext[72] == '.' and subtext[92] == '.':
                            # credit
                            transaction.credit = self._fig_format(subtext[:95].split("  ")[-1].replace(' ', ''))

                        if subtext[112] == '.':
                            #balance
                            transaction.balance = self._fig_format(subtext.split("  ")[-1].replace(' ', ''))

                elif first_letter == 12 and not subtext[112] == '.':
                    transaction.details =  subtext[9:].split("  ")[1]
                    #print(transaction.details)
                    statement.data[-1].concatinate(transaction)

                if transaction_flag:
                    statement.add(transaction)
        statement.opening_balance = statement.data[0].balance
        statement.closing_balance = statement.data[-1].balance
        return statement
                

                    
                        
    




