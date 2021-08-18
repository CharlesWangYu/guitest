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
import subprocess
import win32gui
import win32con
import win32print
import time
from win32api import GetSystemMetrics

from uia2 import *
from sikuli2 import initCanvas

class RemoteCtrl:
	def __init__(self):
		self.uiaApp		= None
		self.rectangle	= None
		self.sysType	= ''
		self.scale		= self.getScale()
	
	def connect(self):
		pass
	
	def disconnect(self):
		pass
	
	def platform(self):
		return self.sysType
	
	def getScale(self):
		hDC = win32gui.GetDC(0)
		widthOriginal	= win32print.GetDeviceCaps(hDC, win32con.DESKTOPHORZRES)
		#heightOriginal	= win32print.GetDeviceCaps(hDC, win32con.DESKTOPVERTRES)
		#dpiOriginal	= win32print.GetDeviceCaps(hDC, win32con.LOGPIXELSX)
		widthReal		= GetSystemMetrics(0)
		#heightReal		= GetSystemMetrics(1)
		return widthOriginal / widthReal
	
	def getRealRectangle(self, rectangle):
		rectangleReal = rectangle
		rectangleReal.left		= int(self.scale * rectangleReal.left + 0.5)
		rectangleReal.right		= int(self.scale * rectangleReal.right + 0.5)
		rectangleReal.top		= int(self.scale * rectangleReal.top + 0.5)
		rectangleReal.bottom	= int(self.scale * rectangleReal.bottom + 0.5)
		return rectangleReal

class Scrcpy(RemoteCtrl):
	def connect(self):
		# get platform information
		self.adb()
		# start up
		cmd = 'scrcpy -Sw -Tt -m 1024 --window-x 10 --disable-screensaver'
		subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, close_fds=True)
		# capture remote screen
		self.uiaApp = getNullUIAElem()
		while not isUIAElem(self.uiaApp):
			time.sleep(0.1)
			self.uiaApp = findFirstElemByClassName(DesktopRoot, 'SDL_app')
		self.rectangle = self.getRealRectangle(self.uiaApp.CurrentBoundingRectangle)
		self.phoneType	= self.uiaApp.CurrentName
		logging.info('Connect with "%s".' % (self.uiaApp.CurrentName))
		logging.info('Remote control tool is "%s".' % (self.__class__.__name__))
		# set screen information to lackey
		left	= self.rectangle.left
		top		= self.rectangle.top
		width	= self.rectangle.right - self.rectangle.left
		height	= self.rectangle.bottom - self.rectangle.top
		initCanvas(self.rectangle, self.scale)
		logging.info('Screen area is (%d,%d,%d,%d)' %(left, top, width, height))
		logging.info('Screen scale is "%.2f".' % (self.scale))
	
	def disconnect(self):
		closeWindow(self.uiaApp)
		logging.info('Disconnect with smart phone (Andriod system).')
		
	def adb(self):
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
		self.sysType = deviceInfo + '_' + guiSysInfo
		logging.info('Smart phone platform is "%s".' % (self.sysType))

if __name__ == '__main__':
	#pdb.set_trace()
	logging.basicConfig(level = logging.INFO)
	remote = Scrcpy()
	remote.connect()
	remote.disconnect()