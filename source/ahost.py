import pdb
import logging
import os
import sys
import time
import subprocess
import csv
from uia2 import *
from configparser import ConfigParser
from comtypes.client import *
from ctypes import *

LOG_STR = '--- host.py : %d ---'
	
def logTreeItem(node):
	logging.info('----------------------------------------------------------')
	logging.info('Parent\t: %s (%s)' % (node.elem.label, node.elem.ctrlType))
	if not node.left is None:
		logging.info('Child[0]\t: %s (%s)' % (node.left.elem.label, node.left.elem.ctrlType))
		curr = node.left.right
		cnt = 1
		while not curr is None:
			logging.info('Child[%d]\t: %s (%s)' % (cnt, curr.elem.label, curr.elem.ctrlType))
			cnt = cnt + 1
			curr = curr.right

# It's EDD's host application's abstract class.
class Host:
	def __init__(self, root=None):
		self.root = root
		self.host = None
		self.curr = None
		self.__csvFile = None
		self.__treeDeepth = 0
		self.__csvColumn = 10
	
	def startUp(self):
		pass
	
	def shutDown(self):
		pass
	
	def load(self, ddfdi):
		pass
	
	def unload(self):
		pass
	
	def createTree(self, root):
		assert not root == None
		assert not root.isVariableNode()
		logging.debug(LOG_STR % sys._getframe().f_lineno)
		path = root.getPath()
		uiaElem = self.host
		for node in path:
			logging.debug(LOG_STR % sys._getframe().f_lineno)
			uiaElem = node.select(uiaElem)
			logging.debug(LOG_STR % sys._getframe().f_lineno)
			if not node.isEqual(root): continue
			node.appendChildren(uiaElem)
			logging.debug(LOG_STR % sys._getframe().f_lineno)
			logTreeItem(node)
			currNode = node.left
			if currNode is None:
				continue
			logging.debug(LOG_STR % sys._getframe().f_lineno)
			if not currNode.isVariableNode():
				logging.debug(LOG_STR % sys._getframe().f_lineno)
				self.createTree(currNode)
			logging.debug(LOG_STR % sys._getframe().f_lineno)
			currNode = currNode.right
			while not currNode == None:
				logging.debug(LOG_STR % sys._getframe().f_lineno)
				if not currNode.isVariableNode():
					logging.debug(LOG_STR % sys._getframe().f_lineno)
					self.createTree(currNode)
				currNode = currNode.right
				logging.debug(LOG_STR % sys._getframe().f_lineno)
			logging.debug(LOG_STR % sys._getframe().f_lineno)
		logging.debug(LOG_STR % sys._getframe().f_lineno)
		time.sleep(0.5)
	
	def __preTraverseLabel(self, node):
		rowElement = []
		if node == None or node.elem == None:
			return
		for x in range(0, self.__csvColumn):
			if(x != self.__treeDeepth):
				rowElement.append('')
			else:
				rowElement.append(node.elem.label)
		rowElement.append(node.elem.label)
		rowElement.append(node.getStyle())
		self.__csvFile.writerow(rowElement)
		self.__treeDeepth += 1
		self.__preTraverseLabel(node.left)
		self.__treeDeepth -= 1
		self.__preTraverseLabel(node.right)
	
	def __preTraverseEnumOpts(self, node):
		rowElement = []
		if node == None or node.elem == None:
			return
		if node.isEnumNode():
			if not node.elem.readonly:
				rowElement.append(node.elem.label)
				self.__csvFile.writerow(rowElement)
				rowElement.clear()
				for item in node.elem.options:
					rowElement.append('')
					rowElement.append(item)
					self.__csvFile.writerow(rowElement)
					rowElement.clear()
			else:
				rowElement.append(node.elem.label + ' (Not Read)')
				self.__csvFile.writerow(rowElement)
				rowElement.clear()
		self.__preTraverseEnumOpts(node.left)
		self.__preTraverseEnumOpts(node.right)
	
	def __preTraverseBitEnumOpts(self, node):
		rowElement = []
		if node == None or node.elem == None:
			return
		if(node.isBitEnumNode()):
			rowElement.append(node.elem.label)
			self.__csvFile.writerow(rowElement)
			rowElement.clear()
			for item in node.elem.options:
				rowElement.append('')
				rowElement.append(item)
				self.__csvFile.writerow(rowElement)
				rowElement.clear()
		self.__preTraverseBitEnumOpts(node.left)
		self.__preTraverseBitEnumOpts(node.right)
			
	def dumpMenuLabel2Csv(self, root):
		headers = ['ITEM0', 'ITEM1', 'ITEM2', 'ITEM3', 'ITEM4', 'ITEM5', 'ITEM6', 'ITEM7', 'ITEM8', 'ITEM9', 'LABEL', 'STYLE']
		outputPath = os.getcwd() + '\\output\\'
		outputFile = outputPath + 'outputTree.csv'
		if not os.path.exists(outputPath):
			os.makedirs(outputPath)
		with open(outputFile, 'w', newline='', encoding='UTF-8') as self.__csvFile:
			self.__csvFile = csv.writer(self.__csvFile)
			self.__csvFile.writerow(headers)
			self.__preTraverseLabel(root)
	
	def dumpEnumOpt2Csv(self, root):
		headers = ['ENUM', 'OPTION']
		outputPath = os.getcwd() + '\\output\\'
		outputFile = outputPath + 'outputEnumOpts.csv'
		if not os.path.exists(outputPath):
			os.makedirs(outputPath)
		with open(outputFile, 'w', newline='', encoding='UTF-8') as self.__csvFile:
			self.__csvFile = csv.writer(self.__csvFile)
			self.__csvFile.writerow(headers)
			self.__preTraverseEnumOpts(root)
	
	def dumpBitEnumOpt2Csv(self, root):
		headers = ['BITENUM', 'OPTION']
		outputPath = os.getcwd() + '\\output\\'
		outputFile = outputPath + 'outputBitEnumOpts.csv'
		if not os.path.exists(outputPath):
			os.makedirs(outputPath)
		with open(outputFile, 'w', newline='', encoding='UTF-8') as self.__csvFile:
			self.__csvFile = csv.writer(self.__csvFile)
			self.__csvFile.writerow(headers)
			self.__preTraverseBitEnumOpts(root)
	
	def traverse(self, root, func):
		pass

