import time
import unittest
from tests import settings
from bravado.exception import HTTPNotFound
from .utils import Client, SubscriptionMakerMixin


def renew_subscription(subscriptionID):
    r = Client.device.post_device_serialNo_events_subscriptions_subscriptionID(
        serialNo=settings.TEST_DEVICE,
        subscriptionID=subscriptionID,
        subscription=dict(duration=10)
    ).result()

    return r


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
        renew_subscription(self.subscriptionID)


class TestSubscriptionExpiration(SubscriptionMakerMixin, unittest.TestCase):
    DURATION = 1

    def setUp(self):
        self.make_subscription(duration=self.DURATION)

    def test_expired(self):
        # give it an extra second to remove subscription
        time.sleep(self.DURATION + 1)

        with self.assertRaises(HTTPNotFound):
            renew_subscription(self.subscriptionID)
