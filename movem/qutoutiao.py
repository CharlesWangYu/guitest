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

from android import *

class QuTouTiao(App):
	def __init__(self, android):
		super(QuTouTiao, self).__init__(android)
		self.imgPath = os.path.abspath('.') + '\\images\\qutoutiao\\'
		self.isFirstOpen = True
		self.isCanceledGetRightNow = False
		
	def initScreen(self):
		# If program go here, QTT has been opened.
		# If this is the first time of QTT open, it is necessary that wait for clear rubbish message.
		if self.isFirstOpen:
			self.cancelGetRightNow()
			self.isFirstOpen = False
	
	def clickTask(self):
		self.foundThenClick('foot_task')
		self.cancelSignSuccess()
	
	def clickRefresh(self):
		self.foundThenClick('foot_refresh')
		time.sleep(2.5)
	
	def clickMine(self):
		self.foundThenClick('foot_mine')
	
	def clickTopLeftBack(self):
		pos = getTopLeft().right(43).below(80)
		clickPosition(pos)
	
	def clickTopRightBack(self):
		pos = getTopRight().left(43).below(80)
		clickPosition(pos)
	
	def igoreRubbishInfo(self):
		setTimeout(1)
		self.cancelPushingInfo()
		self.cancelGetRightNow()
		self.cancelSignSuccess()
		setTimeout(1)
	
	def cancelGetRightNow(self):
		if self.isCanceledGetRightNow: return
		setTimeout(3)
		if self.foundThenClick('get_right_now', DIRECTION_DOWN, 140):
			self.isCanceledGetRightNow = True
		setTimeout(1)
	
	def cancelSignSuccess(self):
		self.foundThenClick('sign_success', target='sign_success_cancel')
	
	def cancelPushingInfo(self):
		self.foundThenClick('i_know', DIRECTION_DOWN, 70)
	
	def cancelInviteFriends(self):
		self.foundThenClick('invite_friends', DIRECTION_DOWN, 140)
	
	def gotoFirstNews(self):
		while True:
			clickPosition(getCenter().below(250))
			time.sleep(0.5)
			if not self.findPolymorphicImage('praise'): return
			self.clickTopLeftBack()
			self.clickRefresh()
			hoverPosition(getCenter())
			wheelDown(5)
			time.sleep(0.5)
	
	def receiveGoldCoin(self):
		self.clickRefresh()
		self.foundThenClick('receive_gold_coin')
	
	def viewVideo(self, seconds):
		time.sleep(1)
		pos = getCenter().above(215)
		clickPosition(pos)
		time.sleep(seconds)
	
	def viewShortVideo(self, seconds):
		time.sleep(seconds)
	
	def viewArticle(self, seconds):
		hoverPosition(getCenter())
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
			hoverPosition(getCenter())
			wheelDown(1)
			# enter a task
			setSimilarity(0.95)
			if self.foundThenClick('sign_success', DIRECTION_RIGHT, 80):
				pass
			elif self.foundThenClick('view_2_min_video', DIRECTION_RIGHT, 80):
				self.viewVideo(140)
				self.clickTask()
				'''
				if exists(self.img('view_3_min_article.jpg')) :
					pos = getArea(self.img('view_3_min_article.jpg')).getCenter().right(80)
					clickPosition(pos)
					self.viewArticle(180)
					self.panel.clickBackBtn()
				'''
			elif self.foundThenClick('view_short_video', DIRECTION_RIGHT, 80):
				self.viewShortVideo(65)
				if self.panel.isFuncBtnShown():
					self.panel.clickBackBtn()
				else:
					self.clickTopLeftBack()
			elif self.foundThenClick('paly_cash_cow', DIRECTION_RIGHT, 80):
				self.palyCashCow()
				self.panel.clickBackBtn()
			elif self.foundThenClick('to_open_in_task', DIRECTION_DOWN, 7):
				time.sleep(6)
				self.panel.clickBackBtn()
				self.panel.clickBackBtn()
				time.sleep(1)
			else:
				pass
			setSimilarity(0.85)
			# finish opening treasure box
			self.foundThenClick('congratulation_for_open_box', DIRECTION_DOWN, 400)
			if self.foundThenClick('open_treasure_box'):
				self.foundThenClick('congratulation_for_open_box', DIRECTION_DOWN, 400)

class QTTOpen(Task):
	def execute(self):
		self.app.open()

class QTTClose(Task):
	def execute(self):
		self.app.close()

class QTTReceive(Task):
	def execute(self):
		self.app.open()
		self.app.receiveGoldCoin()

class QTTTreasureBox(Task):
	def execute(self):
		self.app.open()
		for count in range(0, 5):
			self.app.openTreasureBox()

class QTTBrowseNews(Task):
	def execute(self):
		self.app.close()
		for count in range(0, 2000):
			self.app.open()
			self.app.clickRefresh()
			self.app.gotoFirstNews()
			self.app.viewArticle(32)
			self.app.close()
	
if __name__ == '__main__':
	import remote
	#pdb.set_trace()
	#os._exit(0)
	logging.basicConfig(level = logging.INFO)
	ctrl = remote.Scrcpy()
	ctrl.connect()
	app = QuTouTiao(android.Android('redmik20pro_miui11'))
	tasks = TaskSet()
	tasks.register(QTTClose(app))
	tasks.register(QTTOpen(app))
	tasks.register(QTTReceive(app))
	#tasks.register(QTTTreasureBox(app))
	tasks.register(QTTBrowseNews(app))
	tasks.execute()
	