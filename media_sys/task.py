import logging
from api_sys.celery import app

from celery import shared_task

import time

@app.task
def dosomething(a,b):
    try:
        s = a + b
        time.sleep(5)
        logging.info("%d + %d = %d" % (a,b, s))
        return s
    except:
        logging.warning('has error')
        return 0

@shared_task
def mul(a,b):
    try:
        s = a * b
        time.sleep(5)
        logging.info("%d * %d = %d" % (a,b, s))
        return s
    except:
        logging.warning('has error')
        return 0


