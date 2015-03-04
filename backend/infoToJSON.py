import json
import os
import io
import sys

from sunlight import openstates
import sunlight
import copytext

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

    addToBills(bills)

    if not os.path.exists(files_destination):
        os.makedirs(files_destination)

    for bill in bills:
        try:
            for subject in bill['scraped_subjects']:
                if 'Education--Higher' in subject:
                    filePath = os.path.join(files_destination, bill['id'] + '.json')
                    with io.open(filePath, mode='w', encoding='utf8') as f:
                        jsonDump = json.dumps(obj=bill, 
                                              ensure_ascii=False, 
                                              separators=(',',':'))
                        f.write(jsonDump)
                    break
        except KeyError:
            print 'ERROR KeyError ' + str(bill)


def addToBills(bills):
    addToObjects(bills, settings.file_path, 'Bills')

def addToLegislators(legislators):
    addToObjects(legislators, settings.file_path, 'Legislators')

def addToObjects(objects, filePath, sheetName): # this is an semi-abstract function so I am explaining it with comments
    object_id_set = {} # e.g. a set of legislators with their keys being their openstate ids
    for _object in objects:
        object_id_set[_object['id']] = _object
    copy = copytext.Copy(filePath) # get our copysheet and instantiate a copytext Copy of it
    sheet = copy[sheetName] # get the correct sheetName e.g. 'Legislators'
    dict = sheet.dict() 
    keySet = set() # make a keyset so that we can add each key to all our legislators so D3 isn't angry
    for entry in dict: # e.g. for each legislator i.d. in 'Legislators'
        if entry in object_id_set: # if that i.d. is in our legislator_id_set
            _object = object_id_set[entry] # get the legislator
            for key in dict[entry]: # for every key value we have to add for the legislator, e.g. 'Higher Education'
                _object[key] = dict[entry][key].unescape() # add that key to our legislator with its associated value
                keySet.add(key)
    for _object in objects:
        for key in keySet:
            if not key in _object:
                _object[key] = '' # for each key that we've added to one of our legislators, if another legislator doesn't have it add the key and just give it an empty string





def produceEnhancedDistrictJSONString(geoJSONString, chamber_string):
    leg_fields = "full_name,district,offices,party,roles,leg_id,photo_url"
    legislators = openstates.legislators(state="tx", active=True, 
                                         chamber=chamber_string,
                                         fields=leg_fields)
    legislator_id_set={}

    for legislator in legislators:
        legislator_id_set[legislator['leg_id']] = legislator
        legislator['higher_ed_bills'] = {'primary':[], 'cosponsor':[]}
        legislator['photo_url'] = 'images/' + legislator['photo_url'].split('images/')[1]


    bill_fields = "id,sponsors,scraped_subjects"
    bills = openstates.bills(state="tx", search_window="session", 
                             fields=bill_fields)
    for bill in bills:
        try:
            for subject in bill['scraped_subjects']:
                if 'Education--Higher' in subject:
                    addSponsorsToSet(legislator_id_set, bill)
                    break
        except KeyError:
            print 'ERROR KeyError ' + str(bill)

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

    addToLegislators(legislators)

    return json.dumps(obj=geoJSON, ensure_ascii=False, separators=(',',':'))


def addSponsorsToSet(legislator_id_set, bill):
    for sponsor in bill['sponsors']:
        if sponsor['leg_id'] in legislator_id_set:
            sponsor_type = sponsor['type']
            legislator = legislator_id_set[sponsor['leg_id']]
            legislator['higher_ed_bills'][sponsor_type].append(bill['id'])
