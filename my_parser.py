
"""
FILE: skeleton_parser.py
------------------
Author: Firas Abuzaid (fabuzaid@stanford.edu)
Author: Perth Charernwattanagul (puch@stanford.edu)
Modified: 04/21/2014

Skeleton parser for CS564 programming project 1. Has useful imports and
functions for parsing, including:

1) Directory handling -- the parser takes a list of eBay json files
and opens each file inside of a loop. You just need to fill in the rest.
2) Dollar value conversions -- the json files store dollar value amounts in
a string like $3,453.23 -- we provide a function to convert it to a string
like XXXXX.xx.
3) Date/time conversions -- the json files store dates/ times in the form
Mon-DD-YY HH:MM:SS -- we wrote a function (transformDttm) that converts to the
for YYYY-MM-DD HH:MM:SS, which will sort chronologically in SQL.

Your job is to implement the parseJson function, which is invoked on each file by
the main function. We create the initial Python dictionary object of items for
you; the rest is up to you!
Happy parsing!
"""

import sys
from json import loads
from re import sub

columnSeparator = "|"

# Dictionary of months used for date transformation
MONTHS = {'Jan':'01','Feb':'02','Mar':'03','Apr':'04','May':'05','Jun':'06',\
        'Jul':'07','Aug':'08','Sep':'09','Oct':'10','Nov':'11','Dec':'12'}

"""
Returns true if a file ends in .json
"""
def isJson(f):
    return len(f) > 5 and f[-5:] == '.json'

"""
Converts month to a number, e.g. 'Dec' to '12'
"""
def transformMonth(mon):
    if mon in MONTHS:
        return MONTHS[mon]
    else:
        return mon

"""
Transforms a timestamp from Mon-DD-YY HH:MM:SS to YYYY-MM-DD HH:MM:SS
"""
def transformDttm(dttm):
    dttm = dttm.strip().split(' ')
    dt = dttm[0].split('-')
    date = '20' + dt[2] + '-'
    date += transformMonth(dt[0]) + '-' + dt[1]
    return date + ' ' + dttm[1]

"""
Transform a dollar value amount from a string like $3,453.23 to XXXXX.xx
"""

def transformDollar(money):
    if money == None or len(money) == 0:
        return money
    return sub(r'[^\d.]', '', money)

"""
Parses a single json file. Currently, there's a loop that iterates over each
item in the data set. Your job is to extend this functionality to create all
of the necessary SQL tables for your database.
"""
def parseJson(json_file):
    with open(json_file, 'r') as f:
        items = loads(f.read())['Items'] # creates a Python dictionary of Items for the supplied json file
        for item in items:
            """
            TODO: traverse the items dictionary to extract information from the
            given `json_file' and generate the necessary .dat files to generate
            the SQL tables based on your relation design
            """
            keys = ['ItemID','Name','Currently','Buy_Price','First_Bid',
                    'Number_of_Bids','Started','Ends','Seller','Description']
            values = []
            for key in keys:
                if key in item and item[key]:
                    value = item[key]
                else: 
                    value = 'NULL'
                if (key == 'Currently' or key == 'First_Bid' or 
                    key == 'Buy_Price' and value != 'NULL'):
                    value = transformDollar(value)
                if key == 'Started' or key == 'Ends' and value != 'NULL':
                    value = transformDttm(value)
                if key == 'Seller' and value != 'NULL':
                    value = value['UserID']
                values.append(value)
            with open("Item.dat",'a+') as item_file:
                item_file.write(columnSeparator.join(values)+"\n")

            with open("Category.dat",'a+') as category_file:
                if 'Category' in item and item['Category']:
                    for category in item['Category']:
                        category_file.write(columnSeparator.join(
                                            [item['ItemID'],category])+"\n")

            subkeys = ['UserID','Rating','Location','Country']
            with open("User.dat",'a+') as user_file:
                if 'Bids' in item and item['Bids']:
                    for bid in item['Bids']:
                        bid = bid['Bid']
                        if 'Bidder' in bid and bid['Bidder']:
                            bidder_values = []
                            bidder = bid['Bidder']
                            for key in subkeys:
                                if key in bidder and bidder[key]:
                                    bidder_values.append(bidder[key])
                                else:
                                    bidder_values.append('NULL')
                            user_file.write(columnSeparator.join(bidder_values)
                                            +"\n")
                seller_values = []
                if 'Seller' in item and item['Seller']:
                    seller = item['Seller']
                    if 'UserID' in seller and seller['UserID']:
                        seller_values.append(seller['UserID'])
                    else:
                        seller_values.append('NULL')
                    if 'Rating' in seller and seller['Rating']:
                        seller_values.append(seller['Rating'])
                    else:
                        seller_values.append('NULL')
                    if 'Location' in item and item['Location']:
                        seller_values.append(item['Location'])
                    else:
                        seller_values.append('NULL')
                    if 'Country' in item and item['Country']:
                        seller_values.append(item['Country'])
                    else:
                        seller_values.append('NULL')
                    user_file.write(columnSeparator.join(seller_values)+"\n")

            with open("Bid.dat",'a+') as bid_file:
                if 'Bids' in item and item['Bids']:
                    for bid in item['Bids']:
                        bid = bid['Bid']
                        bid_values = []
                        if 'ItemID' in item and item['ItemID']:
                            bid_values.append(item['ItemID'])
                        else:
                            bid_values.append('NULL')
                        if 'Bidder' in bid and bid['Bidder']:
                            bidder = bid['Bidder']
                            if 'UserID' in bidder and bidder['UserID']:
                                bid_values.append(bidder['UserID'])
                            else: 
                                bid_values.append('NULL')
                        else:
                            bid_values.append('NULL')
                        if 'Time' in bid and bid['Time']:
                            bid_values.append(transformDttm(bid['Time']))
                        else:
                            bid_values.append('NULL')
                        if 'Amount' in bid and bid['Amount']:
                            bid_values.append(transformDollar(bid['Amount']))
                        else:
                            bid_values.append('NULL')
                        bid_file.write(columnSeparator.join(bid_values)+"\n")
            pass

"""
Loops through each json files provided on the command line and passes each file
to the parser
"""
def main(argv):
    if len(argv) < 2:
        print >> sys.stderr, 'Usage: python skeleton_json_parser.py <path to json files>'
        sys.exit(1)
    # loops over all .json files in the argument
    for f in argv[1:]:
        if isJson(f):
            parseJson(f)
            print "Success parsing " + f

if __name__ == '__main__':
    main(sys.argv)
