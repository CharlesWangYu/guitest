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

WHEEL_DOWN		= 0
WHEEL_UP		= 1
TIMEOUT_LIMIT	= 80	# 8s
WORK_AREA		= lackey.Region(0, 0, win32print.GetDeviceCaps(win32gui.GetDC(0), win32con.DESKTOPHORZRES), win32print.GetDeviceCaps(win32gui.GetDC(0), win32con.DESKTOPVERTRES)) # (x, y, w, h = args)
DEFAULT_SIMILARITY_THRESHOLD	= 0.85

def initGlobalRegion(uiaRect):
	left	= uiaRect.left
	top		= uiaRect.top
	width	= uiaRect.right - uiaRect.left
	height	= uiaRect.bottom - uiaRect.top
	WORK_AREA = lackey.Region(left, top, width, height)
	logging.info('Working area is (%d,%d,%d,%d)' %(left, top, width, height))

def exists(imgName):
	match = WORK_AREA.exists(imgName)
	return match != None and match.getScore() >= DEFAULT_SIMILARITY_THRESHOLD

def clickImage(imgName):
	if exists(imgName):
		WORK_AREA.click(imgName)
		time.sleep(0.1)
	return exists(imgName)

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

def getArea(imgName):
	region = WORK_AREA.exists(imgName)
	if region.getScore() >= DEFAULT_SIMILARITY_THRESHOLD :
		return (region.getX(), region.getY(), region.getW(), region.getH())
	else :
		return (0, 0, 0, 0)

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

def clickArea(area):
	assert area[2] != 0 and area[3] != 0
	region = lackey.Region(area)
	region.click()
	time.sleep(0.1)
	return True

def wheel(direction, steps):
	WORK_AREA.wheel(direction, steps)
	time.sleep(0.1)
	
# TODO
def getCenter(imgName):
	match = exists(imgName)
	return match.getTarget()

def type(text):
	WORK_AREA.type(text)
	time.sleep(0.1)

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
