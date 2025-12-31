from dbcon import *
from requests import Request
from redis import Redis
from rq import Queue
import os


redis_conn = Redis(host=os.getenv('REDIS_HOST', '72.61.229.43'), port=6379, db=0)
queue = Queue('default', connection=redis_conn)

idf_db_conf = DatabaseConfig(
    host= os.getenv('REDIS_URL', '72.61.229.43'),
    database=os.getenv('DATABASE', 'idf_db'),
    user=os.getenv('USER', 'root'),
    password=os.getenv('PASS', 'toor'),
    port=os.getenv('PORT', 3307)
)


def place_request(req:Request):
    db = DatabaseConnection(idf_db_conf)
    db.connect()
    cur = db.cursor
    cur.execute('''INSERT INTO `requests`
                         (`officer_id`, `taxpayer_name`, `taxpayer_tin`, `status`,`msg`, `date_time`)
                         VALUES (%s, %s, %s, %s, %s,NOW())''',
                         (req.user_id, req.taxpayer_name, req.taxpayer_tin, 'pending', 'This request is in the queue.'))
    request_id = cur.lastrowid
    req.request_id = request_id
    for i in range(len(req.statements)):
            cur.execute('''INSERT INTO `statements`(`request_id`, `pdf_name`, `bank_name`) 
                             VALUES (%s,%s,%s)''',(request_id,req.statements[i][0],req.statements[i][1]))
            statement_id = cur.lastrowid
            req.statements[i][2] = statement_id
    db.commit()
    db.disconnect()
    #process_request(req)
    job = queue.enqueue(
        'process_req.process_request',  # Module.function path
        args=[req],
        # kwargs={'bank_type': request.bank_type},
        job_id= "job_"+str(request_id),
        job_timeout=300,  # 5 minutes timeout
        result_ttl=86400,  # Keep result for 24 hours
        failure_ttl=604800,  # Keep failed jobs for 7 days
        description=f"Process statement for user"
    )

    return request_id