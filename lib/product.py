import sys
import requests
import json

def by_id(dojo, id):

    try:
        config = json.load(open('config.json'))
    except:
        print('[ ERROR ] Could not load config.json. Confirm the file exists. Exiting...')
        sys.exit()

    url = str(dojo + '/api/v2/products/' + str(id) + '/')

    try:
        headers = {'Authorization': str('Token ' + config['keys']['v2_api_key'])}

        print('[ STATUS ] Retrieving detials for product id %s' % (id))

        response = requests.request("GET", url, headers=headers)

        return(response.json())
    except:
        print('[ ERROR ] Could not retrieve detials for product id %s' % (id))
        sys.exit()

def product_type(dojo, id):

    try:
        config = json.load(open('config.json'))
    except:
        print('[ ERROR ] Could not load config.json. Confirm the file exists. Exiting...')
        sys.exit()

    url = str(dojo + '/api/v2/product_types/?id=' + str(id))

    try:
        headers = {'Authorization': str('Token ' + config['keys']['v2_api_key'])}

        response = requests.request("GET", url, headers=headers)

        return(response.json()['results'][0]['name'])
    except:
        print('[ ERROR ] Could not retrieve detials for product type id %s' % (id))
        sys.exit()
