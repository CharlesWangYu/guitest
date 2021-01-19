# -*-coding:utf-8 -*-
'''
@File		: sikuli2.py
@Date		: 2021/01/01
@Author		: Wang.Yu
@Version	: 1.0
@Contact	: ouu_cn@163.com
@License	: (C)Copyright 2021, Personal exclusive right.
'''
import pdb
import logging
import time
import win32gui
import win32con
import win32print
import lackey

TIMEOUT_LIMIT	= 80	# 8s
WORK_AREA		= lackey.Region(0, 0, win32print.GetDeviceCaps(win32gui.GetDC(0), win32con.DESKTOPHORZRES), win32print.GetDeviceCaps(win32gui.GetDC(0), win32con.DESKTOPVERTRES)) # (x, y, w, h = args)
DEFAULT_SIMILARITY_THRESHOLD	= 0.85

# init screen scope
def initGlobalRegion(uiaRect):
	global WORK_AREA
	left		= uiaRect.left
	top			= uiaRect.top
	width		= uiaRect.right - uiaRect.left
	height		= uiaRect.bottom - uiaRect.top
	WORK_AREA	= lackey.Region(left, top, width, height)
	logging.info('Working area is (%d,%d,%d,%d)' %(left, top, width, height))

# screen operation
def exists(imgName, timeout=None):
	match = WORK_AREA.exists(imgName, timeout)
	return match != None and match.getScore() >= DEFAULT_SIMILARITY_THRESHOLD

def hoverImage(imgName):
	WORK_AREA.hover(imgName)
	time.sleep(0.1)

def clickImage(imgName):
	if exists(imgName):
		WORK_AREA.click(imgName)
		time.sleep(0.1)
		return True
	else:
		return False

def clickBlock(imgName):
	while not exists(imgName):
		time.sleep(0.1)
	return WORK_AREA.click(imgName)

def clickTimeOut(imgName):
	count = 0
	while (not exists(imgName)) and (count < TIMEOUT_LIMIT):
		time.sleep(0.1)
		count += 1
	if count != TIMEOUT_LIMIT:
		WORK_AREA.click(imgName)
	return count != TIMEOUT_LIMIT

def clickArea(region):
	if region.getW() != 0 and region.getH() != 0 :
		region.click()
		time.sleep(0.1)
		return True
	else :
		return False

def clickPosition(position):
	WORK_AREA.click(position)
	time.sleep(0.1)
	return True

def hoverPosition(position):
	WORK_AREA.hover(position)
	time.sleep(0.1)

def wheelDown(steps):
	WORK_AREA.wheel(0, steps) # 0:Down
	time.sleep(0.1)

def wheelUp(steps):
	WORK_AREA.wheel(1, steps) # 1:Up
	time.sleep(0.1)

def flickDown():
	lackey.SettingsMaster.MoveMouseDelay = 0.01
	pos = WORK_AREA.getCenter()
	WORK_AREA.hover(pos)
	WORK_AREA.mouseDown()
	time.sleep(0.01)
	flickLegth = int(WORK_AREA.getH() / 2 - 200)
	flickStep  = int(flickLegth / 4)
	for count in range(0, 4):
		pos = pos.below(flickStep)
		WORK_AREA.hover(pos)
		time.sleep(0.01)
	WORK_AREA.mouseUp()
	lackey.SettingsMaster.MoveMouseDelay = 0.3
	time.sleep(0.2)

def flickUp():
	lackey.SettingsMaster.MoveMouseDelay = 0.01
	pos = WORK_AREA.getCenter()
	WORK_AREA.hover(pos)
	WORK_AREA.mouseDown()
	time.sleep(0.01)
	flickLegth = int(WORK_AREA.getH() / 2 - 200)
	flickStep  = int(flickLegth / 4)
	for count in range(0, 4):
		pos = pos.above(flickStep)
		WORK_AREA.hover(pos)
		time.sleep(0.01)
	WORK_AREA.mouseUp()
	lackey.SettingsMaster.MoveMouseDelay = 0.3
	time.sleep(0.2)

