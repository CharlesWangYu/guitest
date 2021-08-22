# -*-coding:utf-8 -*-
'''
@File		: fanqiechangting.py
@Date		: 2021/08/16
@Author		: Wang.Yu
@Version	: 1.0
@Contact	: ouu_cn@163.com
@License	: (C)Copyright 2021, Personal exclusive right.
'''
import pdb
import logging
import time

from app import *

class FanQieChangTing(App):
	def __init__(self, model):
		super(FanQieChangTing, self).__init__(model)
		self.imgPath = self.keyPath + 'fanqiechangting\\'
	
	def initEntry(self):
		time.sleep(3)
	
	def keepListening(self, mode=EXECUTION_BACKGROUND, minute=None):
		x = int(self.config['FANQIECHANGTING']['PLAY_PAUSE_BTN_X'])
		y = int(self.config['FANQIECHANGTING']['PLAY_PAUSE_BTN_Y'])
		clickPos(posL2P(makePos(x, y)))
		time.sleep(1)
		if (mode == EXECUTION_BACKGROUND):
			self.clickAndroidHomeBtn()
		else:
			if minute is not None:
				time.sleep(minute * 60)
				clickPos(playPauseBtnPos)
		time.sleep(1)

class FQCTOpen(Task):
	def execute(self):
		self.app.start()

class FQCTClose(Task):
	def execute(self):
		self.app.stop()
	
class FQCTSignIn(Task):
	def execute(self):
		pass
	
class FQCTKeepListening(Task):
	def execute(self):
		self.app.keepListening()
	
if __name__ == '__main__':
	import remote
	#pdb.set_trace()
	#os._exit(0)
	logging.basicConfig(level = logging.INFO)
	ctrl = remote.Scrcpy()
	ctrl.connect()
	app = FanQieChangTing(ctrl.phoneModel)
	tasks = []
	#tasks.append(UnlockSmartPhone(app))
	tasks.append(ClearActiveApp(app))
	tasks.append(FQCTOpen(app))
	#tasks.append(FQCTSignIn(app))
	tasks.append(FQCTKeepListening(app))
	#tasks.append(FQCTClose(app))
	for task in tasks:
		task.execute()
	#ctrl.disconnect()
	