import pdb
import time
import win32api
import win32gui
import win32con

win = win32gui.FindWindow(None, '1111.txt - 记事本')
tid = win32gui.FindWindowEx(win, None, 'Edit', None)
win32gui.SendMessage(tid, win32con.WM_SETTEXT, None, '你好hello word!')
win32gui.PostMessage(tid, win32con.WM_KEYDOWN, win32con.VK_RETURN, 0)
#pdb.set_trace()
win32gui.SetForegroundWindow(win)
win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)
win32api.keybd_event(79, 0, 0, 0) # 79:O
win32api.keybd_event(79, 0, win32con.KEYEVENTF_KEYUP, 0)
win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)
'''
#win32gui.SetForegroundWindow(win)
win32gui.PostMessage(tid, win32con.WM_KEYDOWN, 17, 0)
time.sleep(1)
#win32api.SendMessage(win, win32con.WM_CHAR, 79, 0)
win32gui.PostMessage(tid, win32con.WM_KEYDOWN, 79, 0)
time.sleep(0.0001)
#win32gui.PostMessage(tid, win32con.WM_KEYUP, 79, 0)
time.sleep(1)
#win32gui.PostMessage(tid, win32con.WM_KEYUP, 17, 0)
time.sleep(0.5)
'''
print("%x" % tid)
print("%x" % win)