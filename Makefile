docker_build:
	docker build -t eu.gcr.io/census-rm-ci/rm/census-rm-toolbox .

flake:
	pipenv run flake8

# -i 40014
check:
	PIPENV_PYUP_API_KEY="" pipenv check -i 39611 -i 39608

test: flake check
	ENVIRONMENT=TEST pipenv run pytest