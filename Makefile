lint:
	poetry run flake8 page_analyzer
test:
	poetry run pytest

test-coverage:
	poetry run pytest --cov=page_analyzer tests/ --cov-report xml

project-install:
	poetry build
	poetry publish --dry-run
	python3 -m pip install --user dist/*.whl --force-reinstall

dev:
	poetry run flask --app page_analyzer:app --debug run

PORT ?= 8000
start:
	poetry run gunicorn -w 5 -b 0.0.0.0:$(PORT) page_analyzer:app

create_db:
	sudo -u postgres createuser --createdb analyzer
	sudo -u postgres createdb --owner=analyzer base
	psql base < database.sql