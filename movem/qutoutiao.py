# -*-coding:utf-8 -*-
'''
@File		: qutaotiao.py
@Date		: 2021/01/15
@Author		: Wang.Yu
@Version	: 1.0
@Contact	: ouu_cn@163.com
@License	: (C)Copyright 2021, Personal exclusive right.
'''
import pdb
import logging
import time

from app import *

MAX_NEWS_ABSTRACT_HEIGHT	= 200
TOP_BACK_BTN_X_OFFSET		= 43
TOP_BACK_BTN_Y_OFFSET		= 80
ABSTRACT_POS_X_OFFSET		= 40
ABSTRACT_POS_Y_OFFSET		= 50
NECESSARY_READING_TIMES		= 150
RESIDENCE_ARTICLE_SECOND	= 22

class QuTouTiao(App):
	def __init__(self, platform):
		super(QuTouTiao, self).__init__(platform)
		self.imgPath = os.path.abspath('.') + '\\res\\app\\qutoutiao\\'
		
	def initEntry(self):
		pass
	
	def clickTask(self):
		self.foundThenClick('foot_task')
		#self.cancelSignSuccess()
	
	def clickRefresh(self):
		self.foundThenClick('foot_refresh')
		time.sleep(1.5) # Here are some delay because of connecting network
	
	def clickMine(self):
		self.foundThenClick('foot_mine')
	
	def clickTopLeftBack(self):
		pos = shiftPos(getTopLeft(), SHIFT_RIGHT, TOP_BACK_BTN_X_OFFSET)
		pos = shiftPos(pos, SHIFT_DOWN, TOP_BACK_BTN_Y_OFFSET)
		clickPos(pos)
	
	def clickTopRightBack(self):
		pos = shiftPos(getTopRight(), SHIFT_LEFT, TOP_BACK_BTN_X_OFFSET)
		pos = shiftPos(pos, SHIFT_DOWN, TOP_BACK_BTN_Y_OFFSET)
		clickPos(pos)
	
	def selectAnAbstract(self):
		cnt = 0
		while True:
			xIcons = self.findAllImage('x_below_news')
			if len(xIcons) > 1:
				for x in range(len(xIcons)-1, 0, -1):
					height = xIcons[x].getY() - xIcons[x-1].getY()
					if height < scaleLength(MAX_NEWS_ABSTRACT_HEIGHT):
						pos = getTopLeft(xIcons[x])
						pos = shiftPos(pos, SHIFT_UP, ABSTRACT_POS_Y_OFFSET)
						pos = shiftPos(pos, SHIFT_LEFT, ABSTRACT_POS_X_OFFSET)
						clickPos(pos)
						time.sleep(1)
						if self.isInsideNormalNews():
							return
						elif self.isInsidePoliticalNews():
							self.app.clickAndroidBackBtn()
							time.sleep(0.5)
			hoverPos(getCenter())
			if cnt % 2 == 0: wheelDown(5)
			else: self.clickRefresh()
			time.sleep(0.5)
			cnt += 1
	
	def readOneNews(self, seconds):
		for x in range(0, int(seconds/2)):
			hoverPos(getCenter())
			if x % 2 == 0: wheelDown(3)
			else: wheelUp(2)
			self.checkReadingReward()
	
	def dailySign(self):
		self.clickMine()
		time.sleep(1)
		if self.foundThenClick('daily_sign'):
			time.sleep(2)
			self.clickAndroidBackBtn()
			time.sleep(0.5)
	
	def checkReadingReward(self):
		if self.foundThenClick('reward_for_reading'):
			time.sleep(2.5)
			self.clickAndroidBackBtn()
			time.sleep(1)
	
	def isInsideAbstract(self):
		return self.findFirstImage('flag_abstract_page')
	
	def isInsideNormalNews(self):
		return self.findFirstImage('flag_news_page')
	
	def isInsidePoliticalNews(self):
		return self.findFirstImage('flag_politics_page')
		
	'''
	def igoreRubbishInfo(self):
		setTimeout(1)
		self.cancelPushingInfo()
		self.cancelGetRightNow()
		self.cancelSignSuccess()
		setTimeout(1)
	
	def cancelGetRightNow(self):
		if self.isCanceledGetRightNow: return
		setTimeout(3)
		if self.foundThenClick('get_right_now', SHIFT_DOWN, 140):
			self.isCanceledGetRightNow = True
		setTimeout(1)
	
	def cancelSignSuccess(self):
		self.foundThenClick('sign_success', target='sign_success_cancel')
	
	def cancelPushingInfo(self):
		self.foundThenClick('i_know', SHIFT_DOWN, 70)
	
	def cancelInviteFriends(self):
		self.foundThenClick('invite_friends', SHIFT_DOWN, 140)
	
	def gotoFirstNews(self):
		while True:
			clickPos(shiftPos(getCenter(), SHIFT_DOWN, 250))
			time.sleep(0.5)
			if not self.findPolymorphicImage('praise'): return
			self.clickTopLeftBack()
			self.clickRefresh()
			hoverPos(getCenter())
			wheelDown(5)
			time.sleep(0.5)
	
	def receiveGoldCoin(self):
		self.clickRefresh()
		self.foundThenClick('receive_gold_coin')
	
	def viewVideo(self, seconds):
		time.sleep(1)
		pos = getCenter().above(215)
		clickPos(pos)
		time.sleep(seconds)
	
	def viewShortVideo(self, seconds):
		time.sleep(seconds)
	
	def viewArticle(self, seconds):
		hoverPos(getCenter())
		for x in range(0, int(seconds/2)):
			if x % 2 == 0: wheelDown(3)
			else: wheelUp(2)
			time.sleep(2)
		
	def signInToday(self):
		pass
	
	def palyCashCow(self):
		self.foundThenClick('50_gold_coins')
		time.sleep(65)
		self.clickTopLeftBack()
		self.clickTopRightBack()
		time.sleep(0.1)
	
	def openTreasureBox(self):
		for count in range(0, 3):
			# ready to enter a task for opening treasure box
			self.clickRefresh()
			self.clickTask()
			hoverPos(getCenter())
			wheelDown(1)
			# enter a task
			setSimilarity(0.95)
			if self.foundThenClick('sign_success', SHIFT_RIGHT, 80):
				pass
			elif self.foundThenClick('view_2_min_video', SHIFT_RIGHT, 80):
				self.viewVideo(140)
				self.clickTask()
				#if exists(self.img('view_3_min_article.jpg')) :
				#	pos = getArea(self.img('view_3_min_article.jpg')).getCenter().right(80)
				#	clickPos(pos)
				#	self.viewArticle(180)
				#	self.clickAndroidBackBtn()
			elif self.foundThenClick('view_short_video', SHIFT_RIGHT, 80):
				self.viewShortVideo(65)
				if self.panel.isFuncBtnShown():
					self.clickAndroidBackBtn()
				else:
					self.clickTopLeftBack()
			elif self.foundThenClick('paly_cash_cow', SHIFT_RIGHT, 80):
				self.palyCashCow()
				self.clickAndroidBackBtn()
			elif self.foundThenClick('to_open_in_task', SHIFT_DOWN, 7):
				time.sleep(6)
				self.clickAndroidBackBtn()
				self.clickAndroidBackBtn()
				time.sleep(1)
			else:
				pass
			setSimilarity(0.85)
			# finish opening treasure box
			self.foundThenClick('congratulation_for_open_box', SHIFT_DOWN, 400)
			if self.foundThenClick('open_treasure_box'):
				self.foundThenClick('congratulation_for_open_box', SHIFT_DOWN, 400)
	'''
	
