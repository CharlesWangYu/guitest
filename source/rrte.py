'''
@File		: rrte.py
@Date		: 2020/08/30
@Author		: Wang.Yu
@Version	: 1.0
@Contact	: yu.wang@cn.yokogawa.com
@License	: (C)Copyright 2020 Yokogawa China Co., Ltd.
'''
import pdb
import logging
import sys
import time
import subprocess
from host import *
from uia2 import *
from uiaRRTE import *
from configparser import ConfigParser
from comtypes.client import *
from ctypes import *

class RRTE(Host):
	def startUp(self, cmd):
		subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, close_fds=True)
		logging.info('[Command is executed. Command = %s]' % cmd)
		internal = findFirstElemByAutomationId(DesktopRoot, 'DD_ExplorerView')
		while not isUIAElem(internal):
			time.sleep(1)
			internal = findFirstElemByAutomationId(DesktopRoot, 'DD_ExplorerView')
		self.host = findFirstElemByName(DesktopRoot, 'Reference Run-time Environment', SCOPE_CHILDREN)
		assert isUIAElem(self.host)
	
	def exit(self):
		mainMenuView = findFirstElemByAutomationId(self.host, 'mainMenuView')
		assert isUIAElem(mainMenuView)
		ribbonTAB = findFirstChildElem(mainMenuView)
		assert isUIAElem(ribbonTAB)
		ribbonMenu = findFirstElemByControlType(ribbonTAB,UIAClient.UIA_MenuControlTypeId)
		assert isUIAElem(ribbonMenu)
		expandCombo(ribbonMenu)
		exitButton = findFirstElemByName(ribbonMenu, 'Exit', SCOPE_CHILDREN)
		assert isUIAElem(exitButton)
		pushButton(exitButton)
		time.sleep(30) # Do not shorten the delay. It will cause failure to restart RRTE.

	def pushBtnApply(self):
		time.sleep(0.1)	# Do not move this line. It will cause failure that the apply button can not be pushed.
		topTAB = findFirstElemByName(self.host, 'Fdi.Client.DeviceUi.ViewModel.DeviceUiHostContainerItemViewModel')
		assert isUIAElem(topTAB)
		custom = findFirstElemByControlType(topTAB, UIAClient.UIA_CustomControlTypeId,SCOPE_CHILDREN)
		assert isUIAElem(custom)
		applyBtn = findFirstElemByName(custom,'Apply',SCOPE_CHILDREN)
		assert isUIAElem(applyBtn)
		revertBut = findPreviousSiblingElem(applyBtn)
		assert isUIAElem(revertBut)
		focusItem = findPreviousSiblingElem(revertBut)
		assert isUIAElem(focusItem)
		try:
			focusItem.SetFocus()
			time.sleep(0.1)	# Do not move this line. It will cause failure that the apply button can not be pushed.
			pushButton(applyBtn)
		except Exception as e:
			logging.info('[Error] : Button "Apply" can not be pushed!')
		waitProgressBarClose()

	def setTraceLevel(self, logLevel):
		groupTraceLevel = findFirstElemByName(self.host, 'Trace Level')
		assert isUIAElem(groupTraceLevel)
		listTraceLevel = findFirstChildElem(groupTraceLevel)
		assert isUIAElem(listTraceLevel)
		menuTraceLevel = findFirstChildElem(listTraceLevel)
		assert isUIAElem(menuTraceLevel)
		expandCombo(menuTraceLevel)
		setEditbox(menuTraceLevel, logLevel)
	
	@staticmethod
	def isNeedToGetLog(node):
		n = node.left
		while n != None and n.elem != None:
			if isinstance(n.elem, RVariable):
				return True
			elif isinstance(n.elem, RGroup):
				return RRTE.isNeedToGetLog(n)
			n = n.right
		return False
	
