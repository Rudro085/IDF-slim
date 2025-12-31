import json
from tasks import *

from utils.requests import Request

bank_statements = '[{"bank_name":"EBL","path":"ebl.pdf"},{"bank_name":"UCB","path":"ucb_saving.pdf"}]'

bank_statements = json.loads(bank_statements)
req = Request(123,"rudro",123)
for statement in bank_statements:
    req.add_statements(statement['path'],statement['bank_name'])
    

place_request(req)
