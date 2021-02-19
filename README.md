```
 ______ _______  _____   _____   ______ _______
|_____/ |______ |_____] |     | |_____/    |
|    \_ |______ |       |_____| |    \_    |

__   _ _____ __   _ _____ _______
| \  |   |   | \  |   |   |_____|
|  \_| __|__ |  \_| __|   |     |
```

ReportNinja is a tool for creating custom HTML and PDF pentest reports from DefectDojo. All though DefectDojo has a reporting capability that is built in, the ability to customize your reports is limited when a report that has stringint formating and branding requirements is needed. Reports are created on a per test basis.

This tool utilizes the DefectDojo API for getting platform, engagement, test, and finding details from DefectDojo and then utilizes Jinja2 for templating and HTML generation and the PDFKit for creating the PDF reports.

# Installation and Configuration

To install ReportNinja, follow the steps below in your command line:

  1. git clone https://github.com/secw01f/ReportNinja.git
  2. cd ReportNinja
  3. pip3 install requirements.txt
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

ReportNinja provides the raw json provided by the DefectDojo API to be used in the template so that multiple datapoints can be used for custom reports. For details as to what information is available for each variable provided to Jinja2, please reference the DefectDojo API documentation for the coresponding URL that is provided in the table below.

| Jinja2 Variable |       API URL     | Template Example |
| :-------------: | :---------------: | :--------------- |
|    engagement   | https://exampledojo.com/api/v2/engagements/{id}/ | <p>{{ engagement['name'] }}</p> |
|     product     | https://exampledojo.com/api/v2/products/{id}/ | <p>{{ product['name'] }}</p> |
|   product_type  | https://exampledojo.com/api/v2/product_types/?id={id} | <p>{{  product_type }}</p> |
