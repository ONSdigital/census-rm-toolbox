if [[ -z "$1" ]]; then
  echo "Missing required argument: project ID"
  exit 1
fi
TARGET_PROJECT=$1

if [[ -z "$2" ]]; then
  echo "Missing required argument: whitelist config file"
  exit 1
fi
CONFIG_FILE=$2

pushd "${0%/*}" || exit 1

CURRENT_PROJECT=$(gcloud config get-value project 2> /dev/null)
echo Current project is $CURRENT_PROJECT

gcloud auth application-default login

gcloud config set project $TARGET_PROJECT
gcloud container clusters get-credentials rm-k8s-cluster --region europe-west2 --project $TARGET_PROJECT
pipenv run python whitelist.py $TARGET_PROJECT $CONFIG_FILE || exit 1

gcloud config set project $CURRENT_PROJECT
gcloud container clusters get-credentials rm-k8s-cluster --region europe-west2 --project $CURRENT_PROJECT
echo Restored current project to $(gcloud config get-value project 2> /dev/null)

rm -rf census-rm-whitelist

popd || exit
