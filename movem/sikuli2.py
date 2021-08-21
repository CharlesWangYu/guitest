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
import os
import time
import lackey

from PIL import Image

# All distances in this project are screenshots and measured on a specific monitor. When the projection software is used on different monitors, a specific distance and coordinate transformation must be performed. The width and height of the projection software on a standard monitor are 431x961 pixels respectively.
TIMEOUT_SECOND	= 8
CANVAS			= lackey.Region(0, 0, 0, 0) # (x, y, w, h = args)
X_SCALE			= 1.0 # standard width is 431
Y_SCALE			= 1.0 # standard width is 961

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

###### Init API ######
def initCanvas(uiaRect):
	global	CANVAS
	left	= uiaRect.left
	top		= uiaRect.top
	width	= uiaRect.right - uiaRect.left
	height	= uiaRect.bottom - uiaRect.top
	CANVAS	= lackey.Region(left, top, width, height)

def initScale(xScale, yScale):
	assert(isinstance(xScale, float))
	assert(isinstance(yScale, float))
	global	X_SCALE
	global	Y_SCALE
	X_SCALE = xScale
	Y_SCALE = yScale
	
###### Static API ######
# The following API is used to transfer between logical and physical values.
def widthP2L(pw):
	assert(isinstance(pw, int))
	return int(pw / X_SCALE)
	
def widthL2P(lw):
	assert(isinstance(lw, int))
	return int(lw * X_SCALE)
	
def heightP2L(ph):
	assert(isinstance(ph, int))
	return int(ph / Y_SCALE)
	
def heightL2P(lh):
	assert(isinstance(lh, int))
	return int(lh * Y_SCALE)

def posP2L(pPos):
	assert(isinstance(pPos, lackey.Location) or (isinstance(pPos, tuple) and len(pPos) == 2))
	if isinstance(pPos, lackey.Location): pos = pPos
	else: pos = makePos(pPos)
	lx = int((pos.getX() - getTopLeftX()) / X_SCALE)
	ly = int((pos.getY() - getTopLeftY()) / Y_SCALE)
	return lackey.Location(lx, ly)

def posL2P(lPos):
	assert(isinstance(lPos, lackey.Location) or (isinstance(lPos, tuple) and len(lPos) == 2))
	if isinstance(lPos, lackey.Location): pos = lPos
	else: pos = makePos(lPos)
	px = int(pos.getX() * X_SCALE + getTopLeftX())
	py = int(pos.getY() * Y_SCALE + getTopLeftY())
	return lackey.Location(px, py)

def areaP2L(pArea):
	assert(isinstance(pArea, lackey.Region) or (isinstance(pArea, tuple) and len(pArea) == 4))
	if isinstance(pArea, lackey.Region): area = pArea
	else: area = makeArea(pArea)
	lx = int((getTopLeftX(area) - getTopLeftX()) / X_SCALE)
	ly = int((getTopLeftY(area) - getTopLeftY()) / Y_SCALE)
	lw = int(getWidth(area)  / X_SCALE)
	lh = int(getHeight(area) / Y_SCALE)
	return lackey.Region(lx, ly, lw, lh)

def areaL2P(lArea):
	assert(isinstance(lArea, lackey.Region) or (isinstance(lArea, tuple) and len(lArea) == 4))
	if isinstance(lArea, lackey.Region): area = lArea
	else: area = makeArea(lArea)
	px = int(getTopLeftX(area) * X_SCALE + getTopLeftX())
	py = int(getTopLeftY(area) * Y_SCALE + getTopLeftY())
	pw = int(getWidth(area)  * X_SCALE)
	ph = int(getHeight(area) * Y_SCALE)
	return lackey.Region(px, py, pw, ph)

'''
def scaleWidth(w):
	return int(X_SCALE * w)

def scaleHeight(h):
	return int(Y_SCALE * h)
	
def scalePos(x, y):
	return lackey.Location(x + getTopLeftX(), y + getTopLeftY())
	
def scaleArea(x, y, w, h):
	return lackey.Region(x + getTopLeftX(), y + getTopLeftY(), int(X_SCALE * w), int(Y_SCALE * h))
'''

