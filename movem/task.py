# -*-coding:utf-8 -*-
'''
@File		: app.py
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

from mouse2 import *
from uia2 import *
from sikuli2 import *
from android import * # remote connect in this package

class QuTouTiao:
	def __init__(self, android):
		self.android = android
		self.imgPath = os.path.abspath('.') + '\\images\\qutoutiao\\'
	
	def img(self, fileName):
		return self.imgPath + fileName
	
	def open(self):
		self.android.searchApp('qutoutiao')
		clickImage(self.img('icon.jpg'))
		clickImage(self.img('skip_ads.jpg'))
	
	def close(self):
		self.android.clickHomeBtn()
		self.android.clickTaskBtn()
		self.android.clickTaskCloseBtn()
	
	def clickTask(self):
		if not clickImage(app.img('foot_task1.jpg')):
			clickImage(app.img('foot_task2.jpg'))
		if exists(app.img('sign_success.jpg')) :
			clickImage(app.img('sign_success_cancel.jpg'))
	
	def clickRefresh(self):
		if not clickImage(app.img('foot_refresh1.jpg')):
			clickImage(app.img('foot_refresh2.jpg'))
		time.sleep(0.5)
	
	def clickMine(self):
		if not clickImage(app.img('foot_mine1.jpg')):
			clickImage(app.img('foot_mine2.jpg'))
	
	def viewNews30seconds(self):
		clickImage(app.img('search_frame_icon.jpg'))
		type('tiyuxinwen')
		area = shiftDown(getArea(app.img('search_frame_title.jpg')), 20)
		clickArea(area)
		clickImage(app.img('menu_info.jpg'))
		area = shiftDown(getArea(app.img('menu_info.jpg')), 60)
		clickArea(area)
		wheel(WHEEL_DOWN, 10)
		time.sleep(2)
		wheel(WHEEL_DOWN, 10)
		time.sleep(2)
		wheel(WHEEL_DOWN, 10)
		time.sleep(2)
		wheel(WHEEL_DOWN, 10)
	
class Task:
	def __init__(self, app):
		# The methods in task class must be performed under the premise of establishing a connection with cell phone.
		remote = findFirstElemByClassName(DesktopRoot, 'SDL_app')
		if not isUIAElem(remote):
			os._exit()
		self.app = app
	
	def execute(self):
		pass
	
class QTTBrowseNews(Task):
	def execute(self):
		for count in range(0, 1): # TODO : 1300 times
			self.app.open()
			#self.app.viewNews30seconds(count)
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
	app = QuTouTiao(Android('redmik20pro_miui11'))
	tasks = TaskSet()
	tasks.register(QTTBrowseNews(app))
	tasks.execute()
	