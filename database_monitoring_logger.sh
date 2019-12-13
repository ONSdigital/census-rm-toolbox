while [ 1 ]
do
    python find_slow_event_processing.py
    python action_worker_database_monitor.py
    sleep 59s
done