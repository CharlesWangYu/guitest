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
import re
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
		with open(self.getReportPath(), 'w', newline='', encoding='UTF-8') as reportFile:
			reportFile.write(message + '\r\n')
			logging.info(message)

	def checkAllLogFiles(self, Keyword = 'Error'):
		self.clearReportFile()
		self.writeReportFile('======================== Begin of the Report ========================')
		self.writeReportFile('ReportPath = ' + self.getReportPath())
		self.writeReportFile('ReportData = ' + datetime.datetime.now().strftime('%Y-%m-%d'))
		self.writeReportFile('ReportTime = ' + datetime.datetime.now().strftime('%H:%M:%S'))

		for root, dirs, files in os.walk(self.getLogsPath()):
			for file in files:
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
				for lineTxt in fileTxt.readlines():
					lineNum = lineNum+1
					matchReult = re.search(Keyword, lineTxt, flags=0)
					if matchReult:
						self.writeReportFile('[Line ' + str(lineNum) + ']: ' + lineTxt.replace('\n', ''))
						lineErr = lineErr+1
				self.writeReportFile('As shown above, there are ' + str(lineErr) + ' lines have [' + Keyword + '], please check...')
		else:
			self.writeReportFile('Error：Can not find the file!')


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
	logging.info('==========================================================')
	logging.info('[Start logging] : ' + datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S'))
	rrte.clearLogs()
	rrte.clearOutput()
	rrte.getRRTE_Logs(rrte.root)
	logging.info('[Stop logging] : ' + datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S'))
	logging.info('==========================================================')
	# Confirm error information in log files
	check = logResultCheck()
	check.checkAllLogFiles('Entry')
