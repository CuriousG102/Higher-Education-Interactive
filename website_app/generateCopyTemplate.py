import os

from sunlight import openstates
import sunlight
import xlsxwriter

import settings

sunlight.config.API_KEY = settings.API_KEY

def generateCopyTemplate(file_destination):
    bill_fields = "id,bill_id,title,scraped_subjects"
    bills = []
    pageNo = 1
    while True:
        billsToAdd = openstates.bills(state="tx", search_window="session",
                                      fields=bill_fields, page=pageNo)
        if len(billsToAdd) == 0:
            break

        bills.extend(billsToAdd)
        pageNo += 1
    billsToCopySheet = []

    for bill in bills:
        if 'scraped_subjects' in bill:
            for subject in bill['scraped_subjects']:
                if 'Education--Higher' in subject:
                    billsToCopySheet.append(bill)


    if (not os.path.exists(file_destination)) and (not file_destination == ''):
        os.makedirs(file_destination)

    workbook = xlsxwriter.Workbook(os.path.join(file_destination, 'copysheet.xlsx'))
    bills_sheet = workbook.add_worksheet('Bills')
    bills_sheet.write_row(0, 0, ['key', 'Bill Summary', 'Bill ID', 'title'])

    for i in xrange(1, len(billsToCopySheet) + 1):
        bill = billsToCopySheet[i - 1]
        rowToAdd = [bill['id'], '', bill['bill_id'], bill['title']]
        bills_sheet.write_row(i, 0, rowToAdd)

    leg_fields = 'full_name,leg_id'
    legislators = openstates.legislators(state="tx", active=True, 
                                         chamber='upper',
                                         fields=leg_fields)
    legislators.extend(openstates.legislators(state="tx", active=True, 
                                              chamber='lower',
                                              fields=leg_fields))

    leg_sheet = workbook.add_worksheet('Legislators')
    leg_sheet.write_row(0, 0, ['key', 'Higher Education', 'Name'])

    for i in xrange(1, len(legislators) + 1):
        legislator = legislators[i - 1]
        rowToAdd = [legislator['leg_id'], '', legislator['full_name']]
        leg_sheet.write_row(i, 0, rowToAdd)
    workbook.close()

if __name__ == '__main__': generateCopyTemplate('')

    





