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
from kuaishoujisu import *
from fanqiechangting import *

if __name__ == '__main__':
	#pdb.set_trace()
	#os._exit(0)
	logging.basicConfig(level = logging.INFO)
	#disableSikuliLog()
	remote = Scrcpy()
	remote.connect()
	app = App(remote.platform())
	qtt = QuTouTiao(remote.platform())
	ksj = KuaiShouJiSu(remote.platform())
	fqc = FanQieChangTing(remote.platform())
	# create task list and execute tasks
	tasks = []
	tasks.append(UnlockSmartPhone(app))
	tasks.append(ClearActiveApp(app))
	tasks.append(KSJSOpen(ksj))
	#tasks.append(KSJSSignIn(ksj))
	tasks.append(KSJSBrowseVideo(ksj))
	tasks.append(KSJSClose(ksj))
	tasks.append(FQCTOpen(app))
	tasks.append(FQCTKeepListening(app))
	tasks.append(QTTOpen(qtt))
	tasks.append(QTTSignIn(qtt))
	tasks.append(QTTReadNews(qtt))
	tasks.append(QTTClose(qtt))
	for task in tasks:
		task.execute()
	remote.disconnect()