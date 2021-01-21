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

class App: # Abstract class
	ABOVE	= 0
	BELOW	= 1
	LEFT	= 2
	RIGHT	= 3
	
	def __init__(self, android):
		self.panel = android
		self.imgPath = ''
	
	def img(self, imgName):
		return self.imgPath + imgName
	
	def findPolymorphicImage(self, imgName):
		if re.search('.', imgName): # determined image file name
			return sikuli2.exists(self.img(imgName))
		else: # ambiguous image file name
			for fileName in os.listdir(self.imgPath):
				if fnmatch.fnmatchcase(fileName, imgName + '*.jpg') :
					if sikuli2.exists(self.img(fileName)) :
						return fileName
			return None
	
	def clickPolymorphicImage(self, imgName):
		if re.search('.', imgName): # determined image file name
			sikuli2.clickImage(self.img(imgName))
		else: # ambiguous image file name
			for fileName in os.listdir(self.imgPath):
				if fnmatch.fnmatchcase(fileName, imgName + '*.jpg') :
					if sikuli2.clickImage(self.img(fileName)) :
						return True
			return False
	
	def clickAfterSeeingSth(imgName, direction=None, offset=0, delay=0, target=None):
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
		
		found = findPolymorphicImage(imgName)
		if found is None : return False # can't find image
		# init target
		if target is None:
			targetPos = sikuli2.getArea(self.img(imgName)).getCenter()
		elif isinstance(target, basestring):
			clickTarget = findPolymorphicImage(target)
			if clickTarget is None : return False # can't find target image
			targetPos = sikuli2.getArea(self.img(clickTarget)).getCenter()
		elif isinstance(target, lacky.Region):
			targetPos = target.getCenter()
		elif isinstance(target, lacky.Location):
			targetPos = target
		elif isinstance(target, tuple):
			targetPos = lacky.Location(target)
		# calculate shift
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
		return clickPosition(targetPos)

