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
SIM_THRESHOLD	= 0.7	# It is minimum similarity threshold
TIMEOUT_SECOND	= 8

SHIFT_UP		= 0
SHIFT_DOWN		= 1
SHIFT_LEFT		= 2
SHIFT_RIGHT		= 3

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
	
# Static API
def scaleLength(length):
	global WORK_SCALE
	return WORK_SCALE * length

def scaleArea(x, y, w, h):
	global WORK_SCALE
	return lackey.Region(x, y, WORK_SCALE * w, WORK_SCALE * h)
	
def getCenter(region=None):
	global WORK_SCOPE
	if region is None: region = WORK_SCOPE
	return region.getCenter() # return a coordinate

def getTopLeft(region=None):
	global WORK_SCOPE
	if region is None: region = WORK_SCOPE
	return region.getTopLeft() # return a coordinate

def getTopRight(region=None):
	global WORK_SCOPE
	if region is None: region = WORK_SCOPE
	return region.getTopRight() # return a coordinate

def getBottomLeft(region=None):
	global WORK_SCOPE
	if region is None: region = WORK_SCOPE
	return region.getBottomLeft() # return a coordinate

def getBottomRight(region=None):
	global WORK_SCOPE
	if region is None: region = WORK_SCOPE
	return region.getBottomRight() # return a coordinate

def getWidth(region=None):
	global WORK_SCOPE
	if region is None: region = WORK_SCOPE
	return region.getW() # return a numeric

def getHeight(region=None):
	global WORK_SCOPE
	if region is None: region = WORK_SCOPE
	return region.getH() # return a numeric

def getTopLeftX(region=None):
	global WORK_SCOPE
	if region is None: region = WORK_SCOPE
	return region.getTopLeft().getX() # return a numeric

def getTopLeftY(region=None):
	global WORK_SCOPE
	if region is None: region = WORK_SCOPE
	return region.getTopLeft().getY() # return a numeric

def getImageArea(imgName, region=None):
	global WORK_SCOPE
	if region is None: region = WORK_SCOPE
	match = region.exists(imgName)
	if match != None and match.getScore() >= SIM_THRESHOLD :
		return match # return a area
	else :
		return lackey.Region(0, 0, 0, 0)

def shiftPos(srcPos, direction, offset):
	assert(isinstance(srcPos, lackey.Location))
	assert(direction <= SHIFT_RIGHT)
	assert(offset >= 0)
	shift = WORK_SCALE * offset
	if direction == SHIFT_UP:
		desPos = srcPos.above(shift)
	elif direction == SHIFT_DOWN:
		desPos = srcPos.below(shift)
	elif direction == SHIFT_LEFT:
		desPos = srcPos.left(shift)
	elif direction == SHIFT_RIGHT:
		desPos = srcPos.right(shift)
	return desPos
	
def existImage(imgName, region=None, timeout=None):
	global WORK_SCOPE
	if region is None: region = WORK_SCOPE
	if timeout is None: 
		match = region.exists(imgName)
	else:
		match = region.exists(imgName, timeout)
	return match != None and match.getScore() >= SIM_THRESHOLD

def findImages(imgName, region=None):
	global WORK_SCOPE
	if region is None: region = WORK_SCOPE
	return list(region.findAll(imgName))

# Dynamic API
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
	time.sleep(0.1)

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
		time.sleep(0.1)
	return count != timeout

def clickArea(region):
	assert(region.getW() != 0)
	assert(region.getH() != 0)
	region.click()
	time.sleep(0.1)

def clickPos(position):
	WORK_SCOPE.click(position)
	time.sleep(0.1)

def hoverImage(imgName, region=None):
	global WORK_SCOPE
	if region is None: region = WORK_SCOPE
	region.hover(imgName)

def hoverArea(region):
	assert(region.getW() != 0)
	assert(region.getH() != 0)
	pass # TODO

def hoverPos(position):
	global WORK_SCOPE
	WORK_SCOPE.hover(position)

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
	assert(direction <= SHIFT_RIGHT)
	# calculate filck distance
	distance = getHeight() if direction < SHIFT_LEFT else getWidth()
	distance /= 2
	distance -= 200 if direction < SHIFT_LEFT else 30
	setMoveMouseDelay(0.01)
	pos = getCenter()
	hoverPos(pos)
	mouseDown()
	time.sleep(0.01)
	for count in range(0, 4):
		pos = shiftPos(pos, direction, int(distance / 4))
		hoverPos(pos)
		#time.sleep(0.01)
	mouseUp()
	setMoveMouseDelay(0.3)
	time.sleep(0.2)
	
def flickDown():
	flick(SHIFT_DOWN)

def flickUp():
	flick(SHIFT_UP)

def flickLeft():
	flick(SHIFT_LEFT)

def flickRight():
	flick(SHIFT_RIGHT)

def longFlickUp():
	distance = getTopLeft().getY() + getHeight() - scaleLength(400)
	pos = shiftPos(getCenter(), SHIFT_DOWN, (getHeight() / 2 - scaleLength(200)))
	hoverPos(pos)
	mouseDown()
	time.sleep(0.1)
	for count in range(0, 8):
		if count < 2: delay = 0.02
		elif count < 4: delay = 0.01
		else: delay = 0.005
		setMoveMouseDelay(delay)
		pos = shiftPos(pos, SHIFT_UP, int(distance / 8))
		hoverPos(pos)
	mouseUp()
	setMoveMouseDelay(0.3)
	time.sleep(0.2)
	
def typeChar(text):
	global WORK_SCOPE
	WORK_SCOPE.type(text)
	time.sleep(0.1)

# Set Attribute API
def setSimThreshold(threshold):
	global SIM_THRESHOLD
	SIM_THRESHOLD = threshold

def setMoveMouseDelay(seconds):
	lackey.SettingsMaster.MoveMouseDelay = seconds
	
def setTimeout(seconds):
	lackey.setAutoWaitTimeout(seconds)

def enableSikuliLog():
	lackey.SettingsMaster.ActionLogs	= True
	lackey.SettingsMaster.InfoLogs		= True
	lackey.SettingsMaster.DebugLogs		= True
	lackey.SettingsMaster.ErrorLogs		= True
	lackey.SettingsMaster.UserLogs		= True

def disableSikuliLog():
	lackey.SettingsMaster.ActionLogs	= False
	lackey.SettingsMaster.InfoLogs		= False
	lackey.SettingsMaster.DebugLogs		= False
	lackey.SettingsMaster.ErrorLogs		= False
	lackey.SettingsMaster.UserLogs		= False
	
if __name__ == '__main__':
	#pdb.set_trace()
	logging.basicConfig(level = logging.INFO)
	setSimThreshold(0.75)
	clickImage('.\\images\\win_icon.jpg', lackey.Region(0, 0, 800, 1200))
	target = getImageArea('.\\images\\win_icon.jpg', lackey.Region(0, 0, 800, 1200))
	logging.info('Matched coordinate is (%d, %d)' % (target.x, target.y))
