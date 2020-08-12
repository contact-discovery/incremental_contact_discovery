import unittest


from os import urandom
from random import sample, shuffle
from time import sleep, time

from client import Client


def _newID():
    return urandom(16)

class TestSystem(unittest.TestCase):

    def setUp(self):
        client = Client()
        self.assertTrue(client.reset())

    def test_register_user(self):
        client = Client()

        self.assertTrue(client.register())

    def test_register_many(self):
        for i in range(100):
            client = Client()
            self.assertTrue(client.register())

    def test_unregister_user(self):
        client = Client()

        self.assertTrue(client.register())
        self.assertTrue(client.unregister())

    def test_full_sync_empty(self):
        client = Client()
        self.assertTrue(client.register())

        ids = [_newID() for x in range(10000) ]
        result = client.fullDiscovery(ids)
        self.assertFalse(result is None)
        self.assertEqual(len(result), 0)

    def test_full_sync_existing(self):
        client = Client()
        self.assertTrue(client.register())

        others = [_newID() for x in range(1000) ]
        self.assertTrue(client.addMany(others))

        for i in range(20):
            s = sample(others, 100)
            missing = [_newID() for x in range(900) ]
            all = s + missing
            shuffle(all)
            result = client.fullDiscovery(all)
            self.assertTrue(result)
            self.assertEqual(len(result), 100)

            a = set(s)
            b = set(result)
            self.assertEqual(len(a - b), 0)
            self.assertEqual(len(b - a), 0)

    def test_full_sync_limit(self):
        client = Client()
        self.assertTrue(client.register())
        ids = [_newID() for x in range(1000) ]
        for i in range(20):
            result = client.fullDiscovery(ids)
            self.assertFalse(result is None)
            self.assertEqual(len(result), 0)

        result = client.fullDiscovery(ids, expectError=True)
        self.assertTrue(result is None)

    def test_inc_sync_empty(self):
        client = Client()
        self.assertTrue(client.register())

        ids = [_newID() for x in range(10000) ]
        result = client.incrementalDiscovery(ids)
        self.assertFalse(result is None)
        self.assertEqual(len(result), 2)
        self.assertEqual(len(result[0]), 0)
        self.assertEqual(len(result[1]), 0)

    def test_inc_sync_existing(self):
        client = Client()
        self.assertTrue(client.register())

        existing = [_newID() for x in range(20000) ]
        self.assertTrue(client.addMany(existing))

        deleted = list()
        for i in range(200):
            other = Client()
            self.assertTrue(other.register())
            self.assertTrue(other.unregister())
            deleted.append(other.user)

        for i in range(20):
            e = sample(existing, 100)
            d = sample(deleted, 100)
            missing = [_newID() for x in range(800) ]
            all = e + d + missing
            shuffle(all)
            result = client.incrementalDiscovery(all)
            self.assertFalse(result[0] is None)
            self.assertFalse(result[1] is None)
            self.assertEqual(len(result[0]), 100)
            self.assertEqual(len(result[1]), 100)
            self.assertEqual(set(result[0]), set(e))
            self.assertEqual(set(result[1]), set(d))

    def test_inc_and_full(self):
        client = Client()
        self.assertTrue(client.register())

        ids = [_newID() for x in range(20000) ]
        result = client.incrementalDiscovery(ids)
        self.assertFalse(result is None)

        result = client.fullDiscovery(ids)
        self.assertFalse(result is None)

    def test_inc_leak_rate(self):
        client = Client()
        self.assertTrue(client.register())

        ids = [_newID() for x in range(20000) ]
        result = client.incrementalDiscovery(ids)
        self.assertFalse(result is None)

        ids = [_newID()]
        result = client.incrementalDiscovery(ids, expectError=True)
        self.assertTrue(result[0] is None)

        sleep(5)

        result = client.incrementalDiscovery(ids)
        self.assertFalse(result[0] is None)

    def test_full_leak_rate(self):
        client = Client()
        self.assertTrue(client.register())

        ids = [_newID() for x in range(20000) ]
        result = client.fullDiscovery(ids)
        self.assertFalse(result is None)

        ids = [_newID()]
        result = client.fullDiscovery(ids, expectError=True)
        self.assertTrue(result is None)

        sleep(5)

        result = client.incrementalDiscovery(ids)
        self.assertFalse(result is None)

    def test_create_millions_of_users(self):
        client = Client()
        self.assertTrue(client.createMany(10000000))

    def test_many_syncs(self):
        clients = [Client() for x in range(20)]
        for client in clients:
            self.assertTrue(client.register())

        ids = [_newID() for x in range(20000) ]
        self.assertTrue(client.addMany(ids))

        # Test with almost empty server
        start = time()
        for i in range(10):
            result = clients[i].fullDiscovery(ids)
            self.assertFalse(result is None)
        elapsed_time = (time() - start) / 10
        print("0 users, {:d} contacts: {:.3f} s".format(len(ids),elapsed_time))

        # Add users to reach 20M
        self.assertTrue(client.createMany(9999980))
        self.assertTrue(client.createMany(9980000))

        start = time()
        for i in range(10):
            result = clients[i+10].fullDiscovery(ids)
            self.assertFalse(result is None)
        elapsed_time = (time() - start) / 10
        print("20M users, {:d} contacts: {:.3f} s".format(len(ids),elapsed_time))

if __name__ == '__main__':
    unittest.main()
