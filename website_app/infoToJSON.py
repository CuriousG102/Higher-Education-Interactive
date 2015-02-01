import json
import os
import io

from sunlight import openstates
import sunlight

import settings

sunlight.config.API_KEY = settings.API_KEY

def produceBillJSONFiles(files_destination):
    bill_fields = "bill_id,title,alternate_titles,action_dates,actions,chamber,\
    updated_at,id,scraped_subjects,type,versions,votes"

    # bills = openstates.bills(state="tx", search_window="session",
    #                          fields=bill_fields)
    bills = []
    pageNo = 1

    while True:
        billsToAdd = openstates.bills(state="tx", search_window="session",
                                      fields=bill_fields, page=pageNo)
        if len(billsToAdd) == 0:
            break

        bills.extend(billsToAdd)
        pageNo += 1

    if not os.path.exists(files_destination):
        os.makedirs(files_destination)

    for bill in bills:
        for subject in bill['scraped_subjects']:
            if 'Education--Higher' in subject:
                filePath = os.path.join(files_destination, bill['id'] + '.json')
                with io.open(filePath, mode='w', encoding='utf8') as f:
                    jsonDump = json.dumps(obj=bill, 
                                          ensure_ascii=False, 
                                          separators=(',',':'))
                    f.write(jsonDump)
                break



def produceEnhancedDistrictJSONString(geoJSONString, chamber_string):
    leg_fields = "full_name,district,offices,party,roles,leg_id,photo_url"
    legislators = openstates.legislators(state="tx", active=True, 
                                         chamber=chamber_string,
                                         fields=leg_fields)
    legislator_id_set={}

    for legislator in legislators:
        legislator_id_set[legislator['leg_id']] = legislator
        legislator['higher_ed_bills'] = {'primary':[], 'cosponsor':[]}


    bill_fields = "id,sponsors,scraped_subjects"
    bills = openstates.bills(state="tx", search_window="session", 
                             fields=bill_fields)
    for bill in bills:
        for subject in bill['scraped_subjects']:
            if 'Education--Higher' in subject:
                addSponsorsToSet(legislator_id_set, bill)
                break

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
            legislator['higher_ed_bills'][sponsor_type].append(bill['id'])
