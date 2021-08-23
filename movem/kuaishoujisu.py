# -*-coding:utf-8 -*-
'''
@File		: kuaishoujisu.py
@Date		: 2021/08/12
@Author		: Wang.Yu
@Version	: 1.0
@Contact	: ouu_cn@163.com
@License	: (C)Copyright 2021, Personal exclusive right.
'''
import pdb
import logging
import time

from app import *

class KuaiShouJiSu(App):
	def __init__(self, model):
		super(KuaiShouJiSu, self).__init__(model)
		self.imgPath = self.keyPath + 'kuaishoujisu\\'
	
	def initEntry(self):
		for i in range(0, 3):
			time.sleep(1)
			self.foundThenClick('i_know')
	
	def browseVideo(self, minute):
		for x in range(0, int(minute * 10)):
			time.sleep(6)
			hoverPos(getCenter())
			longFlickUp()
	
	def toMakeMoney(self):
		x = int(self.config['KUAISHOUJISU']['TOP_LEFT_SETTING_X'])
		y = int(self.config['KUAISHOUJISU']['TOP_LEFT_SETTING_Y'])
		clickPos(posL2P(makePos(x, y)))
		time.sleep(0.5)
		self.foundThenClick('make_money')
		time.sleep(0.5)
		hoverPos(getCenter())
		time.sleep(2)
		wheelDown(5)
		time.sleep(2)
	
	def watchAdOnce(self):
		self.foundThenClick('watch_ad')
		time.sleep(35)
		self.clickAndroidBackBtn()
		time.sleep(1)
	
	def watchLiveRoomOnce(self):
		x = int(self.config['KUAISHOUJISU']['LIVE_ROOM_ATTENTION_X'])
		y = int(self.config['KUAISHOUJISU']['LIVE_ROOM_ATTENTION_Y'])
		w = int(self.config['KUAISHOUJISU']['LIVE_ROOM_ATTENTION_W'])
		h = int(self.config['KUAISHOUJISU']['LIVE_ROOM_ATTENTION_H'])
		area = areaL2P(makeArea(x, y, w, h))
		self.foundThenClick('watch_live_broadcast')
		time.sleep(65)
		self.clickAndroidBackBtn()
		time.sleep(2)
		while self.matchImage('attetion_right_now') is not None:
			time.sleep(1)
		self.foundThenClick('exit_live_broadcast', region=area)
		time.sleep(1)

class KSJSOpen(Task):
	def execute(self):
		self.app.start()

class KSJSClose(Task):
	def execute(self):
		self.app.stop()
	
class KSJSSignIn(Task):
	def execute(self):
		pass
	
class KSJSWatchAd(Task):
	def execute(self):
		times = int(self.app.config['KUAISHOUJISU']['WATCH_AD_TIMES'])
		self.app.toMakeMoney()
		for count in range(0, times):
			self.app.watchAdOnce()
		time.sleep(1)
		self.app.clickAndroidBackBtn()
	
class KSJSWatchLiveRoom(Task):
	def execute(self):
		times = int(self.app.config['KUAISHOUJISU']['WATCH_LIVE_ROOM_TIMES'])
		self.app.toMakeMoney()
		for count in range(0, times):
			self.app.watchLiveRoomOnce()
		time.sleep(1)
		self.app.clickAndroidBackBtn()
	
class KSJSBrowseVideo(Task):
	def execute(self):
		self.app.browseVideo(180)
	
if __name__ == '__main__':
	import remote
	#pdb.set_trace()
	#os._exit(0)
	logging.basicConfig(level = logging.INFO)
	ctrl = remote.Scrcpy()
	ctrl.connect()
	app = KuaiShouJiSu(ctrl.phoneModel)
	tasks = []
	#tasks.append(UnlockSmartPhone(app))
	tasks.append(ClearActiveApp(app))
	tasks.append(KSJSOpen(app))
	#tasks.append(KSJSSignIn(app))
	tasks.append(KSJSWatchLiveRoom(app))
	tasks.append(KSJSWatchAd(app))
	tasks.append(KSJSBrowseVideo(app))
	tasks.append(KSJSClose(app))
	for task in tasks:
		task.execute()
	ctrl.disconnect()
	