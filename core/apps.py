from django.apps import AppConfig
from django.conf import settings

class CoreConfig(AppConfig):
    name = 'core'

    def ready(self):
        from .scheduler import Scheduler
        if settings.SCHEDULER_AUTOSTART:
        	Scheduler.start()
