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
	app = QuTouTiao(Android('M2007J17C_V125')) # TODO:Android(ctrl.type)
	# create task list
	tasks = []
	tasks.append(QTTClose(app))
	tasks.append(QTTOpen(app))
	tasks.append(QTTReceive(app))
	#tasks.append(QTTTreasureBox(app))
	tasks.append(QTTBrowseNews(app))
	# execute tasks
	for task in tasks:
		task.execute()