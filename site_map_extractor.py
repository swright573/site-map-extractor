from burp import IBurpExtender
from burp import ITab
from burp import IHttpRequestResponse
from burp import IResponseInfo
from javax import swing
from javax.swing import JFileChooser
from javax.swing import BorderFactory
from javax.swing import JOptionPane
from javax.swing.filechooser import FileNameExtensionFilter
from javax.swing.border import EmptyBorder
from java.awt import BorderLayout
from java.awt import Color
from java.awt import Font
from java.awt import Dimension
from java.awt import GridLayout
import java.lang as lang
import os.path

class BurpExtender(IBurpExtender, ITab):
    #
    # Implement IBurpExtender
    #
    def registerExtenderCallbacks(self, callbacks):

        print 'Loading Brp Extract Site Map extension ...'
        # Set up extension environment
        self._callbacks = callbacks
        self._helpers = callbacks.getHelpers()
        self._callbacks.setExtensionName('Site Map Extractor')
        self.drawUI()
        self._callbacks.addSuiteTab(self)
        print '\nExtension loaded successfully!'

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
        self.uiLinksRun = swing.JButton('Run',actionPerformed=self.exportLinks)
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
        self.uiRcode5xx = swing.JCheckBox('5XX     ', False)
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
        self.uiLogArea = swing.JTextArea('')
        self.uiLogArea.setLineWrap(True)
        self.uiLogPane.setViewportView(self.uiLogArea)
        self.uiLogPane.setPreferredSize(Dimension(350,200))

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
                .addComponent(self.uiLogPane)
                .addGap(20,20,20)))

    def getTabCaption(self):
        return 'Site Map Extractor'

    def getUiComponent(self):
        return self.tab

    def scopeOnly(self):
        # scope only or everything
        if self.uiScopeOnly.isSelected():
            return True
        else:
            return False

    def exportLinks(self, e):
        self.uiLogArea.setText('')
        self.siteMapData = self._callbacks.getSiteMap(None)
        # Export absolute links, relative links, or both?
        if self.uiLinksAbs.isSelected():
            self.destAbs = True
        else:
            self.destAbs = False
        if self.uiLinksRel.isSelected():
            self.destRel = True
        else:
            self.destRel = False

        # build title row for extract based on user choices
        self.uiLogArea.append('Page,Link')
        for i in self.siteMapData:
            self.requestInfo = self._helpers.analyzeRequest(i)
            self.url = self.requestInfo.getUrl()
            if self.scopeOnly() and not(self._callbacks.isInScope(self.url)):
                continue
            self.response = i.getResponse()
            if self.response != None:
                self.responseInfo = self._helpers.analyzeResponse(self.response)
                self.responseOffset = self.responseInfo.getBodyOffset()
                self.responseBody = self._helpers.bytesToString(self.response)[self.responseOffset:]
                self.responseBody = self.responseBody.decode('utf-8','ignore')
                keep_looking = True
                while keep_looking:
                    i = self.responseBody.find('<a href=')
                    if i == -1:
                        break
                    self.responseBody = self.responseBody[i+8:]
                    if self.responseBody[0:7] == '"http://':
                        myOffset = 7
                    elif self.responseBody[0:8] == '"https://':
                        myOffset = 8
                    else:
                        myOffset = 1
                    self.responseBody = self.responseBody[myOffset:]
                    pos = self.responseBody.find('"')
                    self.link = self.responseBody[0:pos]
                    if ('http' in self.link and self.destAbs) or (not 'http' in self.link and self.destRel):
                        # remove any extra CR/LF characters
                        self.uiLogArea.append('\n' + self.stripURLPort(str(self.url)) + ',' + self.lstripWS(self.stripCRLF(self.link)))
            continue
        self.uiLogArea.setCaretPosition(0)

    def exportCodes(self, e):
        self.uiLogArea.setText('')
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

        self.title = 'Request,Referer,Response Code'
        if '3' in self.rcodes:
            self.title+= ',ReDirects To'
        self.uiLogArea.append(self.title)
        for i in self.siteMapData:
            self.requestInfo = self._helpers.analyzeRequest(i)
            self.url = self.requestInfo.getUrl()
            if self.scopeOnly() & self._callbacks.isInScope(self.url) == False:
                continue
            self.response = i.getResponse()
            if self.response != None:
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
                if self.firstDigit in self.rcodes:
                    if self.firstDigit == '1':     # Return code 1xx Informational
                        self.uiLogArea.append('\n' + self.stripURLPort(str(self.url)) + ',' + str(self.referer) + ',' + str(self.responseCode)+ ',')    
                    elif self.firstDigit == '2':   # Return code 2xx Success
                        self.uiLogArea.append('\n' + self.stripURLPort(str(self.url)) + ',' + str(self.referer) + ',' + str(self.responseCode)+ ',')
                    elif self.firstDigit == '3':   # Return code 3xx Redirection
                        self.requestHeaders = self.requestInfo.getHeaders()
                        self.responseHeaders = self.responseInfo.getHeaders()
                        for j in self.responseHeaders:
                            if j.startswith('Location:'):
                                self.location = j.split(' ')[1]
                        self.uiLogArea.append('\n' + self.stripURLPort(str(self.url))+','+str(self.referer)+','+str(self.responseCode)+ ',' + self.location)
                    elif self.firstDigit == '4':   # Return code 4xx Client Error
                        self.uiLogArea.append('\n' + self.stripURLPort(str(self.url)) + ',' + str(self.referer)+ ',' +str(self.responseCode)+ ',')
                    elif self.firstDigit == '5':   # Return code 5xx Server Error
                        self.uiLogArea.append('\n' + self.stripURLPort(str(self.url)) + ',' + str(self.referer)+ ',' +str(self.responseCode)+ ',')
            continue
        self.uiLogArea.setCaretPosition(0)
        
    def exportSiteMap(self,e):
        self.uiLogArea.setText('')
        self.uiLogArea.append('Working ...\n\n')
        f, ok = self.openFile('txt', 'Text files', 'wb')
        if ok:        
            # Retrieve site map data
            self.siteMapData = self._callbacks.getSiteMap(None)
            num_requests = 0
            num_responses = 0
            if self.uiMustHaveResponse.isSelected():
                self.outputAll = False
            else:
                self.outputAll = True
            for i in self.siteMapData:
                try:
                    self.myrequest = i.getRequest()
                except:
                    self.uiLogArea.append('There was a problem getting a request.\n')
                    for i in sys.exc_info():
                        self.uiLogArea.append('Error: %s \n' % i)
                    break
                self.requestInfo = self._helpers.analyzeRequest(i)
                self.url = self.requestInfo.getUrl()
                if self.scopeOnly() and not(self._callbacks.isInScope(self.url)):
                    continue
                try:
                    self.myresponse = i.getResponse()
                except:
                    self.uiLogArea.append('There was a problem getting a response.\n')
                    for i in sys.exc_info():
                        self.uiLogArea.append('Error: %s\n' % i)
                    break
                if self.myresponse != None:
                    f.write('----- REQUEST\n')
                    f.write(self.myrequest)
                    f.write('\n')
                    num_requests += 1
                    f.write('----- RESPONSE\n')
                    f.write(self.myresponse)
                    f.write('\n')
                    num_responses += 1
                elif not self.uiMustHaveResponse:
                    f.write('----- REQUEST\n')
                    f.write(self.myrequest)
                    f.write('\n')
                    num_requests += 1                
                continue
            
            self.uiLogArea.append('Number of requests output was ' + str(num_requests) + '\n')
            self.uiLogArea.append('Number of responses output was ' + str(num_responses) + '\n')
            f.close()

    def savetoCsvFile(self,e):
        if self.uiLogArea.getText() == '':
            JOptionPane.showMessageDialog(self.tab,'The log contains no data.')
            return
        f, ok = self.openFile('csv', 'CSV files', 'w')
        if ok:
            f.write(self.uiLogArea.getText())
            f.close()
            self.uiLogArea.setText('')
            self.uiLogArea.setText('File written successfully')

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
                    f = open(myFilePath, fileparm)
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

    def clearLog(self,e):
        self.uiLogArea.setText('')
