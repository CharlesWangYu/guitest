# -*-coding:utf-8 -*-
'''
@File		: movem.py
@Date		: 2021/01/01
@Author		: Wang.Yu
@Version	: 1.0
@Contact	: ouu_cn@163.com
@License	: (C)Copyright 2021, Personal exclusive right.
'''
import pdb
import logging

from qutoutiao import *

if __name__ == '__main__':
	import remote
	#pdb.set_trace()
	#os._exit(0)
	logging.basicConfig(level = logging.INFO)
	ctrl = remote.Scrcpy()
	ctrl.connect()
	app = QuTouTiao(android.Android('redmik20pro_miui11'))
	tasks = TaskSet()
	tasks.register(QTTClose(app))
	tasks.register(QTTOpen(app))
	tasks.register(QTTReceive(app))
	#tasks.register(QTTTreasureBox(app))
	tasks.register(QTTBrowseNews(app))
	tasks.execute()