'''
@File		: host.py
@Date		: 2020/05/30
@Author		: Wang.Yu
@Version	: 1.0
@Contact	: yu.wang@cn.yokogawa.com
@License	: (C)Copyright 2020 Yokogawa China Co., Ltd.
'''
import pdb
import logging
import os
import sys
import datetime
import time
import subprocess
import csv
from uia2 import *
from uiaRRTE import *
from configparser import ConfigParser
from comtypes.client import *
from ctypes import *

# It's EDD's host application's abstract class.
class Host:
	def __init__(self, root=None):
		self.root = root
		self.host = None
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
	
	def createTree(self, target):
		assert not target == None
		assert not isinstance(target.elem, RVariable)
		path = target.getPath()
		for node in path:
			node.select()
			if not node.isEqual(target): continue
			node.getChildren()
			self.logTreeItem(node)
			currNode = node.left
			if currNode is None:
				continue
			if not isinstance(currNode.elem, RVariable):
				self.createTree(currNode)
			currNode = currNode.right
			while not currNode == None:
				if not isinstance(currNode.elem, RVariable):
					self.createTree(currNode)
				currNode = currNode.right
		time.sleep(0.5)
	
	def logTreeItem(self, node):
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
		if isinstance(node.elem, REnum):
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
		if isinstance(node.elem, RBitEnum):
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
	
	def getStyle(self):
		style = ''
		if isinstance(self.elem, RMenu):
			style = 'MENU'
		elif isinstance(self.elem, RWindow):
			style = 'WINDOW'
		elif isinstance(self.elem, RPage):
			style = 'PAGE'
		elif isinstance(self.elem, RGroup):
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
	
	def select(self):
		return self.elem.select()
	
	def getChildren(self):
		elems = self.elem.getChildren()
		# set path info into element object
		for elem in elems:
			path = []
			path.extend(self.elem.path)
			path.append(elem) # append self to oneself's path
			elem.path = path
		# append children node into tree
		if len(elems) > 0:
			curr = None
			for x in range(0, len(elems)):
				node = TreeNode(elems[x])
				node.parent = self
				if x == 0:
					self.left = node
					curr = self.left
				else :
					curr.right = node
					curr = curr.right

def createParam(uiaElem):
	assert isCustom(uiaElem)
	if isContentNameEnum(uiaElem):
		param = REnum(uiaElem)
		param.option(uiaElem)
	elif isContentNameString(uiaElem):
		param = RString(uiaElem)
	elif isContentNameNumeric(uiaElem):
		param = RNumeric(uiaElem)
	elif isContentNameBitEnum(uiaElem):
		param = RBitEnum(uiaElem)
		param.option(uiaElem)
	elif isContentNameDate(uiaElem):
		param = RDate(uiaElem)
	elif isContentNameTime(uiaElem):
		param = RTime(uiaElem)
	return param
	
class Element: # abstract class
	def __init__(self, label):
		self.path		= None # parent node path
		self.label		= label
		self.ctrlType	= ''
		self.rectangle	= None
	
	def getSelfScope(self, scope):
		pass
	
	def getScopeAfterSelect(self):
		scope = DesktopRoot
		for elem in self.path:
			scope = elem.getSelfScope(scope)
		return scope
	
	def select(self): # extend a node, for example, group, its processing may be inconsistent on different hosts
		pass
	
	def getChildren(self):
		pass

class RElement(Element):
	def __getContentElement(self):
		scope = self.getScopeAfterSelect()
		#all = findAllElem(scope, True, UIAClient.UIA_IsEnabledPropertyId, SCOPE_CHILDREN)
		all = findAllChildren(scope)
		set = []
		for x in range(0, all.Length):
			item = all.GetElement(x)
			if isCustom(item): # variable(others, Enum, BitEnum
				elem = createParam(item)
				elem.ctrlType = 'Custom'
				elem.rectangle = item.CurrentBoundingRectangle
				set.append(elem)
			elif isButton(item): # method
				label = RRTE.getElemSubName(item)
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
	
	def __getLayoutElement(self):
		scope = self.getScopeAfterSelect()
		all = findAllElemByControlType(scope, UIAClient.UIA_TreeItemControlTypeId, SCOPE_CHILDREN)
		set = []
		for x in range(0, all.Length):
			item = all.GetElement(x)
			if isLayoutNameMethod(item):
				label = RRTE.getMenuMethodName(item)
				elem = RMethod(label)
				elem.ctrlType = 'Button'
				elem.rectangle = item.CurrentBoundingRectangle
				set.append(elem)
			elif isLayoutNameMenu(item):
				label = RRTE.getElemSubName(item)
				if isTreeLeaf(item):
					elem = RWindow(label)
				else:
					elem = RMenu(label)
				elem.ctrlType = 'TreeItem'
				elem.rectangle = item.CurrentBoundingRectangle
				set.append(elem)
		return set
	
	def getChildren(self):
		scope = self.getScopeAfterSelect()
		if isPane(scope) or isTabItem(scope) or isGroup(scope):
			return self.__getContentElement()
		else:
			return self.__getLayoutElement()

