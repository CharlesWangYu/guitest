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
		logging.info('--------- 301 ---------')
		path = root.getPath()
		logging.info('--------- 302 ---------')
		uiaElem = self.host
		for node in path:
			logging.info('--------- 303 ---------')
			uiaElem = node.select(uiaElem)
			logging.info('--------- 304 ---------')
			if node.isEqual(root):
				logging.info('--------- 305 ---------')
				node.appendChildren(uiaElem)
				logging.info('--------- 306 ---------')
				logTreeItem(node)
				logging.info('--------- 307 ---------')
				currNode = node.left
				logging.info('--------- 308 ---------')
				if currNode is None:
					continue
				logging.info('--------- 309 ---------')
				if not currNode.isLeafNode():
					self.createTree(currNode)
				logging.info('--------- 310 ---------')
				currNode = currNode.right
				while not currNode == None:
					logging.info('--------- 311 ---------')
					if not currNode.isLeafNode():
						self.createTree(currNode)
					logging.info('--------- 312 ---------')
					currNode = currNode.right
					logging.info('--------- 313 ---------')
				logging.info('--------- 314 ---------')
		logging.info('--------- 315 ---------')
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
	def getElemSubName(elem):
		textbox = findFirstElemByControlType(elem, UIAClient.UIA_TextControlTypeId, SCOPE_CHILDREN)
		text = textbox.CurrentName
		#del textbox
		#gc.collect()
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
		#del desktop, rrte, process
		#gc.collect()

