'''
@File		: rrteAutoLog.py
@Date		: 2020/09/20
@Author		: Wang.Yu
@Version	: 1.0
@Contact	: yu.wang@cn.yokogawa.com
@License	: (C)Copyright 2020 Yokogawa China Co., Ltd.
'''
#import pdb
#import logging
import os
import shutil
import datetime
import re
from configparser import ConfigParser
from host import *
from rrte import *

class logResultCheck:
	logPath =  None
	reportFile = None

	def __init__(self):
		self.config = ConfigParser()
		self.config.read('test.conf', encoding='UTF-8')

	def getLogsPath(self):
		logsPath = self.config['COMM']['OUTPUT_FILE_PATH'].strip("'") + '\\'
		return logsPath

	def getReportPath(self):
		reportPath = self.getLogsPath() + 'CheckReport.txt'
		return reportPath

	def clearReportFile(self):
		if os.path.isfile(self.getReportPath()):
			os.remove(self.getReportPath())

	def writeReportFile(self, message):
		with open(self.getReportPath(), 'a+', newline='', encoding='UTF-8') as reportFile:
			reportFile.write(message + '\r\n')
			logging.info(message)

	def checkAllLogFiles(self):
		self.clearReportFile()
		self.writeReportFile('======================== Begin of the Report ========================')
		self.writeReportFile('ReportPath = ' + self.getReportPath())
		self.writeReportFile('ReportData = ' + datetime.datetime.now().strftime('%Y-%m-%d'))
		self.writeReportFile('ReportTime = ' + datetime.datetime.now().strftime('%H:%M:%S'))
		for root, dirs, files in os.walk(self.getLogsPath()):
			for file in files:
				Keyword = ''
				if os.path.basename(file) == 'AuditTrail.log':
					Keyword = self.config['LOG_ERR']['AUDIT_TRAIL'].strip("'")
				elif os.path.basename(file) == 'DefaultLogger.log':
					Keyword = self.config['LOG_ERR']['DEFAULT_LOGGER'].strip("'")
				elif os.path.basename(file) == 'DMS.log':
					Keyword = self.config['LOG_ERR']['DMS'].strip("'")
				elif os.path.basename(file) == 'FdiContainer.log':
					Keyword = self.config['LOG_ERR']['FDI_CONTAINER'].strip("'")
				elif os.path.basename(file) == 'FDIOPCUACLIENT.log.txt':
					Keyword = self.config['LOG_ERR']['FDIOPCUACLIENT'].strip("'")
				elif os.path.basename(file) == 'HARTModemDriver.log':
					Keyword = self.config['LOG_ERR']['HART_MODEM_DRIVER'].strip("'")
				elif os.path.basename(file) == 'InformationModelServer.log':
					Keyword = self.config['LOG_ERR']['INFORMATION_MODEL_SERVER'].strip("'")
				elif os.path.basename(file) == 'ReferenceHost.log':
					Keyword = self.config['LOG_ERR']['REFERENCE_HOST'].strip("'")
				elif os.path.basename(os.path.join(root, file).encode('utf-8')) == 'StdErrXmtrDD.Log':
					os.remove(file)
				elif os.path.basename(os.path.join(root, file).encode('utf-8')) == 'StdOutXmtrDD.Log':
					os.remove(file)
				elif os.path.basename(os.path.join(root, file).encode('utf-8')) == 'StdXmtrDD.Log':
					os.remove(file)
				elif os.path.basename(file) == 'Trace.log':
					Keyword = self.config['LOG_ERR']['TRACE'].strip("'")
				else:
					continue
				filePath = os.path.join(root, file).encode('utf-8')
				self.checkOneLogFile(Keyword, filePath)
		self.writeReportFile('======================== End of the Report ========================')

	def checkOneLogFile(self, Keyword, filePath):
		if os.path.exists(filePath):
			self.writeReportFile('-------------------------------------------------------------------')
			self.writeReportFile('Checking Log = ' + str(filePath))
			with open(filePath, 'r', encoding='UTF-8')as fileTxt:
				lineNum = 0
				lineErr = 0
				pattern = re.compile(r'' + Keyword + '')
				for lineTxt in fileTxt.readlines():
					lineNum = lineNum+1
					matchReult = re.search(pattern, lineTxt, flags=0)
					if matchReult:
						self.writeReportFile('[Line ' + str(lineNum) + ']: ' + lineTxt.replace('\n', ''))
						lineErr = lineErr+1
				self.writeReportFile('As shown above, there are ' + str(lineErr) + ' lines have [' + Keyword + '], please check...')
		else:
			self.writeReportFile('Error：Can not find the file!')

