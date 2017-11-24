import unittest
from utils import Client, EventSubscription, EventFilter, RestEndpoint


class TestSubscriptions(unittest.TestCase):
    def test_new(self):
        endpoint = RestEndpoint(
            URL="http://example.com/foo",
            method="POST",
            headers=[dict(header1="val1"),
                     dict(header2="val2")]
        )
        subscription = EventSubscription(
            duration=10,
            eventFilters=[EventFilter(topic="topic1"),
                          EventFilter(topic="topic2")],
            destination={'restEndpoint': endpoint},
        )
        res = Client.device.post_device_serialNo_events_subscriptions_new(
            serialNo="A0",
            Subscription=subscription,

        ).result()

        # smoke validate, check that subscriptionID is provided
        # and that it's not zero-length string
        self.assertGreater(len(res.subscriptionID), 0)

    def test_renew(self):
        # TODO: create subscription before renewing
        Client.device.post_device_serialNo_events_subscriptions_subscriptionID(
            serialNo="A0",
            subscriptionID="XXX",
            subscription=dict(duration=10)
        ).result()

    def test_cancel(self):
        # TODO: create subscription before renewing
        Client.device.delete_device_serialNo_events_subscriptions_subscriptionID(
            serialNo="A0",
            subscriptionID="XXX",
        ).result()
