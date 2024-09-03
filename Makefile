
pip-install:
	poetry shell
	poetry export --without-hashes --format=requirements.txt > requirements.txt
	pip-sync requirements.txt

pip-update:
	pip install --upgrade pip pip-tools
	pip-compile requirements.in
	pip-compile requirements-dev.in
	pip-sync requirements.txt requirements-dev.txt

.PHONY: update-db
update-db:
	python standup/manage.py makemigrations
	python standup/manage.py migrate

save-point:
	poetry export --without-hashes --format=requirements.txt > requirements.txt
	git add *
	git commit -n -m 'Save Point'
	git commit push

.PHONY: run
run: 
	doppler run -t $$(doppler configure get token --plain) -- python ./standup/manage.py runserver

