from math import ceil

class Bucket:
    """
    A leaky bucket structure for rate limiting.

    Attributes
    ----------
    max_count : int
        The size of the bucket
    leak_rate : float
        The rate at which the bucket empties (in 1/s)
    drain_period : int
        The time in seconds after which the bucket should be empty

    Methods
    -------
    userCount()
        Get the number of users in the set.
    currentSizeForUser(user, time)
        Get the current bucket state for a user.
    userCanSyncAmount(user, amount, time)
        Check if a user can sync an amount of contacts and update the state.
    cleanUsers(time)
        Remove the state for all users with empty buckets.
    clear()
        Remove all data from the set.
    """

    def userCount(self):
        """ Get the number of users in the set. """
        return len(self._users)

    def __init__(self, max_count : int, drain_period : int):
        """
        Create a new bucket.

        Parameters
        ----------
        max_count : int
            The size of the bucket
        drain_period : int
            The time in seconds after which the bucket should be empty
        """
        self._users = dict()
        self.leak_rate = float(max_count) / float(drain_period)
        self.max_count = max_count
        self.drain_period = float(drain_period)

    def currentSizeForUser(self, user, time : float):
        """
        Get the current bucket state for a user.

        Parameters
        ----------
        user : bytes
            The identifier of the user
        time : float
            The current time in seconds since epoch

        Returns
        -------
        int
            The current bucket state of the user (between 0 and 'max_count')
        """
        timestamp = self._users.get(user)
        if timestamp is None:
            return 0
        if timestamp < time:
            return self.max_count
        return int(ceil((timestamp - time) * self.leak_rate))

    def userCanSyncAmount(self, user, amount : int, time : float):
        """
        Check if a user can sync an amount of contacts and update the state.

        Parameters
        ----------
        user : bytes
            The id of the user
        amount : int
            The number of contacts that the user wants to sync
        time : float
            The current time in seconds since epoch

        Returns
        -------
        bool
            True, if the sync is allowed.
        """
        # Request larger than the maximum allowed count always fail
        if amount > self.max_count:
            return False
        # Get the point in time when the bucket for the user will be empty
        timestamp = self._users.get(user)
        # If the user has no bucket yet, then sync is allowed
        if timestamp is None:
            # Calculate new point in time when bucket will be empty
            self._users[user] = time + amount / self.leak_rate
            return True
        # If bucket is already empty, then sync is allowed
        if timestamp < time:
            # Calculate new point in time when bucket will be empty
            self._users[user] = time + amount / self.leak_rate
            return True
        # Calculate new point in time when bucket would be empty
        timestamp += amount / self.leak_rate
        # If time is further than 'drain_period' in the future, bucket size would be exceeded
        if timestamp > time + self.drain_period:
            return False
        # Set new timestamp before actual sync is done
        self._users[user] = timestamp
        # Allow sync
        return True

    def cleanUsers(self, time : float):
        """
        Remove the state for all users with empty buckets.

        Parameters
        ----------
        time : float
            The current time in seconds since epoch.
        """
        self._users = {k: v for k, v in self._users.items() if v > time }

    def clear(self):
        """ Remove all data from the set. """
        self._users.clear()