class RElement(Element):
	@staticmethod
	def createParam(uiaElem):
		assert isCustom(uiaElem)
		if isContentNameEnum(uiaElem):
			param = REnum(uiaElem)
			param.getOption(uiaElem)
		elif isContentNameString(uiaElem):
			param = RString(uiaElem)
		elif isContentNameNumeric(uiaElem):
			param = RNumeric(uiaElem)
		elif isContentNameBitEnum(uiaElem):
			param = RBitEnum(uiaElem)
			param.getOption(uiaElem)
		elif isContentNameDate(uiaElem):
			param = RDate(uiaElem)
		elif isContentNameTime(uiaElem):
			param = RTime(uiaElem)
		return param
	
	@staticmethod
	def getChildrenFormContent(scope):
		#all = findAllElem(scope, True, UIAClient.UIA_IsEnabledPropertyId, SCOPE_CHILDREN)
		all = findAllChildren(scope)
		set = []
		for x in range(0, all.Length):
			item = all.GetElement(x)
			if isCustom(item): # variable(others, Enum, BitEnum
				elem = RElement.createParam(item)
				elem.ctrlType = 'Custom'
				elem.rectangle = item.CurrentBoundingRectangle
				set.append(elem)
			elif isButton(item): # method
				label = getElemSubName(item)
				elem = RMethod(label)
				elem.ctrlType = 'Button'
				elem.rectangle = item.CurrentBoundingRectangle
				set.append(elem)
			elif isGroup(item): # group
				elem = RGroup(item.CurrentName)
				elem.ctrlType = 'Group'
				elem.rectangle = item.CurrentBoundingRectangle
				set.append(elem)
			elif isTab(item): # page
				uias = findAllElemByControlType(item, UIAClient.UIA_TabItemControlTypeId, SCOPE_CHILDREN)
				pages = []
				for x in range(0, uias.Length):
					elem = uias.GetElement(x)
					page = RPage(elem.CurrentName)
					page.ctrlType = 'TabItem'
					page.rectangle = elem.CurrentBoundingRectangle
					pages.append(page)
				set.extend(pages)
			else:
				pass
		return set
	
	@staticmethod
	def getChildrenFormLayout(scope):
		all = findAllElemByControlType(scope, UIAClient.UIA_TreeItemControlTypeId, SCOPE_CHILDREN)
		set = []
		for x in range(0, all.Length):
			item = all.GetElement(x)
			if isLayoutNameMethod(item):
				label = getMenuMethodName(item)
				elem = RMethod(label)
				elem.ctrlType = 'Button'
				elem.rectangle = item.CurrentBoundingRectangle
				set.append(elem)
			elif isLayoutNameMenu(item):
				label = getElemSubName(item)
				if isTreeLeaf(item):
					elem = RWindow(label)
				else:
					elem = RMenu(label)
				elem.ctrlType = 'TreeItem'
				elem.rectangle = item.CurrentBoundingRectangle
				set.append(elem)
		return set
	
	def getChildren(self):
		scope = self.getAnchorAfterSelect()
		if isPane(scope) or isTabItem(scope) or isGroup(scope):
			return RElement.getChildrenFormContent(scope)
		else:
			return RElement.getChildrenFormLayout(scope)

	def getROAttrStr(self):
		return 'N/A'
	
	def getCurrValStr(self):
		return 'N/A'

class RRoot(RElement):
	def __init__(self, label):
		super(RRoot, self).__init__(label)
		self.style = 'ROOT'
	
	def getSelfAnchor(self, anchor):
		rrte = findFirstElemByName(anchor, 'Reference Run-time Environment', SCOPE_CHILDREN)
		all = findAllElemByControlType(rrte, UIAClient.UIA_CustomControlTypeId, SCOPE_CHILDREN)
		workRoot = all.GetElement(all.Length-1)
		assert isUIAElem(workRoot)
		topTAB = findFirstElemByName(workRoot, 'Fdi.Client.DeviceUi.ViewModel.DeviceUiHostContainerItemViewModel')
		assert isUIAElem(topTAB)
		topTABX = findFirstElemByName(topTAB, 'X')
		assert isUIAElem(topTABX)
		topRoot = findNextSiblingElem(topTABX)
		assert isUIAElem(topRoot)
		return topRoot
	
	def select(self):
		pass
	
	def getChildren(self):
		set = []
		anchor = self.getAnchorAfterSelect()
		# get offline root menu item
		offline = findFirstElemBySubText(anchor, 'Offline')
		if not isUIAElem(offline):
			offline = findFirstElemBySubText(anchor, 'Offline root menu')
			assert isUIAElem(offline)
			menu = RRootMenu('Offline root menu')
		else:
			menu = RRootMenu('Offline')
		menu.ctrlType = 'Button'
		menu.rectangle = offline.CurrentBoundingRectangle
		set.append(menu)
		# get online root menu items
		onlineRoot = findFirstElemByAutomationId(anchor, 'OnlineParameters')
		assert isUIAElem(onlineRoot)
		pane = findFirstElemByControlType(onlineRoot, UIAClient.UIA_PaneControlTypeId)
		assert isUIAElem(pane)
		all = findAllElemByControlType(pane, UIAClient.UIA_ButtonControlTypeId, SCOPE_CHILDREN)
		for x in range(0, all.Length):
			item = all.GetElement(x)
			label = getElemSubName(item)
			#if label == 'Online': continue # TODO
			#if label == 'Device root menu': continue # TODO
			#if label == 'Diagnostic root menu': continue # TODO
			#if label == 'Maintenance root menu': continue # TODO
			#if label == 'Process variables root menu': continue # TODO
			elem = RRootMenu(label)
			elem.ctrlType = 'Button'
			elem.rectangle = item.CurrentBoundingRectangle
			set.append(elem)
		return set

