while [ 1 ]
do
    python monitoring/find_slow_event_processing.py
    python monitoring/action_worker_database_monitor.py
    sleep 59s
done