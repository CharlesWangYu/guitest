import time

import win32api
import win32con
import win32gui

DELAY_OPEN_DPCTT = 4

win32api.WinExec("C:\Program Files (x86)\FDI\FDI Package CTT\FDIPackageCTT.exe", win32con.SW_SHOW)
time.sleep(DELAY_OPEN_DPCTT)
cttHwnd = win32gui.FindWindow(None, 'FDI Package CTT')
print('DPCTT HWND=0x%x' %rrteHwnd)
for i in range(4):
	childHwnd = win32gui.FindWindowEx(cttHwnd, None, 'Menu', None)
	print('Child HWND=0x%x' %childHwnd)