class RRootMenu(RElement):
	def __init__(self, label):
		super(RRootMenu, self).__init__(label)
		self.style = 'MENU'
	
	def getSelfAnchor(self, anchor):
		explorer = findFirstElemByAutomationId(anchor, 'DD_ExplorerView')
		assert isUIAElem(explorer)
		elem = findNextSiblingElem(explorer) # maybe pane or tree
		assert isUIAElem(elem)
		return elem
	
	def select(self):
		anchor = self.path[-2].getAnchorAfterSelect()
		# search root menu button
		if not (self.label == 'Offline' or self.label == 'Offline root menu'):
			onlineRoot = findFirstElemByAutomationId(anchor, 'OnlineParameters')
			assert isUIAElem(onlineRoot)
			pane = findFirstElemByControlType(onlineRoot, UIAClient.UIA_PaneControlTypeId)
			assert isUIAElem(pane)
			btn = findFirstElemBySubText(pane, self.label)
		else:
			btn = findFirstElemBySubText(anchor, self.label)
		# push root menu button
		assert isUIAElem(btn)
		if not isRootMenuPushed(btn):
			pushButton(btn)
			while not isRootMenuPushed(btn):
				time.sleep(0.1)
	
class RMenu(RElement):
	def __init__(self, label):
		super(RMenu, self).__init__(label)
		self.style = 'MENU'
	
	def getSelfAnchor(self, anchor):
		tree = findFirstElemBySubText(anchor, self.label)
		assert isUIAElem(tree)
		return tree
		
	def select(self):
		anchor = self.path[-2].getAnchorAfterSelect()
		tree = findFirstElemBySubText(anchor, self.label)
		assert isUIAElem(tree)
		expandTree(tree)
		while not isTreeItemExpand(tree):
			time.sleep(0.1)

class RWindow(RElement):
	def __init__(self, label):
		super(RWindow, self).__init__(label)
		self.style = 'WINDOW'
	
	def getSelfAnchor(self, anchor):
		leaf = findFirstElemBySubText(anchor, self.label)
		assert isUIAElem(leaf)
		curr = leaf
		while not isTree(curr):
			curr = findParentElem(curr)
			assert isUIAElem(curr)
		pane = findNextSiblingElem(curr)
		assert isUIAElem(pane)
		return pane
	
	def select(self):
		anchor = self.path[-2].getAnchorAfterSelect()
		leaf = findFirstElemBySubText(anchor, self.label)
		assert isUIAElem(leaf)
		pushLeaf(leaf)
		while not isTreeLeafSelected(leaf):
			time.sleep(0.1)

class RPage(RElement):
	def __init__(self, label):
		super(RPage, self).__init__(label)
		self.style = 'PAGE'
	
	def getSelfAnchor(self, anchor):
		tabs = findFirstElemByControlType(anchor, UIAClient.UIA_TabControlTypeId, SCOPE_CHILDREN)
		assert isUIAElem(tabs)
		tab = findFirstElemByName(tabs, self.label)
		assert isUIAElem(tab)
		return tab
	
	def select(self):
		anchor = self.path[-2].getAnchorAfterSelect()
		tabs = findFirstElemByControlType(anchor, UIAClient.UIA_TabControlTypeId, SCOPE_CHILDREN)
		tab = findFirstElemByName(tabs, self.label)
		assert isUIAElem(tab)
		selectTab(tab)
		while not isTabSelected(tab):
			time.sleep(0.1)

class RGroup(RElement):
	def __init__(self, label):
		super(RGroup, self).__init__(label)
		self.style = 'GROUP'
	
	def getSelfAnchor(self, anchor):
		group = findFirstElemByName(anchor, self.label, SCOPE_CHILDREN)
		assert isUIAElem(group)
		return group
	
	def select(self):
		pass

class RVariable(RElement):
	def __init__(self, uiaElem):
		label = getElemSubName(uiaElem)
		super(RVariable, self).__init__(label)
		self.readonly = isEditboxEnabled(uiaElem)
		self.style = 'VARIABLE'
		self.currentVal = getCurrentValString(uiaElem)
	
	def isLeaf(self):
		return True

	def getROAttrStr(self):
		if self.readonly:
			return 'TRUE'
		else:
			return 'FALSE'
	
	def getCurrValStr(self):
		return self.currentVal

