import fitz
from utils.transactions import Transaction 
from utils.statements import Statement

class Ucb_parser:
    def date_format(self,date:str)->str:
        if not len(date) == 10:
            return None
        day, month, year = date.split('-')
        new_date = f"{year}-{month}-{day}"  
        return new_date

    def fig_format(self,num_str:str)->str:
        if num_str == '0.00':
            return ''
        numeric_float = num_str.replace(',', '')
        return numeric_float 
    
    def _remove_newlines(self,string:str)->str:
        return string.replace('\n', ' ')

    def remover(self,pdf_path):
        doc = fitz.open(pdf_path)
        new_doc = fitz.open()

        for page in doc:
            new_page = new_doc.new_page(width=page.rect.width, height=page.rect.height)
            
            # Copy vector graphics (unchanged)
            for drawing in page.get_drawings():
                shape = new_page.new_shape()
                for item in drawing["items"]:
                    if item[0] == "l":
                        shape.draw_line(item[1], item[2])
                    elif item[0] == "re":
                        shape.draw_rect(item[1])
                    elif item[0] == "c":
                        shape.draw_bezier(item[1], item[2], item[3], item[4])
                shape.finish(
                    color=drawing.get("color"),
                    fill=drawing.get("fill"),
                    width=drawing.get("width", 1),
                    dashes=drawing.get("dashes")
                )
                shape.commit()

            # Copy text with CORRECTED coordinates
            blocks = page.get_text("dict")["blocks"]
            for block in blocks[1:]:
                if "lines" in block:
                    for line in block["lines"]:
                        for span in line["spans"]:
                            x, y = span["origin"]  # PDF coordinate system (0,0 at bottom-left)
                            
                            new_page.insert_text(
                                (x, y),  # Use original coordinates directly
                                span["text"],
                                fontsize=span["size"],
                                fontname=span["font"],
                                color=(0, 0, 0)
                            )
        return new_doc
        # new_doc.save(cleaned_pdf_path)
        # new_doc.close()
        # doc.close()

    def parse(self,pdf_file_path,bank_name) -> Statement:
        if not bank_name == "UCB":
            return None
        statement = Statement(pdf_name=pdf_file_path,bank_name="UCB")
        doc = self.remover(pdf_file_path)
        # Extract table
        for page in doc:
            tabs = page.find_tables()
            for tab in tabs:
                for line in tab.extract():
                    transaction = Transaction()
                    if len(line[0]) == 10 and line[0][2] == '-' and line[0][5] == '-':
                        transaction.date = self.date_format(line[0])
                        transaction.cheque = line[1]
                        transaction.ref = line[2]
                        transaction.details = self._remove_newlines(line[3])
                        transaction.transaction_code = self._remove_newlines(line[4])
                        transaction.debit = self.fig_format(line[5])
                        transaction.credit = self.fig_format(line[6])
                        transaction.balance = self.fig_format(line[7])
                        statement.add(transaction)

                    elif line[0] == '':
                        try:
                            transaction.details = line[3]
                            statement.data[-1].concatinate(transaction)
                        except:
                            pass
        # Extract text
        page = doc[0]
        text = page.get_text()
        acc_pos = text.find('A/C No.')
        statement.acc_no = text[acc_pos+11:acc_pos+11+16]
        acc_type_pos = text.find('A/C Type')
        type_text = text[acc_type_pos+12:acc_type_pos+12+3]
        statement.acc_type =  "Savings" if type_text == 'SND' or type_text == 'Sav' else "Current"

        statement.opening_balance = statement.data[0].balance
        statement.closing_balance = statement.data[-1].balance
        return statement
