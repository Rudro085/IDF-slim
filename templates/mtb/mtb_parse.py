
#### MTB ####

import pdfplumber
import pandas as pd
import sqlite3
from thefuzz import fuzz
from utils.transactions import Transaction 
from utils.statements import Statement


class Mtb_parser:
    def _date_format(self,date:str)->str:
        try:
            if not len(date) == 8:
                return '-'
        except:
            return '-'
        day, month, year = date.split('/')
        year = '20'+ year
        new_date = f"{year}-{month}-{day}"
        return new_date

    def _remove_newlines(self,string:str)->str:
        return string.replace('\n', ' ')

    def _fig_format(self,num_str:str)->float:
        for i in range(len(num_str)):
            if num_str[i]=='C':
                num_str = num_str[:i]
                break
        if num_str == '':
            return ''
        numeric_float = num_str.replace(',', '')
        return numeric_float 

    def parse(self,pdf_file_path,bank_name ) -> Statement:
        if not bank_name == "MTB":
            return None
        statement = Statement(pdf_name=pdf_file_path,bank_name="MTB")
        with pdfplumber.open(pdf_file_path) as PDF:

            ### Read Tables ###
            pages = PDF.pages
            for page_index in range(len(pages)):
                table = pages[page_index].extract_table()
                for table_index in range(len(table)-1):
                    table_index += 1
                    entry = table[table_index]
                    transaction = Transaction()
                    if len(entry) < 4 or entry[1]==None:
                        continue
                    if entry[2]=="Opening Balance":
                        statement.opening_balance = self._fig_format(entry[6])
                        continue
                    #print(entry[1])
                    transaction.date = self._date_format(entry[1])
                    transaction.details = self._remove_newlines(entry[2])
                    transaction.ref = entry[3]
                    transaction.debit = self._fig_format(entry[4])
                    transaction.credit = self._fig_format(entry[5])
                    transaction.balance = self._fig_format(entry[6])
                    statement.add(transaction)
            statement.closing_balance = statement.data[-1].balance

            ### Read Texts ###
            text = pages[0].extract_text()
            subtexts = text.split('\n')
            for subtext in subtexts:
                if subtext[:12] == "ACCOUNT NO :":
                    statement.acc_no = subtext[12:].replace(' ', '')
                elif subtext[:14] == "ACCOUNT TYPE :":
                    statement.acc_type = subtext[14:]

        return statement
                    