class RMethod(RElement):
	def __init__(self, label):
		self.path		= None # parent node path
		self.label		= label
		self.ctrlType	= ''
		self.rectangle	= None
		self.readonly	= True
		self.style		= 'METHOD'

	def isLeaf(self):
		return True
	
class RString(RVariable):
	pass

class RDate(RVariable):
	pass

class RTime(RVariable):
	pass

class RNumeric(RVariable):
	pass

class REnum(RVariable):
	def __init__(self, uiaElem):
		assert isContentNameEnum(uiaElem)
		self.path		= None # parent node path
		self.label		= getElemSubName(uiaElem)
		self.ctrlType	= ''
		self.rectangle	= None
		self.readonly	= not isComboboxEnabled(uiaElem)
		self.style		= 'VARIABLE'
		self.__ne107 	= ['No Effect', 'Maintenance Required', 'Failure', 'Out of Specification', 'Function Check']
		self.options 	= []
		self.currentVal = ''
	
	def __isNE107Label(self):
		for item in self.__ne107:
			if self.label == item:
				return True
		return False
	
	def __tryLabelGetting(self, uiaElem):
		variableLabel = self.label
		parent = findParentElem(uiaElem) # pane, page, group
		variable = findFirstElemBySubText(parent, variableLabel)
		newCombo = findFirstElemByControlType(variable, UIAClient.UIA_ComboBoxControlTypeId)
		while not isUIAElem(newCombo):
			time.sleep(0.1)
			parent = findParentElem(uiaElem) # pane, page, group
			variable = findFirstElemBySubText(parent, variableLabel)
			newCombo = findFirstElemByControlType(variable, UIAClient.UIA_ComboBoxControlTypeId)
		return newCombo
	
	def isEnum(self):
		return True
	
	def getOption(self, uiaElem):
		assert isUIAElem(uiaElem)
		if self.readonly: return
		if not self.__isNE107Label():
			parent = findParentElem(uiaElem) # pane, page, group
			combo = findFirstElemByControlType(uiaElem, UIAClient.UIA_ComboBoxControlTypeId)
			assert isUIAElem(combo)
			expandCombo(combo)
			#collapseCombo(combo) # variable refreshed after
			newCombo = self.__tryLabelGetting(uiaElem)
			assert isUIAElem(newCombo)
			all = findAllElemByControlType(newCombo, UIAClient.UIA_ListItemControlTypeId)
			set = []
			for x in range(0, all.Length):
				item = all.GetElement(x)
				enum = findFirstElemByControlType(item, UIAClient.UIA_TextControlTypeId)
				set.append(enum.CurrentName)
				pattern = item.GetCurrentPattern(UIAClient.UIA_SelectionItemPatternId)
				selection = cast(pattern, POINTER(UIAClient.IUIAutomationSelectionItemPattern))
				if selection.CurrentIsSelected:
					self.currentVal = enum.CurrentName
			self.options.extend(set)
		else:
			self.options.extend(self.__ne107)

class RBitEnum(RVariable):
	def __init__(self, uiaElem):
		assert isContentNameBitEnum(uiaElem)
		group = findFirstElemByControlType(uiaElem, UIAClient.UIA_GroupControlTypeId)
		if isUIAElem(group):
			self.label = getElemSubName(group)
		else: # FF & ProfiNet FDI package
			self.label = getElemSubName(uiaElem)
		self.path		= None # parent node path
		self.ctrlType	= ''
		self.rectangle	= None
		self.readonly 	= not isBitEnumGroupEnabled(uiaElem)
		self.style		= 'VARIABLE'
		self.options 	= []
		self.currentVal = []
	
	def isBitEnum(self):
		return True
	
	def getOption(self, uiaElem):
		assert isUIAElem(uiaElem)
		parent = uiaElem # FF & ProfiNet FDI package
		group = findFirstElemByControlType(uiaElem, UIAClient.UIA_GroupControlTypeId)
		if isUIAElem(group):
			parent = group
		custom = findFirstElemByControlType(parent, UIAClient.UIA_CustomControlTypeId)
		assert isUIAElem(custom)
		all = findAllElemByControlType(custom, UIAClient.UIA_CheckBoxControlTypeId)
		set = []
		for x in range(0, all.Length):
			item = all.GetElement(x)
			set.append(item.CurrentName)
			pattern = item.GetCurrentPattern(UIAClient.UIA_TogglePatternId)
			selection = cast(pattern, POINTER(UIAClient.IUIAutomationTogglePattern))
			if selection.CurrentToggleState:
				self.currentVal.append(item.CurrentName)
		self.options.extend(set)