class RRTE(Host):
	def __init__(self, root):
		super(RRTE, self).__init__(root)
		self.config = ConfigParser()
		self.config.read('test.conf', encoding='UTF-8')
	
	def startUp(self):
		inputMode = self.config['MISC']['TEST_FILE_TYPE'].strip("'")
		hostApp	= self.config['MISC']['HOST_APP_PATH'].strip("'") + '\Reference Run-time Environment\Fdi.Reference.Client.exe'
		testFile = self.config['MISC']['TEST_FILE'].strip("'")
		outPath = self.config['MISC']['OUTPUT_PATH'].strip("'")
		logPath = self.config['MISC']['RRTE_LOG_PATH'].strip("'")
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
	
	@staticmethod
	def getElemSubName(elem):
		textbox = findFirstElemByControlType(elem, UIAClient.UIA_TextControlTypeId, SCOPE_CHILDREN)
		text = textbox.CurrentName
		return text
	
	@staticmethod
	def getMenuMethodName(elem):
		btns = findAllElemByControlType(elem, UIAClient.UIA_ButtonControlTypeId, SCOPE_CHILDREN)
		btn = btns.GetElement(btns.Length-1)
		text = btn.CurrentName
		return text
	
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

# It's logic tree, not control view tree in ui automation.
class TreeNode:
	def __init__(self, elem, parent=None, left=None, right=None):
		self.elem	= elem
		self.parent	= parent # It's logic parent node in tree, not in binary tree
		self.left	= left
		self.right	= right
	
	def isEqual(self, ref):
		node1 = self
		node2 = ref
		while not (node1 == None and node2 == None):
			if node1.elem.label == node2.elem.label:
				node1 = node1.parent
				node2 = node2.parent
			else:
				return False
		return True
	
	def isMenuNode(self):
		return isinstance(self.elem, RMenu)
	
	def isWindowNode(self):
		return isinstance(self.elem, RWindow)
	
	def isPageNode(self):
		return isinstance(self.elem, RPage)
	
	def isGroupNode(self):
		return isinstance(self.elem, RGroup)
	
	def isVariableNode(self):
		return isinstance(self.elem, RVariable)
	
	def isEnumNode(self):
		return isinstance(self.elem, REnum)
	
	def isBitEnumNode(self):
		return isinstance(self.elem, RBitEnum)
	
	def getStyle(self):
		style = ''
		if self.isMenuNode():
			style = 'MENU'
		elif self.isWindowNode():
			style = 'WINDOW'
		elif self.isPageNode():
			style = 'PAGE'
		elif self.isGroupNode():
			style = 'GROUP'
		else:
			pass
		return style
	
	def getPath(self):
		path = []
		path.append(self)
		currNode = self
		while not currNode.parent == None:
			currNode = currNode.parent
			path.append(currNode)
		path.reverse()
		return path
	
	def select(self, uiaElem):
		logging.debug(LOG_STR % sys._getframe().f_lineno)
		return self.elem.select(uiaElem)
	
	def appendChildren(self, uiaElem):
		elems = self.elem.children(uiaElem)
		logging.info('Children count is %d' % len(elems))
		if len(elems) > 0:
			size = len(elems)
			logging.info('%d elements will be appended to [%s]' % (size, self.elem.label))
			curr = None
			for x in range(0, size):
				logging.debug(LOG_STR % sys._getframe().f_lineno)
				node = TreeNode(elems[x])
				node.parent = self
				if x == 0:
					logging.debug(LOG_STR % sys._getframe().f_lineno)
					self.left = node
					curr = self.left
				else :
					logging.debug(LOG_STR % sys._getframe().f_lineno)
					curr.right = node
					curr = curr.right

