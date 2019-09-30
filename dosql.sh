if [[ -z "$1" ]]; then
  read -p "Username: " -r username
else
  username=$1
fi
psql "sslmode=require hostaddr=$DB_HOST user=$username dbname=$DB_NAME"
