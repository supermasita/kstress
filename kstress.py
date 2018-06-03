from locust import HttpLocust, TaskSet, task
from KalturaClient import *
from KalturaClient.Plugins.Core import *
import requests
import random
from config import *
import threading

# Client config
config = KalturaConfiguration(partnerId)
config.serviceUrl = serviceUrl 
client = KalturaClient(config)
ktype = KalturaSessionType.ADMIN
secret = admin_secret
userId = None
expiry = 86400
privileges = "disableentitlement"

#
vod_segments_list = []
live_segments_list = []

# 

def start_session():
	""" Use configuration to generate KS
	"""
	# should add session cache
	ks = client.session.start(secret, userId, ktype, partnerId, expiry, privileges)
	client.setKs(ks)


def get_live(entry_id):
	version = None
	result = client.baseEntry.get(entry_id, version)	
	
	try:
		for object in result.liveStreamConfigurations:
			if object.getProtocol().value == "applehttp": 
				return object.url
	except:
		return False


def get_vod_segments(entry_id):
	""" Retrieves segments from entry's flavors and adds to list - Returns nothing
	"""
	filter = KalturaAssetFilter()
	filter.entryIdIn = entry_id
	pager = None
	result = client.flavorAsset.list(filter, pager)
	for flavor in result.objects: 
		m3u8_url = ("https://cfvod.kaltura.com/fhls/p/%i/sp/%i/serveFlavor/entryId/%s/v/11/flavorId/%s/name/a.mp4/index.m3u8" % (partnerId, partnerId, entry_id, flavor.id))
		m3u8 = requests.get(m3u8_url)
		# Todo: handle request error
		for line in m3u8.text.splitlines():
			if not line.startswith('#'):
				vod_segments_list.append(line.replace('https://', '/kVOD/'))


def get_live_segments(live_entry_m3u8):
	
	tmp_list = []
	live_entry_m3u8_ans = requests.get(live_entry_m3u8)

	# Should check that the request returned OK
	

	for line in live_entry_m3u8_ans.text.splitlines():
		if not line.startswith('#'):
			base_url = line.split("?")[0] + "?"
			for line in requests.get(line).text.splitlines():
				if not line.startswith('#'):
					for line in requests.get(base_url + line).text.splitlines():
						if not line.startswith('#'):
							tmp_list.append(base_url + line)
	return tmp_list

def create_live_segments_list(tmp_list):
	live_segments_list = tmp_list[:]


# Called for every user simulated
class WebsiteTasks(TaskSet):

	@task
	def vod_stress(self):
		if is_live is not True:
			self.client.get(random.choice(vod_segments_list))
        
	@task
	def live_stress(self):
		if is_live is True:
			self.client.get(random.choice(live_segments_list))
	

class WebsiteUser(HttpLocust):
	task_set = WebsiteTasks
	min_wait = 5000
	max_wait = 15000

# 		
start_session()

def f(f_stop):
	create_live_segments_list(get_live_segments(live_entry_m3u8))
	#print(live_segments_list[-1])
	#print(len(live_segments_list))
	# do something here ...
	if not f_stop.is_set():
        	# call f() again in 60 seconds
        	threading.Timer(30, f, [f_stop]).start()


if get_live(entry_id):
	print("Testing Live")
	is_live = True
	live_entry_m3u8 = get_live(entry_id)
	f_stop = threading.Event()
	# start calling f now and every 60 sec thereafter
	f(f_stop)
	#get_live_segments(live_entry_m3u8)
	#print(live_segments_list)
else:
	print("Testing VOD")
	get_vod_segments(entry_id)