class Element: # abstract class
	def __init__(self, label):
		self.label		= label
		self.ctrlType	= ''
		#self.rectangle	= None
	
	def select(self, uiaElem): # extend a node, for example, group, its processing may be inconsistent on different hosts
		pass
	
	def children(self, uiaElem):
		pass

class RElement(Element):
	def isString(self, uiaElem):
		return 'Fdi.Ui.ViewModel.Content.StringParameterViewModel' == uiaElem.CurrentName
	
	def isDate(self, uiaElem):
		return 'Fdi.Ui.ViewModel.Content.DateTimeParameterViewModel' == uiaElem.CurrentName
	
	def isTime(self, uiaElem):
		return 'Fdi.Ui.ViewModel.Content.UidTimeSpanViewModel' == uiaElem.CurrentName
	
	def isNumeric(self, uiaElem):
		return 'Fdi.Ui.ViewModel.Content.NumericParameterViewModel' == uiaElem.CurrentName
	
	def isEnum(self, uiaElem):
		return 'Fdi.Ui.ViewModel.Content.EnumerationViewModel' == uiaElem.CurrentName
	
	def isBitEnum(self, uiaElem):
		return 'Fdi.Ui.ViewModel.Content.BitEnumerationViewModel' == uiaElem.CurrentName
	
	def isMethod(self, uiaElem): # in menu tree
		return 'Fdi.Ui.ViewModel.Layout.ActionMenuItemViewModel' == uiaElem.CurrentName
	
	def isMenu(self, uiaElem): # in menu tree, include menu and window
		return 'Fdi.Ui.ViewModel.Layout.RootMenuViewModel' == uiaElem.CurrentName
	
	def isTextEnabled(self, uiaElem):
		assert isUIAElem(uiaElem)
		edit = findFirstElemByControlType(uiaElem, UIAClient.UIA_EditControlTypeId)
		assert isUIAElem(edit)
		return edit.CurrentIsEnabled
	
	def isEnumEnabled(self, uiaElem):
		assert isUIAElem(uiaElem)
		combo = findFirstElemByControlType(uiaElem, UIAClient.UIA_ComboBoxControlTypeId)
		assert isUIAElem(combo)
		return combo.CurrentIsEnabled
	
	def isBitEnumEnabled(self, uiaElem):
		return True
	
	def __createString(self, uiaElem):
		assert self.isString(uiaElem)
		label = RRTE.getElemSubName(uiaElem)
		readonly = not self.isTextEnabled(uiaElem)
		elem = RString(label, readonly)
		return elem
	
	def __createDate(self, uiaElem):
		assert self.isDate(uiaElem)
		label = RRTE.getElemSubName(uiaElem)
		readonly = not self.isTextEnabled(uiaElem)
		elem = RDate(label, readonly)
		return elem
	
	def __createTime(self, uiaElem):
		assert self.isTime(uiaElem)
		label = RRTE.getElemSubName(uiaElem)
		readonly = not self.isTextEnabled(uiaElem)
		elem = RTime(label, readonly)
		return elem
	
	def __createNumeric(self, uiaElem):
		assert self.isNumeric(uiaElem)
		label = RRTE.getElemSubName(uiaElem)
		readonly = not self.isTextEnabled(uiaElem)
		elem = RTime(label, readonly)
		return elem
	
	def __createEnum(self, uiaElem):
		assert self.isEnum(uiaElem)
		label = RRTE.getElemSubName(uiaElem)
		readonly = not self.isEnumEnabled(uiaElem)
		elem = REnum(label, readonly)
		elem.option(uiaElem)
		return elem
	
	def __createBitEnum(self, uiaElem):
		assert self.isBitEnum(uiaElem)
		group = findFirstElemByControlType(uiaElem, UIAClient.UIA_GroupControlTypeId)
		label = RRTE.getElemSubName(group)
		readonly = not self.isBitEnumEnabled(uiaElem)
		elem = RBitEnum(label, readonly)
		elem.option(uiaElem)
		return elem
		
	def __createParam(self, uiaElem):
		assert isCustom(uiaElem)
		if self.isEnum(uiaElem):
			logging.debug(LOG_STR % sys._getframe().f_lineno)
			return self.__createEnum(uiaElem)
		elif self.isString(uiaElem):
			logging.debug(LOG_STR % sys._getframe().f_lineno)
			return self.__createString(uiaElem)
		elif self.isNumeric(uiaElem):
			logging.debug(LOG_STR % sys._getframe().f_lineno)
			return self.__createNumeric(uiaElem)
		elif self.isBitEnum(uiaElem):
			logging.debug(LOG_STR % sys._getframe().f_lineno)
			return self.__createBitEnum(uiaElem)
		elif self.isDate(uiaElem):
			logging.debug(LOG_STR % sys._getframe().f_lineno)
			return self.__createDate(uiaElem)
		elif self.isTime(uiaElem):
			logging.debug(LOG_STR % sys._getframe().f_lineno)
			return self.__createTime(uiaElem)
			
	def __createPage(self, uiaElem):
		assert isTab(uiaElem)
		logging.debug(LOG_STR % sys._getframe().f_lineno)
		uias = findAllElemByControlType(uiaElem, UIAClient.UIA_TabItemControlTypeId, SCOPE_CHILDREN)
		logging.debug(LOG_STR % sys._getframe().f_lineno)
		pages = []
		#logging.info('Page count is %d' % uias.Length)
		for x in range(0, uias.Length):
			logging.debug(LOG_STR % sys._getframe().f_lineno)
			item = uias.GetElement(x)
			logging.debug(LOG_STR % sys._getframe().f_lineno)
			page = RPage(item.CurrentName)
			logging.debug(LOG_STR % sys._getframe().f_lineno)
			page.ctrlType = 'TabItem'
			#page.rectangle = item.CurrentBoundingRectangle
			pages.append(page)
			logging.debug(LOG_STR % sys._getframe().f_lineno)
		logging.debug(LOG_STR % sys._getframe().f_lineno)
		return pages
	
	def __createContentElement(self, uiaElem):
		logging.debug(LOG_STR % sys._getframe().f_lineno)
		# Please attention here!! It will make release IUnKnown object.
		#all = findAllElem4ORCond(uiaElem, UIAClient.UIA_CustomControlTypeId, UIAClient.UIA_ButtonControlTypeId, UIAClient.UIA_GroupControlTypeId, UIAClient.UIA_TabControlTypeId, UIAClient.UIA_ControlTypePropertyId, SCOPE_CHILDREN)
		#all = findAllChildren(uiaElem)
		all = findAllElem(uiaElem, True, UIAClient.UIA_IsEnabledPropertyId, SCOPE_CHILDREN)
		logging.debug(LOG_STR % sys._getframe().f_lineno)
		set = []
		logging.debug(LOG_STR % sys._getframe().f_lineno)
		#for item in uias:
		for x in range(0, all.Length):
			logging.debug(LOG_STR % sys._getframe().f_lineno)
			item = all.GetElement(x)
			if isCustom(item): # variable(others, Enum, BitEnum)
				logging.debug(LOG_STR % sys._getframe().f_lineno)
				elem = self.__createParam(item)
				elem.ctrlType = 'Custom'
				#elem.rectangle = item.CurrentBoundingRectangle
				set.append(elem)
				logging.debug(LOG_STR % sys._getframe().f_lineno)
			elif isButton(item): # method
				logging.debug(LOG_STR % sys._getframe().f_lineno)
				elem = RMethod(RRTE.getElemSubName(item))
				elem.ctrlType = 'Button'
				#elem.rectangle = item.CurrentBoundingRectangle
				set.append(elem)
				logging.debug(LOG_STR % sys._getframe().f_lineno)
			elif isGroup(item): # group
				logging.debug(LOG_STR % sys._getframe().f_lineno)
				elem = RGroup(item.CurrentName)
				elem.ctrlType = 'Group'
				#elem.rectangle = item.CurrentBoundingRectangle
				set.append(elem)
				logging.debug(LOG_STR % sys._getframe().f_lineno)
			elif isTab(item): # page
				logging.debug(LOG_STR % sys._getframe().f_lineno)
				tabs = self.__createPage(item)
				set.extend(tabs)
				logging.debug(LOG_STR % sys._getframe().f_lineno)
			else:
				logging.info('Ignore one element')
		logging.debug(LOG_STR % sys._getframe().f_lineno)
		return set
	
	def __createLayoutElement(self, uiaElem):
		logging.debug(LOG_STR % sys._getframe().f_lineno)
		all = findAllElemByControlType(uiaElem, UIAClient.UIA_TreeItemControlTypeId, SCOPE_CHILDREN)
		logging.debug(LOG_STR % sys._getframe().f_lineno)
		set = []
		logging.debug(LOG_STR % sys._getframe().f_lineno)
		for x in range(0, all.Length):
			logging.debug(LOG_STR % sys._getframe().f_lineno)
			item = all.GetElement(x)
			logging.debug(LOG_STR % sys._getframe().f_lineno)
			if self.isMethod(item):
				logging.debug(LOG_STR % sys._getframe().f_lineno)
				name = RRTE.getMenuMethodName(item)
				elem = RMethod(name)
				logging.debug(LOG_STR % sys._getframe().f_lineno)
				elem.ctrlType = 'Button'
				#elem.rectangle = item.CurrentBoundingRectangle
				set.append(elem)
			elif self.isMenu(item):
				logging.debug(LOG_STR % sys._getframe().f_lineno)
				name = RRTE.getElemSubName(item)
				if isTreeLeaf(item):
					logging.debug(LOG_STR % sys._getframe().f_lineno)
					elem = RWindow(name)
				else:
					logging.debug(LOG_STR % sys._getframe().f_lineno)
					elem = RMenu(name)
				logging.debug(LOG_STR % sys._getframe().f_lineno)
				elem.ctrlType = 'TreeItem'
				#elem.rectangle = item.CurrentBoundingRectangle
				set.append(elem)
		logging.debug(LOG_STR % sys._getframe().f_lineno)
		return set
	
	def children(self, uiaElem):
		#pdb.set_trace()
		logging.debug(LOG_STR % sys._getframe().f_lineno)
		if isPane(uiaElem) or isTabItem(uiaElem) or isGroup(uiaElem):
			logging.debug(LOG_STR % sys._getframe().f_lineno)
			return self.__createContentElement(uiaElem)
		else:
			logging.debug(LOG_STR % sys._getframe().f_lineno)
			return self.__createLayoutElement(uiaElem)

