#coding=utf-8
from lackey import *
from win32api import *
from win32con import *
import os, random
import time
import pynput

mouse = pynput.mouse.Controller()

print('Please put mouse cursor on some image.')
time.sleep(4)
#mouse.click(pynput.mouse.Button.left)
for x in range(0, 10):
	mouse.press(pynput.mouse.Button.left)
	mouse.move(15, 0)
mouse.release(pynput.mouse.Button.left)

os._exit(0)

tmp = GetCursorPos()
print('coordinate is (%d, %d)' % (tmp[0], tmp[1]))
(x, y) = (tmp[0], tmp[1])
print('coordinate is (%d, %d)' % (x, y))
mouse_event(MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
time.sleep(1)
mouse_event(MOUSEEVENTF_MOVE, x+5, y+5, 0, 0);
time.sleep(1)
mouse_event(MOUSEEVENTF_LEFTUP, x+5, y+5, 0, 0);

os._exit(0)

App.open(r'C:\Users\Wangyu\AppData\Local\vysor\Vysor.exe')
time.sleep(4)
click('./imgs/connect_btn.jpg')
time.sleep(1)
click('./imgs/connect_ip.jpg')
time.sleep(1)
click('./imgs/view_btn.jpg')
time.sleep(1)
click('./imgs/home_btn.jpg')
time.sleep(1)
click('./imgs/search_icon.jpg')
time.sleep(1)
if not find('./imgs/jd_icon_small.jpg'):
	click('./imgs/key_j.jpg')
	time.sleep(1)
click('./imgs/jd_icon_small.jpg')
time.sleep(4)
click('./imgs/collar_beans.jpg')
time.sleep(1)
if find('./imgs/screen_lingjingdou_flag.jpg'):
	hover('./imgs/grow_beans_img_big.img')
	#dragDrop(t, Location(t.x + 100, t.y + 100))
	mouseDown(Button.RIGHT)
	mouseMove(t1.left(122))
	mouseUp()
else:
	click('./imgs/sign_in_beans.jpg')
	time.sleep(1)
	click('./imgs/return1.jpg')
	time.sleep(1)