class RRTELog(RRTE):
	# If the correct variable value need to be obtained when the tree structure is established, you need to judge whether the data synchronization operation has been completed in the RRTE screen.
	'''
	def createTree(self, target):
		assert not target == None
		assert not target.elem.isLeaf()
		# migrate to the target screen
		for item in target.elem.path:
			item.select()
		# append children node to the target node
		# wait for parameter synchronization.
		#timeReadParam = int(self.config['LOG']['LOG_LOADING_TIME'].strip("'"))
		#time.sleep(timeReadParam)
		target.appendChildren()
		Host.logTreeItem(target)
		currNode = target.left
		if not currNode is None:
			if not currNode.elem.isLeaf():
				self.createTree(currNode)
			currNode = currNode.right
			while not currNode == None:
				if not currNode.elem.isLeaf():
					self.createTree(currNode)
				currNode = currNode.right
	'''
	
	def startUp(self, cmd=None):
		inputMode = self.config['COMM']['FCG_FILE_TYPE'].strip("'")
		hostApp	= self.config['COMM']['HOST_APP_PATH'].strip("'") + '\Reference Run-time Environment\Fdi.Reference.Client.exe'
		testFile = self.config['COMM']['FCG_FILE'].strip("'")
		outPath = self.config['COMM']['OUTPUT_FILE_PATH'].strip("'")
		execCmd = '\"' + hostApp + '\" -l \"' + testFile + '\"'
		super(RRTELog, self).startUp(execCmd)

	def copyLogs(self, folderName):
		logPath = self.config['LOG']['RRTE_LOG_PATH'].strip("'")
		outPath = self.config['COMM']['OUTPUT_FILE_PATH'].strip("'")
		outPath = outPath + '\\' + folderName
		if os.path.exists(logPath):
			shutil.copytree(logPath, outPath)

	def clearLogs(self):
		logPath = self.config['LOG']['RRTE_LOG_PATH'].strip("'")
		if os.path.exists(logPath):
			shutil.rmtree(logPath)

	def clearOutput(self):
		outPath = self.config['COMM']['OUTPUT_FILE_PATH'].strip("'")
		if os.path.exists(outPath):
			shutil.rmtree(outPath)

	def getLogs(self, node):
		SeparateLogs = self.config['LOG']['LOG_SEPARATED'].strip("'")
		if SeparateLogs == 'ON':
			self.getLogsByScreen(node)
		else:
			self.getLogsByRootMenu(node)

	def getLogsByScreen(self, node):
		timeReadParam = int(self.config['LOG']['LOG_LOADING_TIME'].strip("'"))
		if node == None or node.elem == None:
			return
		if isinstance(node.elem, RWindow) or isinstance(node.elem, RPage):
			RRTELog.logNormal(node)
			if RRTE.isNeedToGetLog(node):
				self.startUp()
				#self.setTraceLevel('Verbose')
				node.selectTargetNode()
				time.sleep(timeReadParam)
				if self.writeParam(node.left):
					self.pushBtnApply()
				self.exit()
				self.copyLogs(node.getPathName())
				self.clearLogs()
		self.getLogsByScreen(node.left)
		self.getLogsByScreen(node.right)

	def getLogsByRootMenu(self, node):
		node = node.left
		while node != None and node.elem != None:
			self.startUp()
			# self.setTraceLevel('Verbose')
			RRTELog.logNormal(node)
			node.selectTargetNode()
			self.getLogsOfRootMenu(node.left)
			self.exit()
			self.copyLogs(node.getPathName())
			self.clearLogs()
			node = node.right

	def getLogsOfRootMenu(self, node):
		timeReadParam = int(self.config['LOG']['LOG_LOADING_TIME'].strip("'"))
		if node == None or node.elem == None:
			return
		if isinstance(node.elem, RWindow) or isinstance(node.elem, RPage):
			logging.info('[Switch screen. Path = \"%s\" (%s)]' % (node.getPathName(), node.elem.ctrlType))
			if RRTE.isNeedToGetLog(node):
				for item in node.elem.path:
					item.select()
				time.sleep(timeReadParam)
				if self.writeParam(node.left):
					self.pushBtnApply()
		self.getLogsOfRootMenu(node.left)
		self.getLogsOfRootMenu(node.right)

	def writeParam(self, node):
		writeFlg = False
		if node == None or node.elem == None:
			return writeFlg
		logging.info('Type = [%s],\tRO = %s,\tLabel = %s,\t\tValue = %s' %(node.elem.ctrlType, node.elem.getROAttrStr(), node.elem.label, node.elem.getCurrValStr()))
		if isinstance(node.elem, RVariable):
			if not node.elem.readonly:
				writeFlg = True
				time.sleep(0.1) # Do not move this line. It will cause failure that the apply button can not be pushed.
				anchor = node.elem.path[-2].getAnchorAfterSelect()
				param = findFirstElemBySubText(anchor, node.elem.label)
				assert isUIAElem(param)
				if isinstance(node.elem, REnum):
					setComboboxCurrVal(param, node.elem.currentVal)
				elif isinstance(node.elem, RBitEnum):
					setGroupCheckboxCurrVal(param)
				else: # Variable other than enum and bitenum, including text, numbers, date and time
					setEditboxCurrVal(param, node.elem.currentVal)
		if isinstance(node.elem, RGroup):
			rtn = self.writeParam(node.left)
			writeFlg = rtn or writeFlg
		rtn = self.writeParam(node.right)
		writeFlg = rtn or writeFlg
		return writeFlg
	
	@staticmethod
	def logNormal(node):
		logging.info('----------------------------------------------------------')
		logging.info('[Start a set of captures. Path = \"%s\" (%s)]' % (node.getPathName(), node.elem.ctrlType))
	
	@staticmethod
	def logAbnormal(node):
		logging.info('----------------------------------------------------------')
		logging.info('[No need to capture log. Path = \"%s\" (%s)]' % (node.getPathName(), node.elem.ctrlType))

if __name__ == '__main__':
	#pdb.set_trace()
	logging.basicConfig(level = logging.INFO)
	# Create tree information from RRTE
	config = ConfigParser()
	config.read('test.conf', encoding='UTF-8')
	top = RRoot('root')
	top.ctrlType = ''
	top.rectangle = None
	top.path = [top]
	root = TreeNode(top)
	rrte = RRTELog(config, root)
	if not rrte.isDesTreeSerialized():
		logging.info('[Start tree generation.] : ' + datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S'))
		rrte.startUp()
		rrte.createTree(rrte.root)
		logging.info('[Finished tree generation.] : ' + datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S'))
		rrte.serializeDesTree()
		rrte.exit()
	else:
		logging.info('[Restore tree generation.] : ' + datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S'))
		rrte.restoreDesTree()
	# Get logging
	logging.info('[Start logging.] : ' + datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S'))
	rrte.clearLogs()
	rrte.clearOutput()
	rrte.getLogs(rrte.root)
	logging.info('[Stop logging.] : ' + datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S'))
	# Confirm error information in log files
	check = logResultCheck()
	check.checkAllLogFiles()
