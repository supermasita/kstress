from locust import HttpLocust, TaskSet, task
from KalturaClient import *
from KalturaClient.Plugins.Core import *
import requests
import random
import time
from config import *
import re

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
			entry = random.choice([entry_id for entry_id, entry_type in entry_type_dict.items() if entry_type != 7])
			for segment in get_vod_segments(entry):
				self.client.get(segment)
        
	@task
	def live_stress(self):
		if 7 in entry_type_dict.values():	
			entry = random.choice([entry_id for entry_id, entry_type in entry_type_dict.items() if entry_type == 7])
			seq_last_prev = 0
			while True:
				segments = get_live_segments(entry)
				seq_last = int(re.search('seg-.*\.ts',segments[-1]).group(0).split("-")[1])
				# Compare the last segment to see if there are any new ones
				if seq_last > seq_last_prev:
					for segment in segments:
						seq = int(re.search('seg-.*\.ts',segment).group(0).split("-")[1])
						# Avoid already requested segments
						if seq > seq_last_prev:
							self.client.get(segment)
							seq_last_prev = seq
				else:
					# No new segments? Wait.
					time.sleep(6)

class WebsiteUser(HttpLocust):
	task_set = WebsiteTasks
	min_wait = 1000
	max_wait = 5000

def start_session():
	""" Use configuration to generate KS.
	"""
	# should I add session cache ?
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
	""" Returns live m3u8 (string).
	"""
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



# Run!
print("Starting session...")
start_session()

print("Checking entry types...")
global entry_type_dict
entry_type_dict = check_entry_types(entry_id)


