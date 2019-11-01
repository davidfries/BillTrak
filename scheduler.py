from pytz import utc
from secrets import secrets as secrets
from apscheduler.triggers import cron
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ProcessPoolExecutor

class EmailScheduler():
    jobstores = {
        'default':SQLAlchemyJobStore(f'postgresql://192.168.5.172/billtrak?user=dj&password={secrets.dbpw}')
    }
    executors = {
    'default': {'type': 'threadpool', 'max_workers': 20},
    'processpool': ProcessPoolExecutor(max_workers=5)
    }
    job_defaults = {
        'coalesce': False,
        'max_instances': 3
    }
    scheduler = BackgroundScheduler()

    def getcron(self):
        return cron.CronTrigger()

    scheduler.configure(jobstores=jobstores, executors=executors, job_defaults=job_defaults, timezone=utc)
    def getscheduler(self):
        return self.scheduler
    