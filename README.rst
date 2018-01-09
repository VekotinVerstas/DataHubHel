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

docker
    Docker containers for running a SensorThings Server and a MQTT Broker.

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

SensortThings Server and MQTT Broker
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The SensorThings Server (STS) and the Mosquitto MQTT Broker can be run using Docker::

    cd docker
    docker-compose up

The command will create two docker images "sts" and "mqttbroker" and run containers using them.

The STS is configured to expose it's HTTP SensorThings API (running on Tomcat) on local port 8080 and the STS's own MQTT broker on port 11883. The STS is also configured to connect to a PostgreSQL server in the host machine. (db: sensorthings, username: sensorthings, password: sensorthings) The database tables can be created by visiting ``http://localhost:8080/SensorThingsService/DatabaseStatus``.

The mosquitto service is configured to expose itselft on local port 1883. It's also configured to bridge the STS's MQTT Broker. The mosquitto will query authentication and authorization from the local datahubhel backend on port 8000.
