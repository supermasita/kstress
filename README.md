# kStress

kStress is a implementation of [Locust](https://locust.io/) to test [Kaltura's eCDN](https://corp.kaltura.com/products/kaltura-ecdn/) KES nodes.

#### Note:
This code is not created nor supported by Kaltura.

#### Features:
* Test multiple entries at the same time (VOD and LIVE)
* LIVE: mimic player behaviour when pulling new segments
* Easy configuration
* Coming soon: Support parent-child KES

#### Requirements:
* [Locust](https://locust.io/)
* [Kaltura's Python client library](http://www.kaltura.com/api_v3/testme/client-libs.php)
* A Kaltura eCDN license and at least one installed KES node

#### How to use:
* Install Locust
* Install Kaltura's Python client library
* Clone this code
* Rename config.py.template to config.py and edit as needed (PID, secret, entries)
* Run Locust, specifying the target server (IP or FQDN):
```
$ locust -f kstress.py --host http://192.168.0.102/
```
* Connect to Locust WebUI (ex: http://127.0.0.1:8089) and start stressing!

#### Screenshots:

![screenshot01](https://imgur.com/oJOsn8w.jpg)
![screenshot02](https://imgur.com/cD0Cpcz.jpg)
![screenshot03](https://imgur.com/jss7tB9.jpg)
![screenshot04](https://imgur.com/Wh927fh.jpg)
![screenshot05](https://imgur.com/eFS1gah.jpg)

