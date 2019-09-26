if [[ -z "$1" ]]; then
  read -p "Username: " -r username
else
  username=$1
fi
read -p "Password: " -rs password
psql "sslmode=require hostaddr=$DB_HOST user=$username dbname=$DB_NAME password=$password"
unset password
