# -*-coding:utf-8 -*-
'''
@File		: task.py
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
import re

import uia2
import sikuli2
import android # remote connect in this package

try:
    basestring
except NameError:
    basestring = str

class App: # Abstract class
	ABOVE	= 0
	BELOW	= 1
	LEFT	= 2
	RIGHT	= 3
	
	def __init__(self, android):
		self.panel = android
		self.imgPath = ''
		self.panel.cancelBlackScreen()
		self.panel.closeUSBUseDlg()
	
	def img(self, imgName):
		return self.imgPath + imgName
	
	def open(self):
		self.panel.clickHomeBtn()
		self.panel.clickTaskBtn()
		if not self.clickAfterSeeingSth('icon', App.BELOW, 100):
			self.panel.clickHomeBtn()
			self.panel.clickSearchBtn()
			icon = self.findPolymorphicImage('icon')
			if icon is None:
				appName = self.__class__.__name__
				self.panel.typeInSearhFrame(appName.lower())
				icon = self.findPolymorphicImage('icon')
				if icon is None:
					print(appName + ' has not been installed in this andriod.')
					return
			assert not icon is None
			self.clickAfterSeeingSth(icon)
		self.initScreen()
	
	def close(self):
		self.panel.clickHomeBtn()
		self.panel.clickTaskBtn()
		self.panel.clickTaskClearBtn()
	
	def initScreen(self):
		pass
	
	def hoverCenter(self):
		sikuli2.hoverPosition(sikuli2.getCenter())
	
	def findPolymorphicImage(self, imgName):
		if re.search('\.', imgName): # determined image file name
			if sikuli2.exists(self.img(imgName)):
				return imgName
			else : 
				return None
		else: # ambiguous image file name
			for fileName in os.listdir(self.imgPath):
				if fnmatch.fnmatchcase(fileName, imgName + '*.jpg'):
					if sikuli2.exists(self.img(fileName)):
						return fileName
			return None
	
	def findAllPolymorphicImage(self, imgName):
		if re.search('\.', imgName): # determined image file name
			return sikuli2.findAll(self.img(imgName))
		else: # ambiguous image file name
			for fileName in os.listdir(self.imgPath):
				if fnmatch.fnmatchcase(fileName, imgName + '*.jpg'):
					return sikuli2.findAll(self.img(fileName))
			return []
	
	def clickPolymorphicImage(self, imgName):
		if re.search('\.', imgName): # determined image file name
			sikuli2.clickImage(self.img(imgName))
		else: # ambiguous image file name
			for fileName in os.listdir(self.imgPath):
				if fnmatch.fnmatchcase(fileName, imgName + '*.jpg'):
					if sikuli2.clickImage(self.img(fileName)):
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
			targetPos = sikuli2.getArea(self.img(imgFile)).getCenter()
		elif isinstance(target, basestring):
			clickTarget = self.findPolymorphicImage(target)
			if clickTarget is None: return False # can't find target image in panel
			targetPos = sikuli2.getArea(self.img(clickTarget)).getCenter()
		elif isinstance(target, lacky.Region):
			targetPos = target.getCenter()
		elif isinstance(target, lacky.Location):
			targetPos = target
		elif isinstance(target, tuple):
			targetPos = lacky.Location(target)
		# calculate shift
		if not direction is None:
			if direction == App.ABOVE:
				targetPos = targetPos.above(offset)
			elif direction == App.BELOW:
				targetPos = targetPos.below(offset)
			elif direction == App.LEFT:
				targetPos = targetPos.left(offset)
			elif direction == App.RIGHT:
				targetPos = targetPos.right(offset)
		# delay and click target
		if delay != 0 : time.sleep(delay)
		return sikuli2.clickPosition(targetPos)
	
class Task:
	def __init__(self, app):
		# The methods in task class must be performed under the premise of establishing a connection with cell phone.
		remote = uia2.findFirstElemByClassName(uia2.DesktopRoot, 'SDL_app')
		if not uia2.isUIAElem(remote):
			os._exit()
		self.app = app
	
	def execute(self):
		pass

class TaskSet:
	def __init__(self):
		self.taskList = []
		
	def register(self, task):
		self.taskList.append(task)
	
	def remove(self, task):
		self.taskList.remove(task)
		
	def execute(self):
		for task in self.taskList:
			task.execute()
	
if __name__ == '__main__':
	import remote
	#pdb.set_trace()
	#os._exit(0)
	logging.basicConfig(level = logging.INFO)
	ctrl = remote.Scrcpy()
	ctrl.connect()
	