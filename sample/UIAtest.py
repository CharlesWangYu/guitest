import pdb
import logging
import time
import subprocess
import xlrd
import win32api
import win32con
import traceback
#import comtypes
from configparser import ConfigParser
from comtypes.client import *
from ctypes import *

DELAY_FOR_DEMO			= 6
#MOUSEEVENTF_LEFTDOWN	= 0x0002
#MOUSEEVENTF_LEFTUP		= 0x0004

if __name__ == '__main__':
	#pdb.set_trace()
	logging.basicConfig(level = logging.INFO)
	# Start UI Automation
	UIAutomationClient = GetModule('UIAutomationCore.dll')
	IUIAutomation = CreateObject('{ff48dba4-60ef-4201-aa87-54103eef594e}', interface=UIAutomationClient.IUIAutomation)
	root = IUIAutomation.GetRootElement()
	# Open excel sample file
	execCmd = '.\Excel_Control_Sample.xlsm'
	subprocess.Popen(execCmd, shell=True, stdout=subprocess.PIPE)
	time.sleep(DELAY_FOR_DEMO)
	# Search button 'MenuA' and push it
	cnd = IUIAutomation.CreatePropertyConditionEx(UIAutomationClient.UIA_NamePropertyId, '工作表 Convert', UIAutomationClient.PropertyConditionFlags_None)
	sheet = root.FindFirst(UIAutomationClient.TreeScope_Descendants, cnd)
	cnd = IUIAutomation.CreatePropertyConditionEx(UIAutomationClient.UIA_NamePropertyId, '对象', UIAutomationClient.PropertyConditionFlags_None)
	menu = sheet.FindFirst(UIAutomationClient.TreeScope_Descendants, cnd)
	#pattern = menu.GetCurrentPattern(UIAutomationClient.UIA_SelectionItemPatternId)
	#ctrl = cast(pattern, #POINTER(UIAutomationClient.IUIAutomationSelectionItemPattern))
	#ctrl.Select()
	left = int(menu.CurrentBoundingRectangle.left)
	rigth = int(menu.CurrentBoundingRectangle.right)
	top = int(menu.CurrentBoundingRectangle.top)
	bottom = int(menu.CurrentBoundingRectangle.bottom)
	x = int((left + rigth) / 2)
	y = int((top + bottom) / 2)
	win32api.SetCursorPos((x, y));
	win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0);
	win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0);
	'''
	try:
		rrteRoot = searchOneElement(root, 'Reference Run-time Environment', UIAutomationClient.UIA_NamePropertyId)
	except Exception as e:
		print ('except:%s' % e)
	'''
