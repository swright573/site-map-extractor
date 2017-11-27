# Site Map Extractor

Site Map Extractor is a Burp extension written in Python that extracts various information from the Site Map. An option lets you select if the full site map is searched or just the in-scope items. There are 3 types of information that can be extracted.

* Extract '<a href=' Links
This function searches responses for links of the form ```<a href=```. Note that this will include links within javascript and in commented out areas. Found links appear in the log and on which page the link was found. You have the option to select only absolute links, only relative links, or both.

Log data can optionally be saved to a .csv file.

* Extract Response Codes
This function finds all requests that returned one of the selected response code ranges (1XX/2XX/3XX/4XX/5XX). The log displays the page requested, the referer if one was specified, the actual response code, and if the response was a redirect, where that was.

The log can optionally be saved to a .csv file.

* Export Site Map to File
This function dumps the site map to a .txt file. You can specify if all requests should be exported or only those with a corresponding response.

In all cases, the extension verifies if an existing file should be over-written.

## Screenshots
Layout:
![Alt text](/Screenshots/SME_screenshot1.jpg?raw=true "Layout")

File Verification:
![Alt text](/Screenshots/SME_screenshot2.jpb?raw=true "File Verification")

##Version
0.9

##Installation
Jython 2.7+ is required for this extension to work  to set it up in Burp's Extender Options before adding the extension. Once that is done, add a new extension in the "Extensions" tab, choose "Python" as the extension type, and point to the "SiteMapExtractor.py" file. A successful load will be confirmed in the Output tab.



