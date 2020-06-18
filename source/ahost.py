import pdb
import logging
#import os
#import sys
import time
import subprocess
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
		assert not root == None
		assert not root.isLeafNode()
		logging.debug('--------- 301 ---------')
		path = root.getPath()
		logging.debug('--------- 302 ---------')
		uiaElem = self.host
		for node in path:
			logging.debug('--------- 303 ---------')
			uiaElem = node.select(uiaElem)
			logging.debug('--------- 304 ---------')
			if node.isEqual(root):
				logging.debug('--------- 305 ---------')
				node.appendChildren(uiaElem)
				logging.debug('--------- 306 ---------')
				logTreeItem(node)
				logging.debug('--------- 307 ---------')
				currNode = node.left
				logging.debug('--------- 308 ---------')
				if currNode is None:
					continue
				logging.debug('--------- 309 ---------')
				if not currNode.isLeafNode():
					self.createTree(currNode)
				logging.debug('--------- 310 ---------')
				currNode = currNode.right
				while not currNode == None:
					logging.debug('--------- 311 ---------')
					if not currNode.isLeafNode():
						self.createTree(currNode)
					logging.debug('--------- 312 ---------')
					currNode = currNode.right
					logging.debug('--------- 313 ---------')
				logging.debug('--------- 314 ---------')
		logging.debug('--------- 315 ---------')
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
		logging.debug('--------- 999 ---------')
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
		logging.debug('--------- 888 ---------')
		return self.elem.select(uiaElem)
	
	def appendChildren(self, uiaElem):
		elems = self.elem.children(uiaElem)
		logging.info('Children count is %d' % len(elems))
		if len(elems) > 0:
			size = len(elems)
			logging.info('%d elements will be appended to [%s]' % (size, self.elem.label))
			curr = None
			for x in range(0, size):
				logging.debug('--------- 207 ---------')
				node = TreeNode(elems[x])
				node.parent = self
				logging.debug('--------- 208 ---------')
				if x == 0:
					logging.debug('--------- 210 ---------')
					self.left = node
					curr = self.left
				else :
					logging.debug('--------- 211 ---------')
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
		return RBitEnum(label)
		
	def createParam(self, uiaElem):
		assert isCustom(uiaElem)
		if self.isEnum(uiaElem):
			logging.debug('--------- 071 ---------')
			return self.createEnum(uiaElem)
		elif self.isString(uiaElem):
			logging.debug('--------- 072 ---------')
			return self.createString(uiaElem)
		elif self.isNumeric(uiaElem):
			logging.debug('--------- 073 ---------')
			return self.createNumeric(uiaElem)
		elif self.isBitEnum(uiaElem):
			logging.debug('--------- 074 ---------')
			return self.createBitEnum(uiaElem)
		elif self.isDate(uiaElem):
			logging.debug('--------- 075 ---------')
			return self.createDate(uiaElem)
		elif self.isTime(uiaElem):
			logging.debug('--------- 076 ---------')
			return self.createTime(uiaElem)
			
	def createPage(self, uiaElem):
		assert isTab(uiaElem)
		logging.debug('--------- 061 ---------')
		uias = findAllElemByControlType(uiaElem, UIAClient.UIA_TabItemControlTypeId, SCOPE_CHILDREN)
		logging.debug('--------- 062 ---------')
		pages = []
		#logging.info('Page count is %d' % uias.Length)
		logging.debug('--------- 063 ---------')
		for x in range(0, uias.Length):
			logging.debug('--------- 064 ---------')
			item = uias.GetElement(x)
			logging.debug('--------- 065 ---------')
			#if item.CurrentName == 'Condensed status map':
			#	continue
			page = RPage(item.CurrentName)
			logging.debug('--------- 066 ---------')
			page.ctrlType = 'TabItem'
			logging.debug('--------- 067 ---------')
			#page.rectangle = item.CurrentBoundingRectangle
			pages.append(page)
			logging.debug('--------- 068 ---------')
		logging.debug('--------- 069 ---------')
		return pages
	
	def children(self, uiaElem):
		#pdb.set_trace()
		logging.debug('--------- 011 ---------')
		if isPane(uiaElem) or isTabItem(uiaElem) or isGroup(uiaElem):
			logging.debug('--------- 012 ---------')
			#all = findAllElem4ORCond(uiaElem, UIAClient.UIA_CustomControlTypeId, UIAClient.UIA_ButtonControlTypeId, UIAClient.UIA_GroupControlTypeId, UIAClient.UIA_TabControlTypeId, UIAClient.UIA_ControlTypePropertyId, SCOPE_CHILDREN)
			all = findAllElem(uiaElem, True, UIAClient.UIA_IsEnabledPropertyId, SCOPE_CHILDREN)
			logging.debug('--------- 013 ---------')
			set = []
			logging.debug('--------- 014 ---------')
			#for item in uias:
			for x in range(0, all.Length):
				logging.debug('--------- 015 ---------')
				item = all.GetElement(x)
				logging.debug('--------- 016 ---------')
				if isCustom(item): # variable(others, Enum, BitEnum)
					logging.debug('--------- 017 ---------')
					elem = self.createParam(item)
					logging.debug('--------- 018 ---------')
					elem.ctrlType = 'Custom'
					logging.debug('--------- 019 ---------')
					#elem.rectangle = item.CurrentBoundingRectangle
					set.append(elem)
					logging.debug('--------- 020 ---------')
				elif isButton(item): # method
					logging.debug('--------- 021 ---------')
					elem = RMethod(RRTE.getElemSubName(item))
					logging.debug('--------- 022 ---------')
					elem.ctrlType = 'Button'
					logging.debug('--------- 023 ---------')
					#elem.rectangle = item.CurrentBoundingRectangle
					set.append(elem)
					logging.debug('--------- 024 ---------')
				elif isGroup(item): # group
					logging.debug('--------- 025 ---------')
					elem = RGroup(item.CurrentName)
					logging.debug('--------- 026 ---------')
					elem.ctrlType = 'Group'
					logging.debug('--------- 027 ---------')
					#elem.rectangle = item.CurrentBoundingRectangle
					set.append(elem)
					logging.debug('--------- 028 ---------')
				elif isTab(item): # page
					logging.debug('--------- 029 ---------')
					tabs = self.createPage(item)
					logging.debug('--------- 030 ---------')
					set.extend(tabs)
					logging.debug('--------- 031 ---------')
				else:
					logging.info('Ignore one element')
			logging.debug('--------- 032 ---------')
			return set
		else:
			logging.debug('--------- 041 ---------')
			all = findAllElemByControlType(uiaElem, UIAClient.UIA_TreeItemControlTypeId, SCOPE_CHILDREN)
			logging.debug('--------- 042 ---------')
			set = []
			logging.debug('--------- 043 ---------')
			for x in range(0, all.Length):
				logging.debug('--------- 044 ---------')
				item = all.GetElement(x)
				logging.debug('--------- 045 ---------')
				name = RRTE.getElemSubName(item)
				logging.debug('--------- 046 ---------')
				if isTreeLeaf(item):
					logging.debug('--------- 047 ---------')
					elem = RWindow(name)
				else:
					logging.debug('--------- 048 ---------')
					elem = RMenu(name)
				logging.debug('--------- 049 ---------')
				elem.ctrlType = 'TreeItem'
				#elem.rectangle = item.CurrentBoundingRectangle
				logging.debug('--------- 050 ---------')
				set.append(elem)
			logging.debug('--------- 051 ---------')
			return set

