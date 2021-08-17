# -*-coding:utf-8 -*-
'''
@File		: py
@Date		: 2021/01/01
@Author		: Wang.Yu
@Version	: 1.0
@Contact	: ouu_cn@163.com
@License	: (C)Copyright 2021, Personal exclusive right.
'''
import pdb
import logging
import re
import os
import time
import fnmatch
from configparser import ConfigParser

from sikuli2 import *

try:
    basestring
except NameError:
    basestring = str

EXECUTION_BACKGROUND	= 0
EXECUTION_FOREGROUND	= 1
FOOT_BAR_X_OFFSET		= 90
FOOT_BAR_Y_OFFSET		= 32
SEARCH_ICON_X_OFFSET	= 155
SEARCH_ICON_Y_OFFSET	= 55
TASK_CLEAR_Y_OFFSET		= 98
USB_USE_CANCEL_OFFSET	= 100
MULTI_TASK_Y_OFFSET		= 50
TOP_SEARCH_Y_OFFSET		= 30
TOP_SEARCH_H_OFFSET		= 700
	
class App: # Abstract class
	def __init__(self, platform):
		self.pltPath = os.path.abspath('.') + '\\res\\platform\\' + platform + '\\'
		self.homePos = shiftPos(getBottomLeft(), SHIFT_RIGHT, int(getWidth()/2))
		self.homePos = shiftPos(self.homePos, SHIFT_UP, FOOT_BAR_Y_OFFSET)
		self.taskPos = shiftPos(self.homePos, SHIFT_LEFT,  FOOT_BAR_X_OFFSET)
		self.backPos = shiftPos(self.homePos, SHIFT_RIGHT, FOOT_BAR_X_OFFSET)
		self.QBtnPos = shiftPos(self.homePos, SHIFT_LEFT, SEARCH_ICON_X_OFFSET)
		self.QBtnPos = shiftPos(self.QBtnPos, SHIFT_UP, SEARCH_ICON_Y_OFFSET)
		self.XBtnPos = shiftPos(self.homePos, SHIFT_UP, TASK_CLEAR_Y_OFFSET)
		self.config  = ConfigParser()
		self.config.read(self.pltPath + '_user_info.cfg', encoding='UTF-8')
		self.imgPath = ''
		setTimeout(1)
		setMoveMouseDelay(0.3)
	
	def __platImg(self, fileName):
		return self.pltPath + fileName
	
	def img(self, imgName):
		return self.imgPath + imgName
	
	def findFirstImage(self, imgName):
		if re.search('\\.', imgName): # determined search with full image file name
			if existImage(self.img(imgName)):
				return imgName
			else : 
				return None
		else: # fuzzy search with key word in image file name
			for fileName in os.listdir(self.imgPath):
				if fnmatch.fnmatchcase(fileName, imgName + '*.jpg'):
					if existImage(self.img(fileName)):
						return fileName
			return None
		
	def findAllImage(self, imgName):
		if re.search('\\.', imgName): # determined image file name
			return findImages(self.img(imgName))
		else: # ambiguous image file name
			for fileName in os.listdir(self.imgPath):
				if fnmatch.fnmatchcase(fileName, imgName + '*.jpg'):
					return findImages(self.img(fileName))
			return []
	
	def foundThenClick(self, imgName, direction=None, offset=0):
		imgFile = self.findFirstImage(imgName)
		if imgFile is None:
			return False # can't find source image in panel
		imageArea = getImageArea(self.img(imgFile))
		if getWidth(imageArea) + getHeight(imageArea) == 0:
			logging.info('Image %s has been disappeared.' % imgFile)
			return False
		targetPos = imageArea.getCenter()
		if direction is not None:
			targetPos = shiftPos(targetPos, direction, offset)
		#time.sleep(0.1)
		clickPos(targetPos)
		return True
	
	def clickAndroidHomeBtn(self):
		clickPos(self.homePos)
	
	def clickAndroidTaskBtn(self):
		clickPos(self.taskPos)
	
	def clickAndroidBackBtn(self):
		clickPos(self.backPos)
	
	def clickAndroidSearchBtn(self):
		clickPos(self.QBtnPos)
	
	def clickAndroidTaskClearBtn(self):
		clickPos(self.XBtnPos)
	
	def unlockScreen(self):
		if existImage(self.__platImg('black_sreen.jpg')):
			hoverPos(getCenter())
			rightClick()
		for fileName in os.listdir(self.pltPath):
			if fnmatch.fnmatchcase(fileName, 'lock_usb_debug*.jpg'):
				if existImage(self.__platImg(fileName)):
					hoverPos(getCenter())
					flickUp()
		for fileName in os.listdir(self.pltPath):
			if fnmatch.fnmatchcase(fileName, 'wait_unlock*.jpg'):
				if existImage(self.__platImg(fileName)):
					typeChar(self.config['MISC']['PASSWORD'])
	
	def typeInSearchBar(self, text):
		# calculate top search bar position
		x = getTopLeftX()
		y = getTopLeftY() - scaleLength(TOP_SEARCH_Y_OFFSET)
		w = getWidth()
		h = getHeight() - scaleLength(TOP_SEARCH_H_OFFSET)
		topSearchBar = scaleArea(x, y, w, h)
		# click and type action
		self.clickAndroidSearchBtn()
		time.sleep(0.2)
		clickImage(self.__platImg('x_in_top_search_bar.jpg'), topSearchBar)
		time.sleep(0.3)
		clickImage(self.__platImg('key_input_eng_chi.jpg'))
		time.sleep(0.2)
		#typeChar(text)
		pasteChar(text)
		time.sleep(0.2)
	
	def start(self):
		self.clickAndroidHomeBtn()
		time.sleep(0.8)
		appName = self.__class__.__name__
		self.typeInSearchBar(appName.lower())
		icon = self.findFirstImage('icon_small')
		if icon is None:
			logging.info('APP "' + appName + '" hasn\'t been installed on this andriod device.')
		assert(icon != None)
		self.foundThenClick(icon)
		self.initEntry()
	
	def stop(self):
		self.clickAndroidHomeBtn()
		time.sleep(0.2)
		self.clickAndroidTaskBtn()
		time.sleep(0.3)
	
	def clearAll(self):
		self.clickAndroidHomeBtn()
		time.sleep(0.2)
		self.clickAndroidTaskBtn()
		time.sleep(0.3)
		self.clickAndroidTaskClearBtn()
		time.sleep(0.5)
	
	def initEntry(self):
		# If program go here, APP has been started.
		# Maybe APP is necessary to wait for clearing rubbish message.
		# This method should be implement in subclass.
		pass
	
class Task:
	def __init__(self, app):
		self.app = app
	
	def execute(self):
		pass
	
class UnlockSmartPhone(Task):
	def execute(self):
		self.app.unlockScreen()
	
class ClearActiveApp(Task):
	def execute(self):
		self.app.clearAll()
	
if __name__ == '__main__':
	import remote
	#pdb.set_trace()
	logging.basicConfig(level = logging.INFO)
	ctrl = remote.Scrcpy()
	ctrl.connect()
	app = App(ctrl.platform())
	app.unlockScreen()
	app.typeInSearchBar('京东')
	'''
	app.clickAndroidHomeBtn()
	app.clickAndroidTaskBtn()
	app.clickAndroidTaskClearBtn()
	ctrl.disconnect()
	'''