class RRoot(RElement):
	def select(self, uiaElem):
		'''
		logging.debug(LOG_STR % sys._getframe().f_lineno)
		assert isUIAElem(uiaElem)
		# wait dialog close
		desktop = IUIA.GetRootElement()
		logging.debug(LOG_STR % sys._getframe().f_lineno)
		assert isUIAElem(desktop)
		internal = findFirstElemByAutomationId(desktop, 'DD_ExplorerView')
		logging.debug(LOG_STR % sys._getframe().f_lineno)
		while not isUIAElem(internal):
			time.sleep(1.5)
			internal = findFirstElemByAutomationId(DesktopRoot, 'DD_ExplorerView')
		'''
		time.sleep(1)
		# get main uia element
		logging.debug(LOG_STR % sys._getframe().f_lineno)
		all = findAllElemByControlType(uiaElem, UIAClient.UIA_CustomControlTypeId, SCOPE_CHILDREN)
		logging.debug(LOG_STR % sys._getframe().f_lineno)
		workRoot = all.GetElement(all.Length-1)
		logging.debug(LOG_STR % sys._getframe().f_lineno)
		assert isUIAElem(workRoot)
		topTAB = findFirstElemByName(workRoot, 'Fdi.Client.DeviceUi.ViewModel.DeviceUiHostContainerItemViewModel')
		logging.debug(LOG_STR % sys._getframe().f_lineno)
		assert isUIAElem(topTAB)
		topTABX = findFirstElemByName(topTAB, 'X')
		logging.debug(LOG_STR % sys._getframe().f_lineno)
		assert isUIAElem(topTABX)
		topRoot = findNextSiblingElem(topTABX)
		logging.debug(LOG_STR % sys._getframe().f_lineno)
		assert isUIAElem(topRoot)
		# return top root(right side)
		return topRoot
	
	def children(self, uiaElem):
		set = []
		logging.debug(LOG_STR % sys._getframe().f_lineno)
		# get offline root menu item
		offline = findFirstElemBySubText(uiaElem, 'Offline root menu')
		logging.debug(LOG_STR % sys._getframe().f_lineno)
		assert isUIAElem(offline)
		menu = RRootMenu('Offline root menu')
		logging.debug(LOG_STR % sys._getframe().f_lineno)
		menu.ctrlType = 'Button'
		#menu.rectangle = offline.CurrentBoundingRectangle
		#set.append(menu)
		# get online root menu items
		onlineRoot = findFirstElemByAutomationId(uiaElem, 'OnlineParameters')
		logging.debug(LOG_STR % sys._getframe().f_lineno)
		assert isUIAElem(onlineRoot)
		pane = findFirstElemByControlType(onlineRoot, UIAClient.UIA_PaneControlTypeId)
		logging.debug(LOG_STR % sys._getframe().f_lineno)
		assert isUIAElem(pane)
		all = findAllElemByControlType(pane, UIAClient.UIA_ButtonControlTypeId, SCOPE_CHILDREN)
		logging.debug(LOG_STR % sys._getframe().f_lineno)
		for x in range(0, all.Length):
			logging.debug(LOG_STR % sys._getframe().f_lineno)
			item = all.GetElement(x)
			logging.debug(LOG_STR % sys._getframe().f_lineno)
			label = RRTE.getElemSubName(item)
			logging.debug(LOG_STR % sys._getframe().f_lineno)
			if label == 'Online': continue # TODO
			#if label == 'Device root menu': continue # TODO
			#if label == 'Diagnostic root menu': continue # TODO
			#if label == 'Maintenance root menu': continue # TODO
			#if label == 'Process variables root menu': continue # TODO
			logging.debug(LOG_STR % sys._getframe().f_lineno)
			elem = RRootMenu(label)
			logging.debug(LOG_STR % sys._getframe().f_lineno)
			elem.ctrlType = 'Button'
			#elem.rectangle = item.CurrentBoundingRectangle
			set.append(elem)
			logging.debug(LOG_STR % sys._getframe().f_lineno)
		logging.debug(LOG_STR % sys._getframe().f_lineno)
		return set