class RRoot(RElement):
	def select(self, uiaElem):
		'''
		logging.debug('--------- 151 ---------')
		assert isUIAElem(uiaElem)
		# wait dialog close
		desktop = IUIA.GetRootElement()
		logging.debug('--------- 152 ---------')
		assert isUIAElem(desktop)
		internal = findFirstElemByAutomationId(desktop, 'DD_ExplorerView')
		logging.debug('--------- 153 ---------')
		while not isUIAElem(internal):
			time.sleep(1.5)
			internal = findFirstElemByAutomationId(DesktopRoot, 'DD_ExplorerView')
		'''
		time.sleep(1)
		# get main uia element
		logging.debug('--------- 154 ---------')
		all = findAllElemByControlType(uiaElem, UIAClient.UIA_CustomControlTypeId, SCOPE_CHILDREN)
		logging.debug('--------- 155 ---------')
		workRoot = all.GetElement(all.Length-1)
		logging.debug('--------- 156 ---------')
		assert isUIAElem(workRoot)
		topTAB = findFirstElemByName(workRoot, 'Fdi.Client.DeviceUi.ViewModel.DeviceUiHostContainerItemViewModel')
		logging.debug('--------- 157 ---------')
		assert isUIAElem(topTAB)
		topTABX = findFirstElemByName(topTAB, 'X')
		logging.debug('--------- 158 ---------')
		assert isUIAElem(topTABX)
		topRoot = findNextSiblingElem(topTABX)
		logging.debug('--------- 159 ---------')
		assert isUIAElem(topRoot)
		# return top root(right side)
		return topRoot
	
	def children(self, uiaElem):
		set = []
		logging.debug('--------- 160 ---------')
		# get offline root menu item
		offline = findFirstElemBySubText(uiaElem, 'Offline root menu')
		logging.debug('--------- 161 ---------')
		assert isUIAElem(offline)
		menu = RRootMenu('Offline root menu')
		logging.debug('--------- 162 ---------')
		menu.ctrlType = 'Button'
		#menu.rectangle = offline.CurrentBoundingRectangle
		set.append(menu)
		# get online root menu items
		onlineRoot = findFirstElemByAutomationId(uiaElem, 'OnlineParameters')
		logging.debug('--------- 163 ---------')
		assert isUIAElem(onlineRoot)
		pane = findFirstElemByControlType(onlineRoot, UIAClient.UIA_PaneControlTypeId)
		logging.debug('--------- 164 ---------')
		assert isUIAElem(pane)
		all = findAllElemByControlType(pane, UIAClient.UIA_ButtonControlTypeId, SCOPE_CHILDREN)
		logging.debug('--------- 165 ---------')
		for x in range(0, all.Length):
			logging.debug('--------- 166 ---------')
			item = all.GetElement(x)
			logging.debug('--------- 167 ---------')
			label = RRTE.getElemSubName(item)
			logging.debug('--------- 168 ---------')
			if label == 'Online': continue # TODO
			#if label == 'Device root menu': continue # TODO
			#if label == 'Diagnostic root menu': continue # TODO
			#if label == 'Maintenance root menu': continue # TODO
			#if label == 'Process variables root menu': continue # TODO
			logging.debug('--------- 169 ---------')
			elem = RRootMenu(label)
			logging.debug('--------- 170 ---------')
			elem.ctrlType = 'Button'
			#elem.rectangle = item.CurrentBoundingRectangle
			set.append(elem)
			logging.debug('--------- 171 ---------')
		logging.debug('--------- 172 ---------')
		return set