# The following API does not distinguish logical and physical values.
def makeArea(region):
	assert(isinstance(region, tuple) and len(region) == 4)
	return lackey.Region(region)

def makePos(pos):
	assert(isinstance(pos, tuple) and len(pos) == 2)
	return lackey.Location(pos)
	
def getCenter(region=None):
	if region is None: region = CANVAS
	return region.getCenter() # return a coordinate

def getTopLeft(region=None):
	if region is None: region = CANVAS
	return region.getTopLeft() # return a coordinate

def getTopRight(region=None):
	if region is None: region = CANVAS
	return region.getTopRight() # return a coordinate

def getBottomLeft(region=None):
	if region is None: region = CANVAS
	return region.getBottomLeft() # return a coordinate

def getBottomRight(region=None):
	if region is None: region = CANVAS
	return region.getBottomRight() # return a coordinate

def getWidth(region=None):
	if region is None: region = CANVAS
	return region.getW() # return a numeric

def getHeight(region=None):
	if region is None: region = CANVAS
	return region.getH() # return a numeric

def getTopLeftX(region=None):
	if region is None: region = CANVAS
	return region.getTopLeft().getX() # return a numeric

def getTopLeftY(region=None):
	if region is None: region = CANVAS
	return region.getTopLeft().getY() # return a numeric

def getX(pos):
	return pos.getX() # return a numeric
	
def getY(pos):
	return pos.getY() # return a numeric

# This API is used to get the physical area
def getImageArea(imgName, region=None):
	if region is None: region = CANVAS
	match = region.exists(imgName)
	'''
	if match != None and match.getScore() >= SIM_THRESHOLD :
		return match # return a area
	else :
		return lackey.Region(0, 0, 0, 0)
	'''
	return match

def shiftPos(srcPos, direction, logicalOffset):
	# This API is used to transfer PHYSICAL values. This API is often used for coordinate transformation in actual coding, so I short it's function name. 
	# Notice ： Please pay attention to the third parameter that is still a logical value because of adapting to various actual sizes.
	assert(isinstance(srcPos, lackey.Location))
	lPos = posP2L(srcPos)
	lPos = shiftLogicalPos(lPos, direction, logicalOffset)
	desPos = posL2P(lPos)
	return desPos

def shiftLogicalPos(srcPos, direction, logicalOffset):
	assert(isinstance(srcPos, lackey.Location))
	assert(isinstance(direction, int) and direction <= SHIFT_RIGHT)
	assert(isinstance(logicalOffset, int) and logicalOffset > 0)
	
	if direction == SHIFT_UP:
		desPos = srcPos.above(logicalOffset)
	elif direction == SHIFT_DOWN:
		desPos = srcPos.below(logicalOffset)
	elif direction == SHIFT_LEFT:
		desPos = srcPos.left(logicalOffset)
	elif direction == SHIFT_RIGHT:
		desPos = srcPos.right(logicalOffset)
	return desPos
	
def existImage(imgName, region=None, timeout=None):
	if region is None: region = CANVAS
	if timeout is None: 
		match = region.exists(imgName)
	else:
		match = region.exists(imgName, timeout)
	#return match != None and match.getScore() >= SIM_THRESHOLD
	return match != None

def findImage(imgName, region=None):
	if region is None: region = CANVAS
	return region.findBest(imgName)
	
def findImages(imgName, region=None):
	if region is None: region = CANVAS
	return list(region.findAll(imgName))

###### Dynamic API ######
# Notice : When parameters such as length, coordinates, and area are used in the following APIs, the physical length, coordinates, and area are uniformly adopted.
def waitImage(imgName):
	count = 0
	timeout = TIMEOUT_SECOND * 10
	while (not existImage(imgName)) and (count < timeout):
		time.sleep(0.1)
		count += 1
	return count != timeout # True: success, False: overtime

