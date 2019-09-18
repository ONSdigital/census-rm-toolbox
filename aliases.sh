shopt -s expand_aliases
alias queuetool='python queue_manipulator.py'
alias findbadmessages='python poison_message_queue_finder.py -r'
alias findpubsubmessages='python get_pubsub_messages.py'
alias pubsubmessagetobucket='python put_message_on_bucket.py'
alias buckettopubsub='publish_message_from_bucket.py'
alias dosql='psql "sslmode=require hostaddr=$DB_HOST user=$DB_USERNAME dbname=$DB_NAME password=$DB_PASSWORD"'
alias dosql-i-know-what-i-am-doing='chmod +x i_know_what_i_am_doing.sh && ./i_know_what_i_am_doing.sh n00dleBla5terBadg3r'
alias helpme='echo "Commands: findbadmessages, queuetool [-h], vi, curl, dosql"'