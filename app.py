from flask import Flask, request, make_response # Handle requests
from time  import time # Time measurements
from os import urandom # Randomness for user creation

import Messages_pb2 # Import the protocol buffer definitions

# Import the bucket and user set classes
from userSet import UserSet, ExpiringUserSet
from bucket import Bucket
from errors import ICDError, AuthenticationError, RateLimitError, MissingDataError, InvalidDataError

# MARK: Configuration

# The amount of time (in seconds) until S2 buckets are empty
s2_period = 86400

# The time interval for which contacts remain in set S2 (in seconds)
s2_delta = 864000

# The maximum amount of contacts for each user
# This number will specify the leak rate as follows:
# S1 will allow 'max_contacts' checks every 's2_delta' seconds
# S2 will allow 'max_contacts' checks every 's2_period' seconds
max_contacts = 20000

# MARK: Variables

# Set S1: All registered users
# The keys are the identifiers of all registered users
# The values are their authentication tokens
s1 = UserSet()

# Set S2: All users registered in the last 's2_delta' seconds.
# The keys are the user identifiers
# The values are the time when they should be removed from the set
s2_added = ExpiringUserSet(expiration_time=s2_delta)

# Set S2: All users unregistered in the last 's2_delta' seconds.
# The keys are the user identifiers
# The values are the time when they should be removed from the set
s2_removed = ExpiringUserSet(expiration_time=s2_delta)


# S1 buckets: The bucket values for all registered users when doing a full sync
# The keys are the user identifiers, the values are the timestamps when the
# bucket will be empty.
# Storing the state like this requires only 1 data point for each user,
# and also allows fast calculations.
# However, it requires the values to be updated in case the bucket parameters
# are changed during runtime.
s1_buckets = Bucket(max_contacts, drain_period=s2_delta)

# S2 buckets: The bucket values for all registered users when doing an incremental sync
# The keys are the user identifiers, the values are the timestamps when the
# bucket will be empty.
# Storing the state like this requires only 1 data point for each user,
# but requires a bit more calculation when checking the buckets.
# However, it requires the values to be updated in case the bucket parameters
# are changed during runtime.
s2_buckets = Bucket(max_contacts, drain_period=s2_period)

# The flask application to facilitate contact discovery
application = Flask(__name__)


# MARK: Responses

# Create an error to send for a full sync request
def _makeErrorResponse(error : ICDError):
    """
    Convert an error into response to sent to the client

    Parameters
    ----------
    error: ICDError
        An error thrown during execution.

    Returns
    -------
    response_class
        The response for the client
    """
    response = Messages_pb2.Response()
    response.result = error.result
    serialized = response.SerializeToString()
    data = make_response(serialized)
    return data

# Create a new response with the discovery result
def _makeResponse(added = [], removed = []):
    """
    Convert added and removed users into a response.

    Parameters
    ----------
    added: array(bytes)
        The users added since the last synchronization
    removed: array(bytes)
        The users removed since the last synchronization

    Returns
    -------
    response_class
        The response for the client
    """
    response = Messages_pb2.Response()
    response.result = Messages_pb2.Result.SUCCESS
    response.added_users.extend(added)
    response.removed_users.extend(removed)
    serialized = response.SerializeToString()
    data = make_response(serialized)
    return data


# MARK: Authentication

def _getDataFromRequest():
    """
    Extract user, auth_token and identifiers from the request.

    Returns
    ----------
    tuple
        User identifier, authentication token, identifiers

    Exceptions
    ----------
    MissingDataError
        The request contains no body data
    InvalidDataError
        The received body data is not a valid protobuf object
    """
    # Extract the data from the request, which should be a serialized ICD_Request
    data = request.get_data()
    if data is None:
        raise MissingDataError()

    # Try to create the protobuf object
    received_request = Messages_pb2.Request()
    try:
        received_request.ParseFromString(data)
    except:
        raise InvalidDataError()
    return received_request.user, received_request.auth_token, received_request.identifiers

def _checkAuthentication():
    """
    Check the received request and authenticate the user.

    Returns
    ----------
    tuple
        The user identifier and a list of contact identifiers

    Exceptions
    ----------
    MissingDataError
        The request contains no body data
    InvalidDataError
        The received body data is not a valid protobuf object
    AuthenticationError
        The user identifier or authentication token is invalid
    """
    user, auth_token, identifiers = _getDataFromRequest()
    # Check that the user exists, and that the authentication is valid
    if not s1.isValidUser(user, auth_token):
        raise AuthenticationError()
    return user, identifiers

def _checkAuthenticationAndExtractIdentifiers():
    """
    Check the received request, authenticate the user, and extract the identifiers.

    Returns
    -------
    tuple
        The user and the list of identifiers provided by the user

    Exceptions
    ----------
    MissingDataError
        The request contains no body data
    InvalidDataError
        The received body data is not a valid protobuf object
    AuthenticationError
        The user identifier or authentication token is invalid
    RateLimitError
        The user has exceeded his capacity to sync
    """
    user, identifiers = _checkAuthentication()

    if len(identifiers) > max_contacts:
        raise RateLimitError()
    return user, identifiers


# MARK: User management

def _time():
    """
    The current time in seconds.

    Returns
    -------
    int
        The time since epoch in seconds
    """
    return int(time())

def addNewUser(user, auth_token):
    """
    Register a new user.

    Parameters
    ----------
    user: bytes
        The users identifier
    auth_token: bytes
        The authentication token of the user
    """
    # Add to S1
    s1.addUser(user, auth_token)
    # Add to the set of added users
    # The value is the time when the user should be removed from the set
    s2_added.addUser(user, _time())
    # Remove from unregistered users, just in case the user was recently deleted
    s2_removed.removeUser(user)

