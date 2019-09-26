if [[ -z "$1" ]]; then
  echo "Missing required argument: project ID"
  exit 1
fi
TARGET_PROJECT=$1

pushd "${0%/*}" || exit 1
echo "Attempting to remove whitelist entry '${USER}_cloudshell' from $TARGET_PROJECT"
pipenv run python remove_cloudshell_ip.py "$TARGET_PROJECT"
popd || exit
