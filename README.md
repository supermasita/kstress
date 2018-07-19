# kStress

kStress is a implementation of [Locust](https://locust.io/) to test [Kaltura's eCDN](https://corp.kaltura.com/products/kaltura-ecdn/) KES nodes.

#### Note:
This code is not created nor supported by Kaltura.

#### Features:
* Test multiple entries at the same time (VOD and LIVE)
* LIVE: mimic player behaviour when pulling new segments
* Easy configuration
* Locust will hit a KES based on the eCDN delivery rules, as normal user would do
  * Parent-child supported
  * "API gateway" not yet supported

#### Requirements:
* [Locust](https://locust.io/)
* [Kaltura's Python client library](http://www.kaltura.com/api_v3/testme/client-libs.php)
* A Kaltura eCDN license and at least one installed KES node

#### How to use (single server):
* Install Locust
* Install Kaltura's Python client library
* Clone this code
* Rename config.py.template to config.py and edit as needed (PID, secret, entries)
* Run Locust, specifying the file: 
```
$ locust -f kstress.py 
```
* Connect to Locust WebUI (ex: http://127.0.0.1:8089) and start stressing!

#### How to use (multi server):
* On all servers:
  * Install Locust 
  * Install Kaltura's Python client library
  * Clone this code 
  * Rename config.py.template to config.py and edit as needed (PID, secret, entries)
* On master server:
  * Run Locust, specifying the file and master: 
```
$ locust -f kstress.py --master
```
* On slave servers:
  * Run Locust, specifying the file and master: 
```
$ locust -f kstress.py --master-host={IP_OF_THE_MASTER_SERVER}
```
* Connect to Locust WebUI on master (ex: http://127.0.0.1:8089) and start stressing!

#### Screenshots:

![screenshot01](https://imgur.com/oJOsn8w.jpg)
![screenshot02](https://imgur.com/cD0Cpcz.jpg)
![screenshot03](https://imgur.com/jss7tB9.jpg)
![screenshot04](https://imgur.com/Wh927fh.jpg)
![screenshot05](https://imgur.com/eFS1gah.jpg)

