import unittest

from os import urandom
from random import sample, randrange, shuffle
from time import time

# Import the bucket and user set classes
from userSet import UserSet, ExpiringUserSet
from bucket import Bucket

def _randomBytes():
    return urandom(16)

def _randomUser():
    return _randomBytes(), _randomBytes()

def _seconds():
    return int(time())

class TestComponents(unittest.TestCase):

    # MARK: User set tests

    def test_user_set_add_remove(self):
        mySet = UserSet()

        user, token = _randomUser()
        self.assertFalse(mySet.isValidUser(user, token))
        self.assertEqual(mySet.userCount(), 0)

        mySet.addUser(user, token)
        self.assertTrue(mySet.userExists(user))
        self.assertTrue(mySet.isValidUser(user, token))
        self.assertEqual(mySet.userCount(), 1)

        mySet.removeUser(user)
        self.assertFalse(mySet.userExists(user))
        self.assertFalse(mySet.isValidUser(user, token))
        self.assertEqual(mySet.userCount(), 0)

    def test_user_set_remove_missing(self):
        mySet = UserSet()

        user, token = _randomUser()
        self.assertFalse(mySet.isValidUser(user, token))
        self.assertEqual(mySet.userCount(), 0)

        mySet.removeUser(user)
        self.assertFalse(mySet.isValidUser(user, token))
        self.assertEqual(mySet.userCount(), 0)

    def test_user_set_add_twice(self):
        mySet = UserSet()

        user, token = _randomUser()
        self.assertFalse(mySet.isValidUser(user, token))
        self.assertEqual(mySet.userCount(), 0)

        mySet.addUser(user, token)
        self.assertTrue(mySet.isValidUser(user, token))
        self.assertEqual(mySet.userCount(), 1)

        mySet.addUser(user, token)
        self.assertTrue(mySet.isValidUser(user, token))
        self.assertEqual(mySet.userCount(), 1)

    def test_user_set_invalid_token(self):
        mySet = UserSet()

        user, token = _randomUser()
        mySet.addUser(user, token)

        other = _randomBytes()
        self.assertTrue(mySet.isValidUser(user, token))
        self.assertFalse(mySet.isValidUser(user, other))

    def test_user_set_add_multiple(self):
        mySet = UserSet()

        user1, token1 = _randomUser()
        self.assertFalse(mySet.isValidUser(user1, token1))
        self.assertEqual(mySet.userCount(), 0)

        mySet.addUser(user1, token1)
        self.assertTrue(mySet.isValidUser(user1, token1))
        self.assertEqual(mySet.userCount(), 1)

        user2, token2 = _randomUser()
        self.assertFalse(mySet.isValidUser(user2, token2))

        mySet.addUser(user2, token2)
        self.assertTrue(mySet.isValidUser(user2, token2))
        self.assertEqual(mySet.userCount(), 2)

        user3, token3 = _randomUser()
        self.assertFalse(mySet.isValidUser(user3, token3))

        mySet.addUser(user3, token3)
        self.assertTrue(mySet.isValidUser(user3, token3))
        self.assertEqual(mySet.userCount(), 3)

        mySet.removeUser(user2)
        self.assertFalse(mySet.isValidUser(user2, token2))
        self.assertEqual(mySet.userCount(), 2)

        mySet.removeUser(user1)
        self.assertFalse(mySet.isValidUser(user1, token1))
        self.assertEqual(mySet.userCount(), 1)

        mySet.removeUser(user3)
        self.assertFalse(mySet.isValidUser(user3, token3))
        self.assertEqual(mySet.userCount(), 0)

    def test_user_set_intersection(self):
        mySet = UserSet()

        # Add 1000 users
        users = set()
        for i in range(1000):
            user, token = _randomUser()
            mySet.addUser(user, token)
            users.add(user)

        self.assertEqual(mySet.userCount(), 1000)

        # Create 1000 non-existing users
        other = [ _randomBytes() for x in range(1000) ]

        # Sample users and others 100 times
        for i in range(100):
            existingCount = randrange(1000)
            otherCount = randrange(1000)
            setA = sample(users, existingCount)
            setB = sample(other, otherCount)
            all = setA + setB
            shuffle(all)
            self.assertEqual(len(all), existingCount + otherCount)

            found = mySet.containedUsers(all)
            self.assertEqual(len(found), existingCount)
            a = set(setA)
            b = set(found)
            self.assertEqual(len(a - b), 0)
            self.assertEqual(len(b - a), 0)


    # MARK: Expiring set tests

    def test_exp_set_add_remove(self):
        mySet = ExpiringUserSet(expiration_time=86400)
        self.assertEqual(mySet.userCount(), 0)

        user = _randomBytes()
        mySet.addUser(user, 1234)
        self.assertEqual(mySet.userCount(), 1)

        mySet.removeUser(user)
        self.assertEqual(mySet.userCount(), 0)

    def test_exp_set_remove_missing(self):
        mySet = ExpiringUserSet(expiration_time=86400)
        self.assertEqual(mySet.userCount(), 0)

        user = _randomBytes()
        mySet.removeUser(user)
        self.assertEqual(mySet.userCount(), 0)

    def test_exp_set_add_twice(self):
        mySet = ExpiringUserSet(expiration_time=86400)
        self.assertEqual(mySet.userCount(), 0)

        user = _randomBytes()
        mySet.addUser(user, 1234)
        self.assertEqual(mySet.userCount(), 1)

        mySet.addUser(user, 1235)
        self.assertEqual(mySet.userCount(), 1)

    def test_exp_set_add_multiple(self):
        mySet = ExpiringUserSet(expiration_time=86400)
        self.assertEqual(mySet.userCount(), 0)

        user1 = _randomBytes()
        mySet.addUser(user1, 1234)
        self.assertEqual(mySet.userCount(), 1)

        user2 = _randomBytes()
        mySet.addUser(user2, 12345)
        self.assertEqual(mySet.userCount(), 2)

        user3 = _randomBytes()
        mySet.addUser(user3, 123456)
        self.assertEqual(mySet.userCount(), 3)

        mySet.removeUser(user2)
        self.assertEqual(mySet.userCount(), 2)

        mySet.removeUser(user1)
        self.assertEqual(mySet.userCount(), 1)

        mySet.removeUser(user3)
        self.assertEqual(mySet.userCount(), 0)

    def test_exp_set_update_set(self):
        mySet = ExpiringUserSet(expiration_time=86400)
        self.assertEqual(mySet.userCount(), 0)

        user1 = _randomBytes()
        mySet.addUser(user1, 1234)
        self.assertEqual(mySet.userCount(), 1)

        user2 = _randomBytes()
        mySet.addUser(user2, 12345)
        self.assertEqual(mySet.userCount(), 2)

        mySet.update(1235 + 86400)
        self.assertEqual(mySet.userCount(), 1)

        remaining = mySet.containedUsers([user1, user2])
        self.assertEqual(len(remaining), 1)
        self.assertEqual(remaining, [user1])

    def test_exp_set_intersection(self):
        mySet = ExpiringUserSet(expiration_time=86400)

        # Add 1000 users
        users = set()
        for i in range(1000):
            user = _randomBytes()
            mySet.addUser(user, randrange(86400))
            users.add(user)

        self.assertEqual(mySet.userCount(), 1000)

        # Create 1000 non-existing users
        other = [ _randomBytes() for x in range(1000) ]

        # Sample users and others 100 times
        for i in range(100):
            existingCount = randrange(1000)
            otherCount = randrange(1000)
            setA = sample(users, existingCount)
            setB = sample(other, otherCount)
            all = setA + setB
            shuffle(all)
            self.assertEqual(len(all), existingCount + otherCount)

            found = mySet.containedUsers(all)
            self.assertEqual(len(found), existingCount)
            a = set(setA)
            b = set(found)
            self.assertEqual(len(a - b), 0)
            self.assertEqual(len(b - a), 0)

    # MARK: Bucket tests

    def test_bucket_initial_sync(self):
        myBucket = Bucket(20000, drain_period=86400)

        user = _randomBytes()
        self.assertTrue(myBucket.userCanSyncAmount(user, 20000, 1234))

    def test_bucket_initial_too_large(self):
        myBucket = Bucket(20000, drain_period=86400)

        user = _randomBytes()
        self.assertFalse(myBucket.userCanSyncAmount(user, 20001, 1234))

    def test_bucket_sync_too_many(self):
        myBucket = Bucket(20000, drain_period=86400)

        user = _randomBytes()
        self.assertTrue(myBucket.userCanSyncAmount(user, 20000, 1234))
        self.assertFalse(myBucket.userCanSyncAmount(user, 20001, 100000))

    def test_bucket_sync_too_fast(self):
        myBucket = Bucket(20000, drain_period=86400)

        user = _randomBytes()
        self.assertTrue(myBucket.userCanSyncAmount(user, 10000, 1234))
        self.assertEqual(myBucket.currentSizeForUser(user, 1234), 10000)
        self.assertTrue(myBucket.userCanSyncAmount(user, 10000, 1235))
        self.assertFalse(myBucket.userCanSyncAmount(user, 10000, 1236))

    def text_bucket_drain(self):
        myBucket = Bucket(20000, drain_period=86400)

        user = _randomBytes()
        self.assertTrue(myBucket.userCanSyncAmount(user, 20000, 1234))
        self.assertEqual(myBucket.currentSizeForUser(user, 1234), 20000)
        self.assertEqual(myBucket.currentSizeForUser(user, 1234+21600), 5000)
        self.assertEqual(myBucket.currentSizeForUser(user, 1234+43200), 10000)
        self.assertEqual(myBucket.currentSizeForUser(user, 1234+64800), 15000)
        self.assertEqual(myBucket.currentSizeForUser(user, 1234+86400), 20000)

    def test_bucket_sync_multiple(self):
        myBucket = Bucket(20000, drain_period=86400)

        user1 = _randomBytes()
        user2 = _randomBytes()
        user3 = _randomBytes()

        self.assertTrue(myBucket.userCanSyncAmount(user1, 10000, 0))
        self.assertTrue(myBucket.userCanSyncAmount(user2, 15000, 0))
        self.assertTrue(myBucket.userCanSyncAmount(user3, 20000, 0))

        self.assertTrue(myBucket.userCanSyncAmount(user1, 10000, 1000))
        self.assertFalse(myBucket.userCanSyncAmount(user2, 15000, 10000))
        self.assertTrue(myBucket.userCanSyncAmount(user3, 20000, 100000))

        self.assertFalse(myBucket.userCanSyncAmount(user1, 10000, 10000))
        self.assertTrue(myBucket.userCanSyncAmount(user2, 1000, 20000))
        self.assertFalse(myBucket.userCanSyncAmount(user3, 20000, 110000))

    def test_bucket_clean(self):
        myBucket = Bucket(20000, drain_period=86400)

        user1 = _randomBytes()
        user2 = _randomBytes()
        user3 = _randomBytes()

        self.assertTrue(myBucket.userCanSyncAmount(user1, 10000, 0))
        self.assertTrue(myBucket.userCanSyncAmount(user2, 15000, 0))
        self.assertTrue(myBucket.userCanSyncAmount(user3, 20000, 0))

        myBucket.cleanUsers(50000)
        self.assertEqual(myBucket.userCount(), 2)
        self.assertTrue(myBucket.userCanSyncAmount(user1, 20000, 50000))
        self.assertFalse(myBucket.userCanSyncAmount(user2, 20000, 50000))
        self.assertFalse(myBucket.userCanSyncAmount(user3, 15000, 50000))


if __name__ == '__main__':
    unittest.main()
