import os
from datetime import datetime

from django.conf import settings
from django.core.management import BaseCommand




class Command(BaseCommand):
    help = 'Creates daily backup of database'

    def handle(self, *args, **options):
        now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        backup_dir = os.path.join(settings.BASE_DIR, "backup")
        os.makedirs(backup_dir, exist_ok=True)

        file_name = f"db_backup_{now}.json"
        file_path = os.path.join(backup_dir, file_name)

        os.system(f"python manage.py dumpdata > {file_path}")
        self.stdout.write(self.style.SUCCESS(f"✅ Backup created: {file_name}"))