class RRoot(RElement):
	def getSelfScope(self, scope):
		rrte = findFirstElemByName(scope, 'Reference Run-time Environment', SCOPE_CHILDREN)
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
		scope = self.getScopeAfterSelect()
		# get offline root menu item
		offline = findFirstElemBySubText(scope, 'Offline')
		if not isUIAElem(offline):
			offline = findFirstElemBySubText(scope, 'Offline root menu')
			assert isUIAElem(offline)
			menu = RRootMenu('Offline root menu')
		else:
			menu = RRootMenu('Offline')
		menu.ctrlType = 'Button'
		menu.rectangle = offline.CurrentBoundingRectangle
		set.append(menu)
		# get online root menu items
		onlineRoot = findFirstElemByAutomationId(scope, 'OnlineParameters')
		assert isUIAElem(onlineRoot)
		pane = findFirstElemByControlType(onlineRoot, UIAClient.UIA_PaneControlTypeId)
		assert isUIAElem(pane)
		all = findAllElemByControlType(pane, UIAClient.UIA_ButtonControlTypeId, SCOPE_CHILDREN)
		for x in range(0, all.Length):
			item = all.GetElement(x)
			label = RRTE.getElemSubName(item)
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
		self.current = None
	
	def getSelfScope(self, scope):
		explorer = findFirstElemByAutomationId(scope, 'DD_ExplorerView')
		assert isUIAElem(explorer)
		elem = findNextSiblingElem(explorer) # maybe pane or tree
		assert isUIAElem(elem)
		return elem
	
	def select(self):
		scope = self.path[-2].getScopeAfterSelect()
		# search root menu button
		if not (self.label == 'Offline' or self.label == 'Offline root menu'):
			onlineRoot = findFirstElemByAutomationId(scope, 'OnlineParameters')
			assert isUIAElem(onlineRoot)
			pane = findFirstElemByControlType(onlineRoot, UIAClient.UIA_PaneControlTypeId)
			assert isUIAElem(pane)
			btn = findFirstElemBySubText(pane, self.label)
		else:
			btn = findFirstElemBySubText(scope, self.label)
		# push root menu button
		assert isUIAElem(btn)
		if not self.label == self.current:
			pushButton(btn)
			self.current = self.label
			#RRTE.waitDialogClose()
			time.sleep(6)
		else:
			time.sleep(1)
	
class RMenu(RElement):
	def getSelfScope(self, scope):
		tree = findFirstElemBySubText(scope, self.label)
		assert isUIAElem(tree)
		return tree
		
	def select(self):
		scope = self.path[-2].getScopeAfterSelect()
		tree = findFirstElemBySubText(scope, self.label)
		assert isUIAElem(tree)
		expandTree(tree)
		time.sleep(0.5)

class RWindow(RElement):
	def getSelfScope(self, scope):
		leaf = findFirstElemBySubText(scope, self.label)
		assert isUIAElem(leaf)
		curr = leaf
		while not isTree(curr):
			curr = findParentElem(curr)
			assert isUIAElem(curr)
		pane = findNextSiblingElem(curr)
		assert isUIAElem(pane)
		return pane
	
	def select(self):
		scope = self.path[-2].getScopeAfterSelect()
		leaf = findFirstElemBySubText(scope, self.label)
		assert isUIAElem(leaf)
		pushLeaf(leaf)
		time.sleep(1)

class RPage(RElement):
	def getSelfScope(self, scope):
		tabs = findFirstElemByControlType(scope, UIAClient.UIA_TabControlTypeId, SCOPE_CHILDREN)
		assert isUIAElem(tabs)
		tab = findFirstElemByName(tabs, self.label)
		assert isUIAElem(tab)
		return tab
	
	def select(self):
		scope = self.path[-2].getScopeAfterSelect()
		tabs = findFirstElemByControlType(scope, UIAClient.UIA_TabControlTypeId, SCOPE_CHILDREN)
		tab = findFirstElemByName(tabs, self.label)
		assert isUIAElem(tab)
		selectTab(tab)
		time.sleep(0.5)

class RGroup(RElement):
	def getSelfScope(self, scope):
		group = findFirstElemByName(scope, self.label, SCOPE_CHILDREN)
		assert isUIAElem(group)
		return group
	
	def select(self):
		pass

class RVariable(RElement):
	def __init__(self, uiaElem):
		label = RRTE.getElemSubName(uiaElem)
		super(RVariable, self).__init__(label)
		self.readonly = not isEditboxEnabled(uiaElem)

class RMethod(RVariable):
	def __init__(self, label):
		self.path		= None # parent node path
		self.label		= label
		self.ctrlType	= ''
		self.rectangle	= None
		self.readonly	= True

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
		self.label		= RRTE.getElemSubName(uiaElem)
		self.ctrlType	= ''
		self.rectangle	= None
		self.readonly	= not isComboboxEnabled(uiaElem)
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
			#collapseCombo(combo) # variable refreshed after
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
	def __init__(self, uiaElem):
		assert isContentNameBitEnum(uiaElem)
		group = findFirstElemByControlType(uiaElem, UIAClient.UIA_GroupControlTypeId)
		if isUIAElem(group):
			self.label = RRTE.getElemSubName(group)
		else: # FF & ProfiNet FDI package
			self.label = RRTE.getElemSubName(uiaElem)
		self.path		= None # parent node path
		self.ctrlType	= ''
		self.rectangle	= None
		self.readonly 	= not isBitEnumGroupEnabled(uiaElem)
		self.options = []
	
	def option(self, uiaElem):
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
		self.options.extend(set)

if __name__ == '__main__':
	#pdb.set_trace()
	logging.basicConfig(level = logging.INFO)
	logging.info('[Start RRTE] : ' + datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S'))
	top = RRoot('root')
	top.ctrlType = ''
	top.rectangle = None
	top.path = [top]
	root = TreeNode(top)
	rrte = RRTE(root)
	rrte.startUp()
	rrte.createTree(rrte.root)
	logging.info('[Finished tree generation] : ' + datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S'))
	rrte.dumpMenuLabel2Csv(rrte.root)
	rrte.dumpEnumOpt2Csv(rrte.root)
	rrte.dumpBitEnumOpt2Csv(rrte.root)
	t = datetime.datetime.now()
	logging.info('[Finished label collection] : ' + datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S'))
