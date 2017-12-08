#!/usr/bin/env python

import json
import pika
import sys
import time

EVENTS_QUEUE = "events"

EVENTS = dict(
    online="Device/Online",
    heartbeat="Device/Heartbeat",
    offline="Device/Offline",
    error="Device/Error",
    inst_created="ModelInstance/Created",
    inst_modified="ModelInstance/Modified",
    inst_removed="ModelInstance/Removed",
)


def timestamp():
    epoch_time = time.time()
    return epoch_time


def generate_payload(event_name):
    if event_name in ["online", "heartbeat", "offline"]:
        return None

    if event_name == "error":
        return dict(errorCode=123,
                    errorMessage="flux capacitor malfunction")

    if event_name == "inst_created":
        return dict(modelID="234", modelInstanceID="53",
                    hidden=False)

    if event_name == "inst_modified":
        return dict(modelInstanceID="53", hidden=True)

    if event_name == "inst_removed":
        return dict(modelInstanceID="72")


def generate_event_json(device, event_name):
    ed = dict(device=device,
              timestamp=timestamp(),
              topic=EVENTS[event_name])

    payload = generate_payload(event_name)
    if payload is not None:
        ed["payload"] = payload

    return json.dumps(ed)


def bail_out(msg):
    print(msg)
    sys.exit(0)


def usage():
    msg = "usage:"
    for ev in EVENTS:
        msg += "\n  %s <device serial #> %s" % (sys.argv[0], ev)
    return msg


def send_event(device, event_name):
    body = generate_event_json(device, event_name)

    connection = pika.BlockingConnection(
        pika.ConnectionParameters("localhost"))
    channel = connection.channel()
    channel.queue_declare(queue=EVENTS_QUEUE)
    channel.basic_publish(exchange='',
                          routing_key=EVENTS_QUEUE,
                          body=body)

    connection.close()


if len(sys.argv) < 3:
    bail_out(usage())

device, event_name = sys.argv[1:3]

if event_name not in EVENTS:
    bail_out("unknown event '%s', I know about %s" %
             (event_name, ", ".join(EVENTS)))

send_event(device, event_name)
