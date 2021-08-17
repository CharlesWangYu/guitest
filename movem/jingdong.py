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

from app import *

BRAND_LIST = ['芝华仕','老板','方太','海尔','长虹','TCL','康佳','创维','酷开','海信','万家乐','小天鹅','火星人','美的','格力','苏泊尔','格兰仕','小米']

FOOTER_BTN_HOME_X_OFFSET	= 55	# form left of screen
FOOTER_BTN_SORT_X_OFFSET	= 135	# form left of screen
FOOTER_BTN_FIND_X_OFFSET	= 220	# form left of screen
FOOTER_BTN_CART_X_OFFSET	= 300	# form left of screen
FOOTER_BTN_MINE_X_OFFSET	= 385	# form left of screen
FOOTER_BTN_Y_OFFSET			= 70	# form bottom of screen
STUDIO_SEARCH_BAR_X_OFFSET	= 100	# form left of screen
STUDIO_SEARCH_BAR_Y_OFFSET	= 130	# form top of screen
STUDIO_TO_ATTENTION			= 200


def getAttentionImgYCoordinate(region):
	assert isinstance(region, lackey.Region)
	return getY(getCenter(region))
	
class JingDong(App):
	def __init__(self, platform):
		super(JingDong, self).__init__(platform)
		self.imgPath = os.path.abspath('.') + '\\res\\app\\jingdong\\'
	
	def initEntry(self):
		time.sleep(3)

	def clickHome(self):
		pos = shiftPos(getBottomLeft(), SHIFT_UP, FOOTER_BTN_Y_OFFSET)
		pos = shiftPos(pos, SHIFT_RIGHT, FOOTER_BTN_HOME_X_OFFSET)
		clickPos(pos)

	def clickSort(self):
		pos = shiftPos(getBottomLeft(), SHIFT_UP, FOOTER_BTN_Y_OFFSET)
		pos = shiftPos(pos, SHIFT_RIGHT, FOOTER_BTN_SORT_X_OFFSET)
		clickPos(pos)

	def clickFind(self):
		pos = shiftPos(getBottomLeft(), SHIFT_UP, FOOTER_BTN_Y_OFFSET)
		pos = shiftPos(pos, SHIFT_RIGHT, FOOTER_BTN_FIND_X_OFFSET)
		clickPos(pos)

	def clickCart(self):
		pos = shiftPos(getBottomLeft(), SHIFT_UP, FOOTER_BTN_Y_OFFSET)
		pos = shiftPos(pos, SHIFT_RIGHT, FOOTER_BTN_CART_X_OFFSET)
		clickPos(pos)

	def clickMine(self):
		pos = shiftPos(getBottomLeft(), SHIFT_UP, FOOTER_BTN_Y_OFFSET)
		pos = shiftPos(pos, SHIFT_RIGHT, FOOTER_BTN_MINE_X_OFFSET)
		clickPos(pos)
	
	def enterLiveBroadcastChannel(self):
		self.clickHome()
		time.sleep(0.3)
		return self.foundThenClick('live_broadcast_channel')
	
	def listLiveRooms(self, brand):
		pos = shiftPos(getTopLeft(), SHIFT_RIGHT, STUDIO_SEARCH_BAR_X_OFFSET)
		pos = shiftPos(pos, SHIFT_DOWN, STUDIO_SEARCH_BAR_Y_OFFSET)
		clickPos(pos) # click search bar in live room
		time.sleep(1)
		pasteChar(brand)
		time.sleep(1)
		self.foundThenClick('search_button_in_keyboard')
		time.sleep(0.5)
		self.foundThenClick('search_more_live_room')
		time.sleep(0.2)
		attentionList = findImages(self.img('studio_with_attention.jpg'))
		attentionList.extend(findImages(self.img('studio_without_attention.jpg')))
		attentionList.sort(key=getAttentionImgYCoordinate)
		#logging.info('There are %d live rooms with %s brand have been found.' % (len(attentionList), brand))
		studioList = []
		for img in attentionList:
			x = getX(getCenter(img)) - scaleLength(STUDIO_TO_ATTENTION)
			y = getY(getCenter(img))
			studioList.append(scalePos(x, y))
		return studioList # return a studios' position list
	
	def isLiveRoom(self):
		if self.findFirstImage('flag_live_room') is None: return False
		else: return True
		
	def collectBeansFromLiveRoom(self, brand):
		time.sleep(1)
		liveRooms = self.listLiveRooms(brand)
		for room in liveRooms:
			clickPos(room)
			time.sleep(2)
			if not self.isLiveRoom(): # is not active live room
				time.sleep(0.8)
				self.clickAndroidBackBtn() # return from inactive live room
				time.sleep(0.8)
				continue
			if self.foundThenClick('interactive_lottery'): # has lottery card
				time.sleep(0.8)
				self.foundThenClick('lottery_right_now')
				time.sleep(0.8)
				self.clickAndroidBackBtn() # return form lottery message
				time.sleep(0.8)
			self.clickAndroidBackBtn() # return from live room
			time.sleep(0.5)
		self.clickAndroidBackBtn() # return from live room list to live broadcast channel
		time.sleep(0.5)
		
	'''
	def clickLiveRoomBack(self):
		pos = sikuli2.getTopRight().left(30).below(70)
		sikuli2.clickPos(pos)

	def clickLiveRoomShare(self):
		pos = sikuli2.getTopRight().left(73).below(70)
		sikuli2.clickPos(pos)

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
			else: self.clickAndroidBackBtn()
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
	'''
	
