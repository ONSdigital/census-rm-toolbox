while [ 1 ]
do
    python -m toolbox.monitoring.find_slow_event_processing
    python -m toolbox.monitoring.action_worker_database_monitor
    sleep 59s
done