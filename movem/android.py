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
from pynput import *

import sikuli2

class Android:
	def __init__(self, type):
		self.imgPath = os.path.abspath('.') + '\\images\\' + type + '\\'
	
	def img(self, fileName):
		return self.imgPath + fileName
	
	def clickFuncBtn(self, funcName):
		icons = []
		btnBlack = self.img(funcName) + '_black.jpg'
		btnWhite = self.img(funcName) + '_white.jpg'
		icons.append(btnBlack)
		icons.append(btnWhite)
		for count in range(0, 4):
			for icon in icons:
				if sikuli2.exists(icon):
					sikuli2.clickImage(icon)
					return
			time.sleep(0.1)

	def clickHomeBtn(self):
		self.clickFuncBtn('home')

	def clickTaskBtn(self):
		self.clickFuncBtn('task')

	def clickBackBtn(self):
		self.clickFuncBtn('back')

	def clickSearchBtn(self):
		sikuli2.clickImage(self.img('search_icon.jpg'))
	
	def clickTaskCloseBtn(self):
		sikuli2.clickImage(self.img('close.jpg'))
		time.sleep(0.2)

	def typeInSearhFrame(self, appName):
		sikuli2.clickImage(self.img('search_frame_cancel.jpg'))
		sikuli2.type(appName)

	def searchApp(self, appName):
		self.clickHomeBtn()
		self.clickSearchBtn()
		self.typeInSearhFrame(appName)
	
if __name__ == '__main__':
	import remote
	#pdb.set_trace()
	logging.basicConfig(level = logging.INFO)
	ctrl = remote.Scrcpy()
	ctrl.connect()
	android = Android('redmik20pro_miui11')
	android.searchApp('qutoutiao')
