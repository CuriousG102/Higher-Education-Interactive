import json

from sunlight import openstates
import sunlight

import settings

sunlight.config.API_KEY = settings.API_KEY

def produceEnhancedDistrictJSONString(geoJSONString, chamber_string):
    leg_fields = "full_name,district,offices,party,roles,leg_id,photo_url"
    legislators = openstates.legislators(state="tx", active=True, 
                                         chamber=chamber_string,
                                         fields=leg_fields)
    legislator_id_set={}

    for legislator in legislators:
        legislator_id_set[legislator['leg_id']] = legislator


    bill_fields = "id,sponsors,scraped_subjects"
    bills = openstates.bills(state="tx", search_window="session", 
                             fields=bill_fields)
    for bill in bills:
        for subject in bill['scraped_subjects']:
            if 'Education--Higher' in subject:
                addSponsorsToSet(legislator_id_set, bill)

    decoder = json.JSONDecoder()
    geoJSON = decoder.decode(geoJSONString)
    chamberName = ''
    if (chamber_string == 'upper'): 
        chamberName = 'senate'
    else:
        chamberName = 'house'
    districts = geoJSON['objects'][chamberName]['geometries']
    legislator_district_set = {}
    for legislator in legislators:
        legislator_district_set[int(legislator['district'])] = legislator
    for district in districts:
        if int(district['id']) in legislator_district_set:
            district['properties'] = {}
            district['properties']['legislator'] = legislator_district_set[int(district['id'])]

    return json.dumps(obj=geoJSON, ensure_ascii=False, separators=(',',':'))


def addSponsorsToSet(legislator_id_set, bill):
    for sponsor in bill['sponsors']:
        if sponsor['leg_id'] in legislator_id_set:
            sponsor_type = sponsor['type']
            legislator = legislator_id_set[sponsor['leg_id']]
            if not 'higher_ed_bills' in legislator:
                legislator['higher_ed_bills'] = {}
                legislator['higher_ed_bills'][sponsor_type] = [bill['id']]
            else:
                if not sponsor_type in legislator['higher_ed_bills']:
                    legislator['higher_ed_bills'][sponsor_type] = [bill['id']]
                else:
                    legislator['higher_ed_bills'][sponsor_type].append(bill['id'])
