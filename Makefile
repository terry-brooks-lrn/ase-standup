
pip-install:
	poetry shell
	poetry export --without-hashes --format=requirements.txt > requirements.txt
	pip-sync requirements.txt

pip-update:
	pip install --upgrade pip pip-tools
	pip-compile requirements.in
	pip-compile requirements-dev.in
	pip-sync requirements.txt requirements-dev.txt


update-db:
	poetry shell
	python wmanage.py makemigrations
	python manage.py migrate
