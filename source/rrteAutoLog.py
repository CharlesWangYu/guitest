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
import datetime
from host import *
from rrte import *

######TextCheck#######
class TextCheck:
	def __init__(self):
		self.config = ConfigParser()
		self.config.read('test.conf', encoding='UTF-8')

	def checkAllLogFiles(self, Keyword = 'Error'):
		logPath = self.config['MISC']['OUTPUT_PATH'].strip("'")
		logPath = logPath + '\\'
		reportPath = logPath + 'CheckReport.txt'
		if os.path.isfile(reportPath):
			os.remove(reportPath)
		checkReort ='============ Begin of the Report ============ \r\n'
		checkReort = checkReort + 'ReportPath = ' + logPath + '\r\n'
		checkReort = checkReort + 'ReportData = ' + datetime.datetime.now().strftime('%Y-%m-%d')  + '\r\n'
		checkReort = checkReort + 'ReportTime = ' + datetime.datetime.now().strftime('%H:%M:%S')  + '\r\n'
		logging.info(checkReort)
		for root, dirs, files in os.walk(logPath):
			for file in files:
				filePath = os.path.join(root, file).encode('utf-8')
				logging.info('------------------------------------------')
				logging.info('Find Out File: %s' %(filePath))
				checkReort = checkReort + '------------------------------------------------------------------\r\n'
				checkReort = checkReort + self.checkOneLogFile(Keyword, filePath)

		checkReort = checkReort + '============ End of the Report ============'
		with open(reportPath, 'w', newline='', encoding='UTF-8') as reportFile:
			reportFile.write(checkReort)

	def checkOneLogFile(self, Keyword, filePath):
		checkResult = ''
		if os.path.exists(filePath):
			message = 'FilePath = ' + str(filePath)
			checkResult = checkResult + message + '\r\n'
			message = '>>>Start to check file'
			checkResult = checkResult + message + '\r\n'
			with open(filePath, 'r', encoding='UTF-8')as fileTxt:
				lineNum = 0
				lineErr = 0
				for lineTxt in fileTxt.readlines():
					lineNum = lineNum+1
					matchReult = re.search(Keyword, lineTxt, flags=0)
					if matchReult:
						message = '[Line ' + str(lineNum) + ']: ' + lineTxt.replace('\n', '')
						checkResult = checkResult + message + '\r\n'
						lineErr = lineErr+1
				message = 'As shown above, there are ' + str(lineErr) + ' lines have [' + Keyword + '], please check...'
				checkResult = checkResult + message + '\r\n'
			message = '>>>Completed checking file'
			checkResult = checkResult + message + '\r\n'
		else:
			message ='Error：Can not find the file!'
			checkResult = checkResult + message + '\r\n'
		logging.info(checkResult)
		return checkResult

if __name__ == '__main__':
	#pdb.set_trace()
	logging.basicConfig(level = logging.INFO)
	# Create tree information from RRTE
	top = RRoot('root')
	top.ctrlType = ''
	top.rectangle = None
	top.path = [top]
	root = TreeNode(top)
	rrte = RRTE(root)
	if not os.path.exists('./tree.bin'):
		logging.info('[Start RRTE] : ' + datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S'))
		rrte.startUp()
		rrte.createTree(rrte.root)
		logging.info('[Finished tree generation] : ' + datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S'))
		rrte.serialize()
		rrte.exit()
	else:
		logging.info('[Restore tree generation] : ' + datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S'))
		rrte.restore()
	# Get logging
	logging.info('[Start logging] : ' + datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S'))
	rrte.clearLogs()
	rrte.clearOutput()
	rrte.getLogByScreen(rrte.root)
	#rrte.getLogByRootMenu(rrte.root)
	logging.info('[Stop logging] : ' + datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S'))
	#logging.info('>>>>>> Log getting finished')
	#logging.info('==========================================================')
	# Confirm error information in log files
	#text = TextCheck()
	#text.checkAllLogFiles('Entry')
