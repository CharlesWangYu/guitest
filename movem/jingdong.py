# -*-coding:utf-8 -*-
'''
@File		: jingdong.py
@Date		: 2021/01/23
@Author		: Wang.Yu
@Version	: 1.0
@Contact	: ouu_cn@163.com
@License	: (C)Copyright 2021, Personal exclusive right.
'''
import pdb
import logging
import time

from task import *

class JingDong(App):
	def __init__(self, android):
		super(JingDong, self).__init__(android)
		self.imgPath = os.path.abspath('.') + '\\images\\jingdong\\'

	def clickHome(self):
		self.foundThenClick('foot_home')

	def clickSort(self):
		self.foundThenClick('foot_sort')

	def clickDiscovery(self):
		self.foundThenClick('foot_discovery')

	def clickCart(self):
		self.foundThenClick('foot_cart')

	def clickMine(self):
		self.foundThenClick('foot_mine')

	def clickLiveRoomBack(self):
		pos = sikuli2.getTopRight().left(30).below(70)
		sikuli2.clickPosition(pos)

	def clickLiveRoomShare(self):
		pos = sikuli2.getTopRight().left(73).below(70)
		sikuli2.clickPosition(pos)

	def enterMoreChanel(self):
		if self.findPolymorphicImage('more_channel_title.jpg'):
			self.hoverCenter()
			sikuli2.wheelUp(30)
			return True
		else:
			self.clickHome()
			self.hoverCenter()
			for count in range(0,6):
				if self.foundThenClick('more_channel.jpg'):
					return True
				else:
					sikuli2.flickLeft()
			return False

	def enterLiveRoom(self):
		self.clickHome()
		self.hoverCenter()
		for count in range(0,6):
			if self.foundThenClick('live_room_entry'):
				return True
			time.sleep(0.5)
		return False
	
	def enterBoBoRock(self):
		self.enterLiveRoom()
		for count in range(0,6):
			if self.foundThenClick('boborock'):
				return True
			time.sleep(0.5)
		return False

	def enterSuperMarket(self):
		self.clickHome()
		self.hoverCenter()
		for count in range(0,6):
			if self.foundThenClick('supermarket'):
				return True
			else:
				sikuli2.flickRight()
		return False

	def enterBeansRoom(self):
		self.clickHome()
		self.hoverCenter()
		for count in range(0,6):
			if self.foundThenClick('get_beans.jpg'):
				return True
			else:
				sikuli2.flickRight()
		return False

	def enterChannel(self, channelName):
		if not self.enterMoreChanel(): return False
		for count in range(0,20):
			if self.foundThenClick(channelName):
				time.sleep(2)
				return True
			else:
				sikuli2.wheelDown(3)
				time.sleep(0.4)
		return False

	def signInBoBoRock(self):
		# wait for boborock displayed
		self.hoverCenter()
		for count in range(0,6):
			if self.findPolymorphicImage('sign_in_boborock_finished.jpg'): return True
			if self.findPolymorphicImage('sign_in_boborock.jpg'): break
			time.sleep(0.5)
		# sign in
		if not self.foundThenClick('sig_in_boborock.jpg'): return False
		logging.info('The beans for sign in boborock have been successfully obtained!')
		time.sleep(0.5)
		self.foundThenClick('boborock_reward_ok.jpg')
		time.sleep(0.5)
		return True

	def shareAndViewBroadcast(self):
		delay = [120, 120, 120]
		self.hoverCenter()
		for count in range(0,3):
			# wait for 'to view' button displayed
			time.sleep(0.5)
			toShare = False
			toView  = False
			for count in range(0,6):
				if self.findPolymorphicImage('to_share_broadcast.jpg'):
					toShare = True
					break
				if self.findPolymorphicImage('to_view_broadcast.jpg'):
					toShare = True
					break
				time.sleep(0.5)
			if not (toShare or toView): return
			# enter live room
			if toShare: self.foundThenClick('to_share_broadcast.jpg')
			else: self.foundThenClick('to_view_broadcast.jpg')
			# share broadcast to wechat
			time.sleep(0.5)
			self.clickLiveRoomShare()
			time.sleep(0.5)
			self.foundThenClick('share_to_wechat_friends.jpg')
			time.sleep(1)
			self.foundThenClick('share_to_assistant.jpg')
			time.sleep(0.5)
			self.foundThenClick('wechat_share_button.jpg')
			time.sleep(0.5)
			self.foundThenClick('return_to_jingdog.jpg')
			# view live broadcast
			if self.findPolymorphicImage('boborock_get_beans_flag.jpg'):
				while True:
					# lottery
					if self.findPolymorphicImage('lottery_right_now.jpg'):
						self.foundThenClick('lottery_right_now.jpg')
						time.sleep(0.5)
						self.foundThenClick('lottery_finished.jpg')
					# finish viewing
					if self.findPolymorphicImage('boborock_get_beans.jpg'): break
					# view 10 seconds again
					time.sleep(10)
			# exit live room
			if self.foundThenClick('boborock_get_beans.jpg'): time.sleep(0.5)
			else: self.panel.clickBackBtn()
			# collect beans
			for count in range(0,2):
				if self.foundThenClick('boborock_collect_beans.jpg'):
					logging.info('The beans in boborock have been successfully obtained!')
				time.sleep(0.5)
				self.foundThenClick('boborock_reward_ok.jpg')
				time.sleep(0.5)

	def overturnCard(self):
		# wait for cards displayed
		self.hoverCenter()
		for count in range(0,6):
			if self.findPolymorphicImage('card_overturned'): return True
			if self.findPolymorphicImage('overturn_and_attention'): break
			sikuli2.wheelDown(5)
			time.sleep(0.5)
		# overtur and go back
		cards = self.findAllPolymorphicImage('card_back.jpg')
		if len(cards) == 0:
			target = self.findPolymorphicImage('mysterious_card.jpg')
		else:
			target = cards[0]
			for card in cards:
				if target.getTopLeft().getX() > card.getTopLeft().getX():
					target = card
		if target is None: return False
		if not sikuli2.clickArea(target): return False
		#self.foundThenClick('bean_after_overturn', App.BELOW, 270)
		return True
	
