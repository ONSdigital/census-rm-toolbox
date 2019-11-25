cd /app/groundzero/
psql "sslmode=verify-ca sslrootcert=/root/.postgresql-rw/root.crt sslcert=/root/.postgresql-rw/postgresql.crt sslkey=/root/.postgresql-rw/postgresql.key hostaddr=$DB_HOST_RW user=rmuser password=password dbname=$DB_NAME_RW" -f destroy_schemas.sql

rm actionv2.sql
rm casev2.sql
rm uacqid.sql

curl https://raw.githubusercontent.com/ONSdigital/census-rm-ddl/master/groundzero_ddl/actionv2.sql -o actionv2.sql
curl https://raw.githubusercontent.com/ONSdigital/census-rm-ddl/master/groundzero_ddl/casev2.sql -o casev2.sql
curl https://raw.githubusercontent.com/ONSdigital/census-rm-ddl/master/groundzero_ddl/uac_qid.sql -o uacqid.sql

echo "begin transaction;" > header_footer_temp.txt
cat actionv2.sql >> header_footer_temp.txt
echo "commit transaction;" >> header_footer_temp.txt
rm actionv2.sql
mv header_footer_temp.txt actionv2.sql

echo "begin transaction;" > header_footer_temp.txt
cat casev2.sql >> header_footer_temp.txt
echo "commit transaction;" >> header_footer_temp.txt
rm casev2.sql
mv header_footer_temp.txt casev2.sql

echo "begin transaction;" > header_footer_temp.txt
cat uacqid.sql >> header_footer_temp.txt
echo "commit transaction;" >> header_footer_temp.txt
rm uacqid.sql
mv header_footer_temp.txt uacqid.sql

psql "sslmode=verify-ca sslrootcert=/root/.postgresql-rw/root.crt sslcert=/root/.postgresql-rw/postgresql.crt sslkey=/root/.postgresql-rw/postgresql.key hostaddr=$DB_HOST_RW user=rmuser password=password dbname=$DB_NAME_RW" -f casev2.sql
psql "sslmode=verify-ca sslrootcert=/root/.postgresql-rw/root.crt sslcert=/root/.postgresql-rw/postgresql.crt sslkey=/root/.postgresql-rw/postgresql.key hostaddr=$DB_HOST_RW user=rmuser password=password dbname=$DB_NAME_RW" -f actionv2.sql
psql "sslmode=verify-ca sslrootcert=/root/.postgresql-rw/root.crt sslcert=/root/.postgresql-rw/postgresql.crt sslkey=/root/.postgresql-rw/postgresql.key hostaddr=$DB_HOST_RW user=rmuser password=password dbname=$DB_NAME_RW" -f uacqid.sql
