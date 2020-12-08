from __future__ import absolute_import, unicode_literals
from celery.schedules import crontab
from celery import Celery

import os


# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mobiletilbud.settings.development')

app = Celery('mobiletilbud')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

# app.conf.beat_schedule = {
#     'add-everyday-midnight': {
#         'task': 'telecompanies.tasks.task_fetch_three_offers',
#         'schedule': (crontab(minute='*/10')),
#         # 'schedule': crontab(minute=0, hour=0),
#     },
#     'add-everyday-midnight': {
#         'task': 'telecompanies.tasks.task_fetch_telenor_offers',
#         'schedule': (crontab(minute='*/10')),
#         # 'schedule': crontab(minute=0, hour=0),
#     },
#     'add-everyday-midnight': {
#         'task': 'telecompanies.tasks.task_fetch_telia_offers',
#         'schedule': (crontab(minute='*/10')),
#         # 'schedule': crontab(minute=0, hour=0),
#     },
#     'add-everyday-midnight': {
#         'task': 'telecompanies.tasks.task_fetch_yousee_offers',
#         'schedule': (crontab(minute='*/10')),
#         # 'schedule': crontab(minute=0, hour=0),
#     },
# }

@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
