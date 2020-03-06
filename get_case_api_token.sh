CONFIG_FILE=$1
if [ -z "$CONFIG_FILE" ]; then
  CONFIG_FILE=~/.case-api-auth-config.json
  echo "Defaulting to $CONFIG_FILE"
fi

CLIENT_SECRET=$(python3 -c "import sys, json; print(json.load(sys.stdin)['client_secret'])" <$CONFIG_FILE)
CASE_API_CLIENT_ID=$(python3 -c "import sys, json; print(json.load(sys.stdin)['case_api_client_id'])" <$CONFIG_FILE)
IAP_CLIENT_ID=$(python3 -c "import sys, json; print(json.load(sys.stdin)['iap_client_id'])" <$CONFIG_FILE)
open "https://accounts.google.com/o/oauth2/v2/auth?client_id=$CASE_API_CLIENT_ID&response_type=code&scope=openid%20email&access_type=offline&redirect_uri=urn:ietf:wg:oauth:2.0:oob"

read -p "Paste the auth code and hit ENTER: " AUTH_CODE

REFRESH_TOKEN=$(curl -s \
  --data client_id="$CASE_API_CLIENT_ID" \
  --data client_secret="$CLIENT_SECRET" \
  --data code="$AUTH_CODE" \
  --data redirect_uri=urn:ietf:wg:oauth:2.0:oob \
  --data grant_type=authorization_code \
  https://oauth2.googleapis.com/token | python3 -c "import sys, json; print(json.load(sys.stdin)['refresh_token'])")

echo "Access token:
$(curl -s \
  --data client_id="$CASE_API_CLIENT_ID" \
  --data client_secret="$CLIENT_SECRET" \
  --data refresh_token="$REFRESH_TOKEN" \
  --data grant_type=refresh_token \
  --data audience="$IAP_CLIENT_ID" \
  https://oauth2.googleapis.com/token | python3 -c "import sys, json; print(json.load(sys.stdin)['id_token'])")"
