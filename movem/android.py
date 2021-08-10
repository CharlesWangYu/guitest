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
import fnmatch

from sikuli2 import *

try:
    basestring
except NameError:
    basestring = str
	
FOOT_BAR_HORIZONTAL_OFFSET		= (90 * WORK_SCALE)
FOOT_BAR_VERTICAL_OFFSET		= (32 * WORK_SCALE)
SEARCH_ICON_HORIZONTAL_OFFSET	= (155 * WORK_SCALE)
SEARCH_ICON_VERTICAL_OFFSET		= (55 * WORK_SCALE)
TASK_CLEAR_VERTICAL_OFFSET		= (98 * WORK_SCALE)
USB_USE_CANCEL_OFFSET			= (100 * WORK_SCALE)

class Android:
	def __init__(self, UIType):
		self.imgPath	= os.path.abspath('.') + '\\images\\' + UIType + '\\'
		self.homePos	= getBottomLeft().right(int(getWidth()/2)).above(FOOT_BAR_VERTICAL_OFFSET)
		self.taskPos	= self.homePos.left(FOOT_BAR_HORIZONTAL_OFFSET)
		self.backPos	= self.homePos.right(FOOT_BAR_HORIZONTAL_OFFSET)
		self.QBtnPos	= self.homePos.left(SEARCH_ICON_HORIZONTAL_OFFSET).above(SEARCH_ICON_VERTICAL_OFFSET)
		self.XBtnPos	= self.homePos.above(TASK_CLEAR_VERTICAL_OFFSET)
		self.xUSBPos	= self.homePos.above(FOOT_BAR_HORIZONTAL_OFFSET)
		setTimeout(1)
	
	def img(self, fileName):
		return self.imgPath + fileName
	
	def isFuncBtnShown(self):
		for fileName in os.listdir(self.imgPath):
			if fnmatch.fnmatchcase(fileName, 'home*.jpg'):
				if existImage(self.img(fileName)):
					return True
		return None

	def clickHomeBtn(self):
		clickPosition(self.homePos)

	def clickTaskBtn(self):
		clickPosition(self.taskPos)

	def clickBackBtn(self):
		clickPosition(self.backPos)

	def clickSearchBtn(self):
		clickPosition(self.QBtnPos)
	
	def clickTaskClearBtn(self):
		clickPosition(self.XBtnPos)
		time.sleep(0.5)
	
	def cancelBlackScreen(self):
		if existImage(self.img('black_sreen.jpg')):
			hoverPosition(getCenter())
			rightClick()
		if existImage(self.img('connected_usb.jpg')):
			hoverPosition(getCenter())
			flickUp()
	
	def closeUSBUseDlg(self):
		if existImage(self.img('usb_use.jpg')):
			clickPosition(self.xUSBPos)

	def typeInSearhFrame(self, text):
		clickImage(self.img('search_frame_cancel.jpg'))
		typeChar(text)
	
class App: # Abstract class
	def __init__(self, android):
		self.android = android
		self.imgPath = ''
		self.android.cancelBlackScreen()
		self.android.closeUSBUseDlg()
	
	def img(self, imgName):
		return self.imgPath + imgName
	
	def open(self):
		self.android.clickHomeBtn()
		self.android.clickTaskBtn()
		if not self.clickAfterSeeingSth('icon', DIRECTION_DOWN, 100):
			self.android.clickHomeBtn()
			self.android.clickSearchBtn()
			icon = self.findPolymorphicImage('icon')
			if icon is None:
				appName = self.__class__.__name__
				self.android.typeInSearhFrame(appName.lower())
				icon = self.findPolymorphicImage('icon')
				if icon is None:
					print(appName + ' has not been installed in this andriod.')
					return
			assert not icon is None
			self.clickAfterSeeingSth(icon)
		self.initScreen()
	
	def close(self):
		self.android.clickHomeBtn()
		self.android.clickTaskBtn()
		self.android.clickTaskClearBtn()
	
	def initScreen(self):
		pass
	
	def hoverCenter(self):
		hoverPosition(getCenter())
	
	def findPolymorphicImage(self, imgName):
		if re.search('\.', imgName): # determined image file name
			if existImage(self.img(imgName)):
				return imgName
			else : 
				return None
		else: # ambiguous image file name
			for fileName in os.listdir(self.imgPath):
				if fnmatch.fnmatchcase(fileName, imgName + '*.jpg'):
					if existImage(self.img(fileName)):
						return fileName
			return None
	
	'''
	def findAllPolymorphicImage(self, imgName):
		if re.search('\.', imgName): # determined image file name
			return findAll(self.img(imgName))
		else: # ambiguous image file name
			for fileName in os.listdir(self.imgPath):
				if fnmatch.fnmatchcase(fileName, imgName + '*.jpg'):
					return findAll(self.img(fileName))
			return []
	'''
	
	def clickPolymorphicImage(self, imgName):
		if re.search('\.', imgName): # determined image file name
			clickImage(self.img(imgName))
		else: # ambiguous image file name
			for fileName in os.listdir(self.imgPath):
				if fnmatch.fnmatchcase(fileName, imgName + '*.jpg'):
					if clickImage(self.img(fileName)):
						return True
			return False
	
	def clickAfterSeeingSth(self, imgName, direction=None, offset=0, delay=0, target=None):
		'''
		This method used to click target after the image has been found.
		The target of click can be a image or a certain area or location.
		Args:
			imgName		: image file name for the Pattern in lacky
			direction	: Offset direction
			offset		: Offset when clicked
			delay		: The delay from the finding image to clicking
			target		: Pattern or Region or Location in lacky or (x,y)
						  The default is the image found
		Return:
			Boolean		: Whether the find and click operation is successful
		'''
		assert target is None or isinstance(target, basestring) or isinstance(target, lacky.Region) or isinstance(target, lacky.Location) or isinstance(target, tuple)
		
		imgFile = self.findPolymorphicImage(imgName)
		if imgFile is None: return False # can't find source image in panel
		# init target
		if target is None:
			targetPos = getImageArea(self.img(imgFile)).getCenter()
		elif isinstance(target, basestring):
			clickTarget = self.findPolymorphicImage(target)
			if clickTarget is None: return False # can't find target image in panel
			targetPos = getImageArea(self.img(clickTarget)).getCenter()
		elif isinstance(target, lacky.Region):
			targetPos = target.getCenter()
		elif isinstance(target, lacky.Location):
			targetPos = target
		elif isinstance(target, tuple):
			targetPos = lacky.Location(target)
		# calculate shift
		if not direction is None:
			if direction == DIRECTION_UP:
				targetPos = targetPos.above(offset)
			elif direction == DIRECTION_DOWN:
				targetPos = targetPos.below(offset)
			elif direction == DIRECTION_LEFT:
				targetPos = targetPos.left(offset)
			elif direction == DIRECTION_RIGHT:
				targetPos = targetPos.right(offset)
		# delay and click target
		if delay != 0 : time.sleep(delay)
		return clickPosition(targetPos)
	
class Task:
	def __init__(self, app):
		self.app = app
	
	def execute(self):
		pass
	
if __name__ == '__main__':
	import remote
	#pdb.set_trace()
	logging.basicConfig(level = logging.INFO)
	ctrl = remote.Scrcpy()
	ctrl.connect()
	android = Android('redmik20pro_miui11')
	android.clickHomeBtn()
	android.clickTaskBtn()
	android.clickTaskClearBtn()
