#!/usr/bin/env python

import pika
import json

EVENTS_QUEUE = "events"


def do_maintenance():
    # maintenance hook, e.g. remove expired subscriptions, TBD
    pass


def dispatch_event(device, topic, payload):
    print("send event: device %s, topic %s" % (device, topic))


def init_channel():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters("localhost"))
    channel = connection.channel()
    channel.queue_declare(queue=EVENTS_QUEUE)

    return channel


def parse_body(body):
    ed = json.loads(body.decode("utf-8"))
    return (ed["device"], ed["topic"], None)


def main():
    channel = init_channel()

    for msg in channel.consume(EVENTS_QUEUE, inactivity_timeout=400):
        if msg is None:
            do_maintenance()
            continue

        method, properties, body = msg
        dispatch_event(*parse_body(body))
        channel.basic_ack(method.delivery_tag)


if __name__ == "__main__":
    main()
