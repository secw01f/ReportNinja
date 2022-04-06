import sys
import requests
import json

def by_id(dojo, key, id):

    url = str(dojo + '/api/v2/endpoints/?id=' + str(id))

    try:
        headers = {'Authorization': str('Token ' + key)}

        print('[ STATUS ] Retrieving endpoints for finding id %s' % (id))

        response = requests.request("GET", url, headers=headers)

        details = response.json()['results'][0]

        return(details)
    except:
        print('[ ERROR ] Could not retrieve endpoints for finding id %s' % (id))
        sys.exit()
