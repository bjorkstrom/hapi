#!/usr/bin/env python

import json
import pika
import sys

EVENTS_QUEUE = "events"

EVENTS = dict(
    online="Device/Online",
    heartbeat="Device/Heartbeat",
    offline="Device/Offline",
)


def bail_out(msg):
    print(msg)
    sys.exit(0)


def usage():
    msg = "usage:"
    for ev in EVENTS:
        msg += "\n  %s <device serial #> %s" % (sys.argv[0], ev)
    return msg


def send_event(device, event_name):
    ed = dict(device=device,
              topic=EVENTS[event_name])

    connection = pika.BlockingConnection(
        pika.ConnectionParameters("localhost"))
    channel = connection.channel()
    channel.queue_declare(queue=EVENTS_QUEUE)
    channel.basic_publish(exchange='',
                          routing_key=EVENTS_QUEUE,
                          body=json.dumps(ed))

    connection.close()


if len(sys.argv) < 3:
    bail_out(usage())

device, event_name = sys.argv[1:3]

if event_name not in EVENTS:
    bail_out("unknown event '%s', I know about %s" %
             (event_name, ", ".join(EVENTS)))

send_event(device, event_name)
