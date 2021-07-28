from burp import IBurpExtender
from burp import ITab
from burp import IHttpRequestResponse
from burp import IResponseInfo
from javax import swing
from javax.swing import JFileChooser
from javax.swing import BorderFactory
from javax.swing import JOptionPane
from javax.swing.filechooser import FileNameExtensionFilter
from java.awt import BorderLayout
from javax.swing.border import EmptyBorder
from javax.swing import JTable
from javax.swing.table import DefaultTableModel
from java.awt import Color
from java.awt import Font
from java.awt import Dimension
from java.awt import GridLayout
import java.lang as lang
import os.path
import csv

class BurpExtender(IBurpExtender, ITab):
    #
    # Implement IBurpExtender
    #

    tableData = []
    colNames = ()

    def registerExtenderCallbacks(self, callbacks):

        print('Loading Site Map Extractor ...')
        # Set up extension environment
        self._callbacks = callbacks
        self._helpers = callbacks.getHelpers()
        self._callbacks.setExtensionName('Site Map Extractor')
        self.drawUI()
        self._callbacks.addSuiteTab(self)
        print('\nSite Map Extractor extension loaded successfully!')

    def drawUI(self):
        self.tab = swing.JPanel()
        self.uiLabel = swing.JLabel('Site Map Extractor Options')
        self.uiLabel.setFont(Font('Tahoma', Font.BOLD, 14))
        self.uiLabel.setForeground(Color(235,136,0))

        self.uiScopeOnly = swing.JRadioButton('In-scope only', True)
        self.uiScopeAll = swing.JRadioButton('Full site map', False)
        self.uiScopeButtonGroup = swing.ButtonGroup()
        self.uiScopeButtonGroup.add(self.uiScopeOnly)
        self.uiScopeButtonGroup.add(self.uiScopeAll)

        self.uipaneA = swing.JSplitPane(swing.JSplitPane.HORIZONTAL_SPLIT)
        self.uipaneA.setMaximumSize(Dimension(900,125))
        self.uipaneA.setDividerSize(2)
        self.uipaneB = swing.JSplitPane(swing.JSplitPane.HORIZONTAL_SPLIT)
        self.uipaneB.setDividerSize(2)
        self.uipaneA.setRightComponent(self.uipaneB)
        self.uipaneA.setBorder(BorderFactory.createLineBorder(Color.black))
        
        # UI for Export <a href Links
        self.uiLinksPanel = swing.JPanel()
        self.uiLinksPanel.setPreferredSize(Dimension(200, 75))
        self.uiLinksPanel.setBorder(EmptyBorder(10,10,10,10))
        self.uiLinksPanel.setLayout(BorderLayout())
        self.uiLinksLabel = swing.JLabel("Extract '<a href=' Links")
        self.uiLinksLabel.setFont(Font('Tahoma', Font.BOLD, 14))
        self.uiLinksAbs = swing.JCheckBox('Absolute     ', True)
        self.uiLinksRel = swing.JCheckBox('Relative     ', True)
        # create a subpanel so Run button will be centred
        self.uiLinksRun = swing.JButton('Run',actionPerformed=self.extractLinks)
        self.uiLinksSave = swing.JButton('Save Log to CSV File',actionPerformed=self.savetoCsvFile)
        self.uiLinksClear = swing.JButton('Clear Log',actionPerformed=self.clearLog)
        self.uiLinksButtonPanel = swing.JPanel()
        self.uiLinksButtonPanel.add(self.uiLinksRun)
        self.uiLinksButtonPanel.add(self.uiLinksSave)
        self.uiLinksButtonPanel.add(self.uiLinksClear)
        # add all elements to main Export Links panel
        self.uiLinksPanel.add(self.uiLinksLabel,BorderLayout.NORTH)
        self.uiLinksPanel.add(self.uiLinksAbs,BorderLayout.WEST)
        self.uiLinksPanel.add(self.uiLinksRel,BorderLayout.CENTER)
        self.uiLinksPanel.add(self.uiLinksButtonPanel,BorderLayout.SOUTH)
        self.uipaneA.setLeftComponent(self.uiLinksPanel)  # add Export Links panel to splitpane
        
        # UI for Export Response Codes
        self.uiCodesPanel = swing.JPanel()
        self.uiCodesPanel.setPreferredSize(Dimension(200, 75))
        self.uiCodesPanel.setBorder(EmptyBorder(10,10,10,10))
        self.uiCodesPanel.setLayout(BorderLayout())
        self.uiCodesLabel = swing.JLabel('Extract Response Codes')
        self.uiCodesLabel.setFont(Font('Tahoma', Font.BOLD, 14))
        self.uiRcodePanel = swing.JPanel()
        self.uiRcodePanel.setLayout(GridLayout(1,1))
        self.uiRcode1xx = swing.JCheckBox('1XX  ', False)
        self.uiRcode2xx = swing.JCheckBox('2XX  ', True)
        self.uiRcode3xx = swing.JCheckBox('3XX  ', True)
        self.uiRcode4xx = swing.JCheckBox('4XX  ', True)
        self.uiRcode5xx = swing.JCheckBox('5XX  ', True)
        self.uiCodesRun = swing.JButton('Run',actionPerformed=self.exportCodes)
        self.uiCodesSave = swing.JButton('Save Log to CSV File',actionPerformed=self.savetoCsvFile)
        self.uiCodesClear = swing.JButton('Clear Log',actionPerformed=self.clearLog)        
        self.uiCodesButtonPanel = swing.JPanel()
        self.uiCodesButtonPanel.add(self.uiCodesRun)
        self.uiCodesButtonPanel.add(self.uiCodesSave)
        self.uiCodesButtonPanel.add(self.uiCodesClear)
        self.uiRcodePanel.add(self.uiRcode1xx)
        self.uiRcodePanel.add(self.uiRcode2xx)
        self.uiRcodePanel.add(self.uiRcode3xx)
        self.uiRcodePanel.add(self.uiRcode4xx)
        self.uiRcodePanel.add(self.uiRcode5xx)
        self.uiCodesPanel.add(self.uiCodesLabel,BorderLayout.NORTH)
        self.uiCodesPanel.add(self.uiRcodePanel,BorderLayout.WEST)
        self.uiCodesPanel.add(self.uiCodesButtonPanel,BorderLayout.SOUTH)
        self.uipaneB.setLeftComponent(self.uiCodesPanel)

        # Option 3 UI for Export Sitemap
        self.uiExportPanel = swing.JPanel()
        self.uiExportPanel.setPreferredSize(Dimension(200, 75))
        self.uiExportPanel.setBorder(EmptyBorder(10,10,10,10))
        self.uiExportPanel.setLayout(BorderLayout())
        self.uiExportLabel = swing.JLabel('Export Site Map to File')
        self.uiExportLabel.setFont(Font('Tahoma', Font.BOLD, 14))
        self.uiMustHaveResponse = swing.JRadioButton('Must have a response     ', True)
        self.uiAllRequests = swing.JRadioButton('All     ', False)
        self.uiResponseButtonGroup = swing.ButtonGroup()
        self.uiResponseButtonGroup.add(self.uiMustHaveResponse)
        self.uiResponseButtonGroup.add(self.uiAllRequests)
        self.uiExportRun = swing.JButton('Run',actionPerformed=self.exportSiteMap)
        self.uiExportClear = swing.JButton('Clear Log',actionPerformed=self.clearLog)
        self.uiExportButtonPanel = swing.JPanel()
        self.uiExportButtonPanel.add(self.uiExportRun)
        self.uiExportButtonPanel.add(self.uiExportClear)        
        self.uiExportPanel.add(self.uiExportLabel,BorderLayout.NORTH)
        self.uiExportPanel.add(self.uiMustHaveResponse,BorderLayout.WEST)
        self.uiExportPanel.add(self.uiAllRequests,BorderLayout.CENTER)
        self.uiExportPanel.add(self.uiExportButtonPanel,BorderLayout.SOUTH)
        self.uipaneB.setRightComponent(self.uiExportPanel)

        # UI Common Elements
        self.uiLogLabel = swing.JLabel('Log:')
        self.uiLogLabel.setFont(Font('Tahoma', Font.BOLD, 14))
        self.uiLogPane = swing.JScrollPane()
        layout = swing.GroupLayout(self.tab)
        self.tab.setLayout(layout)
        
        # Thank you to Smeege (https://github.com/SmeegeSec/Burp-Importer/) for helping me figure out how this works.
        # He in turn gave credit to Antonio Sanchez (https://github.com/Dionach/HeadersAnalyzer/)
        layout.setHorizontalGroup(
            layout.createParallelGroup(swing.GroupLayout.Alignment.LEADING)
            .addGroup(layout.createSequentialGroup()
                .addGap(10, 10, 10)
                .addGroup(layout.createParallelGroup(swing.GroupLayout.Alignment.LEADING)
                    .addComponent(self.uiLabel)
                    .addGroup(layout.createSequentialGroup()
                        .addGap(10,10,10)
                        .addComponent(self.uiScopeOnly)
                        .addGap(10,10,10)
                        .addComponent(self.uiScopeAll))
                    .addGap(15,15,15)
                    .addComponent(self.uipaneA)
                    .addComponent(self.uiLogLabel)
                    .addComponent(self.uiLogPane))
                .addContainerGap(26, lang.Short.MAX_VALUE)))
        
        layout.setVerticalGroup(
            layout.createParallelGroup(swing.GroupLayout.Alignment.LEADING)
            .addGroup(layout.createSequentialGroup()
                .addGap(15,15,15)
                .addComponent(self.uiLabel)
                .addGap(15,15,15)
                .addGroup(layout.createParallelGroup()
                    .addComponent(self.uiScopeOnly)
                    .addComponent(self.uiScopeAll))
                .addGap(20,20,20)
                .addComponent(self.uipaneA)
                .addGap(20,20,20)
                .addComponent(self.uiLogLabel)
                .addGap(5,5,5)
                .addComponent(self.uiLogPane)
                .addGap(20,20,20)))

    def getTabCaption(self):
        return 'Site Map Extractor'

    def getUiComponent(self):
        return self.tab

    def scopeOnly(self):
        if self.uiScopeOnly.isSelected():
            return True
        else:
            return False

    def extractLinks(self, e):
        self.blankLog()
        
        #siteMapData only contains first requested entry of a page. Removing that page entry from burp target > site map > content will allow update.
        self.siteMapData = self._callbacks.getSiteMap(None)
        # What links should be extracted? absolute links, relative links, or both?
        self.destAbs = self.destRel = False
        if self.uiLinksAbs.isSelected():
            self.destAbs = True
        if self.uiLinksRel.isSelected():
            self.destRel = True

        # Start building JTable to contain the extracted data
        self.colNames = ('Page', 'HTTPS?', 'Link', 'Description', 'Target', 'Rel=', 'Possible vulnerabilities')
        self.tableData = []
        for i in self.siteMapData:
            try:
                self.requestInfo = self._helpers.analyzeRequest(i)
                self.url = self.requestInfo.getUrl()
            
                if self.scopeOnly() and not(self._callbacks.isInScope(self.url)):
                    continue

                self.urlDecode = self._helpers.urlDecode(str(self.url))
             
                self.response = i.getResponse()
                if self.response == None:   # if there's no response, there won't be any links :-)
                    continue
            
                self.responseInfo = self._helpers.analyzeResponse(self.response)
                self.responseOffset = self.responseInfo.getBodyOffset()
                self.responseBody = self._helpers.bytesToString(self.response)[self.responseOffset:]

                keep_looking = True
                while keep_looking:    # there may be multiple links in the response
                    #TODO: known issue: if link does not start with <a href= it won't be detected
                    i = self.responseBody.lower().find('<a href=')
                
                    #define some variables
                    self.isHttps = None
                    self.Vulnerabilities = ""
                
                    if i == -1:   # no more <a href's found
                        break
                    self.responseBody = self.responseBody[i+8:]
                    isAbsLink = isRelLink = False
                    # Looking for either " or ' around links which can be either absolute or relative
                    # This assumes that for a link, quoting is consistent at front and back
                    if self.responseBody[0:8].lower() == '"http://':
                        myOffset = 8
                        isAbsLink = True
                        endQuote = '"'
                        self.isHttps = False
                        self.Vulnerabilities = "Unencrypted transport"
                    elif self.responseBody[0:8].lower() == "'http://":
                        myOffset = 8
                        isAbsLink = True
                        endQuote = "'"      
                        self.isHttps = False    
                        self.Vulnerabilities = "Unencrypted transport"       
                    elif self.responseBody[0:8].lower() == '"mailto:':
                        myOffset = 0
                        isAbsLink = True
                        endQuote = '"'
                        self.isHttps = "(mailto)"   
                    elif self.responseBody[0:8].lower() == "'mailto:":
                        myOffset = 0
                        isAbsLink = True
                        endQuote = "'"      
                        self.isHttps = "(mailto)"    
                    elif self.responseBody[0:7].lower() == "mailto:":
                        myOffset = 0
                        isAbsLink = True
                        endQuote = ">" #might have space, but might not have space. Assume end will be there for sure. 
                        self.isHttps = "(mailto)"    
                    elif self.responseBody[0:9].lower() == '"https://':
                        myOffset = 9
                        isAbsLink = True
                        endQuote = '"'
                        self.isHttps = True
                    elif self.responseBody[0:9].lower() == "'https://":
                        myOffset = 9
                        isAbsLink = True
                        endQuote = "'"
                        self.isHttps = True
                    elif self.responseBody[0:1] == '"':
                        myOffset = 1
                        isRelLink = True
                        endQuote = '"'
                        self.isHttps = "(Relative)"
                    else:
                        myOffset = 1
                        isRelLink = True
                        endQuote = "'"
                        self.isHttps = "(Relative)"
                    
                    self.responseBody = self.responseBody[myOffset:]
                    pos = self.responseBody.find(endQuote)
                    self.link = self.responseBody[0:pos]
                
                    # Looking for </a> end tag
                    # This assumes that the link is correctly ended
                    posEndTag = self.responseBody.lower().find("</a>")
                    self.fullLink = self.responseBody[0:posEndTag]
                
                    # Looking for > at the end of the <a  tag 
                    # This again assumes that the link is correctly ended
                    posEndA = self.responseBody.lower().find(">")
                    self.description = self.responseBody[posEndA+1:posEndTag]
               
               
                    # Looking for a possible target that is described
                    self.target = ""
                    if self.responseBody.lower().find("target") < posEndA:
                        posTarget = self.responseBody.lower().find("target")
                        #search the end of this parameter - might be ' or " or even a space, but it should be directly after the target
                    
                        if self.responseBody[posTarget+7:posTarget+8] == '"':
                            endQuote = '"'
                        elif self.responseBody[posTarget+7:posTarget+8] == "'":
                            endQuote = "'"
                        else:
                            endQuote = ">"                    
                    
                        posTargetEnd = self.responseBody[posTarget+8:posEndA].lower().find(endQuote)
                        #TODO rework needed
                        self.target = self.responseBody[posTarget+8:posTarget+8+posTargetEnd]
                
                    self.rel = ""
                    if self.responseBody.lower().find("rel") < posEndA:
                        posRel = self.responseBody.lower().find("rel")
                        #search the end of this parameter - might be ' or " or even a space, but it should be directly after the target
                        if self.responseBody[posRel+4:posRel+5] == '"':
                            endQuote = '"'
                        elif self.responseBody[posRel+4:posRel+5] == "'":
                            endQuote = "'"
                        else:
                            endQuote = ">"                    
                    
                        posRelEnd = self.responseBody[posRel+5:posEndA].lower().find(endQuote)
                    
                        self.rel = self.responseBody[posRel+5:posRel+5+posRelEnd]
               
                        #Is this link vulnerable to Tabnabbing?
                        if self.target != "" and not isRelLink:
                            if self.rel.lower().find("noopener") == -1:
                                self.Vulnerabilities = self.Vulnerabilities + " Tabnabbing"       
                    #if rel= is not defined, but target is, the link is still vulnerable for tabnabbing
                    elif self.target != "" and not isRelLink:
                        self.Vulnerabilities = self.Vulnerabilities + " Tabnabbing"       
                    
               
                    if (isAbsLink and self.destAbs) or (isRelLink and self.destRel):
                        # remove white space and extra CR/LF characters
                        self.tableData.append([self.stripURLPort(self.urlDecode), str(self.isHttps), self.lstripWS(self.stripCRLF(self.link)), self.lstripWS(self.stripCRLF(self.description)), self.lstripWS(self.stripCRLF(self.target)), self.lstripWS(self.stripCRLF(self.rel)), self.lstripWS(self.stripCRLF(self.Vulnerabilities))])
           
            except:
                print('An error occured during processing of a link [ ' + str(i) + ' ] ignored it and continued with the next.')
           
        dataModel = DefaultTableModel(self.tableData, self.colNames)
        self.uiLogTable = swing.JTable(dataModel)
        self.uiLogTable.setAutoCreateRowSorter(True);
        
        self.uiLogPane.setViewportView(self.uiLogTable)

    def exportCodes(self, e):
        self.blankLog()
        self.siteMapData = self._callbacks.getSiteMap(None)
        # response codes to be included
        self.rcodes = []
        if self.uiRcode1xx.isSelected():
            self.rcodes += '1'
        if self.uiRcode2xx.isSelected():
            self.rcodes += '2'
        if self.uiRcode3xx.isSelected():
            self.rcodes += '3'
        if self.uiRcode4xx.isSelected():
            self.rcodes += '4'
        if self.uiRcode5xx.isSelected():
            self.rcodes += '5'

        if '3' in self.rcodes:
            self.colNames = ('Request','Referer','Response Code','Redirects To')
        else:
            self.colNames = ('Request','Referer','Response Code')
        self.tableData = []

        for i in self.siteMapData:
            self.requestInfo = self._helpers.analyzeRequest(i)
            self.url = self.requestInfo.getUrl()
            if self.scopeOnly() and not(self._callbacks.isInScope(self.url)):
                continue
            try:
                self.urlDecode = self._helpers.urlDecode(str(self.url))
            except:
                continue
            self.response = i.getResponse()
            if self.response == None:
                continue
            # Get referer if there is one
            self.requestHeaders = self.requestInfo.getHeaders()
            self.referer = ''
            for j in self.requestHeaders:
                if j.startswith('Referer:'):
                    self.fullReferer = j.split(' ')[1]
                    # drop the querystring parameter
                    self.referer = self.fullReferer.split('?')[0] 
            # Get response code
            self.responseInfo = self._helpers.analyzeResponse(self.response)
            self.responseCode = self.responseInfo.getStatusCode()
            self.firstDigit = str(self.responseCode)[0]
            if self.firstDigit not in self.rcodes:
                continue
            if self.firstDigit in ['1','2','4','5']:     # Return codes 1xx, 2xx, 4xx, 5xx
                self.tableData.append([self.stripURLPort(self.urlDecode), str(self.referer), str(self.responseCode)])    
            elif self.firstDigit == '3':   # Return code 3xx Redirection
                self.requestHeaders = self.requestInfo.getHeaders()
                self.responseHeaders = self.responseInfo.getHeaders()
                for j in self.responseHeaders:
                    if j.startswith('Location:'):
                        self.location = j.split(' ')[1]
                self.tableData.append([self.stripURLPort(self.urlDecode), str(self.referer), str(self.responseCode), self.location])

        dataModel = DefaultTableModel(self.tableData, self.colNames)
        self.uiLogTable = swing.JTable(dataModel)
        self.uiLogTable.setAutoCreateRowSorter(True);
        self.uiLogPane.setViewportView(self.uiLogTable)
        
    def exportSiteMap(self,e):
        self.blankLog()
        f, ok = self.openFile('txt', 'Text files', 'wb')
        if ok:        
            # Retrieve site map data
            self.siteMapData = self._callbacks.getSiteMap(None)
            if self.uiMustHaveResponse.isSelected():
                self.outputAll = False
            else:
                self.outputAll = True
            for i in self.siteMapData:
                self.myrequest = i.getRequest()  #self._helpers.urlDecode(i.getRequest())
                self.requestInfo = self._helpers.analyzeRequest(i)
                self.url = self.requestInfo.getUrl()
                if self.scopeOnly() and not(self._callbacks.isInScope(self.url)):
                    continue
                self.myresponse = i.getResponse()  #self._helpers.urlDecode(i.getResponse())
                if self.myresponse != None:
                    f.write('----- REQUEST\r\n')
                    f.write(self.myrequest)  #self._helpers.urlEncode(self.myrequest))
                    f.write('\n')
                    f.write('----- RESPONSE\r\n')
                    f.write(self.myresponse)  #self._helpers.urlEncode(self.myresponse))
                    f.write('\n')
                elif not self.uiMustHaveResponse:
                    f.write('----- REQUEST\r\n')
                    f.write(self.myrequest)  #self._helpers.urlEncode(self.myrequest))
                    f.write('\n')
            f.close()
            JOptionPane.showMessageDialog(self.tab,'The Site Map file was successfully written.')

    def savetoCsvFile(self,e):
        if self.tableData == []:
            JOptionPane.showMessageDialog(self.tab,'The log contains no data.')
            return
        f, ok = self.openFile('csv', 'CSV files', 'wb')
        if ok:
            self.writer = csv.writer(f)
            self.writer.writerow(list(self.colNames))
            for i in self.tableData:
                self.writer.writerow(i)
            f.close()
            JOptionPane.showMessageDialog(self.tab,'The csv file was successfully written.')

    def openFile(self, fileext, filedesc, fileparm):
        myFilePath = ''
        chooseFile = JFileChooser()
        myFilter = FileNameExtensionFilter(filedesc,[fileext])
        chooseFile.setFileFilter(myFilter)
        ret = chooseFile.showOpenDialog(self.tab)
        if ret == JFileChooser.APPROVE_OPTION:
            file = chooseFile.getSelectedFile()
            myFilePath = str(file.getCanonicalPath()).lower()
            if not myFilePath.endswith(fileext):
                myFilePath += '.' + fileext
            okWrite = JOptionPane.YES_OPTION
            if os.path.isfile(myFilePath):
                okWrite = JOptionPane.showConfirmDialog(self.tab,'File already exists. Ok to over-write?','',JOptionPane.YES_NO_OPTION)
                if okWrite == JOptionPane.NO_OPTION:
                    return
            j = True
            while j:
                try:
                    f = open(myFilePath,mode=fileparm)
                    j = False
                except IOError:
                    okWrite = JOptionPane.showConfirmDialog(self.tab,'File cannot be opened. Correct and retry?','',JOptionPane.YES_NO_OPTION)
                    if okWrite == JOptionPane.NO_OPTION:
                        return None, False
            return f, True

    def stripCRLF(self, link):
        link = link.rstrip('\r')
        link = link.rstrip('\n')
        return link

    def lstripWS(self, link):
        return link.lstrip()

    def stripURLPort(self, url):
        # Thanks to shpendk for this code(https://github.com/PortSwigger/site-map-fetcher/)
        return url.split(':')[0] + ':' + url.split(':')[1] + '/' + url.split(':')[2].split('/',1)[1]

    def blankLogTable(self):
        self.tableData = []
        return
    
    # This function is used when program wants to clear the log.
    def blankLog(self):
        self.uiLogPane.setViewportView(None)
        self.blankLogTable()
        return

    # This function is used when the user clicks the Clear Log button.
    def clearLog(self, e):
        self.uiLogPane.setViewportView(None)
        self.blankLogTable()
        return

