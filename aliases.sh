shopt -s expand_aliases
alias queuetool='python queue_manipulator.py'
alias findbadqueues='python poison_message_queue_finder.py -r'
alias findpubsubmessages='python get_pubsub_messages.py'
alias pubsubmessagetobucket='python put_message_on_bucket.py'
alias buckettopubsub='python publish_message_from_bucket.py'
alias dosql='dosql.sh'
alias dosql-i-know-what-i-am-doing='i_know_what_i_am_doing.sh n00dleBla5terBadg3r'
alias helpme='echo "Commands: findbadmessages, queuetool [-h], vi, curl, dosql [username], dumpfilestoqueue, dumpqueuetofiles, listqueues, makemessage"'
alias dumpfilestoqueue='python dump_files_to_queue.py'
alias dumpqueuetofiles='python dump_queue_to_files.py'
alias listqueues='python poison_message_queue_finder.py'
alias makemessage='python message_maker.py'
alias findbadmessages='curl http://$EXCEPTIONMANAGER_HOST:$EXCEPTIONMANAGER_PORT/badmessages | jq'
alias peekmessage='curl http://$EXCEPTIONMANAGER_HOST:$EXCEPTIONMANAGER_PORT/peekmessage'
alias skipmessage='curl http://$EXCEPTIONMANAGER_HOST:$EXCEPTIONMANAGER_PORT/skipmessage'
alias viewskipped='curl http://$EXCEPTIONMANAGER_HOST:$EXCEPTIONMANAGER_PORT/skippedmessages | jq'
alias resetexceptionmanager='curl http://$EXCEPTIONMANAGER_HOST:$EXCEPTIONMANAGER_PORT/reset'

badmessagedetails() {
    curl http://$EXCEPTIONMANAGER_HOST:$EXCEPTIONMANAGER_PORT/badmessage/$1 | jq
}
