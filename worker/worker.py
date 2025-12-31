#!/usr/bin/env python
import os
import sys
import redis
from rq import Worker, Queue, SimpleWorker
import logging

# Configure logging
logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Also log to a file next to this script so logs persist: worker_log.txt
log_file_path = os.path.join(os.path.dirname(__file__), 'content/worker_log.txt')
file_handler = logging.FileHandler(log_file_path, encoding='utf-8')
file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))
logging.getLogger().addHandler(file_handler)

# def start_worker():
#     # Redis connection
#     redis_url = os.getenv('REDIS_URL', 'redis://72.61.229.43:6379/0')
    
#     # Create Redis connection
#     redis_conn = redis.Redis.from_url(redis_url)
    
#     # Define which queues to listen to
#     queue_names = ['high', 'default', 'low']
    
#     # Create and start worker
#     worker = Worker(
#         queues=queue_names,
#         connection=redis_conn,
#         name=os.getenv('WORKER_NAME', 'worker-1')
#     )
    
#     worker.work(with_scheduler=False)

if __name__ == '__main__':
    redis_conn = redis.Redis.from_url(os.getenv('REDIS_URL', 'redis://72.61.229.43:6379/0'))
    q = Queue('default', connection=redis_conn)
    w = SimpleWorker([q], connection=redis_conn)
    w.work()