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
	#disableSikuliLog()
	ctrl = remote.Scrcpy()
	ctrl.connect()
	app = QuTouTiao('M2007J17C_V125') # TODO : App(ctrl.type)
	# create task list and execute tasks
	tasks = []
	tasks.append(UnlockSmartPhone(app))
	tasks.append(ClearActiveApp(app))
	tasks.append(QTTSignIn(app))
	tasks.append(QTTReadNews(app))
	for task in tasks:
		task.execute()