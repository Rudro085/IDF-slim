from fastapi import FastAPI, UploadFile, Form, File
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from contextlib import asynccontextmanager
import threading
from redis import Redis
from rq import Queue
import os,json
import uvicorn
from utils.requests import Request
from utils.banks import AvailableBanks
import tasks


UPLOAD_DIR = "uploaded_pdfs"
os.makedirs(UPLOAD_DIR, exist_ok=True)
app = FastAPI()

# Create Redis connection
redis_conn = Redis(host='72.61.229.43', port=6379, db=0)
queue = Queue('default', connection=redis_conn)

@app.get("/get_bank_list")
async def get_bank_list():
    return list(AvailableBanks.keys())

@app.post("/place_request")
async def place_request(
    officer_id: int = Form(...),
    taxpayer_name: str = Form(...),
    tin: str = Form(...),
    bank_statements: str = Form(...),
):
    try:
        # bank_statements = '[{"bank_name":"EBL","path":"test.pdf"},{"bank_name":"UCB","path":"test2.pdf"}]'
        req = Request(officer_id,taxpayer_name,tin)
        try:
            bank_statements = json.loads(bank_statements)
        except:
            return {"status":"eroor","msg":"Invalid bank statement."}
        for bank_statement in bank_statements:
            req.add_statements(pdf_path=bank_statement["path"],bank_name=bank_statement["bank_name"])
        request_id = tasks.place_request(req)
        return {"status":"success","request_id":request_id}
    except:
        return {"status":"eroor","msg":"Invalid bank statement."}


    #tasks.process_bank_statement("qsndnq",12)
    # job = queue.enqueue(
    #     'tasks.process_bank_statement',  # Module.function path
    #     args=["request.file_path", 12],
    #     # kwargs={'bank_type': request.bank_type},
    #     job_id='10',
    #     job_timeout=300,  # 5 minutes timeout
    #     result_ttl=86400,  # Keep result for 24 hours
    #     failure_ttl=604800,  # Keep failed jobs for 7 days
    #     description=f"Process statement for user"
    # )
    return {"status":"successful"}




if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
