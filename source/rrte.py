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
import shutil
import subprocess
from host import *
from uia2 import *
from uiaRRTE import *
from configparser import ConfigParser
from comtypes.client import *
from ctypes import *

class RRTE(Host):
	def __init__(self, root):
		super(RRTE, self).__init__(root)
		self.config = ConfigParser()
		self.config.read('test.conf', encoding='UTF-8')
	
	def startUp(self):
		inputMode = self.config['COMM']['FCG_FILE_TYPE'].strip("'")
		hostApp	= self.config['COMM']['HOST_APP_PATH'].strip("'") + '\Reference Run-time Environment\Fdi.Reference.Client.exe'
		testFile = self.config['COMM']['FCG_FILE'].strip("'")
		outPath = self.config['COMM']['OUTPUT_FILE_PATH'].strip("'")
		logPath = self.config['LOG']['RRTE_LOG_PATH'].strip("'")
		execCmd = '\"' + hostApp + '\" -l \"' + testFile + '\"'
		subprocess.Popen(execCmd, shell=True, stdout=subprocess.PIPE, close_fds=True)
		logging.info('execCmd = %s' % execCmd)
		internal = findFirstElemByAutomationId(DesktopRoot, 'DD_ExplorerView')
		while not isUIAElem(internal):
			time.sleep(1.5)
			internal = findFirstElemByAutomationId(DesktopRoot, 'DD_ExplorerView')
		time.sleep(5)
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
		time.sleep(20) # Please do not shorten the time, it will cause failure to restart RRTE.

	def copyLogs(self, folderName):
		logPath = self.config['LOG']['RRTE_LOG_PATH'].strip("'")
		outPath = self.config['COMM']['OUTPUT_FILE_PATH'].strip("'")
		outPath = outPath + '\\' + folderName
		if os.path.exists(logPath):
			shutil.copytree(logPath, outPath)

	def clearLogs(self):
		#logging.info('>>>>>> Clearing the log files...')
		logPath = self.config['LOG']['RRTE_LOG_PATH'].strip("'")
		if os.path.exists(logPath):
			shutil.rmtree(logPath)

	def clearOutput(self):
		#logging.info('>>>>>> Clearing the out files...')
		outPath = self.config['COMM']['OUTPUT_FILE_PATH'].strip("'")
		if os.path.exists(outPath):
			shutil.rmtree(outPath)

	def pushBtnApply(self):
		try:
			topTAB   = findFirstElemByName(self.host, 'Fdi.Client.DeviceUi.ViewModel.DeviceUiHostContainerItemViewModel')
			assert isUIAElem(topTAB)
			explorer = findFirstElem(topTAB, 'DD_ExplorerView', UIAClient.UIA_AutomationIdPropertyId)
			assert isUIAElem(explorer)
			treeRoot = findNextSiblingElem(explorer)
			assert isUIAElem(treeRoot)
			paneRoot = findNextSiblingElem(treeRoot)
			assert isUIAElem(paneRoot)
			paneRoot.SetFocus()
			RevertRoot = findNextSiblingElem(paneRoot)
			assert isUIAElem(RevertRoot)
			ApplyRoot  = findNextSiblingElem(RevertRoot)
			assert isUIAElem(ApplyRoot)
			pushButton(ApplyRoot)
			#logging.info('Information: Push the button of <Apply> success')
		except Exception as e:
			print('[Error] : Button "Apply" can not be pushed!')

	def setTraceLevel(self, logLevel):
		groupTraceLevel = findFirstElemByName(self.host, 'Trace Level')
		assert isUIAElem(groupTraceLevel)
		listTraceLevel = findFirstChildElem(groupTraceLevel)
		assert isUIAElem(listTraceLevel)
		menuTraceLevel = findFirstChildElem(listTraceLevel)
		assert isUIAElem(menuTraceLevel)
		expandCombo(menuTraceLevel)
		setEditbox(menuTraceLevel, logLevel)
		#logging.info('Information: TraceLevel = %s' % logLevel)

	def getLogByScreen(self, node):
		loadingDelay = int(self.config['LOG']['LOG_LOADING_TIME'].strip("'"))
		if node == None or node.elem == None:
			return
		if isinstance(node.elem, RWindow) or isinstance(node.elem, RPage):
			logging.info('----------------------------------------------------------')
			self.startUp()
			#self.setTraceLevel('Verbose')
			logging.info('Loging Node\t: %s (%s)' % (node.elem.label, node.elem.ctrlType))
			logFolder = ''
			path = node.getPath()
			for item in path:
				logFolder = logFolder + '\\' + item.elem.label
				item.select()
			logging.info('Node Path\t: %s (%s)' % (logFolder, node.elem.ctrlType))
			time.sleep(loadingDelay)
			self.autoSetParameter(node.left)
			self.pushBtnApply()
			time.sleep(4)
			self.exit()
			logging.info('Loging Copy\t: %s' %(logFolder))
			self.copyLogs(logFolder)
			self.clearLogs()
			logging.info('Loging Finished\t: %s (%s)' % (node.elem.label, node.elem.ctrlType))
		elif node.elem.ctrlType == 'TreeItem':
			pass
		self.getLogByScreen(node.left)
		self.getLogByScreen(node.right)

	def getLogByRootMenu(self, node):
		node = node.left
		while node != None and node.elem != None:
			logging.info('----------------------------------------------------------')
			self.startUp()
			# self.setTraceLevel('Verbose')
			logging.info('Loging Node\t: %s (%s)' % (node.elem.label, node.elem.ctrlType))
			logFolder = ''
			path = node.getPath()
			for item in path:
				logFolder = logFolder + '\\' + item.elem.label
				item.select(self)
			logging.info('Node Path\t: %s (%s)' % (logFolder, node.elem.ctrlType))
			self.getLogsOfRootMenu(node.left)
			self.exitRRTE()
			logging.info('Loging Copy\t: %s' %(logFolder))
			self.copyLogFiles(logFolder)
			self.clearLogPath()
			logging.info('Loging Finished\t: %s (%s)' % (node.elem.label, node.elem.ctrlType))
			node = node.right

	def getLogsOfRootMenu(self, node):

		loadingDelay = int(self.config['MISC']['LOG_LOADING_TIME'].strip("'"))

		if node == None or node.elem == None:
			return
		if node.isWindowNode() or node.isPageNode():
			logging.info('>>>>>>Node Name\t: %s (%s)' % (node.elem.label, node.elem.ctrlType))
			path = node.getPath()
			for item in path:
				item.select(self)
			time.sleep(loadingDelay)
			self.autoSetParameter(node.left)
			self.pushButtonApply()
			time.sleep(4)
		elif node.elem.ctrlType == 'TreeItem':
			pass

		self.getLogsOfRootMenu(node.left)
		self.getLogsOfRootMenu(node.right)

	def autoSetParameter(self, node):
		if node == None or node.elem == None:
			return
		NodeRW  = 'N/A'
		NodeVal = 'N/A'
		if isinstance(node.elem, RVariable):
			if isinstance(node.elem, RMethod):
				pass
			elif isinstance(node.elem, REnum): # TODO
				NodeVal = node.elem.currentVal
				if node.elem.readonly:
					NodeRW = 'Readonly'
				else:
					NodeRW = 'Writable'
					#uiaElem = self.getCurrUiaElem()
					anchor = node.elem.path[-2].getAnchorAfterSelect()
					uiaElem = findFirstElemByName(anchor, node.elem.label)
					uiaElem = findParentElem(uiaElem)
					uiaElem = findFirstElemByControlType(uiaElem, UIAClient.UIA_ComboBoxControlTypeId)
					assert isUIAElem(uiaElem)
					expandCombo(uiaElem)
					time.sleep(1)
					uiaElemArray = findAllElemByControlType(uiaElem, UIAClient.UIA_ListItemControlTypeId)
					for x in range(0, uiaElemArray.Length):
						uiaItem = uiaElemArray.GetElement(x)
						uiaText = findFirstElemByControlType(uiaItem, UIAClient.UIA_TextControlTypeId)
						if uiaText.CurrentName == node.elem.currentVal:
							pass
						else:
							pattern = uiaItem.GetCurrentPattern(UIAClient.UIA_SelectionItemPatternId)
							Selection = cast(pattern, POINTER(UIAClient.IUIAutomationSelectionItemPattern))
							Selection.Select()
							break
					time.sleep(1)
					expandCombo(uiaElem)
					uiaElemArray = findAllElemByControlType(uiaElem, UIAClient.UIA_ListItemControlTypeId)
					for x in range(0, uiaElemArray.Length):
						uiaItem = uiaElemArray.GetElement(x)
						uiaText = findFirstElemByControlType(uiaItem, UIAClient.UIA_TextControlTypeId)
						if uiaText.CurrentName == node.elem.currentVal:
							pattern = uiaItem.GetCurrentPattern(UIAClient.UIA_SelectionItemPatternId)
							Selection = cast(pattern, POINTER(UIAClient.IUIAutomationSelectionItemPattern))
							Selection.Select()
							break
			elif isinstance(node.elem, RBitEnum):
				NodeVal = node.elem.currentVal
				if node.elem.readonly:
					NodeRW = 'Readonly'
				else:
					NodeRW = 'Writable'
					#uiaElem = self.getCurrUiaElem()
					anchor = node.elem.path[-2].getAnchorAfterSelect()
					uiaElem = findFirstElemByName(anchor, node.elem.label)
					uiaElem = findParentElem(uiaElem)
					uiaElem = findFirstElemByControlType(uiaElem, UIAClient.UIA_CustomControlTypeId)
					assert isUIAElem(uiaElem)
					time.sleep(0.4)
					uiaElem = findFirstElemByControlType(uiaElem, UIAClient.UIA_CheckBoxControlTypeId)
					assert isUIAElem(uiaElem)
					pattern = uiaElem.GetCurrentPattern(UIAClient.UIA_TogglePatternId)
					ctrl = cast(pattern, POINTER(UIAClient.IUIAutomationTogglePattern))
					ctrl.Toggle()
					time.sleep(0.4)
					ctrl.Toggle()
					time.sleep(0.4)
			else:
				NodeVal = node.elem.currentVal
				if node.elem.readonly:
					NodeRW = 'Readonly'
				else:
					NodeRW = 'Writable'
					#uiaElem = self.getCurrUiaElem()
					anchor = node.elem.path[-2].getAnchorAfterSelect()
					uiaElem = findFirstElemByName(anchor, node.elem.label)
					uiaElem = findParentElem(uiaElem)
					uiaElem = findFirstElemByControlType(uiaElem, UIAClient.UIA_EditControlTypeId)
					assert isUIAElem(uiaElem)
					setEditbox(uiaElem, '')
					setEditbox(uiaElem, NodeVal)
		logging.info('%s : [Value = %s, RW = %s, Type = %s]' %(node.elem.label, NodeVal, NodeRW, node.elem.ctrlType))
		if isinstance(node.elem, RGroup):
			self.autoSetParameter(node.left)
		self.autoSetParameter(node.right)
	
	@staticmethod
	def waitDialogClose():
		desktop = IUIA.GetRootElement()
		assert isUIAElem(desktop)
		rrte = findFirstElemByName(desktop, 'Reference Run-time Environment', SCOPE_CHILDREN)
		assert isUIAElem(rrte)
		process = findFirstElemByControlType(rrte, UIAClient.UIA_WindowControlTypeId, SCOPE_CHILDREN)
		while isUIAElem(process):
			time.sleep(1.5)
			process = findFirstElemByControlType(rrte, UIAClient.UIA_WindowControlTypeId, SCOPE_CHILDREN)
		time.sleep(1)

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
			if label == 'Online': continue # TODO
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
			#RRTE.waitDialogClose()
			time.sleep(6)
		else:
			time.sleep(0.2)
	
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
		time.sleep(0.5)

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
		time.sleep(1)

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
		time.sleep(0.5)

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

class RMethod(RVariable):
	def __init__(self, label):
		self.path		= None # parent node path
		self.label		= label
		self.ctrlType	= ''
		self.rectangle	= None
		self.readonly	= True
		self.style		= 'METHOD'

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
			time.sleep(0.4)
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
