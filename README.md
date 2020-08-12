# Incremental Contact Discovery

This repository contains sample code to implement a rate-limiting scheme for contact discovery which aims to significantly improve the protection against enumeration attacks, while not impacting legitimate users negatively.

## Motivation

When services such as the Signal messenger implement contact discovery, their aim is to provide the users with the ability to easily discover which of their contacts are also registered with the service. At the same time, the service wants to prevent malicious users from reading out the entire list of registered users by enumerating over possible phone numbers.

## Main idea

Current contact discovery schemes always match with the entire server database for every request, allowing an attacker to extract a lot of information very efficiently. Normal clients however can remember the result of their last sync, and thus only need to regularly check for changes. By allowing clients to sync once with the full database, and perform subsequent syncs only with the set of users which registered with the service in a given teimframe, the service can enforce stricter rate limits for the full set.

Thus, clients can perform two different syncs: A full sync, which returns all contacts currently registered with the server, and an incremental sync, which returns the added and removed users of the last 10 days. The former set has strict rate limits, i.e. 20000 contacts in 10 days, while the latter can be queried more often (20000 contacts per day). Clients are expected to only perform a full sync after they have been offline for more than 10 days.

## Assumptions

The aim of this scheme is to provide a reasonable trade-off between usability and protection of the server database given the following assumptions:

- The server should not store the users contacts
- The set of registered users changes slowly
- The contact set of legitimate clients changes slowly
- The client can keep track of the past state of his contacts

## Implementation

This repository contains a simple Python implementation to show how such a system could be implemented. A simple flask server provides the contact discovery API, which clients can use to query for information.

The users in the system are identified by a byte string, which is often a hash of the phone number.

The communication between clients and the server is based on Google Protocol Buffers, which provide efficient and fast serialization of request data.

The current implementation requires `python3`

**This library is not only meant to showcase the rate-limiting feature, and is not production ready.**

## Parameters

*Incremental contact discovery* comes with three main parameters. These parameters can be set in the `app.py` file.

The maximum number of contacts for each client M:
````python
max_contacts = 20000
````

The time when the leaky bucket for the set `S_2` should be empty. This parameter
determines how often clients can sync with the set `S_2`, i.e. how often they can
check for changes to their contacts.
````python
s2_period = 86400 # In seconds (1 day)
````

The time when the leaky bucket for the set `S_1` should be empty.
This parameter determines how often clients can perform a full sync with the server,
and how long changes to `S_1` will remain in `S_2`.
The parameter should be calculated based on the expected rate of change of the server set `S_1`.
For more details, please refer to the paper.

````python
s2_delta = 864000 # In seconds (10 days)
````

## Installation

The flask server should run inside a virtual environment:

````bash
virtualenv venv -p python3
source venv/bin/activate
````

Inside the environment, install the necessary packages:
````bash
pip install flask requests protobuf
````

Run the test server:
````bash
flask run --port 5000
````

## Running the tests

The implementation comes with a set of tests, which ensure that every thing is working properly.

Run the tests of the buckets and user sets:
````bash
python testComponents.py
````

Run the system tests that interact with the test server (which must be running):
````bash
python -m unittest testSystem
````

Or run individual tests:
````bash
python -m unittest testSystem.TestSystem.test_inc_sync_existing
````

**Note** Some tests will create 20 million users, so run the tests only on suitable hardware,
or remove the test methods `test_create_millions_of_users` and `test_many_syncs` from `testSystem.py`
