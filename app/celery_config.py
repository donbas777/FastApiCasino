import os
from celery import Celery
from dotenv import load_dotenv

load_dotenv()

CELERY_BROKER = os.getenv('CELERY_BROKER')
CELERY_BACKEND = os.getenv('CELERY_BACKEND')

celery_app = Celery(
    'my_app',
    broker=CELERY_BROKER,
    backend=CELERY_BACKEND
)

celery_app.conf.update(
    result_expires=3600,
)
celery_app.conf.broker_connection_retry_on_startup = True
celery_app.autodiscover_tasks(['app.tasks'])