class RRootMenu(RElement):
	def __init__(self, label):
		super(RRootMenu, self).__init__(label)
		self.current = None
		
	def select(self, uiaElem):
		logging.debug(LOG_STR % sys._getframe().f_lineno)
		assert isUIAElem(uiaElem)
		# search root menu button
		if not self.label == 'Offline root menu':
			logging.debug(LOG_STR % sys._getframe().f_lineno)
			onlineRoot = findFirstElemByAutomationId(uiaElem, 'OnlineParameters')
			logging.debug(LOG_STR % sys._getframe().f_lineno)
			assert isUIAElem(onlineRoot)
			pane = findFirstElemByControlType(onlineRoot, UIAClient.UIA_PaneControlTypeId)
			logging.debug(LOG_STR % sys._getframe().f_lineno)
			assert isUIAElem(pane)
			btn = findFirstElemBySubText(pane, self.label)
			logging.debug(LOG_STR % sys._getframe().f_lineno)
		else:
			btn = findFirstElemBySubText(uiaElem, self.label)
			logging.debug(LOG_STR % sys._getframe().f_lineno)
		# push root menu button
		assert isUIAElem(btn)
		logging.debug(LOG_STR % sys._getframe().f_lineno)
		if not self.label == self.current:
			logging.debug(LOG_STR % sys._getframe().f_lineno)
			pushButton(btn)
			logging.debug(LOG_STR % sys._getframe().f_lineno)
			self.current = self.label
			#RRTE.waitDialogClose()
			time.sleep(8)
		else:
			time.sleep(2)
		logging.debug(LOG_STR % sys._getframe().f_lineno)
		explorer = findFirstElemByAutomationId(uiaElem, 'DD_ExplorerView')
		logging.debug(LOG_STR % sys._getframe().f_lineno)
		assert isUIAElem(explorer)
		elem = findNextSiblingElem(explorer)
		logging.debug(LOG_STR % sys._getframe().f_lineno)
		assert isUIAElem(elem)
		logging.debug(LOG_STR % sys._getframe().f_lineno)
		return elem
	
