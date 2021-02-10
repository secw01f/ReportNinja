import requests
import sys
import json

def finding_count(dojo, id):

    try:
        config = json.load(open('config.json'))
    except:
        print('[ ERROR ] Could not load config.json. Confirm the file exists. Exiting...')
        sys.exit()

    url = str(dojo + '/api/v2/findings/?test=' + str(id))

    try:
        headers = {'Authorization': str('Token ' + config['keys']['v2_api_key'])}

        print('[ STATUS ] Retrieving findings count for test id %s' % (id))

        response = requests.request("GET", url, headers=headers)

        return(response.json()['count'])
    except:
        print('[ ERROR ] Could not retrieve finding count for test id %s' % (id))
        sys.exit()

def by_test_id(dojo, id):

    try:
        config = json.load(open('config.json'))
    except:
        print('[ ERROR ] Could not load config.json. Confirm the file exists. Exiting...')
        sys.exit()

    url = str(dojo + '/api/v2/findings/?test=' + str(id))

    try:
        headers = {'Authorization': str('Token ' + config['keys']['v2_api_key'])}

        print('[ STATUS ] Retrieving findings for test id %s' % (id))

        response = requests.request("GET", url, headers=headers)

        return(response.json())
    except:
        print('[ ERROR ] Could not retrieve findings for test id %s' % (id))
        sys.exit()
