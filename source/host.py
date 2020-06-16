import pdb
import logging
import os
import sys
import time
import subprocess
import gc
import xlrd
import win32gui
import win32api
import win32con
#import comtypes
from uia2 import *
from configparser import ConfigParser
from comtypes.client import *
from ctypes import *


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
	
	def startUp(self):
		pass
	
	def shutDown(self):
		pass
	
	def load(self, ddfdi):
		pass
	
	def unload(self):
		pass
		
	def createTree(self, root):
		#pdb.set_trace()
		assert not root == None
		assert not root.isLeafNode()
		path = root.getPath()
		uiaElem = self.host
		for node in path:
			#logging.info('########### 10 ###########')
			uiaElem = node.select(uiaElem)
			if node.isEqual(root):
				node.appendChildren(uiaElem)
				logTreeItem(node)
				currNode = node.left
				if not currNode.isLeafNode(): self.createTree(currNode)
				currNode = currNode.right
				while not currNode == None:
					if not currNode.isLeafNode(): self.createTree(currNode)
					currNode = currNode.right
		time.sleep(0.5)
	
	def traversal(self, root):
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
		#del desktop, rrte, process
		#gc.collect()

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
	
	def isLeafNode(self):
		return isinstance(self.elem, RVariable)

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
		return self.elem.select(uiaElem)
	
	def appendChildren(self, uiaElem):
		elems = self.elem.children(uiaElem)
		logging.info('Children count is %d' % len(elems))
		if len(elems) > 0:
			self.left = TreeNode(elems[0], self)
			currNode = self.left
			for x in range(1, len(elems)):
				currNode.right = TreeNode(elems[x], self)
				currNode = currNode.right

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
	def getElemSubName(self, elem):
		textbox = findFirstElemByControlType(elem, UIAClient.UIA_TextControlTypeId, SCOPE_CHILDREN)
		text = textbox.CurrentName
		#del textbox
		#gc.collect()
		return text
	
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
	
	def createString(self, uiaElem):
		assert self.isString(uiaElem)
		label = self.getElemSubName(uiaElem)
		return RString(label)
	
	def createDate(self, uiaElem):
		assert self.isDate(uiaElem)
		label = self.getElemSubName(uiaElem)
		return RDate(label)
	
	def createTime(self, uiaElem):
		assert self.isTime(uiaElem)
		label = self.getElemSubName(uiaElem)
		return RTime(label)
	
	def createNumeric(self, uiaElem):
		assert self.isNumeric(uiaElem)
		label = self.getElemSubName(uiaElem)
		return RNumeric(label)
	
	def createEnum(self, uiaElem):
		assert self.isEnum(uiaElem)
		label = self.getElemSubName(uiaElem)
		return REnum(label)
	
	def createBitEnum(self, uiaElem):
		assert self.isBitEnum(uiaElem)
		group = findFirstElemByControlType(uiaElem, UIAClient.UIA_GroupControlTypeId)
		label = self.getElemSubName(group)
		#del group
		#gc.collect()
		return RBitEnum(label)
		
	def createParam(self, uiaElem):
		assert isCustom(uiaElem)
		if self.isEnum(uiaElem):
			return self.createEnum(uiaElem)
		elif self.isString(uiaElem):
			return self.createString(uiaElem)
		elif self.isNumeric(uiaElem):
			return self.createNumeric(uiaElem)
		elif self.isBitEnum(uiaElem):
			return self.createBitEnum(uiaElem)
		elif self.isDate(uiaElem):
			return self.createDate(uiaElem)
		elif self.isTime(uiaElem):
			return self.createTime(uiaElem)
			
	def createPage(self, uiaElem):
		assert isTab(uiaElem)
		#pdb.set_trace()
		uias = findAllElemByControlType(uiaElem, UIAClient.UIA_TabItemControlTypeId, SCOPE_CHILDREN)
		pages = []
		logging.info('Page count is %d' % uias.Length)
		for x in range(0, uias.Length):
			#logging.info('########### 02 ###########')
			item = uias.GetElement(x)
			if item.CurrentName == 'Condensed status map':
				continue
			page = RPage(item.CurrentName)
			page.ctrlType = 'TabItem'
			#page.rectangle = item.CurrentBoundingRectangle
			pages.append(page)
			#del item, page
			#gc.collect()
		#del uias
		#gc.collect()
		return pages
	
	def children(self, uiaElem):
		#pdb.set_trace()
		if isPane(uiaElem) or isTabItem(uiaElem) or isGroup(uiaElem):
			all = findAllElem4ORCond(uiaElem, UIAClient.UIA_CustomControlTypeId, UIAClient.UIA_ButtonControlTypeId, UIAClient.UIA_GroupControlTypeId, UIAClient.UIA_TabControlTypeId, UIAClient.UIA_ControlTypePropertyId, SCOPE_CHILDREN)
			set = []
			#for item in uias:
			for x in range(0, all.Length):
				#logging.info('########### 03 ###########')
				item = all.GetElement(x)
				if isCustom(item): # variable(others, Enum, BitEnum)
					elem = self.createParam(item)
					elem.ctrlType = 'Custom'
					#elem.rectangle = item.CurrentBoundingRectangle
					set.append(elem)
					del elem
				elif isButton(item): # method
					elem = RMethod(self.getElemSubName(item))
					elem.ctrlType = 'Button'
					#elem.rectangle = item.CurrentBoundingRectangle
					set.append(elem)
					del elem
				elif isGroup(item): # group
					elem = RGroup(item.CurrentName)
					elem.ctrlType = 'Group'
					#elem.rectangle = item.CurrentBoundingRectangle
					set.append(elem)
					del elem
				elif isTab(item): # page
					tabs = self.createPage(item)
					set.extend(tabs)
					del tabs
				else:
					pass # other uia element
				del item
				#gc.collect()
			del all
			#gc.collect()
			return set
		else:
			all = findAllElemByControlType(uiaElem, UIAClient.UIA_TreeItemControlTypeId, SCOPE_CHILDREN)
			set = []
			for x in range(0, all.Length):
				item = all.GetElement(x)
				name = self.getElemSubName(item)
				if isTreeLeaf(item):
					elem = RWindow(name)
				else:
					elem = RMenu(name)
				elem.ctrlType = 'TreeItem'
				#elem.rectangle = item.CurrentBoundingRectangle
				set.append(elem)
				#del elem, item
				#gc.collect()
			#del all
			#gc.collect()
			return set

