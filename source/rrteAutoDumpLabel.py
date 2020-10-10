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
import datetime
import re
from configparser import ConfigParser
from host import *
from rrte import *

if __name__ == '__main__':
	#pdb.set_trace()
	logging.basicConfig(level = logging.INFO)
	logging.info('[Start RRTE] : ' + datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S'))
	config = ConfigParser()
	config.read('test.conf', encoding='UTF-8')
	top = RRoot('root')
	top.ctrlType = ''
	top.rectangle = None
	top.path = [top]
	root = TreeNode(top)
	rrte = RRTE(config, root)
	rrte.startUp()
	if not rrte.isDesTreeSerialized():
		rrte.createTree(rrte.root)
		logging.info('[Finished tree generation] : ' + datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S'))
		rrte.serializeDesTree()
	else:
		logging.info('[Restore tree generation] : ' + datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S'))
		rrte.restoreDesTree()
	Util.dumpMenuLabel2Csv(rrte.root)
	Util.dumpEnumOpt2Csv(rrte.root)
	Util.dumpBitEnumOpt2Csv(rrte.root)
	t = datetime.datetime.now()
	logging.info('[Finished label collection] : ' + datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S'))
