import time

import win32api
import win32con
import win32gui

DELAY_OPEN_RRET = 4

# Before the formal test, the FDI-IDE license file must be set in the License Manager
win32api.WinExec("C:\Program Files (x86)\FDI\Reference Run-time Environment\Fdi.Reference.Client.exe", win32con.SW_SHOW)
time.sleep(DELAY_OPEN_RRET)
rrteHwnd = win32gui.FindWindow(None, 'Reference Run-time Environment')
#print('RRTE HWND=0x%x' %rrteHwnd)
for i in range(4):
	childHwnd = win32gui.FindWindowEx(rrteHwnd, None, 'Button', None)
	print('Child HWND=0x%x' %childHwnd)