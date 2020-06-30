while [ 1 ]
do
    python -m monitoring.find_slow_event_processing
    python -m monitoring.action_worker_database_monitor
    sleep 59s
done