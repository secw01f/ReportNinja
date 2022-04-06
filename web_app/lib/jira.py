import sys
import requests
import json

def by_finding_id(dojo, key, id):

    url = str(dojo + '/api/v2/jira_finding_mappings/?finding_id=' + str(id))

    try:
        headers = {'Authorization': str('Token ' + key)}

        print('[ STATUS ] Retrieving JIRA ticket for finding id %s' % (id))

        response = requests.request("GET", url, headers=headers)

        return(response.json())
    except:
        print('[ ERROR ] Could not retrieve JIRA ticket for finding id %s' % (id))
        sys.exit()
