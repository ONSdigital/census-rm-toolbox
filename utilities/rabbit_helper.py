from utilities.rabbit_context import RabbitContext


def add_test_queue(binding_key, exchange_name, queue_name, exchange_type='topic'):
    with RabbitContext() as rabbit_connection:
        rabbit_connection.channel.exchange_declare(exchange=exchange_name, exchange_type=exchange_type, durable=True)
        rabbit_connection.channel.queue_declare(queue=queue_name, durable=True)
        rabbit_connection.channel.queue_bind(exchange=exchange_name, queue=queue_name, routing_key=binding_key)


def purge_queues(*queues):
    with RabbitContext() as rabbit_connection:
        for queue in queues:
            rabbit_connection.channel.queue_purge(queue=queue)
