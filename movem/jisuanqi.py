# -*-coding:utf-8 -*-
'''
@File		: jisuanqi.py
@Date		: 2021/07/23
@Author		: Wang.Yu
@Version	: 1.0
@Contact	: ouu_cn@163.com
@License	: (C)Copyright 2021, Personal exclusive right.
'''
import pdb
import logging
import time

from app import *
	
class JiSuanQi(App):
	def __init__(self, model):
		super(JiSuanQi, self).__init__(model)
		self.imgPath = self.keyPath + 'jisuanqi\\'
	
	def initEntry(self):
		time.sleep(1)

	def clickNum1(self):
		self.foundThenClick('1')

	def clickNum2(self):
		self.foundThenClick('2')

	def clickClear(self):
		self.foundThenClick('clear')

	def clickEqual(self):
		self.foundThenClick('equal')

	def clickPlus(self):
		self.foundThenClick('plus')
	
	def demo(self):
		self.clickClear()
		time.sleep(1)
		self.clickClear()
		time.sleep(1)
		self.clickNum1()
		time.sleep(1)
		self.clickPlus()
		time.sleep(1)
		self.clickNum2()
		time.sleep(1)
		self.clickEqual()
		time.sleep(5)
	
class JSQDemo(Task):
	def execute(self):
		self.app.start()
		self.app.demo()
		self.app.stop()

if __name__ == '__main__':
	import remote
	#pdb.set_trace()
	logging.basicConfig(level = logging.INFO)
	ctrl = remote.Scrcpy()
	ctrl.connect()
	jsq = JiSuanQi(ctrl.phoneModel)
	tasks = []
	tasks.append(ClearActiveApp(jsq))
	tasks.append(JSQDemo(jsq))
	for task in tasks:
		task.execute()
	ctrl.disconnect()
