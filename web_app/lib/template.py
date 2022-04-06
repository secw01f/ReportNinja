import bs4
import sys
import json
import os

def template_config(input_file, config_file):

    try:
        config = json.load(open(config_file))
    except:
        print('[ ERROR ] Could not load %s. Confirm the file exists. Exiting...' % (config_file))
        sys.exit()

    try:
        with open(input_file, 'r+') as file:
            code = file.read()
            file.close()

            html = bs4.BeautifulSoup(code, 'html.parser')

            for x in range(0, len(config['elements'])):
                element = html.find_all(id=config['elements'][x]['id'])[0]
                if config['elements'][x]['type'] == 'a':
                    element['href'] = config['elements'][x]['link']
                    element.clear()
                    element.append(config['elements'][x]['text'])
                elif config['elements'][x]['type'] == 'p':
                    element.clear()
                    element.append(config['elements'][x]['text'])
                elif config['elements'][x]['type'] == 'td':
                    element.clear()
                    element.append(config['elements'][x]['text'])
                elif config['elements'][x]['type'] == 'table':
                    for row in range(0, len(config['elements'][x]['rows'])):
                        add_row = html.new_tag('tr')
                        element.append(add_row)
                        for y in range(0, len(config['elements'][x]['rows'][row]['td'])):
                            add_data = html.new_tag('td', style=config['elements'][x]['rows'][row]['td'][y]['css'])
                            add_row.append(add_data)
                            add_data.string = config['elements'][x]['rows'][row]['td'][y]['text']




        with open(input_file, 'w') as output:
            output.write(str(html))
            output.close()
    except:
        print('[ ERROR ] Could not add template config elements to the report')