class JDOpen(Task):
	def execute(self):
		self.app.open()

class JDClose(Task):
	def execute(self):
		self.app.close()

class JDBoBoRock(Task):
	def execute(self):
		if not self.app.enterBoBoRock(): return
		self.app.signInBoBoRock()
		self.app.shareAndViewBroadcast()
		self.app.panel.clickBackBtn()

class JDSignInSuperMarket(Task):
	def execute(self):
		if self.app.enterSuperMarket():
			if self.app.foundThenClick('sign_in_supermarket.jpg'):
				time.sleep(2) # wait for progress
				#self.app.foundThenClick('build_shelves')
				if self.app.foundThenClick('supermarket_reward.jpg'):
					logging.info('The beans in supermarket have been successfully obtained!')
					self.app.foundThenClick('supermarket_reward_ok')
				self.app.panel.clickBackBtn()
				self.app.panel.clickBackBtn()
			self.app.panel.clickBackBtn()

class JDFlopInMakeupShop(Task):
	def execute(self):
		if not self.app.enterChannel('makeup_shop.jpg'): return
		if not self.app.foundThenClick('sign_in_shop_makeup.jpg'): return
		if self.app.overturnCard():
			logging.info('The beans in makeup shop have been successfully obtained!')
		self.app.panel.clickBackBtn()
		self.app.panel.clickBackBtn()

class JDFlopInMotherAndBabyShop(Task):
	def execute(self):
		if not self.app.enterChannel('mother_and_baby_shop.jpg'): return
		if self.app.overturnCard():
			logging.info('The beans in mothre and baby shop have been successfully obtained!')
		self.app.panel.clickBackBtn()

class JDFlopInChildrenClothingShop(Task):
	def execute(self):
		if not self.app.enterChannel('children_clothing_shop.jpg'): return
		if self.app.overturnCard():
			logging.info('The beans in children clothing shop have been successfully obtained!')
		self.app.panel.clickBackBtn()

class JDFlopInUnderWearShop(Task):
	def execute(self):
		if not self.app.enterChannel('under_wear_shop.jpg'): return
		if self.app.overturnCard():
			logging.info('The beans in under wear shop have been successfully obtained!')
		self.app.panel.clickBackBtn()

class JDFlopInDrinkingShop(Task):
	def execute(self):
		if not self.app.enterChannel('drinking_shop.jpg'): return
		if self.app.overturnCard():
			logging.info('The beans in drinking shop have been successfully obtained!')
		self.app.panel.clickBackBtn()

class JDFlopInDigitalDeviceShop(Task):
	def execute(self):
		if not self.app.enterChannel('cool_play_shop.jpg'): return
		if self.app.foundThenClick('digital_device_shop'):
			if self.app.foundThenClick('sign_in_digital_device'):
				time.sleep(2)
				if self.app.overturnCard():
					logging.info('The beans in digital device shop have been successfully obtained!')
				self.app.panel.clickBackBtn()
			self.app.panel.clickBackBtn()
		self.app.panel.clickBackBtn()

class JDFlopInSkinCareShop(Task):
	def execute(self):
		if not self.app.enterChannel('skin_care_shop.jpg'): return
		if self.app.overturnCard():
			logging.info('The beans in skin care shop have been successfully obtained!')
		self.app.panel.clickBackBtn()

if __name__ == '__main__':
	import remote
	#pdb.set_trace()
	#os._exit(0)
	logging.basicConfig(level = logging.INFO)
	#sikuli2.disableInfoLog()
	#sikuli2.disableActionLog()
	ctrl = remote.Scrcpy()
	ctrl.connect()
	app = JingDong(android.Android('redmik20pro_miui11'))
	#app.clickLiveRoomShare()
	#os._exit(0)
	tasks = TaskSet()
	tasks.register(JDClose(app))
	tasks.register(JDOpen(app))
	tasks.register(JDBoBoRock(app))
	'''
	tasks.register(JDSignInSuperMarket(app))
	tasks.register(JDFlopInMakeupShop(app))
	tasks.register(JDFlopInMotherAndBabyShop(app))
	tasks.register(JDFlopInChildrenClothingShop(app))
	tasks.register(JDFlopInUnderWearShop(app))
	tasks.register(JDFlopInDrinkingShop(app))
	tasks.register(JDFlopInDigitalDeviceShop(app))
	tasks.register(JDFlopInSkinCareShop(app))
	'''
	tasks.execute()
