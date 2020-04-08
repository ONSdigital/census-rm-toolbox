pushd "${0%/*}" || exit 1

CURRENT_PROJECT=$(gcloud config get-value project 2> /dev/null)
echo Current project is $CURRENT_PROJECT

gcloud auth application-default login

gcloud config set project census-rm-whitelodge
gcloud container clusters get-credentials rm-k8s-cluster --region europe-west2 --project census-rm-whitelodge
pipenv run python whitelist.py census-rm-whitelodge || exit 1

gcloud config set project $CURRENT_PROJECT
gcloud container clusters get-credentials rm-k8s-cluster --region europe-west2 --project $CURRENT_PROJECT
echo Restored current project to $(gcloud config get-value project 2> /dev/null)

popd || exit
