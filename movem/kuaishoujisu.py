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
	def __init__(self, platform):
		super(KuaiShouJiSu, self).__init__(platform)
		self.imgPath = os.path.abspath('.') + '\\res\\app\\kuaishoujisu\\'
	
	def initEntry(self):
		pass
	
	def browseVideo(self, minute):
		for x in range(0, int(minute * 2)):
			time.sleep(30)
			hoverPos(getCenter())
			longFlickUp()

class KSJSOpen(Task):
	def execute(self):
		self.app.start()

class KSJSClose(Task):
	def execute(self):
		self.app.stop()
	
class KSJSSignIn(Task):
	def execute(self):
		pass
	
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
	app = KuaiShouJiSu(ctrl.platform())
	tasks = []
	tasks.append(UnlockSmartPhone(app))
	tasks.append(ClearActiveApp(app))
	tasks.append(KSJSOpen(app))
	#tasks.append(KSJSSignIn(app))
	tasks.append(KSJSBrowseVideo(app))
	tasks.append(KSJSClose(app))
	for task in tasks:
		task.execute()
	ctrl.disconnect()
	