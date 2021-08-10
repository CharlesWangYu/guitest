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

#WIDTH			= win32print.GetDeviceCaps(win32gui.GetDC(0), win32con.DESKTOPHORZRES)
#HEIGHT			= win32print.GetDeviceCaps(win32gui.GetDC(0), win32con.DESKTOPVERTRES)
WORK_SCOPE		= lackey.Region(0, 0, 0, 0) # (x, y, w, h = args)
WORK_SCALE		= 1
SIM_THRESHOLD	= 0.85
TIMEOUT_SECOND	= 8

DIRECTION_UP	= 0
DIRECTION_DOWN	= 1
DIRECTION_LEFT	= 2
DIRECTION_RIGHT	= 3

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
5. Location：仅仅封装了一个二维坐标点
'''

# Init API
def initScreenScope(uiaRect):
	global		WORK_SCOPE
	left		= uiaRect.left
	top			= uiaRect.top
	width		= uiaRect.right - uiaRect.left
	height		= uiaRect.bottom - uiaRect.top
	WORK_SCOPE	= lackey.Region(left, top, width, height)

def initScreenScale(scale):
	global		WORK_SCALE
	WORK_SCALE 	= scale

# Location Access API
def getCenter():
	global WORK_SCOPE
	return WORK_SCOPE.getCenter() # return a coordinate

def getTopLeft():
	global WORK_SCOPE
	return WORK_SCOPE.getTopLeft() # return a coordinate

def getTopRight():
	global WORK_SCOPE
	return WORK_SCOPE.getTopRight() # return a coordinate

def getBottomLeft():
	global WORK_SCOPE
	return WORK_SCOPE.getBottomLeft() # return a coordinate

def getBottomRight():
	global WORK_SCOPE
	return WORK_SCOPE.getBottomRight() # return a coordinate

def getWidth():
	global WORK_SCOPE
	return WORK_SCOPE.getW() # return a numeric

def getHeight():
	global WORK_SCOPE
	return WORK_SCOPE.getH() # return a numeric

def getTopLeftX():
	global WORK_SCOPE
	return WORK_SCOPE.getTopLeft().getX() # return a numeric

def getTopLeftY():
	global WORK_SCOPE
	return WORK_SCOPE.getTopLeft().getY() # return a numeric

def getImageArea(imgName, region=None):
	global WORK_SCOPE
	if region is None: region = WORK_SCOPE
	match = region.exists(imgName)
	if match != None and match.getScore() >= SIM_THRESHOLD :
		return match # return a area
	else :
		return lackey.Region(0, 0, 0, 0)
	
# Query API
def existImage(imgName, region=None, timeout=None):
	global WORK_SCOPE
	if region is None: region = WORK_SCOPE
	if timeout is None: 
		match = region.exists(imgName)
	else:
		match = region.exists(imgName, timeout)
	return match != None and match.getScore() >= SIM_THRESHOLD

'''
def findAll(imgName, timeout=None):
	return list(WORK_SCOPE.findAll(imgName))