def flickLeft():
	lackey.SettingsMaster.MoveMouseDelay = 0.01
	pos = WORK_AREA.getCenter()
	WORK_AREA.hover(pos)
	WORK_AREA.mouseDown()
	time.sleep(0.01)
	flickLegth = int(WORK_AREA.getW() / 2 - 30)
	flickStep  = int(flickLegth / 4)
	for count in range(0, 4):
		pos = pos.left(flickStep)
		WORK_AREA.hover(pos)
		time.sleep(0.01)
	WORK_AREA.mouseUp()
	lackey.SettingsMaster.MoveMouseDelay = 0.3
	time.sleep(0.2)

def flickRight():
	lackey.SettingsMaster.MoveMouseDelay = 0.01
	pos = WORK_AREA.getCenter()
	WORK_AREA.hover(pos)
	WORK_AREA.mouseDown()
	time.sleep(0.01)
	flickLegth = int(WORK_AREA.getW() / 2 - 30)
	flickStep  = int(flickLegth / 4)
	for count in range(0, 4):
		pos = pos.right(flickStep)
		WORK_AREA.hover(pos)
		time.sleep(0.01)
	WORK_AREA.mouseUp()
	lackey.SettingsMaster.MoveMouseDelay = 0.3
	time.sleep(0.2)

def type(text):
	WORK_AREA.type(text)
	time.sleep(0.1)

def setTimeout(seconds):
	WORK_AREA.setAutoWaitTimeout(seconds)

# coordinate operation
def getCenter():
	return WORK_AREA.getCenter()

def getTopLeft():
	return WORK_AREA.getTopLeft()

def getTopRight():
	return WORK_AREA.getTopRight()

def getBottomLeft():
	return WORK_AREA.getBottomLeft()

def getBottomRight():
	return WORK_AREA.getBottomRight()

def getWidth():
	return WORK_AREA.getW()

def getHeight():
	return WORK_AREA.getH()

def getTopLeftX():
	return WORK_AREA.getTopLeft().getX()

def getTopLeftY():
	return WORK_AREA.getTopLeft().getY()

def getArea(imgName):
	match = WORK_AREA.exists(imgName)
	if match != None  and match.getScore() >= DEFAULT_SIMILARITY_THRESHOLD :
		return match
	else :
		return lackey.Region(0, 0, 0, 0)

'''
def shiftLeft(area, offset):
	assert area[2] != 0 and area[3] != 0
	region = lackey.Region(area).left(offset)
	return (region.getX(), region.getY(), region.getW(), region.getH())

def shiftRight(area, offset):
	assert area[2] != 0 and area[3] != 0
	region = lackey.Region(area).right(offset)
	return (region.getX(), region.getY(), region.getW(), region.getH())

def shiftUp(area, offset):
	assert area[2] != 0 and area[3] != 0
	region = lackey.Region(area).above(offset)
	return (region.getX(), region.getY(), region.getW(), region.getH())

def shiftDown(area, offset):
	assert area[2] != 0 and area[3] != 0
	region = lackey.Region(area).below(offset)
	return (region.getX(), region.getY(), region.getW(), region.getH())
'''

'''
lackey的主要封装：
1. Region：区域（最主要类型，囊括了lackey一半的处理）
2. Pattern：用于封装一个图片
	- path：图像文件路径
	- similarity：相似度阈值
	- offset：距屏幕原点的偏移
3. Match：Region类型子类，用于获取匹配结果
	- X：中心点x轴坐标
	- Y：中心点y轴坐标
	- Score：相似度得分
	- Target
4. Screen：Region类型子类，封装的是PC显示器
5：Location：仅仅封装了一个二维坐标点
'''
	
if __name__ == '__main__':
	#pdb.set_trace()
	logging.basicConfig(level = logging.INFO)
	clickTimeOut('.\\images\\win_icon.jpg')
	target = getCenter('.\\images\\win_icon.jpg')
	logging.info('Matched coordinate is (%d, %d)' % (target.x, target.y))
