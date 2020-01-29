cd /app/groundzero/

PSQL_CONNECT_WRITE_MODE="sslmode=verify-ca sslrootcert=/root/.postgresql-rw/root.crt sslcert=/root/.postgresql-rw/postgresql.crt sslkey=/root/.postgresql-rw/postgresql.key hostaddr=$DB_HOST_RW user=rmuser password=password dbname=$DB_NAME_RW"
psql "$PSQL_CONNECT_WRITE_MODE" -f destroy_schemas.sql

for SCRIPT_NAME in actionv2.sql casev2.sql uacqid.sql ddl_version.sql
do
  rm $SCRIPT_NAME
  curl https://raw.githubusercontent.com/ONSdigital/census-rm-ddl/master/groundzero_ddl/$SCRIPT_NAME -o $SCRIPT_NAME

  echo "begin transaction;" > header_footer_temp.txt
  cat $SCRIPT_NAME >> header_footer_temp.txt
  echo "commit transaction;" >> header_footer_temp.txt
  rm $SCRIPT_NAME
  mv header_footer_temp.txt actionv2.sql

  psql "$PSQL_CONNECT_WRITE_MODE" -f $SCRIPT_NAME
done
