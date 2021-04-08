#!/usr/bin/env python3

import getopt
import sys
import os
import json
import pdfkit
from jinja2 import Environment, FileSystemLoader
from lib import test, findings, product, engagement, endpoints, jira
from lib import template as temp_config

DojoURL = ''
TestID = ''
TestName = ''
FindingsCount = ''
Product = ''
OutputFile = 'Pentest Report'
ReportTemplate = ''
JIRA = False
PDF = False
Config = ''

def banner():
    print(" ______ _______  _____   _____   ______ _______")
    print("|_____/ |______ |_____] |     | |_____/    |   ")
    print("|    \_ |______ |       |_____| |    \_    |   ")
    print("                                            ")
    print("__   _ _____ __   _ _____ _______")
    print("| \  |   |   | \  |   |   |_____|")
    print("|  \_| __|__ |  \_| __|   |     |")

def usage():
    banner()
    print("")
    print("Report Ninja is a tool for creating custom HTML reports from DefectDojo using Jinja2 templates")
    print("")
    print("")
    print("Usage:")
    print("")
    print("Optional:")
    print("-h   help          Prints this usage message")
    print("-o   output        Name of the report generated (Do not include file type i.e. .html)")
    print("-j   jira          Enables the retrieval of JIRA tickets from DefectDojo for use in the report")
    print("-p   pdf           Enables the creation of a pdf version of the report")
    print("-c   temp_config   Template configuration file for adding details to report that aren't in DefectDojo")
    print("")
    print("Required:")
    print("-i   id            DefectDojo ID of the Test you would like to create a report for")
    print("or")
    print("-t   title         DefectDojo Title of the Test you would like create a report for")
    print("")
    print("")
    print("Example:")
    print("")
    print("python3 reportninja.py -i 1 -j -o testreport")
    print('./reportninja.py --title "This Test Title"')

def main():

    global DojoURL
    global TestID
    global TestName
    global FindingsCount
    global Product
    global OutputFile
    global Template
    global JIRA
    global PDF
    global Config

    if not sys.argv[1:]:
        usage()
        sys.exit()

    try:
        opts, args = getopt.getopt(sys.argv[1:], 'hi:t:o:jpc:', ['help', 'id', 'title', 'output', 'jira', 'pdf', 'temp_config'])
    except getopt.GetoptError as err:
        print(str(err))
        usage()
        sys.exit()

    for o,a in opts:
        if o in ('-h', '--help'):
            usage()
            sys.exit()
        elif o in ('-i', '--id'):
            TestID = a
        elif o in ('-t', '--title'):
            TestName = a
        elif o in ('-o', '--output'):
            OutputFile = a
        elif o in ('-j', '--jira'):
            JIRA = True
        elif o in ('-p', '--pdf'):
            PDF = True
        elif o in ('-c', '--temp_config'):
            Config = a

    banner()
    print('\n')

    with open('config.json') as c:
        config = json.load(c)

    DojoURL = config['dojo_url']

    TemplateList = []

    for file in os.walk('templates/'):
        for x in range(len(file[2])):
            TemplateList.append(file[2][x])

    print("Templates:")
    for x in range(len(TemplateList)):
        print(str('Name: ' + TemplateList[x].split('.')[0] + '   ID: ' + str(x)))

    TemplateID = input('Please select a template by ID (Default = 0): ')

    if len(TemplateID) == 0:
        ReportTemplate = TemplateList[0]
    else:
        ReportTemplate = TemplateList[int(TemplateID)]

    if len(DojoURL) == 0:
        print('[ ERROR ] No URL provided for DefectDojo instance! Please add to the config.json file!')
        sys.exit()
    else:
        pass

    if len(TestID) != 0 and len(TestName) == 0:
        TestName = test.by_id(DojoURL, TestID)['title']
    elif len(TestID) == 0 and len(TestName) != 0:
        TestID = test.by_title(DojoURL, TestName)['results'][0]['id']

    FindingsCount = findings.finding_count(DojoURL, TestID)

    Engagement = test.by_id(DojoURL, TestID)['engagement']

    Product = product.by_id(DojoURL, engagement.by_id(DojoURL, Engagement)['product'])

    ProductType = product.product_type(DojoURL, Product['prod_type'])

    Findings = findings.by_test_id(DojoURL, TestID)

    Endpoints = {}

    for finding in Findings['results']:
        keys = []
        for x in range(0, len(finding['endpoints'])):
            keys.append(finding['endpoints'][x])

        for key in keys:
            endpoint_details = endpoints.by_id(DojoURL, key)
            endpoint = endpoint_details['protocol'] + '://' + endpoint_details['host'] + endpoint_details['path']
            Endpoints.update({str(key): endpoint})

    JiraTickets = []

    if JIRA == True:
        for x in Findings['results']:
            try:
                JiraTickets.append(jira.by_finding_id(DojoURL, x['id'])['results'][0]['jira_key'])
            except:
                JiraTickets.append('No Ticket Available')
    else:
        pass

    env = Environment(loader=FileSystemLoader('templates'))
    template = env.get_template(ReportTemplate)

    if JIRA == True:
        output = template.render(engagement= engagement.by_id(DojoURL, Engagement), product=Product, product_type=ProductType, test=test.by_id(DojoURL,TestID), findings=Findings, endpoints=Endpoints, jira=JiraTickets)
    else:
        output = template.render(engagement= engagement.by_id(DojoURL, Engagement), product=Product, product_type=ProductType, test=test.by_id(DojoURL,TestID), findings=Findings, endpoints=Endpoints)

    print('[ STATUS ] Creating report(s). This may take some time...')

    if PDF == True:
        
        options = options = {'quiet': ''}
        
        with open((OutputFile + '.html'), 'w') as file:
            file.write(output)
            file.close()

        if len(Config) != 0:
            temp_config.template_config((OutputFile + '.html'), Config)

            with open(Config, 'r') as config_file:
                contents = json.load(config_file)
                config_file.close()

            if contents['pdf']:
                options = contents['pdf']
            else:
                pass
        else:
            pass

        print('[ COMPLETE ] HTML Report creation complete! Please see %s.html' % (OutputFile))

        pdfkit.from_file((OutputFile + '.html'), (OutputFile + '.pdf'), options=options)

        print('[ COMPLETE ] PDF Report creation complete! Please see %s.pdf' % (OutputFile))

    else:
        with open((OutputFile + '.html'), 'w') as file:
            file.write(output)
            file.close()

        if len(Config) != 0:
            temp_config.template_config((OutputFile + '.html'), Config)
        else:
            pass

        print('[ COMPLETE ] Report creation complete! Please see %s.html' % (OutputFile))

main()