class RMenu(RElement):
	def select(self, uiaElem):
		logging.debug(LOG_STR % sys._getframe().f_lineno)
		assert isUIAElem(uiaElem)
		tree = findFirstElemBySubText(uiaElem, self.label)
		logging.debug(LOG_STR % sys._getframe().f_lineno)
		assert isUIAElem(tree)
		expandTree(tree)
		logging.debug(LOG_STR % sys._getframe().f_lineno)
		time.sleep(1)
		return tree

class RWindow(RElement):
	def select(self, uiaElem):
		logging.debug(LOG_STR % sys._getframe().f_lineno)
		assert isUIAElem(uiaElem)
		leaf = findFirstElemBySubText(uiaElem, self.label)
		logging.debug(LOG_STR % sys._getframe().f_lineno)
		assert isUIAElem(leaf)
		pushLeaf(leaf)
		logging.debug(LOG_STR % sys._getframe().f_lineno)
		time.sleep(2)
		curr = leaf
		while not isTree(curr):
			logging.debug(LOG_STR % sys._getframe().f_lineno)
			curr = findParentElem(curr)
			assert isUIAElem(curr)
		pane = findNextSiblingElem(curr)
		logging.debug(LOG_STR % sys._getframe().f_lineno)
		assert isUIAElem(pane)
		logging.debug(LOG_STR % sys._getframe().f_lineno)
		return pane

