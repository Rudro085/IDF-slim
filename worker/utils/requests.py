class Request:
    def __init__(self,user_id,taxpayer_name,taxpayer_tin):
        self.user_id = user_id
        self.taxpayer_name = taxpayer_name
        self.taxpayer_tin = taxpayer_tin
        self.statements = []
        self.status = 'Pending'
        self.request_id = None
        

    def add_statements(self,pdf_path,bank_name):
        self.statements.append([pdf_path,bank_name,None])

    