class QuTouTiao(App):
	def __init__(self, android):
		super(QuTouTiao, self).__init__(android)
		self.imgPath = os.path.abspath('.') + '\\images\\qutoutiao\\'
		#self.viewPattern = [1, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1]
	'''
	def img(self, fileName):
		return self.imgPath + fileName
		
	def clickPolymorphicBtn(self, imgName):
		for fileName in os.listdir(self.imgPath):
			if fnmatch.fnmatchcase(fileName, imgName + '*.jpg') :
				if sikuli2.clickImage(self.img(fileName)) :
					return
	'''
	
	def open(self):
		self.panel.clickHomeBtn()
		self.panel.clickTaskBtn()
		if not self.clickAfterSeeingSth('icon', APP.BELOW, 100):
			self.panel.clickHomeBtn()
			self.panel.clickSearchBtn()
			#if not sikuli2.clickImage(self.img('icon.jpg')):
			if not findPolymorphicImage('icon') is None:
				self.panel.typeInSearhFrame('qutoutiao')
				self.clickAfterSeeingSth('icon')
		'''
		if sikuli2.exists(self.img('icon.jpg')) :
			sikuli2.clickArea(sikuli2.getArea(self.img('icon.jpg')).below(100))
		else :
			self.panel.clickHomeBtn()
			self.panel.clickSearchBtn()
			if not sikuli2.clickImage(self.img('icon.jpg')):
				self.panel.typeInSearhFrame('qutoutiao')
				sikuli2.clickImage(self.img('icon.jpg'))
		'''
		self.igoreRubbishInfo()
		#sikuli2.clickImage(self.img('skip_ads.jpg'))
	
	def close(self):
		self.panel.clickHomeBtn()
		self.panel.clickTaskBtn()
		self.panel.clickTaskClearBtn()
	
	def clickTask(self):
		self.clickPolymorphicBtn('foot_task')
		if sikuli2.exists(self.img('sign_success.jpg')) :
			sikuli2.clickImage(self.img('sign_success_cancel.jpg'))
	
	def clickRefresh(self):
		self.clickPolymorphicBtn('foot_refresh')
		time.sleep(2.5)
	
	def clickMine(self):
		self.clickPolymorphicBtn('foot_mine')
		
	def clickBack(self):
		pos = sikuli2.getTopLeft().right(40).below(90)
		sikuli2.clickPosition(pos)
	
	def igoreRubbishInfo(self):
		sikuli2.setTimeout(0.4)
		self.cancelPushingInfo()
		self.cancelGettigRightNow()
		self.cancelSignSuccess()
		sikuli2.setTimeout(1)
	
	def cancelGettigRightNow(self):
		'''
		if sikuli2.exists(self.img('get_right_now.jpg')) :
			area = sikuli2.getArea(self.img('get_right_now.jpg')).below(140)
			sikuli2.clickArea(area)
		'''
		for fileName in os.listdir(self.imgPath):
			if fnmatch.fnmatchcase(fileName, 'get_right_now*.jpg') :
				if sikuli2.exists(self.img(fileName)) :
					area = sikuli2.getArea(self.img(fileName)).below(140)
					sikuli2.clickArea(area)
					return
	
	def cancelSignSuccess(self):
		if sikuli2.exists(self.img('sign_success.jpg')) :
			sikuli2.clickImage(self.img('sign_success_cancel.jpg'))
	
	def cancelPushingInfo(self):
		if sikuli2.exists(self.img('i_know.jpg')) :
			area = sikuli2.getArea(self.img(fileName)).below(70)
			sikuli2.clickArea(area)
	
	def cancelInviteFriends(self):
		if sikuli2.exists(self.img('invite_friends.jpg')) :
			area = sikuli2.getArea(self.img('invite_friends.jpg')).below(140)
			sikuli2.clickArea(area)
	
	def gotoFirstNews(self):
		while True:
			pos = sikuli2.getTopLeft().right(int(sikuli2.getWidth()/2)).below(730)
			sikuli2.clickPosition(pos)
			time.sleep(0.5)
			if not sikuli2.exists(self.img('praise.jpg')) : return
			self.clickBack()
			self.clickRefresh()
			sikuli2.hoverPosition(sikuli2.getCenter())
			sikuli2.wheelDown(5)
			time.sleep(0.5)
	
	def receiveGold(self):
		self.clickRefresh()
		sikuli2.clickImage(self.img('receive.jpg'))
	
	def viewNews30seconds(self):
		#self.cancelGettigRightNow()
		self.clickRefresh()
		self.gotoFirstNews()
		sikuli2.hoverPosition(sikuli2.getCenter())
		for x in range(0, len(self.viewPattern)):
			if self.viewPattern[x] : sikuli2.wheelDown(3)
			else : sikuli2.wheelUp(2)
			time.sleep(2)
	
	def viewArticle(self, seconds):
		self.clickRefresh()
		self.gotoFirstNews()
		sikuli2.hoverPosition(sikuli2.getCenter())
		for x in range(0, int(seconds/2)):
			if x % 2 == 0 : sikuli2.wheelDown(3)
			else : sikuli2.wheelUp(2)
			time.sleep(2)
	
	def viewShortVideo(self):
		sikuli2.clickImage(self.img('to_view.jpg'))
		time.sleep(60)
		self.panel.clickBackBtn()
	
	def viewNews3Mins(self):
		pass
		
	def signInToday(self):
		pass
		
	def jumpToOthersApp(self):
		sikuli2.clickImage(self.img('to_open.jpg'))
		time.sleep(6)
		self.panel.clickBackBtn()
		self.panel.clickBackBtn()
		'''
		self.panel.clickHomeBtn()
		self.panel.clickTaskBtn()
		if sikuli2.exists(self.img('icon.jpg')) :
			sikuli2.clickArea(sikuli2.getArea(self.img('icon.jpg')).below(100))
		'''
	
	def openTreasureBox(self):
		for count in range(0, 3):
			# ready to enter a task for opening treasure box
			self.clickRefresh()
			self.clickTask()
			sikuli2.hoverPosition(sikuli2.getCenter())
			sikuli2.wheelDown(1)
			# enter a task
			if sikuli2.exists(self.img('view_2_min_video.jpg')) :
				pos = sikuli2.getArea(self.img('view_2_min_video.jpg')).getCenter().right(80)
				sikuli2.clickPosition(pos)
				self.viewVideo2Mins()
			'''
			if sikuli2.exists(self.img('view_3_min_article.jpg')) :
				pos = sikuli2.getArea(self.img('view_3_min_article.jpg')).getCenter().right(80)
				sikuli2.clickPosition(pos)
				self.viewArticle(180)
				self.panel.clickBackBtn()
			#if sikuli2.exists(self.img('view_short_video.jpg')) :
			if sikuli2.exists(self.img('to_view.jpg')) :
				self.viewShortVideo()
			'''
			if sikuli2.exists(self.img('to_open.jpg')) :
				self.jumpToOthersApp()
			# finish opening treasure box
			sikuli2.clickImage(self.img('open_treasure_box.jpg'))
			if sikuli2.exists(self.img('congratulation_for_open_box.jpg')) :
				area = sikuli2.getArea(self.img('congratulation_for_open_box.jpg')).below(450)
				sikuli2.clickArea(area)
	
class Task:
	def __init__(self, app):
		# The methods in task class must be performed under the premise of establishing a connection with cell phone.
		remote = uia2.findFirstElemByClassName(uia2.DesktopRoot, 'SDL_app')
		if not uia2.isUIAElem(remote):
			os._exit()
		self.app = app
	
	def execute(self):
		pass
	
class QTTOpen(Task):
	def execute(self):
		self.app.open()

class QTTClose(Task):
	def execute(self):
		self.app.close()

class QTTReceive(Task):
	def execute(self):
		self.app.open()
		self.app.receiveGold()

class QTTTreasureBox(Task):
	def execute(self):
		self.app.open()
		for count in range(0, 1): # TODO
			self.app.openTreasureBox()

class QTTBrowseNews(Task):
	def execute(self):
		self.app.close()
		for count in range(0, 2000):
			self.app.open()
			#self.app.viewNews30seconds()
			self.app.self.viewArticle(30)
			self.app.close()

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
	logging.basicConfig(level = logging.INFO)
	ctrl = remote.Scrcpy()
	ctrl.connect()
	app = QuTouTiao(android.Android('redmik20pro_miui11'))
	tasks = TaskSet()
	tasks.register(QTTClose(app))
	tasks.register(QTTTreasureBox(app))
	'''
	tasks.register(QTTOpen(app))
	tasks.register(QTTReceive(app))
	tasks.register(QTTBrowseNews(app))
	'''
	tasks.execute()
	