class RRoot(RElement):
	def select(self, uiaElem):
		assert isUIAElem(uiaElem)
		# wait dialog close
		desktop = IUIA.GetRootElement()
		assert isUIAElem(desktop)
		internal = findFirstElemByAutomationId(desktop, 'DD_ExplorerView')
		while not isUIAElem(internal):
			time.sleep(1.5)
			internal = findFirstElemByAutomationId(DesktopRoot, 'DD_ExplorerView')
		# get main uia element
		all = findAllElemByControlType(uiaElem, UIAClient.UIA_CustomControlTypeId, SCOPE_CHILDREN)
		workRoot = all.GetElement(all.Length-1)
		assert isUIAElem(workRoot)
		topTAB = findFirstElemByName(workRoot, 'Fdi.Client.DeviceUi.ViewModel.DeviceUiHostContainerItemViewModel')
		assert isUIAElem(topTAB)
		topTABX = findFirstElemByName(topTAB, 'X')
		assert isUIAElem(topTABX)
		topRoot = findNextSiblingElem(topTABX)
		assert isUIAElem(topRoot)
		# release memery
		#del desktop, internal, all, workRoot, topTAB, topTABX
		#gc.collect()
		# return top root(right side)
		return topRoot
	
	def children(self, uiaElem):
		set = []
		# get offline root menu item
		offline = findFirstElemBySubText(uiaElem, 'Offline root menu')
		assert isUIAElem(offline)
		menu = RRootMenu('Offline root menu')
		menu.ctrlType = 'Button'
		#menu.rectangle = offline.CurrentBoundingRectangle
		#set.append(menu) # for debug
		# get online root menu items
		onlineRoot = findFirstElemByAutomationId(uiaElem, 'OnlineParameters')
		assert isUIAElem(onlineRoot)
		pane = findFirstElemByControlType(onlineRoot, UIAClient.UIA_PaneControlTypeId)
		assert isUIAElem(pane)
		all = findAllElemByControlType(pane, UIAClient.UIA_ButtonControlTypeId, SCOPE_CHILDREN)
		for x in range(0, all.Length):
			item = all.GetElement(x)
			label = self.getElemSubName(item)
			if label == 'Device root menu' or label == 'Online' or label == 'Diagnostic root menu':
				continue
			elem = RRootMenu(label)
			elem.ctrlType = 'Button'
			#elem.rectangle = item.CurrentBoundingRectangle
			set.append(elem)
			#del item, elem
			#gc.collect()
		#del offline, menu, onlineRoot, pane
		#gc.collect()
		return set

