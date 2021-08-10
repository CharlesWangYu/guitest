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
import subprocess
import win32gui
import win32con
import win32print
import time
from win32api import GetSystemMetrics

import sikuli2
from uia2 import *

class RemoteCtrl:
	def __init__(self):
		self.uiaApp		= None
		self.rectangle	= None
		self.phoneType	= ''
		self.scale		= self.getScale()
	
	def connect(self):
		pass
	
	def disconnect(self):
		pass
	
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
		# start up
		cmd = '"D:\Program Files\Scrcpy\scrcpy.exe -Sw --disable-screensaver --always-on-top"'
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
		sikuli2.initScreenScope(self.rectangle)
		sikuli2.initScreenScale(self.scale)
		logging.info('Screen area is (%d,%d,%d,%d)' %(left, top, width, height))
		logging.info('Screen scale is "%.2f".' % (self.scale))
	
	def disconnect(self):
		closeWindow(self.uiaApp)
		logging.info('Disconnect with smart phone(Andriod system).')

if __name__ == '__main__':
	#pdb.set_trace()
	logging.basicConfig(level = logging.INFO)
	remote = Scrcpy()
	remote.connect()