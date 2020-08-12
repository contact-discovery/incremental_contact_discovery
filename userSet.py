
class UserSet:
    """
    A set of users with their authentication tokens.

    Methods
    -------
    userCount()
        Get the number of users in the set.
    userExists(user):
        Check if a user exists in the set.
    addUser(user, auth_token)
        Add a user to the set.
    removeUser(user):
        Remove a user from the set.
    isValidUser(user, auth_token):
        Check if the authentication token of a user is valid.
    clear()
        Remove all users from the set.
    """

    def __init__(self):
        """ Create a new user set. """
        self._users = dict()

    def userCount(self):
        """ Get the number of users in the set. """
        return len(self._users)

    def userExists(self, user):
        """
        Check if a user exists in the set.

        Parameters
        ----------
        user : bytes
            The identifier of the user

        Returns
        -------
        bool
            True, if the user exists
        """
        return self._users.get(user) is not None

    def addUser(self, user, auth_token):
        """
        Add a user to the set.

        Parameters
        ----------
        user : bytes
            The identifier of the user
        """
        self._users[user] = auth_token

    def removeUser(self, user):
        """
        Remove a user from the set.

        Parameters
        ----------
        user : bytes
            The identifier of the user
        """
        if user not in self._users:
            return
        del self._users[user]

    def isValidUser(self, user, auth_token):
        """
        Check if the authentication token of a user is valid.

        Parameters
        ----------
        user : bytes
            The identifier of the user
        auth_token : bytes
            The authentication token of the user

        Returns
        -------
        bool
            True, if the user and auth_token are valid
        """
        storedToken = self._users.get(user)
        if storedToken is None:
            return False
        return storedToken == auth_token

    def containedUsers(self, users):
        """
        Check which users are contained in the set.

        Parameters
        ----------
        users : list
            The identifiers of the users to check

        Returns
        -------
        list
            The identifiers of the users which where found in the set.
        """
        return [x for x in users if x in self._users]

    def clear(self):
        """ Remove all users from the set. """
        self._users.clear()


class ExpiringUserSet:
    """
    A set of users where the users are removed after an expiration time.

    Attributes
    ----------
    expiration_time : int
        The time after which users are removed from the set

    Methods
    -------
    userCount()
        Get the number of users in the set.
    userExists(user):
        Check if a user exists in the set.
    addUser(identifier, time)
        Add a user to the set.
    removeUser(identifier)
        Remove a user from the set.
    containedUsers(identifiers):
        Check which users are contained in the set.
    update(time)
        Update the set to remove users whose times have elapsed.
    clear()
        Remove all users from the set.
    """

    def __init__(self, expiration_time : int):
        """
        Create a new user set.

        Parameters
        ----------
        expiration_time : int
            The time interval after which users should be removed from the set.
        """
        self._users = dict()
        self.expiration_time = expiration_time

    def userCount(self):
        """ Get the number of users in the set. """
        return len(self._users)

    def userExists(self, user):
        """
        Check if a user exists in the set.

        Parameters
        ----------
        user : bytes
            The identifier of the user

        Returns
        -------
        bool
            True, if the user exists
        """
        return self._users.get(user) is not None

    def addUser(self, user, time : int):
        """
        Add a user to the set.

        Parameters
        ----------
        user : bytes
            The identifier of the user
        time : int
            The current time in seconds since epoch
        """
        removal_time = time + self.expiration_time
        self._users[user] = removal_time

    def removeUser(self, user):
        """
        Remove a user from the set.

        Parameters
        ----------
        identifier : bytes
            The identifier of the user
        """
        if user not in self._users:
            return
        del self._users[user]

    def containedUsers(self, users):
        """
        Check which users are contained in the set.

        Parameters
        ----------
        users : list
            The identifiers of the users to check

        Returns
        -------
        list
            The identifiers of the users which where found in the set.
        """
        return [x for x in users if x in self._users]

    def update(self, time : int):
        """
        Update the set to remove users whose times have elapsed.

        Parameters
        ----------
        time : int
            The current time in seconds since epoch

        Returns
        -------
        int
            The number of removed items
        """
        filtered = dict()
        for k, v in self._users.items():
            if v > time:
                filtered[k] = v
        removed = len(self._users) - len(filtered)
        self._users = filtered
        return removed

    def clear(self):
        """ Remove all users from the set. """
        self._users.clear()
