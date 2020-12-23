#coding=utf-8
from lackey import *
from keyboard import mouse
import os, random
import time

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