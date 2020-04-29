import win32gui
import win32con
win = win32gui.FindWindow(None, '1111.txt - 记事本')
tid = win32gui.FindWindowEx(win, None, 'Edit', None)
win32gui.SendMessage(tid, win32con.WM_SETTEXT, None, '你好hello word!')
win32gui.PostMessage(tid, win32con.WM_KEYDOWN, win32con.VK_RETURN, 0)
print("%x" % tid)
print("%x" % win)