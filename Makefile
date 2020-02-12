docker_build:
	docker build -t eu.gcr.io/census-rm-ci/rm/census-rm-toolbox .

flake:
	pipenv run flake8

check:
	pipenv check