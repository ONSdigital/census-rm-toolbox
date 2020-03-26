pushd "${0%/*}" || exit 1

CURRENT_PROJECT=$(gcloud config get-value project 2> /dev/null)

gcloud auth application-default login

WFH_IP=$(dig +short myip.opendns.com @resolver1.opendns.com)

echo "Whitelisting IP: ${WFH_IP} with name ${USER} WFH"
gcloud config set project census-rm-whitelodge
gcloud container clusters get-credentials rm-k8s-cluster --region europe-west2 --project census-rm-whitelodge
pipenv run python add_cluster_ip.py census-rm-whitelodge "$WFH_IP" "$USER" " WFH" || exit 1
pipenv run python whitelist_service_ip.py $WFH_IP ops || exit 1
pipenv run python whitelist_service_ip.py $WFH_IP rabbitmqmanagement || exit 1
pipenv run python whitelist_service_ip.py $WFH_IP case-api-test || exit 1
pipenv run python whitelist_db_ip.py $WFH_IP "$USER" census-rm-whitelodge

gcloud config set project census-rm-blacklodge
gcloud container clusters get-credentials rm-k8s-cluster --region europe-west2 --project census-rm-blacklodge
pipenv run python add_cluster_ip.py census-rm-blacklodge "$WFH_IP" "$USER" " WFH" || exit 1
pipenv run python whitelist_service_ip.py $WFH_IP ops || exit 1
pipenv run python whitelist_service_ip.py $WFH_IP rabbitmqmanagement || exit 1
pipenv run python whitelist_service_ip.py $WFH_IP case-api-test || exit 1
pipenv run python whitelist_db_ip.py $WFH_IP "$USER" census-rm-blacklodge

gcloud config set project $CURRENT_PROJECT
gcloud container clusters get-credentials rm-k8s-cluster --region europe-west2 --project $CURRENT_PROJECT

popd || exit