# It's logic tree, not control view tree in ui automation.
class TreeNode:
	def __init__(self, elem, parent=None, left=None, right=None):
		logging.info('--------- 999 ---------')
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
		logging.info('--------- 888 ---------')
		return self.elem.select(uiaElem)
	
	def appendChildren(self, uiaElem):
		#logging.info('--------- 201 ---------')
		elems = self.elem.children(uiaElem)
		#logging.info('--------- 202 ---------')
		logging.info('Children count is %d' % len(elems))
		#logging.info('--------- 203 ---------')
		if len(elems) > 0:
			size = len(elems)
			logging.info('%d elements will be appended to [%s]' % (size, self.elem.label))
			curr = None
			for x in range(0, size):
				logging.info('--------- 207 ---------')
				node = TreeNode(elems[x])
				node.parent = self
				logging.info('--------- 208 ---------')
				if x == 0:
					logging.info('--------- 210 ---------')
					self.left = node
					curr = self.left
				else :
					logging.info('--------- 211 ---------')
					curr.right = node
					curr = curr.right
			'''
			#logging.info('--------- 204 ---------')
			self.left = TreeNode(elems[0], self)
			#logging.info('--------- 205 ---------')
			currNode = self.left
			#logging.info('--------- 206 ---------')
			for x in range(1, len(elems)):
				logging.info('--------- 207 ---------')
				node = TreeNode(elems[x], self)
				logging.info('--------- 208 ---------')
				currNode.right = node
				logging.info('--------- 209 ---------')
				del node
				logging.info('--------- 210 ---------')
				currNode = currNode.right
			#logging.info('--------- 211 ---------')
			'''

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
	
	def createString(self, uiaElem):
		assert self.isString(uiaElem)
		label = RRTE.getElemSubName(uiaElem)
		return RString(label)
	
	def createDate(self, uiaElem):
		assert self.isDate(uiaElem)
		label = RRTE.getElemSubName(uiaElem)
		return RDate(label)
	
	def createTime(self, uiaElem):
		assert self.isTime(uiaElem)
		label = RRTE.getElemSubName(uiaElem)
		return RTime(label)
	
	def createNumeric(self, uiaElem):
		assert self.isNumeric(uiaElem)
		label = RRTE.getElemSubName(uiaElem)
		return RNumeric(label)
	
	def createEnum(self, uiaElem):
		assert self.isEnum(uiaElem)
		label = RRTE.getElemSubName(uiaElem)
		return REnum(label)
	
	def createBitEnum(self, uiaElem):
		assert self.isBitEnum(uiaElem)
		group = findFirstElemByControlType(uiaElem, UIAClient.UIA_GroupControlTypeId)
		label = RRTE.getElemSubName(group)
		#del group
		#gc.collect()
		return RBitEnum(label)
		
	def createParam(self, uiaElem):
		assert isCustom(uiaElem)
		if self.isEnum(uiaElem):
			logging.info('--------- 071 ---------')
			return self.createEnum(uiaElem)
		elif self.isString(uiaElem):
			logging.info('--------- 072 ---------')
			return self.createString(uiaElem)
		elif self.isNumeric(uiaElem):
			logging.info('--------- 073 ---------')
			return self.createNumeric(uiaElem)
		elif self.isBitEnum(uiaElem):
			logging.info('--------- 074 ---------')
			return self.createBitEnum(uiaElem)
		elif self.isDate(uiaElem):
			logging.info('--------- 075 ---------')
			return self.createDate(uiaElem)
		elif self.isTime(uiaElem):
			logging.info('--------- 076 ---------')
			return self.createTime(uiaElem)
			
	def createPage(self, uiaElem):
		assert isTab(uiaElem)
		logging.info('--------- 061 ---------')
		#pdb.set_trace()
		uias = findAllElemByControlType(uiaElem, UIAClient.UIA_TabItemControlTypeId, SCOPE_CHILDREN)
		logging.info('--------- 062 ---------')
		pages = []
		logging.info('Page count is %d' % uias.Length)
		logging.info('--------- 063 ---------')
		for x in range(0, uias.Length):
			logging.info('--------- 064 ---------')
			#logging.info('########### 02 ###########')
			item = uias.GetElement(x)
			logging.info('--------- 065 ---------')
			#if item.CurrentName == 'Condensed status map':
			#	continue
			page = RPage(item.CurrentName)
			logging.info('--------- 066 ---------')
			page.ctrlType = 'TabItem'
			logging.info('--------- 067 ---------')
			#page.rectangle = item.CurrentBoundingRectangle
			pages.append(page)
			logging.info('--------- 068 ---------')
			#del item, page
			#gc.collect()
		#del uias
		#gc.collect()
		logging.info('--------- 069 ---------')
		return pages
	
	def children(self, uiaElem):
		#pdb.set_trace()
		logging.info('--------- 011 ---------')
		if isPane(uiaElem) or isTabItem(uiaElem) or isGroup(uiaElem):
			logging.info('--------- 012 ---------')
			#all = findAllElem4ORCond(uiaElem, UIAClient.UIA_CustomControlTypeId, UIAClient.UIA_ButtonControlTypeId, UIAClient.UIA_GroupControlTypeId, UIAClient.UIA_TabControlTypeId, UIAClient.UIA_ControlTypePropertyId, SCOPE_CHILDREN)
			all = findAllElem(uiaElem, True, UIAClient.UIA_IsEnabledPropertyId, SCOPE_CHILDREN)
			logging.info('--------- 013 ---------')
			set = []
			logging.info('--------- 014 ---------')
			#for item in uias:
			for x in range(0, all.Length):
				logging.info('--------- 015 ---------')
				#logging.info('########### 03 ###########')
				item = all.GetElement(x)
				logging.info('--------- 016 ---------')
				if isCustom(item): # variable(others, Enum, BitEnum)
					logging.info('--------- 017 ---------')
					elem = self.createParam(item)
					logging.info('--------- 018 ---------')
					elem.ctrlType = 'Custom'
					logging.info('--------- 019 ---------')
					#elem.rectangle = item.CurrentBoundingRectangle
					set.append(elem)
					logging.info('--------- 020 ---------')
					#del elem
				elif isButton(item): # method
					logging.info('--------- 021 ---------')
					elem = RMethod(RRTE.getElemSubName(item))
					logging.info('--------- 022 ---------')
					elem.ctrlType = 'Button'
					logging.info('--------- 023 ---------')
					#elem.rectangle = item.CurrentBoundingRectangle
					set.append(elem)
					logging.info('--------- 024 ---------')
					#del elem
				elif isGroup(item): # group
					logging.info('--------- 025 ---------')
					elem = RGroup(item.CurrentName)
					logging.info('--------- 026 ---------')
					elem.ctrlType = 'Group'
					logging.info('--------- 027 ---------')
					#elem.rectangle = item.CurrentBoundingRectangle
					set.append(elem)
					logging.info('--------- 028 ---------')
					#del elem
				elif isTab(item): # page
					logging.info('--------- 029 ---------')
					tabs = self.createPage(item)
					logging.info('--------- 030 ---------')
					set.extend(tabs)
					logging.info('--------- 031 ---------')
					#del tabs
				else:
					logging.info('Ignore one element')
				#del item
				#gc.collect()
			#del all
			#gc.collect()
			logging.info('--------- 032 ---------')
			return set
		else:
			logging.info('--------- 041 ---------')
			all = findAllElemByControlType(uiaElem, UIAClient.UIA_TreeItemControlTypeId, SCOPE_CHILDREN)
			logging.info('--------- 042 ---------')
			set = []
			logging.info('--------- 043 ---------')
			for x in range(0, all.Length):
				logging.info('--------- 044 ---------')
				item = all.GetElement(x)
				logging.info('--------- 045 ---------')
				name = RRTE.getElemSubName(item)
				logging.info('--------- 046 ---------')
				if isTreeLeaf(item):
					logging.info('--------- 047 ---------')
					elem = RWindow(name)
				else:
					logging.info('--------- 048 ---------')
					elem = RMenu(name)
				logging.info('--------- 049 ---------')
				elem.ctrlType = 'TreeItem'
				#elem.rectangle = item.CurrentBoundingRectangle
				logging.info('--------- 050 ---------')
				set.append(elem)
				#del elem, item
				#gc.collect()
			#del all
			#gc.collect()
			logging.info('--------- 051 ---------')
			return set