class QTTOpen(Task):
	def execute(self):
		self.app.start()
	
class QTTClose(Task):
	def execute(self):
		self.app.stop()
	
# Enter 'mine' page everyday to get qualification for withdraw cash
class QTTSignIn(Task):
	def execute(self):
		self.app.dailySign()
	
# Read news (article) to get golden coin
class QTTReadNews(Task):
	def execute(self):
		self.app.clickRefresh()
		for count in range(0, NECESSARY_READING_TIMES):
			self.app.clickRefresh()
			self.app.selectAnAbstract()
			time.sleep(0.5)
			self.app.readOneNews(RESIDENCE_ARTICLE_SECOND)
			self.app.clickAndroidBackBtn()
			time.sleep(0.5)
	
'''
class QTTReceive(Task):
	def execute(self):
		self.app.start()
		self.app.receiveGoldCoin()

class QTTTreasureBox(Task):
	def execute(self):
		self.app.start()
		for count in range(0, 5):
			self.app.openTreasureBox()
'''
	
if __name__ == '__main__':
	import remote
	#pdb.set_trace()
	#os._exit(0)
	logging.basicConfig(level = logging.INFO)
	ctrl = remote.Scrcpy()
	ctrl.connect()
	app = QuTouTiao(ctrl.platform())
	tasks = []
	tasks.append(ClearActiveApp(app))
	tasks.append(QTTOpen(app))
	tasks.append(QTTSignIn(app))
	tasks.append(QTTReadNews(app))
	tasks.append(QTTClose(app))
	for task in tasks:
		task.execute()
	ctrl.disconnect()
	