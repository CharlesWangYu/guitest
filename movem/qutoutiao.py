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

from task import *

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
		self.clickAfterSeeingSth('foot_task')
		self.cancelSignSuccess()
	
	def clickRefresh(self):
		self.clickAfterSeeingSth('foot_refresh')
		time.sleep(2.5)
	
	def clickMine(self):
		self.clickAfterSeeingSth('foot_mine')
	
	def clickTopLeftBack(self):
		pos = sikuli2.getTopLeft().right(43).below(80)
		sikuli2.clickPosition(pos)
	
	def clickTopRightBack(self):
		pos = sikuli2.getTopRight().left(43).below(80)
		sikuli2.clickPosition(pos)
	
	def igoreRubbishInfo(self):
		sikuli2.setTimeout(1)
		self.cancelPushingInfo()
		self.cancelGetRightNow()
		self.cancelSignSuccess()
		sikuli2.setTimeout(1)
	
	def cancelGetRightNow(self):
		if self.isCanceledGetRightNow: return
		sikuli2.setTimeout(3)
		if self.clickAfterSeeingSth('get_right_now', App.BELOW, 140):
			self.isCanceledGetRightNow = True
		sikuli2.setTimeout(1)
	
	def cancelSignSuccess(self):
		self.clickAfterSeeingSth('sign_success', target='sign_success_cancel')
	
	def cancelPushingInfo(self):
		self.clickAfterSeeingSth('i_know', App.BELOW, 70)
	
	def cancelInviteFriends(self):
		self.clickAfterSeeingSth('invite_friends', App.BELOW, 140)
	
	def gotoFirstNews(self):
		while True:
			pos = sikuli2.getCenter().below(250)
			sikuli2.clickPosition(pos)
			time.sleep(0.5)
			if not self.findPolymorphicImage('praise'): return
			self.clickTopLeftBack()
			self.clickRefresh()
			self.hoverCenter()
			sikuli2.wheelDown(5)
			time.sleep(0.5)
	
	def receiveGoldCoin(self):
		self.clickRefresh()
		self.clickAfterSeeingSth('receive_gold_coin')
	
	def viewVideo(self, seconds):
		time.sleep(1)
		pos = sikuli2.getCenter().above(215)
		sikuli2.clickPosition(pos)
		time.sleep(seconds)
	
	def viewShortVideo(self, seconds):
		time.sleep(seconds)
	
	def viewArticle(self, seconds):
		self.hoverCenter()
		for x in range(0, int(seconds/2)):
			if x % 2 == 0: sikuli2.wheelDown(3)
			else: sikuli2.wheelUp(2)
			time.sleep(2)
		
	def signInToday(self):
		pass
	
	def palyCashCow(self):
		self.clickAfterSeeingSth('50_gold_coins')
		time.sleep(65)
		self.clickTopLeftBack()
		self.clickTopRightBack()
		time.sleep(0.1)
	
	def openTreasureBox(self):
		for count in range(0, 3):
			# ready to enter a task for opening treasure box
			self.clickRefresh()
			self.clickTask()
			self.hoverCenter()
			sikuli2.wheelDown(1)
			# enter a task
			sikuli2.setSimilarity(0.95)
			if self.clickAfterSeeingSth('sign_success', App.RIGHT, 80):
				pass
			elif self.clickAfterSeeingSth('view_2_min_video', App.RIGHT, 80):
				self.viewVideo(140)
				self.clickTask()
				'''
				if sikuli2.exists(self.img('view_3_min_article.jpg')) :
					pos = sikuli2.getArea(self.img('view_3_min_article.jpg')).getCenter().right(80)
					sikuli2.clickPosition(pos)
					self.viewArticle(180)
					self.panel.clickBackBtn()
				'''
			elif self.clickAfterSeeingSth('view_short_video', App.RIGHT, 80):
				self.viewShortVideo(65)
				if self.panel.isFuncBtnShown():
					self.panel.clickBackBtn()
				else:
					self.clickTopLeftBack()
			elif self.clickAfterSeeingSth('paly_cash_cow', App.RIGHT, 80):
				self.palyCashCow()
				self.panel.clickBackBtn()
			elif self.clickAfterSeeingSth('to_open_in_task', App.BELOW, 7):
				time.sleep(6)
				self.panel.clickBackBtn()
				self.panel.clickBackBtn()
				time.sleep(1)
			else:
				pass
			sikuli2.setSimilarity(0.85)
			# finish opening treasure box
			self.clickAfterSeeingSth('congratulation_for_open_box', App.BELOW, 400)
			if self.clickAfterSeeingSth('open_treasure_box'):
				self.clickAfterSeeingSth('congratulation_for_open_box', App.BELOW, 400)

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
	