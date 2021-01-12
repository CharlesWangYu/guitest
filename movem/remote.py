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

import uia2
import sikuli2

class RemoteCtrl:
	def __init__(self):
		self.uiaApp		= None
		self.rectangle	= None
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
		cmd = '"D:\Program Files\scrcpy-win64-v1.17\scrcpy.exe"'
		subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, close_fds=True)
		self.uiaApp = uia2.getNullUIAElem()
		while not uia2.isUIAElem(self.uiaApp):
			time.sleep(0.1)
			self.uiaApp = uia2.findFirstElemByClassName(uia2.DesktopRoot, 'SDL_app')
		self.rectangle = self.getRealRectangle(self.uiaApp.CurrentBoundingRectangle)
		logging.info('Connect with "%s".' % (self.uiaApp.CurrentName))
		logging.info('Remote control tool is "%s".' % (self.__class__.__name__))
		sikuli2.initGlobalRegion(self.rectangle)
		logging.info('System display scale is "%.2f".' % (self.scale))
	
	def disconnect(self):
		closeWindow(self.uiaApp)
		logging.info('Disconnect with cell phone.')

if __name__ == '__main__':
	#pdb.set_trace()
	logging.basicConfig(level = logging.INFO)
	remote = Scrcpy()
	remote.connect()
	time.sleep(4)
	#remote.disconnect()