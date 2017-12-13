#!/usr/bin/env python
import pika
import json
import time
from hapi.dbmodels import Device
import requests
import threading
from queue import Queue

EVENTS_QUEUE = "events"
queue = Queue(maxsize=0)


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
        "timestamp": epoch2iso(timestamp),
    }

    if payload is not None:
        request_body["description"] = payload

    headers = {}
    for header in restEndpoint.httpheaders:
        headers[header.name] = header.value
    for _ in range(3):
        if reSend_event(restEndpoint.url, request_body, headers):
            break


def reSend_event(url, request_body, headers):
    """
    Send event or resend it if there is an error
    """
    try:
        r = requests.post(url, json=request_body, headers=headers)
        r.raise_for_status()
        print(r)
        return True
    except requests.exceptions.RequestException as err:
        print("OOps: Something Else", err)
    except requests.exceptions.HTTPError as errh:
        print("Http Error:", errh)
    except requests.exceptions.ConnectionError as errc:
        print("Error Connecting:", errc)
    except requests.exceptions.Timeout as errt:
        print("Timeout Error:", errt)
    return False


def dispatch_event(device, topic, payload, timestamp):
    dev = Device.get(device)
    subs = dev.subscriptions
    for sub in subs:
        for subTopic in sub.topics:
            if subTopic.topic == topic:
                print("send event: device %s, topic %s" % (device, topic))
                send_event(device, topic, sub.restEndpoint, timestamp, payload)


def init_channel():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters("localhost"))
    channel = connection.channel()
    channel.queue_declare(queue=EVENTS_QUEUE)

    return channel


def parse_body(body):
    ed = json.loads(body.decode("utf-8"))
    return ed["device"], ed["topic"], ed.get("payload"), ed["timestamp"]


def sender_thread(events_queue):
    while True:
        data = events_queue.get()
        print("sender thread %s", data)
        dispatch_event(*data)


def main():
    channel = init_channel()
    data = []

    t = threading.Thread(target=sender_thread, args=(queue, ))
    t.start()

    for msg in channel.consume(EVENTS_QUEUE, inactivity_timeout=400):
        if msg is None:
            do_maintenance()
            continue
        method, properties, body = msg
        data = parse_body(body)
        print("main thread %s", data)
        queue.put(data)
        channel.basic_ack(method.delivery_tag)


if __name__ == "__main__":
    main()
