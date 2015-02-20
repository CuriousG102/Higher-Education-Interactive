import sunlight
from sunlight import openstates

import os
import sys
import urllib2

import settings

sunlight.config.API_KEY = settings.API_KEY

def makeRepImagesLocal(folderPath):
	for chamber_string in ['upper', 'lower']:
		legislators = openstates.legislators(state="tx", active=True, 
	                                         chamber=chamber_string,
	                                         fields="photo_url")
		for legislator in legislators:
			# print legislator['photo_url'].split('images/')[1]
			with open(os.path.join(folderPath, 
								   legislator['photo_url'].split('images/')[1].replace('small', 'large')), 'wb') as f:
				try:
					page = urllib2.urlopen(legislator['photo_url'].replace('small', 'large'))
					content = page.read()
					page.close()
					f.write(content)
				except:
					print legislator['photo_url'].replace('small', 'large') + " ERROR " + str(sys.exc_info()[0])

if __name__ == "__main__":
	makeRepImagesLocal('../website_app/images/')