mig:
	python3 manage.py makemigrations
	python3 manage.py migrate

run:
	python manage.py runserver

createsuperuser:
	python manage.py createsuperuser

loadwords:
	python manage.py loaddata apps/fixtures/words.json
