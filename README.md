## Site Map Extractor
Site Map Extractor is a Burp extension written in Python that extracts various information from the Site Map. Optionally you can select to search the full site map or just the in-scope items. There are 3 types of information that can be extracted.

#### Extract '<a href=' Links (and reports two possible vulnerabilities: 'unencrypted transport' & 'tabnabbing')
This function searches responses for links of the form ```<a href=```. Note that this will include links within javascript and in commented out areas, but not links that start differently ```<a target="ignored" href=```. The log displays the found links and the page the link was found on. You have the option to select absolute links, relative links, or both.

Log data can optionally be saved to a .csv file.

#### Extract Response Codes
This function finds all requests that returned one of the selected response code ranges (1xx/2xx/3xx/4xx/5xx). The log displays the page requested, the referer if one was specified, the specific response code, and if the response was a redirect, where the page was redirected.

The log can optionally be saved to a .csv file.

#### Export Site Map to File
This function saves the site map requests and responses to a .txt file. You can specify that all requests should be exported or only those with a corresponding response. The full content of the requests and responses is saved. This enables you to write independent code to further process the site map as you wish.

**Note:** In all cases, the extension verifies if an existing file should be over-written.

### Screenshots
##### Layout:
![Layout](/Screenshots/SME-Screenshot1.JPG)

##### File Verification:
![File Verification](/Screenshots/SME-Screenshot2.JPG)

#### Version
1.2

#### Installation
Jython (2.7+) is required for this extension to work  to set it up in Burp's Extender Options before adding the extension. Once that is done, add a new extension in the "Extensions" tab, choose "Python" as the extension type, and point to the "SiteMapExtractor.py" file. A successful load will be confirmed in the Output tab.



