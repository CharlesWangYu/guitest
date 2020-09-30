'''
@File		: rrteAutoDumpLabel.py
@Date		: 2020/08/30
@Author		: Wang.Yu
@Version	: 1.0
@Contact	: yu.wang@cn.yokogawa.com
@License	: (C)Copyright 2020 Yokogawa China Co., Ltd.
'''
#import pdb
#import logging
import os
import datetime
import re
from host import *
from rrte import *

if __name__ == '__main__':
	#pdb.set_trace()
	logging.basicConfig(level = logging.INFO)
	logging.info('[Start RRTE] : ' + datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S'))
	top = RRoot('root')
	top.ctrlType = ''
	top.rectangle = None
	top.path = [top]
	root = TreeNode(top)
	rrte = RRTE(root)
	rrte.startUp()
	if not os.path.exists('./tree.bin'):
		rrte.createTree(rrte.root)
		logging.info('[Finished tree generation] : ' + datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S'))
		rrte.serialize()
	else:
		logging.info('[Restore tree generation] : ' + datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S'))
		rrte.restore()
	Util.dumpMenuLabel2Csv(rrte.root)
	Util.dumpEnumOpt2Csv(rrte.root)
	Util.dumpBitEnumOpt2Csv(rrte.root)
	t = datetime.datetime.now()
	logging.info('[Finished label collection] : ' + datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S'))
