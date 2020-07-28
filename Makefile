docker_build:
	docker build -t eu.gcr.io/census-rm-ci/rm/census-rm-toolbox .

flake:
	pipenv run flake8

check:
	PIPENV_PYUP_API_KEY="" pipenv check

test: flake check
	ENVIRONMENT=TEST pipenv run pytest