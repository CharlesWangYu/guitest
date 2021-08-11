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
import re
import os
import time
import fnmatch

from sikuli2 import *

try:
    basestring
except NameError:
    basestring = str

FOOT_BAR_X_OFFSET		= 90
FOOT_BAR_Y_OFFSET		= 32
SEARCH_ICON_X_OFFSET	= 155
SEARCH_ICON_Y_OFFSET	= 55
TASK_CLEAR_Y_OFFSET		= 98
USB_USE_CANCEL_OFFSET	= 100

class Android:
	def __init__(self, UIType):
		self.imgPath	= os.path.abspath('.') + '\\images\\' + UIType + '\\'
		self.homePos	= shiftPos(getBottomLeft(), SHIFT_RIGHT, int(getWidth()/2))
		self.homePos	= shiftPos(self.homePos, SHIFT_UP, FOOT_BAR_Y_OFFSET)
		self.taskPos	= shiftPos(self.homePos, SHIFT_LEFT,  FOOT_BAR_X_OFFSET)
		self.backPos	= shiftPos(self.homePos, SHIFT_RIGHT, FOOT_BAR_X_OFFSET)
		self.QBtnPos	= shiftPos(self.homePos, SHIFT_LEFT, SEARCH_ICON_X_OFFSET)
		self.QBtnPos	= shiftPos(self.QBtnPos, SHIFT_UP, SEARCH_ICON_Y_OFFSET)
		self.XBtnPos	= shiftPos(self.homePos, SHIFT_UP, TASK_CLEAR_Y_OFFSET)
		#self.xUSBPos	= shiftPos(self.homePos, SHIFT_UP, FOOT_BAR_Y_OFFSET)
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
		clickPos(self.homePos)

	def clickTaskBtn(self):
		clickPos(self.taskPos)

	def clickBackBtn(self):
		clickPos(self.backPos)

	def clickSearchBtn(self):
		clickPos(self.QBtnPos)
	
	def clickTaskClearBtn(self):
		clickPos(self.XBtnPos)
		time.sleep(0.5)
	
	def unlockScreen(self):
		if existImage(self.img('black_sreen.jpg')):
			hoverPos(getCenter())
			rightClick()
		if existImage(self.img('connected_usb.jpg')):
			hoverPos(getCenter())
			flickUp()
		if existImage(self.img('wait_unlock.jpg')):
			typeChar('771130')
	
	'''
	def closeUSBUseDlg(self):
		if existImage(self.img('usb_use.jpg')):
			clickPos(self.xUSBPos)
	'''
	
	def typeInSearchBar(self, text):
		clickImage(self.img('search_frame_cancel.jpg'))
		typeChar(text)
	
class App: # Abstract class
	def __init__(self, android):
		self.android = android
		self.imgPath = ''
		self.android.unlockScreen()
		#self.android.closeUSBUseDlg()
	
	def img(self, imgName):
		return self.imgPath + imgName
	
	def findImage(self, imgName):
		if re.search('\.', imgName): # determined search with full image file name
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
	
	'''
	def findAllPolymorphicImage(self, imgName):
		if re.search('\.', imgName): # determined image file name
			return findAll(self.img(imgName))
		else: # ambiguous image file name
			for fileName in os.listdir(self.imgPath):
				if fnmatch.fnmatchcase(fileName, imgName + '*.jpg'):
					return findAll(self.img(fileName))
			return []
	
	def clickPolymorphicImage(self, imgName):
		if re.search('\.', imgName): # determined image file name
			clickImage(self.img(imgName))
		else: # ambiguous image file name
			for fileName in os.listdir(self.imgPath):
				if fnmatch.fnmatchcase(fileName, imgName + '*.jpg'):
					if clickImage(self.img(fileName)):
						return True
			return False
	'''
	
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
	'''
	def foundThenClick(self, imgName, direction=None, offset=0, delay=0, target=None):
		assert target is None or isinstance(target, basestring) or isinstance(target, lacky.Region) or isinstance(target, lacky.Location) or isinstance(target, tuple)
		
		imgFile = self.findImage(imgName)
		if imgFile is None: return False # can't find source image in panel
		# init target
		if target is None:
			targetPos = getImageArea(self.img(imgFile)).getCenter()
		elif isinstance(target, basestring):
			clickTarget = self.findImage(target)
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
			if direction == SHIFT_UP:
				targetPos = targetPos.above(offset)
			elif direction == SHIFT_DOWN:
				targetPos = targetPos.below(offset)
			elif direction == SHIFT_LEFT:
				targetPos = targetPos.left(offset)
			elif direction == SHIFT_RIGHT:
				targetPos = targetPos.right(offset)
		# delay and click target
		if delay != 0 : time.sleep(delay)
		return clickPos(targetPos)
	'''
	
	def foundThenClick(self, imgName, direction=None, offset=0):
		imgFile = self.findImage(imgName)
		if imgFile is None: return False # can't find source image in panel
		targetPos = getImageArea(self.img(imgFile)).getCenter()
		if direction is not None:
			targetPos = shiftPos(targetPos, direction, offset)
		#time.sleep(0.1)
		return clickPos(targetPos)
	
	def open(self):
		self.android.clickHomeBtn()
		self.android.clickTaskBtn()
		if not self.foundThenClick('icon', SHIFT_DOWN, 100):
			self.android.clickHomeBtn()
			self.android.clickSearchBtn()
			icon = self.findImage('icon')
			if icon is None:
				appName = self.__class__.__name__
				self.android.typeInSearchBar(appName.lower())
				icon = self.findImage('icon')
				if icon is None:
					logging.info('APP "' + appName + '" hasn\'t been installed on this andriod device.')
			assert not icon is None
			self.foundThenClick(icon)
		self.initScreen()
	
	def close(self):
		self.android.clickHomeBtn()
		self.android.clickTaskBtn()
		self.android.clickTaskClearBtn()
	
	def initScreen(self):
		pass
	
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
	android = Android('M2007J17C_V125')
	android.clickHomeBtn()
	android.clickTaskBtn()
	android.clickTaskClearBtn()
