install: dependencies initdb data

test: lint test-python

lint:
	@echo "Linting Python files"
	flake8 --ignore=E121,W404,F403,E501,E402 --exclude=./docs/*,./env/*,./venv/*,migrations,.git . || exit 1
	@echo ""

test-python:
	@echo "Running Python tests"
	python manage.py test -v 3 || exit 1
	@echo ""

initdb:
	@echo "Setting up database"
	python manage.py syncdb
	python manage.py migrate

dependencies:
	@echo "Installing python packages"
	pip install --upgrade "flake8>=2.0"
	pip install --upgrade -r requirements.txt
	pip install -r requirements.txt

server:
	@echo "Running development server"
	python manage.py runserver 0.0.0.0:7000

data:
	@echo "Installing fixtures"
	python manage.py loaddata apps/taxonomy/fixtures/languages.json
	python manage.py loaddata apps/taxonomy/fixtures/taxonrank.json

test-tree: fixtures traversalorder

fixtures:
	python manage.py loaddata apps/taxonomy/fixtures/test_tree.json
	python manage.py loaddata apps/taxonomy/fixtures/test_taxonnameconcept.json
	python manage.py loaddata apps/taxonomy/fixtures/test_taxonnode.json
	python manage.py loaddata apps/taxonomy/fixtures/test_edge.json
	python manage.py loaddata apps/taxonomy/fixtures/test_act.json
	python manage.py loaddata apps/taxonomy/fixtures/test_traversalorder.json

traversalorder:
	@echo "Populating pre traversal order"
	python manage.py populate_pre_traversal

