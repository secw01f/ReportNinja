import sys
import requests
import json

def by_id(dojo, key, id):

    url = str(dojo + '/api/v2/engagements/' + str(id) + '/')

    try:
        headers = {'Authorization': str('Token ' + key)}

        print('[ STATUS ] Retrieving data for engagment id %s' % (id))

        response = requests.request("GET", url, headers=headers)

        return(response.json())
    except:
        print('[ ERROR ] Could not retrieve data for engagement id %s' % (id))
        sys.exit()
