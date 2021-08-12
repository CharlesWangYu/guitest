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

from remote import *
from qutoutiao import *

if __name__ == '__main__':
	#pdb.set_trace()
	#os._exit(0)
	logging.basicConfig(level = logging.INFO)
	#disableSikuliLog()
	remote = Scrcpy()
	remote.connect()
	app = QuTouTiao(remote.platform())
	# create task list and execute tasks
	tasks = []
	tasks.append(UnlockSmartPhone(app))
	tasks.append(ClearActiveApp(app))
	tasks.append(QTTOpen(app))
	tasks.append(QTTSignIn(app))
	tasks.append(QTTReadNews(app))
	tasks.append(QTTClose(app))
	for task in tasks:
		task.execute()
	remote.disconnect()