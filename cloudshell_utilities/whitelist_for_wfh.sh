if [[ -z "$1" ]]; then
  echo "Missing required argument: WFH IP Address"
  exit 1
fi
if [[ -z "$2" ]]; then
  echo "Missing required argument: WFH Person's Name"
  exit 1
fi
WFH_IP=$1
WFH_NAME=$2
pushd "${0%/*}" || exit 1

CURRENT_PROJECT=$(gcloud config get-value project 2> /dev/null)

echo "Whitelisting IP: ${WFH_IP} with name ${WFH_NAME} WFH"
gcloud config set project census-rm-whitelodge
gcloud container clusters get-credentials rm-k8s-cluster --region europe-west2 --project census-rm-whitelodge
pipenv run python whitelist_service_ip.py $WFH_IP ops || exit 1
pipenv run python whitelist_service_ip.py $WFH_IP rabbitmqmanagement || exit 1
pipenv run python whitelist_service_ip.py $WFH_IP case-api-test || exit 1
pipenv run python whitelist_db_ip.py $WFH_IP "$WFH_NAME" census-rm-whitelodge

gcloud config set project census-rm-blacklodge
gcloud container clusters get-credentials rm-k8s-cluster --region europe-west2 --project census-rm-blacklodge
pipenv run python whitelist_service_ip.py $WFH_IP ops || exit 1
pipenv run python whitelist_service_ip.py $WFH_IP rabbitmqmanagement || exit 1
pipenv run python whitelist_service_ip.py $WFH_IP case-api-test || exit 1
pipenv run python whitelist_db_ip.py $WFH_IP "$WFH_NAME" census-rm-blacklodge

gcloud config set project $CURRENT_PROJECT

popd || exit
