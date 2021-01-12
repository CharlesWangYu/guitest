# -*-coding:utf-8 -*-
'''
@File		: _movem.py
@Date		: 2021/01/01
@Author		: Wang.Yu
@Version	: 1.0
@Contact	: ouu_cn@163.com
@License	: (C)Copyright 2021, Personal exclusive right.
'''
import pdb
import logging
import drivers.remote

if __name__ == '__main__':
	#pdb.set_trace()
	logging.basicConfig(level = logging.INFO)
	ctrl = drivers.remote.Scrcpy()
	ctrl.connect()