class RRootMenu(RElement):
	def __init__(self, label):
		super(RRootMenu, self).__init__(label)
		self.current = None
		
	def select(self, uiaElem):
		assert isUIAElem(uiaElem)
		# search root menu button
		if not self.label == 'Offline root menu':
			onlineRoot = findFirstElemByAutomationId(uiaElem, 'OnlineParameters')
			assert isUIAElem(onlineRoot)
			pane = findFirstElemByControlType(onlineRoot, UIAClient.UIA_PaneControlTypeId)
			assert isUIAElem(pane)
			btn = findFirstElemBySubText(pane, self.label)
			#del onlineRoot, pane
		else:
			btn = findFirstElemBySubText(uiaElem, self.label)
		# push root menu button
		assert isUIAElem(btn)
		if not self.label == self.current:
			pushButton(btn)
			self.current = self.label
			#RRTE.waitDialogClose()
			time.sleep(4)
		explorer = findFirstElemByAutomationId(uiaElem, 'DD_ExplorerView')
		assert isUIAElem(explorer)
		elem = findNextSiblingElem(explorer)
		#del btn, explorer
		#gc.collect()
		assert isUIAElem(elem)
		return elem
	
class RMenu(RElement):
	def select(self, uiaElem):
		assert isUIAElem(uiaElem)
		#pdb.set_trace()
		tree = findFirstElemBySubText(uiaElem, self.label)
		assert isUIAElem(tree)
		expandTree(tree)
		#del tree
		#gc.collect()
		time.sleep(1)
		return tree

class RWindow(RElement):
	def select(self, uiaElem):
		assert isUIAElem(uiaElem)
		leaf = findFirstElemBySubText(uiaElem, self.label)
		assert isUIAElem(leaf)
		pushLeaf(leaf)
		time.sleep(1)
		curr = leaf
		while not isTree(curr):
			curr = findParentElem(curr)
			assert isUIAElem(curr)
		pane = findNextSiblingElem(curr)
		#del leaf, curr
		#gc.collect()
		assert isUIAElem(pane)
		return pane

class RPage(RElement):
	def select(self, uiaElem):
		assert isUIAElem(uiaElem)
		#pdb.set_trace()
		tabs = findFirstElemByControlType(uiaElem, UIAClient.UIA_TabControlTypeId, SCOPE_CHILDREN)
		tab = findFirstElemByName(tabs, self.label)
		assert isUIAElem(tab)
		selectTab(tab)
		#del tabs
		#gc.collect()
		time.sleep(1)
		return tab

class RGroup(RElement):
	def select(self, uiaElem):
		assert isUIAElem(uiaElem)
		#pdb.set_trace()
		group = findFirstElemByName(uiaElem, self.label, SCOPE_CHILDREN)
		time.sleep(1)
		assert isUIAElem(group)
		return group

class RVariable(RElement):
	pass

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
	pass

class RBitEnum(RVariable):
	pass

def test():
	logging.info('--------- 002 ---------')
	desktop1 = IUIA.GetRootElement()
	desktop2 = IUIA.GetRootElement()
	set = []
	set.append(desktop1)
	set.append(desktop2)
	logging.info('--------- 003 ---------')
	return set
	#assert isUIAElem(desktop)

if __name__ == '__main__':
	#pdb.set_trace()
	logging.basicConfig(level = logging.DEBUG)
	logging.info('--------- 001 ---------')
	desktops = test()
	logging.info('--------- 004 ---------')
	del desktops[0]
	logging.info('--------- 005 ---------')
	pdb.set_trace()
	top = RRoot('root')
	top.ctrlType = ''
	#top.rectangle = None
	root = TreeNode(top)
	rrte = RRTE(root)
	#pdb.set_trace()
	rrte.startUp()
	rrte.createTree(rrte.root)