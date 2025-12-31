from utils.requests import Request
from db.dbops import DBOps
import queue


db = DBOps()
req = Request(1,"System", 123)
req.add_statements("ebl.pdf","EBL")

request_queue = queue.Queue()

req_id = db.request_handler(req)
req.request_id = req_id

print("Request id: " + str(req.request_id))

request_queue.put(req)

print("1")
req_a = request_queue.get()

print("Request id: " + str(req_a.request_id))

db.request_process(req_a)




