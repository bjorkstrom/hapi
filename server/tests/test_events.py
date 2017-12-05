import unittest
from utils import Client, EventSubscription, EventFilter, RestEndpoint


class SubscriptionMakerMixin:
    def make_subscription(self):
        endpoint = RestEndpoint(
            URL="http://example.com/foo",
            method="POST",
            headers=[
                dict(name="header1", value="val1"),
                dict(name="header2", value="val2")]
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

        self.subscriptionID = res.subscriptionID

    def cancel_subscription(self):
        dev = Client.device
        dev.delete_device_serialNo_events_subscriptions_subscriptionID(
            serialNo="A0",
            subscriptionID=self.subscriptionID,
        ).result()


class TestSubscriptions(SubscriptionMakerMixin, unittest.TestCase):
    def setUp(self):
        self.make_subscription()

    def tearDown(self):
        self.cancel_subscription()

    def test_new_cancel(self):
        """
        test creating and canceling a subscription,

        the new subscription is created and canceled implicitly by
        the test case set-up and tear-down code
        """

        # smoke validate, check that subscriptionID is provided
        # and that it's not zero-length string
        self.assertGreater(len(self.subscriptionID), 0)

    def test_renew(self):
        Client.device.post_device_serialNo_events_subscriptions_subscriptionID(
            serialNo="A0",
            subscriptionID=self.subscriptionID,
            subscription=dict(duration=10)
        ).result()
