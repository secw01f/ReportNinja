```
 ______ _______  _____   _____   ______ _______
|_____/ |______ |_____] |     | |_____/    |
|    \_ |______ |       |_____| |    \_    |

__   _ _____ __   _ _____ _______
| \  |   |   | \  |   |   |_____|
|  \_| __|__ |  \_| __|   |     |
```

ReportNinja is a tool for creating custom HTML and PDF pentest reports from DefectDojo. All though DefectDojo has a reporting capability that is built in, the ability to customize your reports is limited when a report that has stringint formating and branding requirements is needed. Reports are created on a per test basis.

This tool utilizes the DefectDojo API for getting platform, engagement, test, and finding details from DefectDojo and then utilizes Jinja2 for templating and HTML generation, and the python PDFKit module for creating the PDF reports.

# Installation and Configuration

To install ReportNinja, follow the steps below in your command line:

  **Note** If you are running ReportNinja in Kali Linux, Debian, or on Ubuntu systems, you may need to install the [wkhtmltopdf](https://wkhtmltopdf.org/downloads.html) binary if extended use of the pdfkit features like headers, footers, and TOC is required. This is not required for standard use of ReportNinja.

  1. git clone https://github.com/secw01f/ReportNinja.git
  2. cd ReportNinja
  3. pip3 install -r requirements.txt
  4. python3 reportninja.py -h

  **Note** ReportNinja does not currently work when run from a symbolic link. This is due to the requirement of the config.json file to be present.

To configure ReportNinja, follow the steps below.

  1. Open config.json in a text editor of your choice.
  2. Copy your apiv2 key from DefectDojo.
  3. Replace the value under "v2_api_key" in the config.json file.
  4. Replace the value under "dojo_url" with the url to your DefectDojo instance with no / at the end.
  5. Save the file.

  **Note** The "v1_api_key" value is available for those that still use the DefectDojo v1 API and would like to build intigrations for that API. ReportNinja by default does not utilize the v1 API as it is in the process of being depricated.
  
# Templates

ReportNinja utilizes the Jinja2 templating framework in order generate the HTML for a report. Any custom HTML reports created are to be stored in the "templates" directory that is located in the same folder as reportninja.py. When ReportNinja is run, it will list the templates stored in the "templates" directory so that they may be selected by their assigned ID at runtime. This allows a user to maintain multiple templates on the same installation.

ReportNinja provides the raw JSON provided by the DefectDojo API to be used in the template so that multiple datapoints can be used for custom reports. For details as to what information is available for each variable provided to Jinja2, please reference the DefectDojo API documentation for the coresponding URL that is provided in the table below.

| Jinja2 Variable |    API URL/Path   | Template Example |
| :-------------: | :---------------: | :--------------- |
|    engagement   | https://exampledojo.com/api/v2/engagements/{id}/ | <p>{{ engagement['name'] }}</p> |
|     product     | https://exampledojo.com/api/v2/products/{id}/ | <p>{{ product['name'] }}</p> |
|   product_type  | https://exampledojo.com/api/v2/product_types/?id={id} | <p>{{  product_type }}</p> |
|      test       | https://exampledojo.com/api/v2/tests/{id}/ | <p>{{ test['title'] }}</p> |
|    findings     | https://exampledojo.com/api/v2/findings/?test={id} | {% for finding in findings['results'] %}<p>{{ finding['name'] }}</p>{% endfor %} |
|    endpoints    | N/A | {% for finding in findings['results'] %}{% for endpoint in finding['endpoints'] %}<p>{{ endpoints[endpoint\|string] }}</p>{% endfor %}{% endfor %} |
|      jira       | N/A | {% set count = namespace(value=0) %}{% for finding in findings['results'] %}{% set count.value = count.value + 1 %}<p>{{ jira[count.value - 1] }}{% endfor %}{% endfor %} |

Finding images stored in DefectDojo can be integrated into reports without having to manage files by using the ```src="data:image/png;base64,"``` attribute in your HTML "img" tag and using a Jinja2 reference in the template to the base64 encoded image(s) in the finding output. It should be noted that becuase the images are hard coded into the generated HTML document, the image can sometimes be broken up between two pages by PDFkit when generating the PDF. Some adjustments may need to be made in the template design to account for this.

If javascript is going to be utilized in any part of the template, the javascript must be coded into the HTML file itself so that the output of the code is maintained if the HTML file is converted to a PDF.

# Template Configuration Files

There are times when data that does not come out of DefectDojo needs to go into a report. For this situation, the use of a Template Configuration File can add this data to your generated report. The template for a Template Configuration File is listed in this repo. There are three HTML elements that are supported by the Template Configuration File, which are link (a), paragraph (p), and table data (td). Additional configurations for PDFkit can also be passed to ReportNinja through the Template Configuration File.

# DefectDojo JIRA Integration

ReportNinja utilizes DefectDojo's JIRA integration in order to be able to provide the JIRA ID for a finding that has been opened if desired. ReportNinja loads the JIRA findings for the report as a dictionary at run time that ligns up with the order in which DefectDojo provides the findings to ReportNinja. DefectDojo lists findings in order of criticality, from Critical down to Low, so it is recommended that findings be listed in this manor in the report if using the JIRA integration.