def removeUser(user):
    """
    Remove a registered user.

    Parameters
    ----------
    user: bytes
        The users identifier
    """
    # Remove the user from the full set
    s1.removeUser(user)
    # Remove from new users, just in case the user was recently added
    s2_added.removeUser(user)
    # Add the user to the set of unregistered users
    # The value is the time when the user should be removed from the set
    s2_removed.addUser(user, _time())

# MARK: Set updates

def _updateUserSets():
    """ Remove expired users from S_2 """
    currentTime = _time()
    removedFromAdded = s2_added.update(currentTime)
    removedFromRemoved = s2_removed.update(currentTime)

# MARK: Request entry points

def _catchRequestErrors(callback):
    # Update all sets to the current time
    _updateUserSets()
    try:
        return callback()
    except ICDError as e:
        return _makeErrorResponse(e)

# Initiates a full sync with S1.
@application.route("/discovery/full", methods=['POST'])
def fullDiscovery():
    return _catchRequestErrors(_fullDiscoveryWithErrors)

def _fullDiscoveryWithErrors():
    """
    Perform a full sync with S1.

    Returns
    -------
    bytes
        The data to sent to the client containing the response to the request

    Exceptions
    ----------
    AuthenticationError
        The user identifier or authentication token is invalid
    RateLimitError
        The user has exceeded his capacity to sync
    MissingDataError
        The request contains no body data
    InvalidDataError
        The received body data is not a valid protobuf object
    """
    # Extract data, check authentication, and get identifiers
    user, identifiers = _checkAuthenticationAndExtractIdentifiers()
    if len(identifiers) == 0:
        return _makeResponse()

    # Check the rate limit
    if not s1_buckets.userCanSyncAmount(user, amount=len(identifiers), time=time()):
        raise RateLimitError()

    # Now do the actual discovery
    found = s1.containedUsers(identifiers)
    return _makeResponse(found)

# Initiates an incremental sync with S2.
@application.route("/discovery/incremental", methods=['POST'])
def incrementalDiscovery():
    """
    Perform an incremental sync with S2.

    The request must be a POST request, with a valid protobuf object
    'Messages_pb2.Request' as the body data.

    The user must be registered.
    """
    return _catchRequestErrors(_incrementalDiscoveryWithErrors)

def _incrementalDiscoveryWithErrors():
    """
    Perform an incremental sync with S2.

    Returns
    -------
    response_class
        The data to sent to the client containing the response to the request

    Exceptions
    ----------
    AuthenticationError
        The user identifier or authentication token is invalid
    RateLimitError
        The user has exceeded his capacity to sync
    MissingDataError
        The request contains no body data
    InvalidDataError
        The received body data is not a valid protobuf object
    """
    # Extract data, check authentication, and get identifiers
    user, identifiers = _checkAuthenticationAndExtractIdentifiers()
    if len(identifiers) == 0:
        return _makeResponse()

    # Check the rate limit
    if not s2_buckets.userCanSyncAmount(user, amount=len(identifiers), time=time()):
        raise RateLimitError()

    # Now do the actual discovery
    addedUsers = s2_added.containedUsers(identifiers)
    removedUsers = s2_removed.containedUsers(identifiers)
    return _makeResponse(addedUsers, removedUsers)

@application.route("/user/register", methods=['POST'])
def registerUser():
    """
    Register a new user.

    The request must be a POST request, with a valid protobuf object
    'Messages_pb2.Request' as the body data (containing a user name and an auth_token)
    """
    return _catchRequestErrors(_registerUserWithErrors)

def _registerUserWithErrors():
    user, auth_token, _ = _getDataFromRequest()
    addNewUser(user, auth_token)
    return _makeResponse()

@application.route("/user/delete", methods=['POST'])
def deleteUser():
    """
    Delete a registered user.

    The request must be a POST request, with a valid protobuf object
    'Messages_pb2.Request' as the body data (containing a valid user name and auth_token)
    """
    return _catchRequestErrors(_deleteUserWithErrors)

def _deleteUserWithErrors():
    user, _ = _checkAuthentication()
    removeUser(user)
    return _makeResponse()


# MARK: Test functions

@application.route("/reset", methods=['GET'])
def resetServer():
    s1_buckets.clear()
    s2_buckets.clear()
    s1.clear()
    s2_added.clear()
    s2_removed.clear()
    return "Success"

@application.route("/test/create/<int:number>", methods=['GET'])
def createUsers(number):
    if number > 10000000:
        print("{:d} is too many users to create".format(number))
        return "Too many"
    print("Creating {:d} users...".format(number))
    for i in range(number):
        user = urandom(16)
        token = urandom(16)
        addNewUser(user, token)
    return "Success"

@application.route("/test/add/many", methods=['POST'])
def addUsers():
    _, _, ids = _getDataFromRequest()
    for id in ids:
        token = urandom(16)
        addNewUser(id, token)
    return _makeResponse()


# MARK: Application start

print("Incremental discovery service is ready...")
print("Maximum contacts: {:d}".format(max_contacts))
print("Full sync: {:d} contacts per {:d} seconds ({:.3f} contacts/s)".format(max_contacts, s2_delta, s1_buckets.leak_rate))
print("Incremental sync: {:d} contacts per day ({:.3f} contacts/s)".format(max_contacts, s2_buckets.leak_rate))

if __name__ == "__main__":
    application.run()
