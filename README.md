# cwxDataCollector

## Synopsis

 Data collector service for the cwx sensors to send data.  Written in python, using sqlite3 and cherrypy.

## How to run:

 Simply run the server.  Either make executable with chmod, or use python:

 python server.py

 That's it.  At this point, whatever machine you started it on should open port 8080, and start listening
 for connections.  You can set the sensor nodes to use "http://your-ip:8080" as their server string, and they
 should ping the server pointed to by your-ip


## How to test:

 You can test the data server by using the curl command line utility, like this:

```
curl 'http://127.0.0.1/keep?sensor=testSensor&data=42&sensorType=vcc'
```