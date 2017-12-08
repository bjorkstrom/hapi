#!/usr/bin/env python
import pika
import json
import time
from hapi.dbmodels import Device
import requests

EVENTS_QUEUE = "events"


def do_maintenance():
    # maintenance hook, e.g. remove expired subscriptions, TBD
    pass


def epoch2iso(epoch):
    """
    convert unix epoch timestamp to ISO 8601 UTC date-time string
    """
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(epoch))


def send_event(device, topic, restEndpoint, timestamp):
    """
    send the event to subscription's destination
    """
    payload = {
        "topic": topic,
        "device": device,
        "timestamp": epoch2iso(timestamp)
    }

    headers = {}
    for header in restEndpoint.httpheaders:
        headers[header.name] = header.value

    r = requests.post(restEndpoint.url, json=payload, headers=headers)
    print(r)


def dispatch_event(device, topic, payload, timestamp):
    dev = Device.get(device)
    subs = dev.subscriptions
    for sub in subs:
        for subTopic in sub.topics:
            if subTopic.topic == topic:
                print("send event: device %s, topic %s" % (device, topic))
                send_event(device, topic, sub.restEndpoint, timestamp)


def init_channel():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters("localhost"))
    channel = connection.channel()
    channel.queue_declare(queue=EVENTS_QUEUE)

    return channel


def parse_body(body):
    ed = json.loads(body.decode("utf-8"))
    return ed["device"], ed["topic"], None, ed["timestamp"]


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
