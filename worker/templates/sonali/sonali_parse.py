import pdfplumber
from utils.transactions import Transaction 
from utils.statements import Statement
from thefuzz import fuzz

class Sonali_parser:
    def _date_format(self,date:str)->str:
        months = {
            'Jan': '01',
            'Feb': '02',
            'Mar': '03',
            'Apr': '04',
            'May': '05',
            'Jun': '06',
            'Jul': '07',
            'Aug': '08',
            'Sep': '09',
            'Oct': '10',
            'Nov': '11',
            'Dec': '12'
        }
        if not len(date) == 11:
            return None
        day, month, year = date.split('-')
        #year = '20'+ year
        new_date = f"{year}-{months[month]}-{day}"  
        return new_date

    def _fig_format(self,num_str:str)->str:
        if num_str == None:
            return 0.
        for i in range(len(num_str)):
            if num_str[i]=='C':
                num_str = num_str[:i]
                break
        if num_str == '':
            return ''
        numeric_float = num_str.replace(',', '')
        return numeric_float 
    
    def parse(self, pdf_file_path,bank_name) -> Statement:
        if not bank_name == "Sonali":
            return None
        statement = Statement(pdf_name=pdf_file_path,bank_name="Sonali")
        with pdfplumber.open(pdf_file_path) as PDF:
            # Extract tables
            pages = PDF.pages
            for page_index in range(len(pages)):
                table = pages[page_index].extract_table()
                for table_index in range(len(table)-1):
                    table_index += 1
                    entry = table[table_index]
                    #print(entry)
                    if len(entry) < 4:
                        pass
                    elif fuzz._ratio(entry[3],'Balance B/F') > 90  :
                        pass
                    elif fuzz._ratio(entry[3],'Opening Balance') > 90 :
                        statement.opening_balance = self._fig_format(entry[7])
                    elif entry[1] == None:
                        pass
                    else:
                        transaction = Transaction()
                        transaction.date = self._date_format(entry[1])
                        transaction.transaction_code = entry[3]
                        transaction.details = entry[3]
                        transaction.debit = self._fig_format(entry[4])
                        transaction.credit = self._fig_format(entry[5])
                        transaction.balance = self._fig_format(entry[7])
                        statement.add(transaction)
            # Extract texts
            page = PDF.pages[0]
            subtext = page.extract_text()
            start = subtext.find('Account Number :')
            statement.acc_no = subtext[start+17:start + 17 + 13]
            statement.acc_type = "Current" if not subtext.find("CA - Current Account") == -1 else "Savings"
            statement.closing_balance = statement.data[-1].balance
            

        return statement

