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
class WebsiteTasks(TaskSet):

	@task
	def vod_stress(self):
		if 1 in entry_type_dict.values():	
			enn = random.choice([entry_id for entry_id, entry_type in entry_type_dict.items() if entry_type != 7])
			self.client.get(random.choice(entry_segments_dict[enn]))
        
	@task
	def live_stress(self):
		if 7 in entry_type_dict.values():	
			enn = random.choice([entry_id for entry_id, entry_type in entry_type_dict.items() if entry_type == 7])
			self.client.get(random.choice(entry_segments_dict[enn]))


class WebsiteUser(HttpLocust):
	task_set = WebsiteTasks
	min_wait = 5000
	max_wait = 15000

def start_session():
	""" Use configuration to generate KS
	"""
	# should add session cache
	ks = client.session.start(secret, userId, ktype, partnerId, expiry, privileges)
	client.setKs(ks)


def check_entry_types(entry_id):
	""" Checks entry ids and returns a dictionary with {id: type}
	"""
	entry_dict = {}
	filter = KalturaBaseEntryFilter()
	filter.idIn = entry_id
	filter.StatusIn = "READY"
	
	result = client.baseEntry.list(filter)	
	
	for object in result.objects:
		if int(object.type.value) == 7 :
			if int(object.liveStatus.value) == 1 :
				entry_dict[object.id] = int(object.type.value)
			else:
				print("%s is not streaming" % object.id)
		else:
			entry_dict[object.id] = int(object.type.value)

	return entry_dict
	
def get_vod_segments(entry_id):
	""" Retrieves segments from entry's flavors and adds to list. Returns nothing.
	"""
	vod_segments_list = []
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
	return vod_segments_list


def get_live_m3u8(entry_id):
	version = None
	result = client.baseEntry.get(entry_id, version)	
	
	for object in result.liveStreamConfigurations:
		if object.getProtocol().value == "applehttp":
			return object.url


def get_live_segments(entry_id):
	""" Returns list of live segments.
	"""	
	live_segments_list = []
	live_entry_m3u8_ans = requests.get(get_live_m3u8(entry_id))

	# Should check that the request returned OK
	
	for line in live_entry_m3u8_ans.text.splitlines():
		if not line.startswith('#'):
			base_url = line.split("?")[0] + "?"
			for line in requests.get(line).text.splitlines():
				if not line.startswith('#'):
					for line in requests.get(base_url + line).text.splitlines():
						if not line.startswith('#'):
							live_segments_list.append(base_url + line)
	return live_segments_list

def update_live(update_live_stop):
	""" Updates live segments every 60 seconds.
	"""
	print("Updating live segments...")
	update_live_segments_dict(entry_type_dict)
	if not update_live_stop.is_set():
        	# call update_live() again in 30 seconds
        	threading.Timer(60, update_live, [update_live_stop]).start()

#def create_segments_dict(entry_type_dict):
#	entry_segments_dict = {}
#	for entry_id,entry_type in entry_type_dict.items():
#		if entry_type != 7:
#			entry_segments_dict[entry_id] = get_vod_segments(entry_id)
#		else:
#			entry_segments_dict[entry_id] = get_live_segments(entry_id)
#	
#	return entry_segments_dict

def update_vod_segments_dict(entry_type_dict):
	for entry_id,entry_type in entry_type_dict.items():
		if entry_type != 7:
			entry_segments_dict[entry_id] = get_vod_segments(entry_id)
	

def update_live_segments_dict(entry_type_dict):
	for entry_id,entry_type in entry_type_dict.items():
		if entry_type == 7:
			entry_segments_dict[entry_id] = get_live_segments(entry_id)
	



# Run!
start_session()

global entry_type_dict
global entry_segments_dict
entry_segments_dict = {}

entry_type_dict = check_entry_types(entry_id)

entry_segments_dict = {}
update_vod_segments_dict(entry_type_dict)

#update_live_segments_dict(entry_type_dict)
update_live_stop = threading.Event()
update_live(update_live_stop)

