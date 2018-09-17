test:
	pytest -v

ship:
	python setup.py sdist bdist_wheel
	twine upload dist/* --skip-existing

dev:
	gulp --cwd aploader/staticapp/

database:
	dropdb aploader --if-exists
	createdb aploader
