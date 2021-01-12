# -*-coding:utf-8 -*-
'''
@File		: mouse2.py
@Date		: 2021/01/01
@Author		: Wang.Yu
@Version	: 1.0
@Contact	: ouu_cn@163.com
@License	: (C)Copyright 2021, Personal exclusive right.
'''
import pdb
import logging
from numpy import *
from pynput import *

DRAG_STEP_DISTANCE	= 10
SWIPE_STEP_DISTANCE	= 15
SWIPE_DISTANCE		= 150

m = mouse.Controller()

def getCursorPos():
	return m.position

'''
def leftClick(desPt):
	(x, y) = desPt
	m.move(x, y)
	m.press(mouse.Button.left)
	m.release(mouse.Button.left)
'''

def pressMove(srcPt, desPt, step = DRAG_STEP_DISTANCE):
	(x0, y0) = m.position
	(x1, y1) = srcPt
	(x2, y2) = desPt
	
	xDiff = x2 - x1
	yDiff = y2 - y1
	dist  = int(sqrt(square(xDiff) + square(yDiff)))
	count = int(dist / step)
	xStep = int(xDiff / dist * step)
	yStep = int(yDiff / dist * step)
	xResi = xDiff - xStep * count
	yResi = yDiff - yStep * count
	
	m.move(x1 - x0, y1 - y0)
	for x in range(0, count):
		m.press(mouse.Button.left)
		m.move(xStep, yStep)
	m.press(mouse.Button.left)
	m.move(xResi, yResi)
	m.release(mouse.Button.left)

def dragTo(desPt, step = DRAG_STEP_DISTANCE):
	pressMove(m.position, desPt, step)

def dragLeft(diff):
	(x, y) = m.position
	desPt = (x - diff, y)
	dragTo(desPt)

def dragRight(diff):
	(x, y) = m.position
	desPt = (x + diff, y)
	dragTo(desPt)

def dragUp(diff):
	(x, y) = m.position
	desPt = (x, y - diff)
	dragTo(desPt)

def dragDown(diff):
	(x, y) = m.position
	desPt = (x, y + diff)
	dragTo(desPt)

def swipeTo(desPt):
	(x1, y1) = m.position
	(x2, y2) = desPt
	xDiff = int((x2 - x1) / 2)
	yDiff = int((y2 - y1) / 2)
	midPt = (x1 + xDiff, y1 + yDiff)
	pressMove(m.position, midPt, SWIPE_STEP_DISTANCE)
	dist  = int(sqrt(square(xDiff) + square(yDiff)))
	count = int(dist / SWIPE_STEP_DISTANCE)
	xStep = int(xDiff / dist * SWIPE_STEP_DISTANCE)
	yStep = int(yDiff / dist * SWIPE_STEP_DISTANCE)
	xResi = xDiff - xStep * count
	yResi = yDiff - yStep * count
	for x in range(0, count):
		m.move(xStep, yStep)
	m.move(xResi, yResi)

def swipeLeft():
	(x, y) = m.position
	desPt = (x - SWIPE_DISTANCE, y)
	swipeTo(desPt)

def swipeRight():
	(x, y) = m.position
	desPt = (x + SWIPE_DISTANCE, y)
	swipeTo(desPt)

def swipeUp():
	(x, y) = m.position
	desPt = (x, y - SWIPE_DISTANCE)
	swipeTo(desPt)

def swipeDown():
	(x, y) = m.position
	desPt = (x, y + SWIPE_DISTANCE)
	swipeTo(desPt)

if __name__ == '__main__':
	import time
	#pdb.set_trace()
	logging.basicConfig(level = logging.INFO)
	# test drag
	logging.info('Please put mouse cursor on an icon.')
	logging.info('The icon will move 40 dip to the right.')
	time.sleep(4)
	dragRight(100)
	time.sleep(4)
	logging.info('')
	logging.info('Please put mouse cursor on an icon.')
	logging.info('The icon will swipe upward.')
	time.sleep(4)
	swipeUp()
