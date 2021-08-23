# -*-coding:utf-8 -*-
'''
@File		: remote.py
@Date		: 2021/01/01
@Author		: Wang.Yu
@Version	: 1.0
@Contact	: ouu_cn@163.com
@License	: (C)Copyright 2021, Personal exclusive right.
'''
import pdb
import logging
import os
import sys
import subprocess
import time

from uia2 import *
from sikuli2 import initCanvas

class RemoteCtrl:
	def __init__(self):
		self.uiaApp		= None
		self.rectangle	= None
		self.scrcpy		= None
		self.scrcpyLog	= None
		self.phoneModel = self.getPhoneModel()
	
	def connect(self):
		pass
	
	def disconnect(self):
		pass
	
	def getPhoneModel(self):
		'''
		The hardware and UI system information of smart phone can be capture
		with the following adb command in terminal.
		1. "adb shell getprop ro.product.model"				[M2007J17C]
		2. "adb shell getprop ro.product.odm.marketname"	[Redmi Note 9 Pro]
		3. "adb shell getprop ro.miui.ui.version.code"		[11]
		4. "adb shell getprop ro.miui.ui.version.name"		[V125]
		'''
		cmd = 'adb shell getprop ro.product.model'
		out = os.popen(cmd)
		deviceInfo = out.read().splitlines()[0]
		out.close()
		cmd = 'adb shell getprop ro.miui.ui.version.name'
		out = os.popen(cmd)
		guiSysInfo = out.read().splitlines()[0]
		out.close()
		model = deviceInfo + '_' + guiSysInfo
		model = model.replace(' ', '')
		logging.info('Smart phone platform type is "%s".' % model)
		return model

class Scrcpy(RemoteCtrl):
	def __is64BitSystem(self):
		return sys.maxsize > 2**32
	
	def connect(self):
		# start up
		if self.phoneModel == 'RedmiK20Pro_V12':
			cmd = 'scrcpy -w -Tt -m 1024 --window-x 10 --disable-screensaver'
		else:
			cmd = 'scrcpy -Sw -Tt -m 1024 --window-x 10 --disable-screensaver'
		self.scrcpyLog = open('scrcpy.log','wb')
		self.scrcpy = subprocess.Popen(cmd, shell=True, stdout=self.scrcpyLog, stderr=self.scrcpyLog, close_fds=True)
		# capture remote screen
		self.uiaApp = getNullUIAElem()
		while not isUIAElem(self.uiaApp):
			time.sleep(0.1)
			self.uiaApp = findFirstElemByClassName(DesktopRoot, 'SDL_app')
		self.rectangle	= self.uiaApp.CurrentBoundingRectangle
		logging.info('Connect to an Andriod smartphone with %s.' % (self.__class__.__name__))
		# set screen information to lackey
		initCanvas(self.uiaApp.CurrentBoundingRectangle)
		top		= self.uiaApp.CurrentBoundingRectangle.top
		bottom	= self.uiaApp.CurrentBoundingRectangle.bottom
		left	= self.uiaApp.CurrentBoundingRectangle.left
		right	= self.uiaApp.CurrentBoundingRectangle.right
		width	= right - left
		height	= bottom - top
		logging.info('Screen area is (%d,%d,%d,%d)' %(left, top, width, height))
	
	def disconnect(self):
		closeWindow(self.uiaApp)
		self.scrcpyLog.close()
		subprocess.Popen.terminate(self.scrcpy)
		time.sleep(2)
		os.remove('./scrcpy.log')
		logging.info('Disconnect the Andriod smartphone.')

if __name__ == '__main__':
	#pdb.set_trace()
	logging.basicConfig(level = logging.INFO)
	remote = Scrcpy()
	remote.connect()
	#remote.disconnect()
