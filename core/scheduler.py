import logging

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ProcessPoolExecutor, ThreadPoolExecutor
from django_apscheduler.jobstores import register_events, register_job
from django_apscheduler.models import DjangoJobExecution

from django.conf import settings
from services.profile_service import ProfileService

class Scheduler:
    scheduler = BackgroundScheduler(settings.SCHEDULER_CONFIG)
    
    @register_job(scheduler, "interval", minutes=1)
    def profile_update_job():
        DjangoJobExecution.objects.delete_old_job_executions(604_800) # 7 days
        ProfileService.update_profiles()

    @classmethod
    def start(cls):
        if settings.DEBUG:
            logging.basicConfig()
            logging.getLogger('apscheduler').setLevel(logging.DEBUG)
        register_events(cls.scheduler)
        cls.scheduler.start()