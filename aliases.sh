shopt -s expand_aliases
alias queuetool='python queue_manipulator.py'
alias findbadmessages='python poison_message_queue_finder.py -r'
alias dosql='psql "sslmode=require hostaddr=$DB_HOST user=$DB_USERNAME dbname=$DB_NAME password=$DB_PASSWORD"'
alias dosql-i-know-what-i-am-doing='chmod +x i_know_what_i_am_doing.sh && ./i_know_what_i_am_doing.sh n00dleBla5terBadg3r'
alias helpme='echo "Commands: findbadmessages, queuetool [-h], vi, curl, dosql, dumpfilestoqueue, dumpqueuetofiles, listqueues"'
alias dumpfilestoqueue='python dump_files_to_queue.py'
alias dumpqueuetofiles='python dump_queue_to_files.py'
alias listqueues='python poison_message_queue_finder.py'