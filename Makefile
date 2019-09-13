docker_build:
	docker build -t eu.gcr.io/census-rm-ci/rm/census-rm-toolbox .

apply-deployment:
	kubectl apply -f census-rm-toolbox-deployment.yml

connect-to-pod:
	kubectl exec -it `kubectl get pods -o name | grep -m1 census-rm-toolbox | cut -d'/' -f 2` -- /bin/bash

delete-pod:
	kubectl delete deploy census-rm-toolbox