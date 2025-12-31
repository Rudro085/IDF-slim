from fastapi import FastAPI, UploadFile, Form, File
from fastapi.responses import JSONResponse
from typing import List
import uvicorn
import os
from fastapi.middleware.cors import CORSMiddleware
from db.dbops import DBOps
from utils.requests import Request
import threading
import queue

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # OR specify ["http://127.0.0.1:5500", "http://localhost:5500"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploaded_pdfs"
os.makedirs(UPLOAD_DIR, exist_ok=True)

request_queue = queue.Queue()

def queue_handler():
    global request_queue
    db = DBOps()
    
    while True:
        if not request_queue.empty():
            req = request_queue.get()
            print(req.request_id)
            db.request_process(req)


@app.post("/upload_statements")
async def upload_statements(
    
    user_id:int = Form(...),
    name: str = Form(...),
    tin: str = Form(...),
    banks: List[str] = Form(...),
    files: List[UploadFile] = File(...)
):
    global request_queue
    # Validation: banks and files must have same length
    if len(banks) != len(files):
        return JSONResponse(
            {"error": "Number of banks and files must match."},
            status_code=400
        )

    saved_files = []
    for bank, file in zip(banks, files):
        filename = f"{file.filename}"
        filepath = os.path.join(UPLOAD_DIR, filename)
        with open(filepath, "wb") as f:
            f.write(await file.read())
        saved_files.append({"bank": bank, "file": filename})
    # Tested

    db = DBOps()
    req = Request(user_id,name,tin)
    for saved_file in saved_files:
        req.add_statements(saved_file['file'],saved_file['bank'])
    req_id = db.request_handler(req)
    req.request_id = req_id
    request_queue.put(req)
    db.close()


    return {
        "message": req_id,
        "taxpayer": {"name": name, "tin": tin},
        "files": saved_files
    }


if __name__ == "__main__":
    thread = threading.Thread(target=queue_handler, daemon=True)
    thread.start()
    uvicorn.run("mainapi:app", host="0.0.0.0", port=8000, reload=False)