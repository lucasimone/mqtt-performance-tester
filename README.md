# MQTT Performance Tester
![Title](images/topology.png)


This projects contains a set of Python scripts used to test the performance of MQTT over SAT links.
It basically publish several messages with different payload size to a specific MQTT
broker that is host on the other side of a Satellite network.
We used OpenSAND to simulate the SAT link and Mosquitto as MQTT Broker implementation.



## Getting Started

There are several information required to start this test.
These are stored (at the moment) in the init file of the module.
Here the list:

* Payload size: from 128 to 1280 bytes are general used values
* QoS: Quality of Service used by Mosquitto (1 or 2)
* Topic: where the message will be publish
* Host: this is the real location where the publish wil be sent
* Interface: this is the interface to sniff MQTT & TCP traffic.

## Prerequisites

* A linux based OS
* Python (2.x or 3.x)
* [Moqsquitto](https://mosquitto.org/)
* [TSHARK](https://www.wireshark.org/docs/man-pages/tshark.html)
* [TCPDUMP](http://www.tcpdump.org/)


Since I had some issues installing Mosquitto on OsX  I put this useful link:
[how to install-mqtt-server](https://simplifiedthinking.co.uk/2015/10/03/install-mqtt-server/)

## Installing

```bash
clone https://github.com/lucasimone/mqtt-performance-tester.git
cd mqtt-performance-tester
pip install -r requirements.txt
```



## Running the test

To execute the performance tests use this script

```bash
sudo ./start_test.sh.sh
```

or use the python syntax as follow:

```bash
python -m tester
```

If you don't have a configuration file in the cfg folder the default one will be automatically generated.
Logs of the test will be stored int he Log folder.



## Authors

* [Luca Lamorte](mailto:luca.lamorte@gmail.com) - Initial work - [M2M SAT Project](https://artes.esa.int/projects/m2msat)

See also the list of [contributors](contributors.md) who participated in this project.


## Acknowledgments

## MIT License
Copyright (c) 2017, Luca Lamorte
All rights reserved.
