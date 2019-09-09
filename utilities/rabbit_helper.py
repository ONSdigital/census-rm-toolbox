import functools

from utilities.rabbit_context import RabbitContext

connection = None
rabbit = None


def init_rabbit(queue):
    global connection, rabbit
    rabbit = RabbitContext(queue_name=queue)
    connection = rabbit.open_connection()


def start_listening_for_messages(queue, on_message_callback, timeout=30):
    global connection, rabbit
    connection.call_later(
        delay=timeout,
        callback=functools.partial(_timeout_callback, rabbit))

    rabbit.channel.basic_consume(
        queue=queue,
        on_message_callback=on_message_callback)
    rabbit.channel.start_consuming()


def get_queue_qty():
    return rabbit.get_queue_message_qty()


def _timeout_callback(rabbit_connection):
    rabbit_connection.close_connection()


def add_test_queue(binding_key, exchange_name, queue_name, exchange_type='topic'):
    with RabbitContext() as rabbit_connection:
        rabbit_connection.channel.exchange_declare(exchange=exchange_name, exchange_type=exchange_type, durable=True)
        rabbit_connection.channel.queue_declare(queue=queue_name, durable=True)
        rabbit_connection.channel.queue_bind(exchange=exchange_name, queue=queue_name, routing_key=binding_key)


def purge_queues(*queues):
    with RabbitContext() as rabbit_connection:
        for queue in queues:
            rabbit_connection.channel.queue_purge(queue=queue)
