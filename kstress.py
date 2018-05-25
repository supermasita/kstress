from locust import HttpLocust, TaskSet, task
from KalturaClient import *
from KalturaClient.Plugins.Core import *
import requests
import random
from config import *

segment_list = []


def startsession():
	""" Use configuration to generate KS
	"""
	ks = client.session.start(secret, userId, ktype, partnerId, expiry, privileges)
	client.setKs(ks)

def getentries():
	""" List entries - Returns strings - Requires a KS generated for the client
	"""
	startsession()

	filter = KalturaAssetFilter()
	filter.entryIdEqual = entry_id
	pager = None
	
	result = client.flavorAsset.list(filter, pager)

	for flavor in result.objects: 
		m3u8_url = ("https://cfvod.kaltura.com/fhls/p/%i/sp/%i/serveFlavor/entryId/%s/v/11/flavorId/%s/name/a.mp4/index.m3u8" % (partnerId, partnerId, entry_id, flavor.id))

		m3u8 = requests.get(m3u8_url)

		for line in m3u8.text.splitlines():
			if not line.startswith('#'):
				segment_list.append(line.replace('https://', '/kVOD/'))



class WebsiteTasks(TaskSet):
	def on_start(self):
		getentries()
    
	@task
	def segment_a(self):
		self.client.get(random.choice(segment_list))
        

class WebsiteUser(HttpLocust):
	task_set = WebsiteTasks
	min_wait = 5000
	max_wait = 15000
