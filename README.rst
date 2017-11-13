DataHubHel
==========

DataHubHel is an IoT platform for Helsinki.

.. warning::
    Work on progress. Come back in a few weeks or so.

The project consists of the following parts:

backend
    API backend powered by Django Rest Framework.

frontend
    React app for testing log-in flows and Thing/Service registration.


Development
-----------

Backend
~~~~~~~

First create a Python virtualenv::

    virtualenv -p python3.6 venv
    . venv/bin/activate

Then install the Python packages to the virtualenv::

    pip install prequ
    prequ sync backend/requirements*.txt

And create a PostgreSQL database::

    sudo -u postgres createuser -d -P datahubhel
    sudo -u postgres createdb -O datahubhel datahubhel
