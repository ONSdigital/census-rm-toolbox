while [ 1 ]
do
    python monitoring/poison_message_queue_finder.py
    sleep 15s
done