class RRoot(RElement):
	def select(self, uiaElem):
		'''
		logging.info('--------- 151 ---------')
		assert isUIAElem(uiaElem)
		# wait dialog close
		desktop = IUIA.GetRootElement()
		logging.info('--------- 152 ---------')
		assert isUIAElem(desktop)
		internal = findFirstElemByAutomationId(desktop, 'DD_ExplorerView')
		logging.info('--------- 153 ---------')
		while not isUIAElem(internal):
			time.sleep(1.5)
			internal = findFirstElemByAutomationId(DesktopRoot, 'DD_ExplorerView')
		'''
		time.sleep(1)
		# get main uia element
		logging.info('--------- 154 ---------')
		all = findAllElemByControlType(uiaElem, UIAClient.UIA_CustomControlTypeId, SCOPE_CHILDREN)
		logging.info('--------- 155 ---------')
		workRoot = all.GetElement(all.Length-1)
		logging.info('--------- 156 ---------')
		assert isUIAElem(workRoot)
		topTAB = findFirstElemByName(workRoot, 'Fdi.Client.DeviceUi.ViewModel.DeviceUiHostContainerItemViewModel')
		logging.info('--------- 157 ---------')
		assert isUIAElem(topTAB)
		topTABX = findFirstElemByName(topTAB, 'X')
		logging.info('--------- 158 ---------')
		assert isUIAElem(topTABX)
		topRoot = findNextSiblingElem(topTABX)
		logging.info('--------- 159 ---------')
		assert isUIAElem(topRoot)
		# release memery
		#del desktop, internal, all, workRoot, topTAB, topTABX
		#gc.collect()
		# return top root(right side)
		return topRoot
	
	def children(self, uiaElem):
		set = []
		logging.info('--------- 160 ---------')
		# get offline root menu item
		offline = findFirstElemBySubText(uiaElem, 'Offline root menu')
		logging.info('--------- 161 ---------')
		assert isUIAElem(offline)
		menu = RRootMenu('Offline root menu')
		logging.info('--------- 162 ---------')
		menu.ctrlType = 'Button'
		#menu.rectangle = offline.CurrentBoundingRectangle
		#set.append(menu) # for debug
		# get online root menu items
		onlineRoot = findFirstElemByAutomationId(uiaElem, 'OnlineParameters')
		logging.info('--------- 163 ---------')
		assert isUIAElem(onlineRoot)
		pane = findFirstElemByControlType(onlineRoot, UIAClient.UIA_PaneControlTypeId)
		logging.info('--------- 164 ---------')
		assert isUIAElem(pane)
		all = findAllElemByControlType(pane, UIAClient.UIA_ButtonControlTypeId, SCOPE_CHILDREN)
		logging.info('--------- 165 ---------')
		for x in range(0, all.Length):
			logging.info('--------- 166 ---------')
			item = all.GetElement(x)
			logging.info('--------- 167 ---------')
			label = RRTE.getElemSubName(item)
			logging.info('--------- 168 ---------')
			#if label == 'Device root menu' or label == 'Online' or label == 'Diagnostic root menu':
			if label == 'Online':
				continue
			logging.info('--------- 169 ---------')
			elem = RRootMenu(label)
			logging.info('--------- 170 ---------')
			elem.ctrlType = 'Button'
			#elem.rectangle = item.CurrentBoundingRectangle
			set.append(elem)
			#del item, elem
			#gc.collect()
			logging.info('--------- 171 ---------')
		#del offline, menu, onlineRoot, pane
		#gc.collect()
		logging.info('--------- 172 ---------')
		return set

