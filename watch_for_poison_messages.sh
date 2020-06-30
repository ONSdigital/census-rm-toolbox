while [ 1 ]
do
    python -m monitoring.poison_message_queue_finder
    sleep 15s
done