class JDOpen(Task):
	def execute(self):
		self.app.start()

class JDClose(Task):
	def execute(self):
		self.app.stop()
	
class JDCollectFromLiveRoom(Task):
	def execute(self):
		self.app.enterLiveBroadcastChannel()
		for brand in BRAND_LIST:
			self.app.collectBeansFromLiveRoom(brand)
	
'''
class JDBoBoRock(Task):
	def execute(self):
		if not self.app.enterBoBoRock(): return
		self.app.signInBoBoRock()
		self.app.shareAndViewBroadcast()
		self.app.clickAndroidBackBtn()

class JDSignInSuperMarket(Task):
	def execute(self):
		if self.app.enterSuperMarket():
			if self.app.foundThenClick('sign_in_supermarket.jpg'):
				time.sleep(2) # wait for progress
				#self.app.foundThenClick('build_shelves')
				if self.app.foundThenClick('supermarket_reward.jpg'):
					logging.info('The beans in supermarket have been successfully obtained!')
					self.app.foundThenClick('supermarket_reward_ok')
				self.app.clickAndroidBackBtn()
				self.app.clickAndroidBackBtn()
			self.app.clickAndroidBackBtn()

class JDFlopInMakeupShop(Task):
	def execute(self):
		if not self.app.enterChannel('makeup_shop.jpg'): return
		if not self.app.foundThenClick('sign_in_shop_makeup.jpg'): return
		if self.app.overturnCard():
			logging.info('The beans in makeup shop have been successfully obtained!')
		self.app.clickAndroidBackBtn()
		self.app.clickAndroidBackBtn()

class JDFlopInMotherAndBabyShop(Task):
	def execute(self):
		if not self.app.enterChannel('mother_and_baby_shop.jpg'): return
		if self.app.overturnCard():
			logging.info('The beans in mothre and baby shop have been successfully obtained!')
		self.app.clickAndroidBackBtn()

class JDFlopInChildrenClothingShop(Task):
	def execute(self):
		if not self.app.enterChannel('children_clothing_shop.jpg'): return
		if self.app.overturnCard():
			logging.info('The beans in children clothing shop have been successfully obtained!')
		self.app.clickAndroidBackBtn()

class JDFlopInUnderWearShop(Task):
	def execute(self):
		if not self.app.enterChannel('under_wear_shop.jpg'): return
		if self.app.overturnCard():
			logging.info('The beans in under wear shop have been successfully obtained!')
		self.app.clickAndroidBackBtn()

class JDFlopInDrinkingShop(Task):
	def execute(self):
		if not self.app.enterChannel('drinking_shop.jpg'): return
		if self.app.overturnCard():
			logging.info('The beans in drinking shop have been successfully obtained!')
		self.app.clickAndroidBackBtn()

class JDFlopInDigitalDeviceShop(Task):
	def execute(self):
		if not self.app.enterChannel('cool_play_shop.jpg'): return
		if self.app.foundThenClick('digital_device_shop'):
			if self.app.foundThenClick('sign_in_digital_device'):
				time.sleep(2)
				if self.app.overturnCard():
					logging.info('The beans in digital device shop have been successfully obtained!')
				self.app.clickAndroidBackBtn()
			self.app.clickAndroidBackBtn()
		self.app.clickAndroidBackBtn()

class JDFlopInSkinCareShop(Task):
	def execute(self):
		if not self.app.enterChannel('skin_care_shop.jpg'): return
		if self.app.overturnCard():
			logging.info('The beans in skin care shop have been successfully obtained!')
		self.app.clickAndroidBackBtn()
'''

if __name__ == '__main__':
	import remote
	#pdb.set_trace()
	logging.basicConfig(level = logging.INFO)
	ctrl = remote.Scrcpy()
	ctrl.connect()
	app = JingDong(ctrl.platform())
	tasks = []
	#tasks.append(UnlockSmartPhone(app))
	tasks.append(ClearActiveApp(app))
	tasks.append(JDOpen(app))
	tasks.append(JDCollectFromLiveRoom(app))
	tasks.append(JDClose(app))
	for task in tasks:
		task.execute()
	ctrl.disconnect()
