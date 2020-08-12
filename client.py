from os import urandom

import requests
import urllib3

import Messages_pb2

urllib3.disable_warnings()

class Client:
    """
    A simple client to facilitate contact discovery.

    Attributes
    ----------
    user : bytes
        The user identifier.
    auth_token : bytes
        The authentication token of the user.

    Methods
    -------
    register()
        Register the user with the server.
    unregister()
        Unregister the user from the server.
    fullDiscovery(contacts)
        Perform a full discovery.
    incrementalDiscovery(contacts)
        Perform an incremental discovery.
    """

    def __init__(self, user = None, server = "http://localhost:5000/"):
        """
        Create a new client.

        Parameters
        ----------
        user : bytes
            The user identifier. Passing None will create a random user.
        server : string
            The url of the server.
        """
        if user is None:
            self.user = urandom(16)
        else:
            self.user = user
        self.auth_token = urandom(16)
        self.server = server

    def _makeProtobuf(self):
        """ Create a protobuf object containing the user and the token. """
        protobuf = Messages_pb2.Request()
        protobuf.user = self.user
        protobuf.auth_token = self.auth_token
        return protobuf

    def _makeProtobufData(self):
        """ Create a serialized protobuf with the user info. """
        protobuf = self._makeProtobuf()
        return protobuf.SerializeToString()

    def _makeProtobufWithContacts(self, contacts):
        """ Create a serialized protobuf request with contacts. """
        protobuf = self._makeProtobuf()
        protobuf.identifiers.extend(contacts)
        return protobuf.SerializeToString()

    def _post(self, url, data, printError=True):
        """
        Initiate a post request to a sub-url.

        Parameters
        ----------
        url : string
            The sub-url to send the post request to.
        data: bytes
            The body data to include in the request.

        Returns
        -------
        Messages_pb2.Response
            The response from the server, or None if the request failed.
        """
        r = requests.post(self.server + url, data=data, timeout=10)
        if r.status_code != 200:
            if printError:
                print("POST to {} failed with code {:d}".format(url, r.status_code))
            return None

        result = Messages_pb2.Response()
        result.ParseFromString(r.content)

        if result.result != Messages_pb2.Result.SUCCESS:
            if printError:
                print("POST to {} failed with status {}".format(url, result.result))
            return None
        return result

    def register(self):
        """ Register the user with the server. """
        post_data = self._makeProtobufData()

        if self._post("user/register", post_data) is not None:
            return True
        return False

    def unregister(self):
        """ Unregister the user from the server. """
        post_data = self._makeProtobufData()

        if self._post("user/delete", post_data) is not None:
            return True
        return False

    def fullDiscovery(self, contacts, expectError=False):
        """
        Perform a full discovery.

        Parameters
        ----------
        contacts: list
            The identifiers of the users to check.

        Returns
        -------
        list or None
            The list of the found users or None if the request failed.
        """
        post_data = self._makeProtobufWithContacts(contacts)

        result = self._post("discovery/full", post_data, printError= not expectError)
        if result is None:
            return None
        return result.added_users

    def incrementalDiscovery(self, contacts, expectError=False):
        """
        Perform an incremental discovery.

        Parameters
        ----------
        contacts: list
            The identifiers of the users to check.

        Returns
        -------
        (list, list) or (None, None)
            The lists of the new and removed users or (None, None) if the request failed.
        """
        post_data = self._makeProtobufWithContacts(contacts)

        result = self._post("discovery/incremental", post_data, printError= not expectError)
        if result is None:
            return None, None
        return result.added_users, result.removed_users

    def reset(self):
        """ Reset the test server and delete all data. """
        r = requests.get(self.server + "reset")
        return r.status_code == 200

    def createMany(self, number : int):
        url = self.server + "test/create/{:d}".format(number)
        r = requests.get(url)
        return r.status_code == 200

    def addMany(self, contacts):
        post_data = self._makeProtobufWithContacts(contacts)
        result = self._post("test/add/many", post_data)
        return result is not None
