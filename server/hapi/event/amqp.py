import json
import pika
import time


EVENTS_QUEUE = "events"


def send_event(event):
    """
    Send event to our AMPQ event's queue.

    Will add a timestamp to the event, using 'now' time.

    :param event: event description as a dictionary
    """

    event["timestamp"] = time.time()

    connection = pika.BlockingConnection(
        pika.ConnectionParameters("localhost"))
    channel = connection.channel()
    channel.queue_declare(queue=EVENTS_QUEUE)
    channel.basic_publish(exchange="",
                          routing_key=EVENTS_QUEUE,
                          body=json.dumps(event))
    connection.close()
