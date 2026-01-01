import time
import redis
from rq import get_current_job
from datetime import datetime
from utils.dbcon import *
from utils.requests import Request
from utils.statements import Statement 
from utils.banks import AvailableBanks
import json
from utils.enums import *
from utils import category
import os


idf_db_conf = DatabaseConfig(
    host=os.getenv('HOST', '72.61.229.43'),
    database=os.getenv('DATABASE', 'nbr'),
    user=os.getenv('USER', 'nbr'),
    password=os.getenv('PASS', 'nbr@123'),
    port=os.getenv('PORT', 3306)
)
upload_dir = "content"

# Create Redis connection

# def match_tags_for_text(text: str, tag_weights: dict) -> list:
#     if not text:
#         return []
#     text_l = text.lower()
#     matched = []
#     for tag in tag_weights.keys():
#         pattern = r'\b' + re.escape(tag.lower()) + r'\b'
#         if re.search(pattern, text_l):
#             matched.append(tag)
#     return matched

# def annotate_transactions_with_tags(cur, tag_weights, request_id, statement_id):
#     cur.execute("SELECT * FROM `transactions` WHERE request_id=%s AND statement_id=%s",
#                 (request_id, statement_id))
#     rows = cur.fetchall()
#     for row in rows:
#         # cursor returns dicts (see dbcon.py), adapt if your cursor returns tuples
#         text = ' '.join(filter(None, [str(row.get('details') or ''), str(row.get('transaction_code') or '')]))
#         tags = match_tags_for_text(text, tag_weights)
#         tags_json = json.dumps(tags, ensure_ascii=False)
#         cur.execute("UPDATE `transactions` SET `tags`=%s WHERE id=%s", (tags_json, row.get('id')))



def get_fiscal_year(date_str):
    # date_str expected in YYYY-MM-DD format
    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    year = date_obj.year
    # Fiscal year starts from July 1 (month >= 7)
    if date_obj.month >= 7:
        return f"{year}-{year+1}"
    else:
        return f"{year-1}-{year}"



    

