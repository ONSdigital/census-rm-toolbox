if [[ -z "$1" ]]; then
  read -p "Username: " -r username
else
  username=$1
fi
PGOPTIONS="-c default_transaction_read_only=true" psql "sslmode=verify-ca sslrootcert=/home/toolbox/.postgresql-action/root.crt sslcert=/home/toolbox/.postgresql-action/postgresql.crt sslkey=/home/toolbox/.postgresql-action/postgresql.key hostaddr=$DB_HOST_ACTION user=$username dbname=$DB_NAME" -e -L ~/.audit/$CURRENT_USER/sqla_${username}_$(date --iso-8601=ns).log
