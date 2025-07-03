

from django.apps import AppConfig

class AppsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps'

    def ready(self):
        try:
            from . import tasks
            tasks.start()
        except Exception as e:
            import logging
            logging.error(f"🚨 Scheduler error: {e}")