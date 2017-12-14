import json
import time
import unittest

from dateutil import parser
from hapi.event import amqp
from tests.integration import restdest

from tests.validation import utils
from tests import settings


class TestSubscriptions(utils.SubscriptionMakerMixin, unittest.TestCase):
    URL_PATH = "/test"

    HEADER1 = "Test-Str"
    VALUE1 = "test-val2"

    HEADER2 = "Test-Num"
    VALUE2 = "24"

    def setUp(self):
        self.make_subscription(
                "http://localhost:8081%s" % self.URL_PATH,
                [
                    dict(name=self.HEADER1, value=self.VALUE1),
                    dict(name=self.HEADER2, value=self.VALUE2)],
                ["Device/Online", "Device/Offline"],
                10*60)

        self.events_dest = restdest.EventsRestDest()

    def tearDown(self):
        self.cancel_subscription()

    def assert_event_req(self, event_req, expected_topic):
        """
        assert that event request's have expected format and data

        event_req is a tuple of (path, headers, body) of the
        POST request that was made to deliver the event to the
        Rest Endpoint
        """
        path, headers, body = event_req

        # check request's PATH
        assert path == self.URL_PATH

        # check that our custom headers were included
        assert headers[self.HEADER1] == self.VALUE1
        assert headers[self.HEADER2] == self.VALUE2

        # check that post body is valid json
        event_desc = json.loads(body.decode("utf-8"))

        # check that correct device and topic are specified
        assert event_desc["device"] == settings.TEST_DEVICE
        assert event_desc["topic"] == expected_topic

        # check that timestamp is parsable and seems reasonable,
        # e.g. not in the future
        dt = parser.parse(event_desc["timestamp"])
        assert dt.timestamp() <= time.time()

    def test_event_delivery(self):
        """
        Check that delivering event to a RestEndpoint destination
        works
        """
        for sub_topic in ["Online", "Offline"]:
            ev = dict(device=settings.TEST_DEVICE,
                      topic="Device/%s" % sub_topic)
            amqp.send_event(ev)

        events = self.events_dest.get_recv_events(2)
        self.assert_event_req(events[0], "Device/Online")
        self.assert_event_req(events[1], "Device/Offline")