class RPage(RElement):
	def select(self, uiaElem):
		logging.debug(LOG_STR % sys._getframe().f_lineno)
		assert isUIAElem(uiaElem)
		tabs = findFirstElemByControlType(uiaElem, UIAClient.UIA_TabControlTypeId, SCOPE_CHILDREN)
		logging.debug(LOG_STR % sys._getframe().f_lineno)
		tab = findFirstElemByName(tabs, self.label)
		logging.debug(LOG_STR % sys._getframe().f_lineno)
		assert isUIAElem(tab)
		selectTab(tab)
		logging.debug(LOG_STR % sys._getframe().f_lineno)
		time.sleep(1)
		logging.debug(LOG_STR % sys._getframe().f_lineno)
		return tab

class RGroup(RElement):
	def select(self, uiaElem):
		logging.debug(LOG_STR % sys._getframe().f_lineno)
		assert isUIAElem(uiaElem)
		group = findFirstElemByName(uiaElem, self.label, SCOPE_CHILDREN)
		logging.debug(LOG_STR % sys._getframe().f_lineno)
		time.sleep(1)
		assert isUIAElem(group)
		logging.debug(LOG_STR % sys._getframe().f_lineno)
		return group

class RVariable(RElement):
	def __init__(self, label, readonly=False):
		super(RVariable, self).__init__(label)
		self.readonly = readonly