def process_request(req:Request):
    """
    Actual processing function that runs in background
    """
    request_id = req.request_id
    db = DatabaseConnection(idf_db_conf)
    db.connect()

    cur = db.cursor
    try:
        cur.execute("UPDATE `requests` SET `status`='processing' WHERE id = %s", (req.request_id,))
        db.commit()
        
        for statement in req.statements:
            st_path = statement[0]
            st_bank = statement[1]
            st_id = statement[2]
            bank_processor = AvailableBanks[st_bank]
            
            try:
                st = bank_processor.run(upload_dir + '/' + st_path, st_bank)
            except Exception as e:
                print(f"Error processing {st_path}: {e}")
                cur.execute("UPDATE `requests` SET `status`='Error' WHERE id = %s", (req.request_id,))
                db.commit()
                return
            fiscal_year_set = set()
            for data in st.data:
                fiscal_year = get_fiscal_year(data.date)
                fiscal_year_set.add(int(fiscal_year.split('-')[0]))
                cur.execute('''INSERT INTO `transactions`(`request_id`, `statement_id`, `date`, `fiscal_year`, `transaction_code`, 
                                `details`, `ref`, `cheque`, `debit`, `credit`, `balance`, `Cat_L1`, `Cat_L2`, `Cat_L3`) 
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''',(
                                    request_id, st_id, data.date, fiscal_year, data.transaction_code, 
                                    data.details, data.ref, data.cheque, data.debit, data.credit, data.balance, 
                                    data.result['type1'].value, data.result['type2'].value, data.result['type3'].value
                                ))
            #convert dict to JSON string
            tags = json.dumps(category.get_frequent_phrases(st), ensure_ascii=False)
            from_year = min(fiscal_year_set) - 1
            to_year = max(fiscal_year_set) + 1
            cur.execute('''UPDATE `statements` SET 
                                `acc_no`=%s, `acc_type`=%s, `opening_balance`=%s,
                                `closing_balance`=%s, `tags`=%s, `from_year`=%s, `to_year`=%s 
                                WHERE id = %s AND request_id = %s''', (
                                    st.acc_no, st.acc_type, st.opening_balance, st.closing_balance, 
                                    tags, from_year, to_year, st_id, req.request_id
                                ))
        cur.execute("UPDATE `requests` SET `status`='Done' WHERE id = %s", (req.request_id,))
        db.commit()
        #db.disconnect()
        #Summerization Logic Here

        cur.execute('''SELECT * FROM `statements` WHERE `request_id`=%s''',(req.request_id,))
        statements = cur.fetchall()
        summery_list = []
        for statement in statements:
            # cursor uses dictionary=True so rows are dicts
            s_id = statement.get('id')
            request_id_stmt = statement.get('request_id')
            pdf_name = statement.get('pdf_name')
            bank_name = statement.get('bank_name')
            acc_no = statement.get('acc_no')
            acc_type = statement.get('acc_type')
            opening_balance = statement.get('opening_balance')
            closing_balance = statement.get('closing_balance')
            from_year = statement.get('from_year')
            to_year = statement.get('to_year')

            # ensure from_year/to_year exist
            if from_year is None or to_year is None:
                continue

            for i in range(int(from_year), int(to_year)):
                fiscal_year = f"{i}-{i+1}"
                cur.execute('''SELECT * FROM `transactions` WHERE `request_id`= %s AND `statement_id`=%s AND `fiscal_year`=%s''',
                            (request_id_stmt or request_id, s_id, fiscal_year))
                transactions = cur.fetchall()
                total_debit = 0.
                total_credit = 0.
                credit_interest = 0.
                source_tax = 0.
                yearend_balance = 0.
                total_cash = 0.
                total_transfer = 0.
                total_cheque = 0.
                total_others = 0.
                for transaction in transactions:
                    # `transaction` is a dict (cursor was created with dictionary=True)
                    try:
                        cat_l1 = int(transaction.get('Cat_L1') or 0)
                        cat_l2 = int(transaction.get('Cat_L2') or 0)
                    except Exception:
                        # skip malformed row
                        continue

                    debit_val = float(transaction.get('debit') or 0.0)
                    credit_val = float(transaction.get('credit') or 0.0)
                    balance_val = transaction.get('balance')
                    yearend_balance = float(balance_val) if (balance_val is not None and balance_val != '') else 0.0

                    # total debit and total credit
                    if cat_l1 == Cat_L1.debit.value:
                        total_debit += debit_val
                    elif cat_l1 == Cat_L1.credit.value:
                        total_credit += credit_val
                    # credit interest and source tax
                    if cat_l2 == Cat_L2.creditInterest.value:
                        credit_interest += credit_val
                    elif cat_l2 == Cat_L2.sourceTax.value:
                        source_tax += debit_val
                cur.execute('''INSERT INTO `summery`(`request_id`, `statement_id`, `pdf_name`,`bank_name`,`acc_no`,`acc_type`, `fiscal_year`, `total_debit`, `total_credit`, `credit_interest`, 
                                    `source_tax`, `yearend_balance`, `total_cash`, `total_transfer`, `total_cheque`, `total_others`) VALUES (%s,%s,
                                    %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',
                                    (request_id,s_id,pdf_name,bank_name,acc_no,acc_type,fiscal_year,total_debit,total_credit,credit_interest,source_tax,yearend_balance,total_cash,total_transfer,total_cheque,total_others)
                                    )
        
        cur.execute("UPDATE `requests` SET `status`='Done' WHERE id = %s", (req.request_id,))
        db.commit()
    except:
        cur.execute("UPDATE `requests` SET `status`='Error' WHERE id = %s", (req.request_id,))
        db.commit()


         
          
    

