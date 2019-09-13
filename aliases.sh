shopt -s expand_aliases
alias queuetool='python queue_manipulator.py'
alias findbadmessages='python poison_message_queue_finder.py -r'
alias dosql='psql "sslmode=require hostaddr=$DB_HOST user=$DB_USERNAME dbname=$DB_NAME password=$DB_PASSWORD"'