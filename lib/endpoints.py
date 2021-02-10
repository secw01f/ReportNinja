import sys
import requests
import json

def by_id(dojo, id):

    try:
        config = json.load(open('config.json'))
    except:
        print('[ ERROR ] Could not load config.json. Confirm the file exists. Exiting...')
        sys.exit()

    url = str(dojo + '/api/v2/endpoints/?id=' + str(id))

    try:
        headers = {'Authorization': str('Token ' + config['keys']['v2_api_key'])}

        print('[ STATUS ] Retrieving endpoints for finding id %s' % (id))

        response = requests.request("GET", url, headers=headers)

        details = response.json()['results'][0]

        return(details)
    except:
        print('[ ERROR ] Could not retrieve endpoints for finding id %s' % (id))
        sys.exit()
