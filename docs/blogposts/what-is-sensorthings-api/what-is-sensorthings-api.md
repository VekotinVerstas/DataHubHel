# What is SensorThings API

When working in the IoT space, especially when working with devices from several manufacturers, one might quickly notice the vast selectionof APIs that need to be used to integrate with several systems. While this is true when handling web services or implementing cross-platform applications as well, IoT-systems can quickly grow to include products from tens of differentmanufacturers in a short amount of time. Handling multiple different datamodels, syntaxes, and protocols can be cumbersome. Also, storing sensory dataand metadata in an easily accessible way is not an easy task. Those are the main problems the SensorThings API is designed  to solve. Giving us an [Open GeospatialConsortium (OGC)](https://en.wikipedia.org/wiki/Open_Geospatial_Consortium) standardized solution to unify the way we handle and structure our IoT data as well as specifying an API for how to do so.

## How it works

Opening the SensorThings API specifications might be a bit daunting and scary in the beginning since it is an enormous document describing all the ins and outs of the API. However, after understanding the basic principles of the entities one can quite easily get a general idea of the framework.

There are two main parts to the Sensor Things API, sensing entities and the API interface. While the specification defines the interface and the create-update-delete functionality separately, from here on out they together will be referred to as the REST API.



### Entities

![entities](media/entities.png)



Entities are the data models of SensorThings API, they dictate how data can be stored and linked to each other. 

| Entity                                                       | Description                                                  |
| ------------------------------------------------------------ | ------------------------------------------------------------ |
| [`Thing`](http://docs.opengeospatial.org/is/15-078r6/15-078r6.html#25) | A physical or virtual object. Example: a car, a person, a computer or headphones |
| [`Location`](http://docs.opengeospatial.org/is/15-078r6/15-078r6.html#26) | Location of a `Thing`.  Can be used to store the coordinates of a `Thing`. At the time of writing [GeoJSON](http://geojson.org/) is the only supported encoding type for locations. |
| [`HistoricalLocation`](http://docs.opengeospatial.org/is/15-078r6/15-078r6.html#27) | A set of locations, including the current and previous `Location`s |
| [`Datastream`](http://docs.opengeospatial.org/is/15-078r6/15-078r6.html#28) | Groups a collection of `Observation`s  made by a `Sensor`. The datastream also stores metadata about the observations that are being made. For instance, datastreams can include which unit an observation has, i.e °C or Hg. It also links to the `ObservedPropery` of a `Sensor` . |
| [` Observation`](http://docs.opengeospatial.org/is/15-078r6/15-078r6.html#31) | A measurement or value of a property. Only holds the actual value, no type information. A description of the value is stored in an `ObservedPropery` and the unit of the measured value is stored in the `Datastream`. |
| [`ObservedProperty`](http://docs.opengeospatial.org/is/15-078r6/15-078r6.html#30) | Specifies the phenomenon of an `Observation` . Example: The temperature in an area or the stress of a person. |
| [`Sensor`](http://docs.opengeospatial.org/is/15-078r6/15-078r6.html#29) | An instrument that produces an estimated value of a property. Example: Temperature sensor, lux sensor, moisture sensor. |
| [`FeatureOfInterest`](http://docs.opengeospatial.org/is/15-078r6/15-078r6.html#32) | The feature of interest of an `Observation.` This can be the same as a `Location` for a `Thing`but could also be its own value. |

As the SensorThings API is a general framework for IoT it tries too keep everything as non-specific as possible and includes parts that can be used in several ways depending on how your project is structured. An example of this flexibility is the entities `Location` and `FeatureOfInterest`. Both can be used for adding location-like data to other entities. However, one is linked to a `Thing` and the other to an `Observation`. So, which one should be used? This can be a bit tricky to get a hang of at first, but one example could be a temperature sensor in a market square. The market square could be the `FeatureOfInterest` and could be stored as a polygon (multiple coordinate values connected to each other) that encompasses the market square, while the `Location` could be the exact location of the `Thing` that has a temperature `Sensor`.



### REST API

The SensorThings RESTFul API uses the HTTP methods and responses that many developers are already familiar with. As such, creating, fetching, updating and deleting entities is a breeze. However, the way URLs are structures differs somewhat from the`https://<domain>/<entityType>/<entityId>` pattern that is common in made REST APIs. Instead of using a slash (`/`) as a separator between type and id, parentheses are used, and slashes are only used when one wants to access sub-entity types. For instance, if a client wants to access a `Sensor` with the id 3 the URL `https://<domain>/Sensors(3)` would be used, and not `https://<domain>/Sensors/3` that many are familiar with. While at first this might seem weird, one quickly gets used to the pattern.

Where the API really shines however is when clients want to do more complex queries. There is a vast number of different queries that can be asked from the API. There are two main types of query extensions that can be made: returned property specifiers and query parameters. These are put after resource part (after `/Sensors` in the example above) of the URL and starts with the normal HTTP query separator `?` followed by a dollar-sign ($) to start a query. An ampersand (&) is used if several types of queries are combined. 

Return properties can be modified by using either `$expand` for expanding data from an entity relationship or by using `$select` which limits the returned value accordingly. An example of using these would be `https://<domain>/Datastreams(51)?$select=id,Sensor&$expand=Sensor`. This would return three things, the id of the `Datastream`, a hyperlink to the `Sensor` linked to the `Datastream`, and the entire `Sensor` object. The sensor object will have the same format as if it were fetched directly from the API as in the example before.

Query parameters include `$orderby`, `$top`, `$skip` ,`$count` and `$filter`. The three first are self-explanatory, and `$count` includes information about how many entities that the total dataset includes. The powerful part of the API however is `$filter`. It lets the client filter down the returned values in detail. Combined with its built-in filter operations, which lets the client use things like logical, comparison, arithmetic and grouping operators as well as string, date, math and spatial and geospatial functions, one can create highly complex queries straight from the API. As an example found in the specifications `http://<domain>/Things?$filter=geo.distance(Locations/location, geography’POINT(-122, 43)’) gt 1` returns `Thing`s where the distance between their last known locations and POINT(-122 43) is greater than 1.

All this flexibility in the API makes it easy to create complex queries without having to do a lot of heavy lifting on the client side. To SmartThings server implementers however, a lot of work is required to comply with all the standards features.



### Real time data using MQTT

Fetching data from via HTTP(S) from REST endpoints a powerful way to fetch large amounts of information in one go. However, many times getting information as soon as it arrives enables developers to create a much nicer experience for their users. Applications such as graphing and notification systems can be made with ease if information can be push to a client instead of the client needing to pull information from a server. SensorThings solves this by specifying a [MQTT extension](http://docs.opengeospatial.org/is/15-078r6/15-078r6.html#85) that can be added to SensorThings servers. 

[MQTT](http://mqtt.org/) is a publish/subscribe messaging protocol that works on top of the TCP/IP protocol. It was designed to require as little coding effort as well as less bandwidth to transmit data between a client and a broker.

SensorThings allows users to hook into `Datastream` and listen to its`Observations` as they come in using MQTT. While not having the same filter capabilities as the REST API, it still allows the client to get information much faster than using polling techniques.



## Get started with SensorThings

To get up and running with SensorThings you will need a service implementation. If you are not planning on building one yourself, there are several choices currently available. Both commercial and open-source solutions exist.

Taking the commercial route, there is [SensorUp](https://www.sensorup.com/), which provides a ready to go fully specification compliant cloud platform. Complete with training and support programs they also offer SensorThings SDKs for most major mobile platforms as well as charting SDKs and ready-made dashboards. SensorUp is ran by one of the editors of the SensorThings API specification, Steve Liang.

On the open-source side of things one has several choices, but only a few which both offer fully specification compliant solutions and are still active. The most complete solution is Fraunhofers [FROST server](https://github.com/FraunhoferIOSB/FROST-Server), which supports as much of the specifications as SensorUp does. It is written in Java and is easy to set up using Docker Compose. There is also Firefox’s [GOST server](https://www.gostserver.xyz/) implemented in Go which is not as feature complete as FROSTwhen it comes to the specifications but includes a nice dashboard and is as easy to set up.