'''

# Action API
def waitImage(imgName):
	count = 0
	timeout = TIMEOUT_SECOND * 10
	while (not existImage(imgName)) and (count < timeout):
		time.sleep(0.1)
		count += 1
	return count != timeout # True: success, False: overtime

def clickImage(imgName, region=None):
	global WORK_SCOPE
	if region is None: region = WORK_SCOPE
	if existImage(imgName, region):
		region.click(imgName)
		time.sleep(0.1)
		return True
	else:
		return False

def clickImageBlock(imgName, region=None):
	global WORK_SCOPE
	if region is None: region = WORK_SCOPE
	while not existImage(imgName, region):
		time.sleep(0.1)
	return region.click(imgName)

def clickImageTimeOut(imgName, region=None):
	global WORK_SCOPE
	if region is None: region = WORK_SCOPE
	count = 0
	timeout = TIMEOUT_SECOND * 10
	while (not existImage(imgName, region)) and (count < timeout):
		time.sleep(0.1)
		count += 1
	if count != timeout:
		region.click(imgName)
	return count != timeout

def clickArea(region):
	assert(region.getW() != 0)
	assert(region.getH() != 0)
	region.click()
	time.sleep(0.1)

def clickPosition(position):
	WORK_SCOPE.click(position)
	time.sleep(0.1)

def hoverImage(imgName, region=None):
	global WORK_SCOPE
	if region is None: region = WORK_SCOPE
	region.hover(imgName)
	time.sleep(0.1)

def hoverArea(region):
	assert(region.getW() != 0)
	assert(region.getH() != 0)
	pass # TODO

def hoverPosition(position):
	global WORK_SCOPE
	WORK_SCOPE.hover(position)
	time.sleep(0.1)

def wheelDown(steps):
	global WORK_SCOPE
	WORK_SCOPE.wheel(0, steps) # 0:Down
	time.sleep(0.1)

def wheelUp(steps):
	global WORK_SCOPE
	WORK_SCOPE.wheel(1, steps) # 1:Up
	time.sleep(0.1)

def mouseDown():
	global WORK_SCOPE
	WORK_SCOPE.mouseDown()

def mouseUp():
	global WORK_SCOPE
	WORK_SCOPE.mouseUp()
	
def leftClick():
	mouse = lackey.Mouse()
	mouse.click(button=mouse.LEFT)

def rightClick():
	mouse = lackey.Mouse()
	mouse.click(button=mouse.RIGHT)

def flick(direction):
	assert(direction <= DIRECTION_RIGHT)
	# calculate filck distance
	distance = WORK_SCOPE.getH() if direction < DIRECTION_LEFT else WORK_SCOPE.getW()
	distance /= 2
	distance -= 200 if direction < DIRECTION_LEFT else 30
	lackey.SettingsMaster.MoveMouseDelay = 0.01
	pos = WORK_SCOPE.getCenter()
	hoverPosition(pos)
	mouseDown()
	time.sleep(0.01)
	flickStep  = int(distance / 4)
	for count in range(0, 4):
		if direction == DIRECTION_UP:
			pos = pos.above(flickStep)
		elif direction == DIRECTION_DOWN:
			pos = pos.below(flickStep)
		elif direction == DIRECTION_LEFT:
			pos = pos.left(flickStep)
		elif direction == DIRECTION_RIGHT:
			pos = pos.right(flickStep)
		hoverPosition(pos)
	mouseDown()
	lackey.SettingsMaster.MoveMouseDelay = 0.3
	time.sleep(0.2)
	
def flickDown():
	flick(DIRECTION_DOWN)

def flickUp():
	flick(DIRECTION_UP)

def flickLeft():
	flick(DIRECTION_LEFT)

def flickRight():
	flick(DIRECTION_RIGHT)

def typeChar(text):
	global WORK_SCOPE
	WORK_SCOPE.type(text)
	time.sleep(0.1)

# Set Attribute API
def setSimThreshold(threshold):
	global SIM_THRESHOLD
	SIM_THRESHOLD = threshold

def setTimeout(seconds):
	lackey.setAutoWaitTimeout(seconds)

def enableInfoLog():
	lackey.SettingsMaster.InfoLogs = True

def disableInfoLog():
	lackey.SettingsMaster.InfoLogs = False

def enableActionLog():
	lackey.SettingsMaster.ActionLogs = True

def disableActionLog():
	lackey.SettingsMaster.ActionLogs = False
	
if __name__ == '__main__':
	#pdb.set_trace()
	logging.basicConfig(level = logging.INFO)
	setSimThreshold(0.75)
	clickImage('.\\images\\win_icon.jpg', lackey.Region(0, 0, 800, 1200))
	target = getImageArea('.\\images\\win_icon.jpg', lackey.Region(0, 0, 800, 1200))
	logging.info('Matched coordinate is (%d, %d)' % (target.x, target.y))
