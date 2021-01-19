# -*-coding:utf-8 -*-
'''
@File		: android.py
@Date		: 2021/01/01
@Author		: Wang.Yu
@Version	: 1.0
@Contact	: ouu_cn@163.com
@License	: (C)Copyright 2021, Personal exclusive right.
'''
import pdb
import logging
import os
import time
from numpy import *

import sikuli2

FOOT_BAR_HORIZONTAL_OFFSET		= 90
FOOT_BAR_VERTICAL_OFFSET		= 32
SEARCH_ICON_HORIZONTAL_OFFSET	= 155
SEARCH_ICON_VERTICAL_OFFSET		= 55
TASK_CLEAR_VERTICAL_OFFSET		= 98

class Android:
	def __init__(self, type):
		self.imgPath		= os.path.abspath('.') + '\\images\\' + type + '\\'
		self.homeBtnPos		= sikuli2.getBottomLeft().right(int(sikuli2.getWidth()/2)).above(FOOT_BAR_VERTICAL_OFFSET)
		self.taskBtnPos		= self.homeBtnPos.left(FOOT_BAR_HORIZONTAL_OFFSET)
		self.backBtnPos		= self.homeBtnPos.right(FOOT_BAR_HORIZONTAL_OFFSET)
		self.searchIconPos	= self.homeBtnPos.left(SEARCH_ICON_HORIZONTAL_OFFSET).above(SEARCH_ICON_VERTICAL_OFFSET)
		self.taskClearPos	= self.homeBtnPos.above(TASK_CLEAR_VERTICAL_OFFSET)
		sikuli2.setTimeout(1)
	
	def img(self, fileName):
		return self.imgPath + fileName

	def clickHomeBtn(self):
		sikuli2.clickPosition(self.homeBtnPos)

	def clickTaskBtn(self):
		sikuli2.clickPosition(self.taskBtnPos)

	def clickBackBtn(self):
		sikuli2.clickPosition(self.backBtnPos)

	def clickSearchBtn(self):
		sikuli2.clickPosition(self.searchIconPos)
	
	def clickTaskClearBtn(self):
		sikuli2.clickPosition(self.taskClearPos)
		time.sleep(0.5)

	def typeInSearhFrame(self, appName):
		sikuli2.clickImage(self.img('search_frame_cancel.jpg'))
		sikuli2.type(appName)

	def searchApp(self, appName):
		self.clickHomeBtn()
		self.clickSearchBtn()
		if exists(app.img('sign_success.jpg')) :
			self.typeInSearhFrame(appName)
	
if __name__ == '__main__':
	import remote
	#pdb.set_trace()
	logging.basicConfig(level = logging.INFO)
	ctrl = remote.Scrcpy()
	ctrl.connect()
	android = Android('redmik20pro_miui11')
	#android.searchApp('qutoutiao')
	android.clickHomeBtn()
	android.clickTaskBtn()
	android.clickTaskClearBtn()
