
pip-install:
	poetry shell
	poetry export --without-hashes --format=requirements.txt > requirements.in
	pip-sync requirements.txt

pip-update:
	pip install --upgrade pip pip-tools
	pip-compile requirements.in
	pip-compile requirements-dev.in
	pip-sync requirements.txt requirements-dev.txt


update-db:
	python standup/manage.py makemigrations
	python standup/manage.py migrate

save-point:
	npx --yes dotenv-vault@1.24.0 push --yes
	poetry export --without-hashes --format=requirements.txt > requirements.txt
	pip-sync requirements.txt
	git add *
	git commit -m 'Save Point'
	git commit push

go:
	python standup/manage.py runserver