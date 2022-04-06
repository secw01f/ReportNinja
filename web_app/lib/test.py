import sys
import requests
import json

def by_id(dojo, key, id):

    url = str(dojo + '/api/v2/tests/' + str(id) + '/')

    try:
        headers = {'Authorization': str('Token ' + key)}

        print('[ STATUS ] Retrieving data for test id %s' % (id))

        response = requests.request("GET", url, headers=headers)

        return(response.json())
    except:
        print('[ ERROR ] Could not retrieve data for test id %s' % (id))
        sys.exit()

def by_title(dojo, key, title):

    url = str(dojo + '/api/v2/tests/?title='+ title)

    try:
        headers = {'Authorization': str('Token ' + key)}

        print('[ STATUS ] Retrieving data for the test titled %s' % (title))

        response = requests.request("GET", url, headers=headers)

        return(response.json())
    except:
        print('[ ERROR ] Could not retrieve data for the test titled %s' % (title))
        sys.exit()