class RRootMenu(RElement):
	def __init__(self, label):
		super(RRootMenu, self).__init__(label)
		self.current = None
		
	def select(self, uiaElem):
		logging.debug('--------- 131 ---------')
		assert isUIAElem(uiaElem)
		# search root menu button
		if not self.label == 'Offline root menu':
			logging.debug('--------- 132 ---------')
			onlineRoot = findFirstElemByAutomationId(uiaElem, 'OnlineParameters')
			logging.debug('--------- 133 ---------')
			assert isUIAElem(onlineRoot)
			pane = findFirstElemByControlType(onlineRoot, UIAClient.UIA_PaneControlTypeId)
			logging.debug('--------- 134 ---------')
			assert isUIAElem(pane)
			btn = findFirstElemBySubText(pane, self.label)
			logging.debug('--------- 135 ---------')
		else:
			btn = findFirstElemBySubText(uiaElem, self.label)
			logging.debug('--------- 136 ---------')
		# push root menu button
		assert isUIAElem(btn)
		logging.debug('--------- 137 ---------')
		if not self.label == self.current:
			logging.debug('--------- 138 ---------')
			pushButton(btn)
			logging.debug('--------- 139 ---------')
			self.current = self.label
			#RRTE.waitDialogClose()
			time.sleep(8)
		logging.debug('--------- 140 ---------')
		explorer = findFirstElemByAutomationId(uiaElem, 'DD_ExplorerView')
		logging.debug('--------- 141 ---------')
		assert isUIAElem(explorer)
		elem = findNextSiblingElem(explorer)
		logging.debug('--------- 142 ---------')
		assert isUIAElem(elem)
		logging.debug('--------- 143 ---------')
		return elem
	
class RMenu(RElement):
	def select(self, uiaElem):
		logging.debug('--------- 101 ---------')
		assert isUIAElem(uiaElem)
		tree = findFirstElemBySubText(uiaElem, self.label)
		logging.debug('--------- 102 ---------')
		assert isUIAElem(tree)
		expandTree(tree)
		logging.debug('--------- 103 ---------')
		time.sleep(1)
		return tree

class RWindow(RElement):
	def select(self, uiaElem):
		logging.debug('--------- 106 ---------')
		assert isUIAElem(uiaElem)
		leaf = findFirstElemBySubText(uiaElem, self.label)
		logging.debug('--------- 107 ---------')
		assert isUIAElem(leaf)
		pushLeaf(leaf)
		logging.debug('--------- 108 ---------')
		time.sleep(2)
		curr = leaf
		while not isTree(curr):
			logging.debug('--------- 109 ---------')
			curr = findParentElem(curr)
			assert isUIAElem(curr)
		pane = findNextSiblingElem(curr)
		logging.debug('--------- 110 ---------')
		assert isUIAElem(pane)
		logging.debug('--------- 111 ---------')
		return pane

class RPage(RElement):
	def select(self, uiaElem):
		logging.debug('--------- 115 ---------')
		assert isUIAElem(uiaElem)
		tabs = findFirstElemByControlType(uiaElem, UIAClient.UIA_TabControlTypeId, SCOPE_CHILDREN)
		logging.debug('--------- 116 ---------')
		tab = findFirstElemByName(tabs, self.label)
		logging.debug('--------- 117 ---------')
		assert isUIAElem(tab)
		selectTab(tab)
		logging.debug('--------- 118 ---------')
		time.sleep(1)
		logging.debug('--------- 119 ---------')
		return tab

class RGroup(RElement):
	def select(self, uiaElem):
		logging.debug('--------- 122 ---------')
		assert isUIAElem(uiaElem)
		group = findFirstElemByName(uiaElem, self.label, SCOPE_CHILDREN)
		logging.debug('--------- 123 ---------')
		time.sleep(1)
		assert isUIAElem(group)
		logging.debug('--------- 124 ---------')
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