def clickImage(imgName, region=None):
	if region is None: region = CANVAS
	if existImage(imgName, region):
		region.click(imgName)
		time.sleep(0.1)
		return True
	else:
		return False

def clickImageBlock(imgName, region=None):
	if region is None: region = CANVAS
	while not existImage(imgName, region):
		time.sleep(0.1)
	return region.click(imgName)
	time.sleep(0.1)

def clickImageTimeOut(imgName, region=None):
	if region is None: region = CANVAS
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
	CANVAS.click(position)
	time.sleep(0.1)

def hoverImage(imgName, region=None):
	if region is None: region = CANVAS
	region.hover(imgName)

def hoverArea(region):
	assert(region.getW() != 0)
	assert(region.getH() != 0)
	pass # TODO

def hoverPos(position):
	CANVAS.hover(position)

def wheelDown(steps):
	CANVAS.wheel(0, steps) # 0:Down
	time.sleep(0.1)

def wheelUp(steps):
	CANVAS.wheel(1, steps) # 1:Up
	time.sleep(0.1)

def mouseDown():
	CANVAS.mouseDown()

def mouseUp():
	CANVAS.mouseUp()
	
def leftClick():
	mouse = lackey.Mouse()
	mouse.click(button=mouse.LEFT)

def rightClick():
	mouse = lackey.Mouse()
	mouse.click(button=mouse.RIGHT)

def flick(direction, startPos=None):
	assert(isinstance(direction, int) and direction <= SHIFT_RIGHT)
	assert(isinstance(startPos, lackey.Location))
	# calculate filck distance
	distance = 961 if direction < SHIFT_LEFT else 431
	distance /= 2
	distance -= 200 if direction < SHIFT_LEFT else 30
	setMoveMouseDelay(0.01)
	if startPos is None: pos = getCenter()
	else: pos = startPos
	hoverPos(pos)
	mouseDown()
	time.sleep(0.01)
	for count in range(0, 4):
		pos = shiftPos(pos, direction, int(distance / 4))
		hoverPos(pos)
	mouseUp()
	setMoveMouseDelay(0.3)
	time.sleep(0.2)
	
def flickDown(startPos=None):
	flick(SHIFT_DOWN, startPos)

def flickUp(startPos=None):
	flick(SHIFT_UP, startPos)

def flickLeft(startPos=None):
	flick(SHIFT_LEFT, startPos)

def flickRight(startPos=None):
	flick(SHIFT_RIGHT, startPos)

def shortFlickUp():
	distance = heightL2P(240)
	pos = shiftPos(getCenter(), SHIFT_DOWN, 100)
	hoverPos(pos)
	mouseDown()
	time.sleep(0.1)
	setMoveMouseDelay(0.2)
	for count in range(0, 4):
		pos = shiftPos(pos, SHIFT_UP, int(distance / 4))
		hoverPos(pos)
	mouseUp()
	setMoveMouseDelay(0.3)
	time.sleep(0.2)
	
def longFlickUp():
	distance = heightL2P(961-400)
	pos = shiftPos(getCenter(), SHIFT_DOWN, int(961 / 2 - 200))
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
	CANVAS.type(text)
	time.sleep(0.1)

def pasteChar(text):
	CANVAS.paste(text)
	time.sleep(0.1)

###### OCR process API ######
def testImageArea(x, y, w, h):
	region = areaP2L(x, y, w, h)
	region.saveScreenCapture(os.path.abspath('.') + '\\', 'test')
	
def saveImageFile(path=None, file=None, region=None):
	if region is None: region = CANVAS
	if (path is None) and (file is None):
		region.saveScreenCapture()
	elif file is None:
		region.saveScreenCapture(path)
	else:
		region.saveScreenCapture(path, file)

###### Set Attribute API ######
def setSimThreshold(similarity):
	lackey.SettingsMaster.MinSimilarity = similarity

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
