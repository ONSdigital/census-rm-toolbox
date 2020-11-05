if [ "$1" != "n00dleBla5terBadg3r" ]; then
    echo "You do not know what you are doing. Please refrain from button mashing."
    exit 1
fi

echo "This will enter DESTRUCTIVE and DANGEROUS database write mode. Do you know what you are doing?"
read response

if [ "$response" != "yes" ]; then
    echo "Disaster averted. Please RTFM."
    exit 1
fi

for i in {1..10}
do
    tput bel
done

setterm -term linux -fore yellow --bold on
echo -e '\n'

echo '██████╗ ███████╗     ██████╗ █████╗ ██████╗ ███████╗███████╗██╗   ██╗██╗'
echo '██╔══██╗██╔════╝    ██╔════╝██╔══██╗██╔══██╗██╔════╝██╔════╝██║   ██║██║ '
echo '██████╔╝█████╗      ██║     ███████║██████╔╝█████╗  █████╗  ██║   ██║██║ '
echo '██╔══██╗██╔══╝      ██║     ██╔══██║██╔══██╗██╔══╝  ██╔══╝  ██║   ██║██║  '
echo '██████╔╝███████╗    ╚██████╗██║  ██║██║  ██║███████╗██║     ╚██████╔╝███████╗'
echo '╚═════╝ ╚══════╝     ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚═╝      ╚═════╝ ╚══════╝'
echo
echo "You'd better know what you're doing, buddy."
echo 'Godspeed...'
echo

if [[ -z "$2" ]]; then
  read -p "Username: " -r username
else
  username=$2
fi

psql "sslmode=verify-ca sslrootcert=/home/toolbox/.postgresql-rw/root.crt sslcert=/home/toolbox/.postgresql-rw/postgresql.crt sslkey=/home/toolbox/.postgresql-rw/postgresql.key hostaddr=$DB_HOST_RW user=$username dbname=$DB_NAME_RW" -e -L ~/.audit/$CURRENT_USER/sql_RW_${username}_$(date --iso-8601=ns).log
tput sgr0
