# kStress

kStress is a implementation of [Locust](https://locust.io/) to test [Kaltura's eCDN](https://corp.kaltura.com/products/kaltura-ecdn/) KES nodes.

#### Features:
* Test multiple entries at the same time (VOD and LIVE)
* LIVE: mimic player behaviour when pulling new segments
* Easy configuration
* Coming soon: Support parent-child KES

#### Requirements:
* [Locust](https://locust.io/)
* [Kaltura's Python client library](http://www.kaltura.com/api_v3/testme/client-libs.php)

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
