#!/usr/bin/env python
import pika
import json
import time
from hapi.dbmodels import Device
import requests
from requests.exceptions import RequestException, HTTPError
from requests.exceptions import ConnectionError, Timeout
import threading
from queue import Queue

EVENTS_QUEUE = "events"
SEND_RETRIES = 3
RETRY_COOLDOWN = 1.5


def do_maintenance():
    # maintenance hook, e.g. remove expired subscriptions, TBD
    pass


def epoch2iso(epoch):
    """
    convert unix epoch timestamp to ISO 8601 UTC date-time string
    """
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(epoch))


def send_event(device, topic, restEndpoint, timestamp, payload):
    """
    send the event to subscription's destination
    """
    request_body = {
        "topic": topic,
        "device": device,
        "timestamp": epoch2iso(timestamp)
    }

    if payload is not None:
        request_body["description"] = payload

    headers = {}
    for header in restEndpoint.httpheaders:
        headers[header.name] = header.value

    for _ in range(SEND_RETRIES):
        if http_post_event(restEndpoint.url, headers, request_body):
            break


def http_post_event(url, headers, body):
    """
    make a HTTP POST request to specified url

    :return True of the POST was successfull, False on errors
    """
    try:
        r = requests.post(url, json=body, headers=headers)
        r.raise_for_status()
        return True
    except (RequestException, HTTPError, ConnectionError, Timeout) as e:
        print("error POSTing to '%s': %s" % (url, e))

    return False


def dispatch_event(device, topic, payload, timestamp):
    dev = Device.get(device)
    subs = dev.subscriptions
    for sub in subs:
        for subTopic in sub.topics:
            if subTopic.topic == topic:
                send_event(device, topic, sub.restEndpoint, timestamp, payload)
            time.sleep(RETRY_COOLDOWN)


def init_channel():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters("localhost"))
    channel = connection.channel()
    channel.queue_declare(queue=EVENTS_QUEUE)

    return channel


def parse_body(body):
    # TODO: check that body is a valid event json,
    # e.g. handle errors:
    # - can't parse json
    # - keys are missing
    # handle by writing a warning and dropping the event
    ed = json.loads(body.decode("utf-8"))
    return ed["device"], ed["topic"], ed.get("payload"), ed["timestamp"]


def sender_thread(events_queue):
    while True:
        data = events_queue.get()
        dispatch_event(*data)


def main():
    events_queue = Queue(maxsize=0)
    channel = init_channel()

    t = threading.Thread(target=sender_thread, args=(events_queue,))
    t.start()

    for msg in channel.consume(EVENTS_QUEUE, inactivity_timeout=400):
        if msg is None:
            do_maintenance()
            continue
        method, properties, body = msg
        data = parse_body(body)
        events_queue.put(data)
        channel.basic_ack(method.delivery_tag)


if __name__ == "__main__":
    main()