class RRootMenu(RElement):
	def __init__(self, label):
		super(RRootMenu, self).__init__(label)
		self.current = None
		
	def select(self, uiaElem):
		logging.info('--------- 131 ---------')
		assert isUIAElem(uiaElem)
		# search root menu button
		if not self.label == 'Offline root menu':
			logging.info('--------- 132 ---------')
			onlineRoot = findFirstElemByAutomationId(uiaElem, 'OnlineParameters')
			logging.info('--------- 133 ---------')
			assert isUIAElem(onlineRoot)
			pane = findFirstElemByControlType(onlineRoot, UIAClient.UIA_PaneControlTypeId)
			logging.info('--------- 134 ---------')
			assert isUIAElem(pane)
			btn = findFirstElemBySubText(pane, self.label)
			logging.info('--------- 135 ---------')
			#del onlineRoot, pane
		else:
			btn = findFirstElemBySubText(uiaElem, self.label)
			logging.info('--------- 136 ---------')
		# push root menu button
		assert isUIAElem(btn)
		logging.info('--------- 137 ---------')
		if not self.label == self.current:
			logging.info('--------- 138 ---------')
			pushButton(btn)
			logging.info('--------- 139 ---------')
			self.current = self.label
			#RRTE.waitDialogClose()
			time.sleep(8)
		logging.info('--------- 140 ---------')
		explorer = findFirstElemByAutomationId(uiaElem, 'DD_ExplorerView')
		logging.info('--------- 141 ---------')
		assert isUIAElem(explorer)
		elem = findNextSiblingElem(explorer)
		logging.info('--------- 142 ---------')
		#del btn, explorer
		#gc.collect()
		assert isUIAElem(elem)
		logging.info('--------- 143 ---------')
		return elem
	
class RMenu(RElement):
	def select(self, uiaElem):
		logging.info('--------- 101 ---------')
		assert isUIAElem(uiaElem)
		#pdb.set_trace()
		tree = findFirstElemBySubText(uiaElem, self.label)
		logging.info('--------- 102 ---------')
		assert isUIAElem(tree)
		expandTree(tree)
		logging.info('--------- 103 ---------')
		#del tree
		#gc.collect()
		time.sleep(1)
		return tree

class RWindow(RElement):
	def select(self, uiaElem):
		logging.info('--------- 106 ---------')
		assert isUIAElem(uiaElem)
		leaf = findFirstElemBySubText(uiaElem, self.label)
		logging.info('--------- 107 ---------')
		assert isUIAElem(leaf)
		pushLeaf(leaf)
		logging.info('--------- 108 ---------')
		time.sleep(2)
		curr = leaf
		while not isTree(curr):
			logging.info('--------- 109 ---------')
			curr = findParentElem(curr)
			assert isUIAElem(curr)
		pane = findNextSiblingElem(curr)
		logging.info('--------- 110 ---------')
		#del leaf, curr
		#gc.collect()
		assert isUIAElem(pane)
		logging.info('--------- 111 ---------')
		return pane

class RPage(RElement):
	def select(self, uiaElem):
		logging.info('--------- 115 ---------')
		assert isUIAElem(uiaElem)
		#pdb.set_trace()
		tabs = findFirstElemByControlType(uiaElem, UIAClient.UIA_TabControlTypeId, SCOPE_CHILDREN)
		logging.info('--------- 116 ---------')
		tab = findFirstElemByName(tabs, self.label)
		logging.info('--------- 117 ---------')
		assert isUIAElem(tab)
		selectTab(tab)
		logging.info('--------- 118 ---------')
		#del tabs
		#gc.collect()
		time.sleep(1)
		logging.info('--------- 119 ---------')
		return tab

class RGroup(RElement):
	def select(self, uiaElem):
		logging.info('--------- 122 ---------')
		assert isUIAElem(uiaElem)
		#pdb.set_trace()
		group = findFirstElemByName(uiaElem, self.label, SCOPE_CHILDREN)
		logging.info('--------- 123 ---------')
		time.sleep(1)
		assert isUIAElem(group)
		logging.info('--------- 124 ---------')
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
	logging.info('--------- 001 ---------')
	desktop = IUIA.GetRootElement()
	console = findFirstElemByAutomationId(desktop, 'Console Window')
	all = findAllElem(console, '', UIAClient.UIA_ClassNamePropertyId, SCOPE_CHILDREN)
	logging.info('--------- 002 ---------')
	return all
	#assert isUIAElem(desktop)

if __name__ == '__main__':
	#pdb.set_trace()
	logging.basicConfig(level = logging.DEBUG)
	'''
	logging.info('--------- 011 ---------')
	all = test()
	set = []
	for x in range(0, all.Length):
		logging.info('--------- 012 ---------')
		item = all.GetElement(x)
		logging.info('--------- 013 ---------')
		label = item.CurrentAutomationId
		logging.info('--------- 014 ---------')
		elem = RMethod(label)
		elem.ctrlType = 'Button'
		set.append(elem)
		logging.info('--------- 017 ---------')
	logging.info('--------- 018 ---------')
	pdb.set_trace()
	'''
	top = RRoot('root')
	top.ctrlType = ''
	#top.rectangle = None
	root = TreeNode(top)
	rrte = RRTE(root)
	#pdb.set_trace()
	rrte.startUp()
	rrte.createTree(rrte.root)