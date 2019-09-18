if [ $1 != "n00dleBla5terBadg3r" ]; then
    echo You do not know what you are doing. Please refrain from button mashing.
    exit 1
fi

echo This will enter DESTRUCTIVE and DANGEROUS database write mode. Do you know what you are doing?
read response

if [ $response != "yes" ]; then
    echo Disaster averted. Please RTFM.
    exit 1
fi

for i in {1..10}
do
    tput bel
done

setterm -term linux -fore red
echo '██████╗ ███████╗ █████╗ ████████╗██╗  ██╗    ██╗    ██╗██╗███████╗██╗  ██╗    ███╗   ███╗ ██████╗ ██████╗ ███████╗'
echo '██╔══██╗██╔════╝██╔══██╗╚══██╔══╝██║  ██║    ██║    ██║██║██╔════╝██║  ██║    ████╗ ████║██╔═══██╗██╔══██╗██╔════╝'
echo '██║  ██║█████╗  ███████║   ██║   ███████║    ██║ █╗ ██║██║███████╗███████║    ██╔████╔██║██║   ██║██║  ██║█████╗'
echo '██║  ██║██╔══╝  ██╔══██║   ██║   ██╔══██║    ██║███╗██║██║╚════██║██╔══██║    ██║╚██╔╝██║██║   ██║██║  ██║██╔══╝'
echo '██████╔╝███████╗██║  ██║   ██║   ██║  ██║    ╚███╔███╔╝██║███████║██║  ██║    ██║ ╚═╝ ██║╚██████╔╝██████╔╝███████╗'
echo '╚═════╝ ╚══════╝╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝     ╚══╝╚══╝ ╚═╝╚══════╝╚═╝  ╚═╝    ╚═╝     ╚═╝ ╚═════╝ ╚═════╝ ╚══════╝'
echo "You better know what you're doing, buddy."
echo 'Godspeed...'
echo

psql "sslmode=verify-ca sslrootcert=/root/.postgresql-rw/root.crt sslcert=/root/.postgresql-rw/postgresql.crt sslkey=/root/.postgresql-rw/postgresql.key hostaddr=$DB_HOST_RW user=$DB_USERNAME dbname=$DB_NAME_RW password=$DB_PASSWORD"
setterm -reset
chmod -x i_know_what_i_am_doing.sh
