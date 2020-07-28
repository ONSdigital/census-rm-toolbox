shopt -s expand_aliases
alias queuetool='python -m message_tools.queue_manipulator'
alias findbadqueues='python -m monitoring.poison_message_queue_finder -r'
alias findpubsubmessages='python -m message_tools.get_pubsub_messages'
alias pubsubmessagetobucket='python -m message_tools.put_message_on_bucket'
alias buckettopubsub='python -m message_tools.publish_message_from_bucket'
alias dosql='dosql.sh'
alias dosqla='dosql-action.sh'
alias dosql-i-know-what-i-am-doing='i_know_what_i_am_doing.sh n00dleBla5terBadg3r'
alias dosql-i-know-what-i-am-doing-action='i_know_what_i_am_doing_action.sh g1n0rm0usHam5t3r'
alias helpme='echo "Commands: helpme, msgwizard, findbad, baddetails, queuetool [-h], vi, curl, dosql [username], sftp, dumpfilestoqueue, dumpqueuetofiles, listqueues, makemessage, peekmessage, skipmessage, viewskipped, resetexceptionmanager, qidcheck [qid], fulfilment, weekendfulfilment"'
alias dumpfilestoqueue='python -m message_tools.dump_files_to_queue'
alias adventure='python adventure.py'
alias dumpqueuetofiles='python -m message_tools.dump_queue_to_files'
alias listqueues='python -m monitoring.poison_message_queue_finder'
alias makemessage='python -m message_tools.message_maker'
alias findbad='curl -s http://$EXCEPTIONMANAGER_HOST:$EXCEPTIONMANAGER_PORT/badmessages | jq'
alias viewskipped='curl -s http://$EXCEPTIONMANAGER_HOST:$EXCEPTIONMANAGER_PORT/skippedmessages | jq'
alias resetexceptionmanager='curl -s http://$EXCEPTIONMANAGER_HOST:$EXCEPTIONMANAGER_PORT/reset'
alias msgwizard='python -m message_tools.bad_message_wizard'
alias qidcheck='python qid_checksum_validator.py --modulus $QID_MODULUS --factor $QID_FACTOR'
alias qidlink='python questionnaire_linking.py'
alias fulfilment='python -m monitoring.fulfilment_count'
alias weekendfulfilment='python -m monitoring.weekend_fulfilment_count'
alias reminderbatch='python -m reminder_batch_scheduler.reminder_batch'
alias bulkrefusals='python -m bulk_processing.refusal_processor'
alias bulknewaddresses='python -m bulk_processing.new_address_processor'

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