class RMethod(RVariable):
	pass

class RString(RVariable):
	pass

class RDate(RVariable):
	pass

class RTime(RVariable):
	pass

class RNumeric(RVariable):
	pass

class REnum(RVariable):
	def __init__(self, label, readonly):
		super(REnum, self).__init__(label, readonly)
		self.__ne107 = ['No Effect', 'Maintenance Required', 'Failure', 'Out of Specification', 'Function Check']
		self.options = []
	
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
	
	def option(self, uiaElem):
		assert isUIAElem(uiaElem)
		if self.readonly: return
		if not self.__isNE107Label():
			parent = findParentElem(uiaElem) # pane, page, group
			combo = findFirstElemByControlType(uiaElem, UIAClient.UIA_ComboBoxControlTypeId)
			assert isUIAElem(combo)
			expandCombo(combo)
			collapseCombo(combo) # variable refreshed after
			newCombo = self.__tryLabelGetting(uiaElem)
			assert isUIAElem(newCombo)
			all = findAllElemByControlType(newCombo, UIAClient.UIA_ListItemControlTypeId)
			set = []
			for x in range(0, all.Length):
				item = all.GetElement(x)
				enum = findFirstElemByControlType(item, UIAClient.UIA_TextControlTypeId)
				set.append(enum.CurrentName)
			self.options.extend(set)
		else:
			self.options.extend(self.__ne107)

class RBitEnum(RVariable):
	def __init__(self, label, readonly):
		super(RBitEnum, self).__init__(label, readonly)
		self.options = []
	
	def option(self, uiaElem):
		assert isUIAElem(uiaElem)
		group = findFirstElemByControlType(uiaElem, UIAClient.UIA_GroupControlTypeId)
		assert isUIAElem(group)
		custom = findFirstElemByControlType(group, UIAClient.UIA_CustomControlTypeId)
		assert isUIAElem(custom)
		all = findAllElemByControlType(custom, UIAClient.UIA_CheckBoxControlTypeId)
		set = []
		for x in range(0, all.Length):
			item = all.GetElement(x)
			set.append(item.CurrentName)
		self.options.extend(set)

if __name__ == '__main__':
	#pdb.set_trace()
	logging.basicConfig(level = logging.DEBUG)
	top = RRoot('root')
	top.ctrlType = ''
	#top.rectangle = None
	root = TreeNode(top)
	rrte = RRTE(root)
	rrte.startUp()
	rrte.createTree(rrte.root)
	rrte.dumpMenuLabel2Csv(rrte.root)
	rrte.dumpEnumOpt2Csv(rrte.root)
	rrte.dumpBitEnumOpt2Csv(rrte.root)
