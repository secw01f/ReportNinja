import sys
import requests
import json

def by_id(dojo, key, id):

    url = str(dojo + '/api/v2/products/' + str(id) + '/')

    try:
        headers = {'Authorization': str('Token ' + key)}

        print('[ STATUS ] Retrieving detials for product id %s' % (id))

        response = requests.request("GET", url, headers=headers)

        return(response.json())
    except:
        print('[ ERROR ] Could not retrieve detials for product id %s' % (id))
        sys.exit()

def product_type(dojo, key, id):

    url = str(dojo + '/api/v2/product_types/?id=' + str(id))

    try:
        headers = {'Authorization': str('Token ' + key)}

        response = requests.request("GET", url, headers=headers)

        return(response.json()['results'][0]['name'])
    except:
        print('[ ERROR ] Could not retrieve detials for product type id %s' % (id))
        sys.exit()
