if [[ -z "$1" ]]; then
  echo "Missing required argument: project ID"
  exit 1
fi
TARGET_PROJECT=$1
pushd "${0%/*}" || exit 1

echo "Setting project to $TARGET_PROJECT"
gcloud config set project "$TARGET_PROJECT"

echo "Creating and setting kubectl context for $TARGET_PROJECT"
gcloud container clusters get-credentials rm-k8s-cluster --region europe-west2 --project "$TARGET_PROJECT"

CLOUDSHELL_IP=$(dig +short myip.opendns.com @resolver1.opendns.com)

echo "Whitelisting cloudshell IP: $CLOUDSHELL_IP with name ${USER}_cloudshell"
pipenv run python whitelist_cluster_ip.py "$TARGET_PROJECT" "$CLOUDSHELL_IP" "$USER" "_cloudshell" || exit 1

echo "Test cluster connection by running 'kubectl get pods'"
popd || exit
