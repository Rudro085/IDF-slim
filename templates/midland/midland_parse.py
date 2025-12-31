import tabula
import numpy as np
import pandas as pd
from thefuzz import fuzz
from utils.transactions import Transaction 
from utils.statements import Statement
import pdfplumber

# Read PDF file without treating the first row as a header

class Midland_parser:
    def date_format(self,date: str) -> str:
        
        if not len(date) == 8:
            return None
        day, month, year = date.split('/')
        year = '20' + year
        new_date = f"{year}-{month}-{day}"
        return new_date

    def fig_format(self,num_str: str) -> str:
        try:
            num_str = str(num_str)
        except:
            pass
        for i in range(len(num_str)):
            if num_str[i] == 'C':
                num_str = num_str[:i]
                break
        if num_str == '0.00':
            return ''
        numeric_float = num_str.replace(',', '')
        return numeric_float


    def parse(self, pdf_file_path,bank_name) -> Statement:
        if not bank_name == "Midland":
            return None
        # read table data
        statement = Statement(pdf_name=pdf_file_path,bank_name="Midland")
        tables = tabula.read_pdf(pdf_file_path, pages='all', pandas_options={'header': None})
        for page in tables:
            for i in range(len(page.index)):
                entry =list(page.iloc[i])  # Corrected indexing
                transaction = Transaction()
                if fuzz._ratio(entry[2], 'OPENING BALANCE') > 90:
                    continue
                elif pd.isna(entry[3]):
                    transaction.details = entry[2]
                    statement.data[-1].concatinate(transaction)
                else:
                    transaction.date = self.date_format(entry[1])
                    transaction.details = entry[2]
                    transaction.debit = self.fig_format(entry[3])
                    transaction.credit = self.fig_format(entry[4])
                    transaction.balance = self.fig_format(entry[5])
                    statement.add(transaction)
        statement.opening_balance = statement.data[0].balance
        statement.closing_balance = statement.data[-1].balance
        
        # read text data
        with pdfplumber.open(pdf_file_path) as doc:
            pages = doc.pages
            subtext = pages[0].extract_text()
            start = subtext.find('Account No. :')
            statement.acc_no = subtext[start+14:start + 14 + 15]
            statement.acc_type = "Current" if not subtext.find("CURRENT") == -1 else "Savings"
        return statement


