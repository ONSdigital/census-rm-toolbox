shopt -s expand_aliases
alias queuetool='python queue_manipulator.py'
alias findbadqueues='python poison_message_queue_finder.py -r'
alias findpubsubmessages='python get_pubsub_messages.py'
alias pubsubmessagetobucket='python put_message_on_bucket.py'
alias buckettopubsub='python publish_message_from_bucket.py'
alias dosql='dosql.sh'
alias dosql-i-know-what-i-am-doing='i_know_what_i_am_doing.sh n00dleBla5terBadg3r'
alias helpme='echo "Commands: helpme, msgwizard, findbad, baddetails, queuetool [-h], vi, curl, dosql [username], sftp, dumpfilestoqueue, dumpqueuetofiles, listqueues, makemessage, peekmessage, skipmessage, viewskipped, resetexceptionmanager, qidcheck [qid]"'
alias dumpfilestoqueue='python dump_files_to_queue.py'
alias adventure='python adventure.py'
alias dumpqueuetofiles='python dump_queue_to_files.py'
alias listqueues='python poison_message_queue_finder.py'
alias makemessage='python message_maker.py'
alias findbad='curl -s http://$EXCEPTIONMANAGER_HOST:$EXCEPTIONMANAGER_PORT/badmessages | jq'
alias viewskipped='curl -s http://$EXCEPTIONMANAGER_HOST:$EXCEPTIONMANAGER_PORT/skippedmessages | jq'
alias resetexceptionmanager='curl -s http://$EXCEPTIONMANAGER_HOST:$EXCEPTIONMANAGER_PORT/reset'
alias msgwizard='python bad_message_wizard.py'
alias qidcheck='python qid_checksum_validator.py'
alias fulfilment='python fulfilment_count.py'
alias weekendfulfilment='python weekend_fulfilment_count.py'

baddetails() {
    curl -s http://$EXCEPTIONMANAGER_HOST:$EXCEPTIONMANAGER_PORT/badmessage/$1 | jq
}

peekmessage() {
    echo "----PEEK START----"
    echo
    curl -s http://$EXCEPTIONMANAGER_HOST:$EXCEPTIONMANAGER_PORT/peekmessage/$1
    echo
    echo "-----PEEK END-----"
}

skipmessage() {
    curl -s http://$EXCEPTIONMANAGER_HOST:$EXCEPTIONMANAGER_PORT/skipmessage/$1
}
