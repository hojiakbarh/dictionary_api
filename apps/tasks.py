import logging

from apscheduler.schedulers.background import BackgroundScheduler
from django.core.management import call_command


def start():
    scheduler = BackgroundScheduler()

    # Har kunda 1 marta backup_db commandini chaqiradi

    scheduler.add_job(
        lambda: call_command('backup_bd'),
        trigger='interval',
        days=1,
        id='daily_backup_job',
        replace_existing=True,
    )
    try:
        scheduler.start()
        logging.info("✅ Apscheduler started successfully.")
    except Exception as e:
        logging.error(f"❌ Scheduler failed: {e}")