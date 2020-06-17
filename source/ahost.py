import pdb
import logging
#import os
#import sys
import time
import subprocess
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
		assert not root.isVariableNode()
		logging.info('--------- 001 ---------')
		path = root.getPath()
		logging.info('--------- 002 ---------')
		uiaElem = self.host
		for node in path:
			logging.info('--------- 003 ---------')
			uiaElem = node.select(uiaElem)
			logging.info('--------- 004 ---------')
			if node.isEqual(root):
				logging.info('--------- 005 ---------')
				node.appendChildren(uiaElem)
				logging.info('--------- 006 ---------')
				logTreeItem(node)
				logging.info('--------- 007 ---------')
				currNode = node.left
				if currNode is None:
					continue
				if not currNode.isVariableNode():
					logging.info('--------- 008 ---------')
					self.createTree(currNode)
				currNode = currNode.right
				logging.info('--------- 009 ---------')
				while not currNode == None:
					logging.info('--------- 010 ---------')
					if not currNode.isVariableNode():
						logging.info('--------- 011 ---------')
						self.createTree(currNode)
						logging.info('--------- 012 ---------')
					currNode = currNode.right
				logging.info('--------- 013 ---------')
		logging.info('--------- 014 ---------')
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
		time.sleep(1)
		desktop = IUIA.GetRootElement()
		assert isUIAElem(desktop)
		rrte = findFirstElemByName(desktop, 'Reference Run-time Environment', SCOPE_CHILDREN)
		assert isUIAElem(rrte)
		process = findFirstElemByControlType(rrte, UIAClient.UIA_WindowControlTypeId, SCOPE_CHILDREN)
		while isUIAElem(process):
			time.sleep(2.5)
			process = findFirstElemByControlType(rrte, UIAClient.UIA_WindowControlTypeId, SCOPE_CHILDREN)
		time.sleep(5)

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
	
	def isVariableNode(self):
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
		logging.info('--------- 051 ---------')
		return self.elem.select(uiaElem)
		logging.info('--------- 052 ---------')
	
	def appendChildren(self, uiaElem):
		assert isUIAElem(uiaElem)
		logging.info('--------- 101 ---------')
		elems = self.elem.children(uiaElem)
		logging.info('--------- 102 ---------')
		elemNum = len(elems)
		logging.info('Children count is %d' % elemNum)
		if elemNum == 0: return
		curr = None
		for x in range(0, elemNum):
			logging.info('--------- 103 ---------')
			elem = elems[x]
			node = TreeNode(elem, self)
			logging.info('--------- 104 ---------')
			if x == 0:
				logging.info('--------- 105 ---------')
				self.left = node
				curr = self.left
			else:
				logging.info('--------- 106 ---------')
				curr.right = node
				curr = curr.right
			logging.info('--------- 107 ---------')
		logging.info('--------- 108 ---------')

class Element: # abstract class
	def __init__(self, label):
		self.label		= label
		self.ctrlType	= ''
		self.rectangle	= None
	
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
			logging.info('--------- 201 ---------')
			return self.createEnum(uiaElem)
		elif self.isString(uiaElem):
			logging.info('--------- 202 ---------')
			return self.createString(uiaElem)
		elif self.isNumeric(uiaElem):
			logging.info('--------- 203 ---------')
			return self.createNumeric(uiaElem)
		elif self.isBitEnum(uiaElem):
			logging.info('--------- 204 ---------')
			return self.createBitEnum(uiaElem)
		elif self.isDate(uiaElem):
			logging.info('--------- 205 ---------')
			return self.createDate(uiaElem)
		elif self.isTime(uiaElem):
			logging.info('--------- 206 ---------')
			return self.createTime(uiaElem)
			
	def createPage(self, uiaElem):
		assert isTab(uiaElem)
		logging.info('--------- 211 ---------')
		uias = findAllElemByControlType(uiaElem, UIAClient.UIA_TabItemControlTypeId, SCOPE_CHILDREN)
		logging.info('--------- 212 ---------')
		pages = []
		#logging.info('Page count is %d' % uias.Length)
		for x in range(0, uias.Length):
			logging.info('--------- 213 ---------')
			item = uias.GetElement(x)
			logging.info('--------- 214 ---------')
			page = RPage(item.CurrentName)
			logging.info('--------- 215 ---------')
			page.ctrlType = 'TabItem'
			pages.append(page)
			logging.info('--------- 216 ---------')
		logging.info('--------- 217 ---------')
		return pages
	
	def children(self, uiaElem):
		assert isUIAElem(uiaElem)
		logging.info('--------- 220 ---------')
		if isPane(uiaElem) or isTabItem(uiaElem) or isGroup(uiaElem):
			logging.info('--------- 221 ---------')
			#all = findAllElem4ORCond(uiaElem, UIAClient.UIA_CustomControlTypeId, UIAClient.UIA_ButtonControlTypeId, UIAClient.UIA_GroupControlTypeId, UIAClient.UIA_TabControlTypeId, UIAClient.UIA_ControlTypePropertyId, SCOPE_CHILDREN) # Please attention here!! It will make release IUnKnown object.
			all = findAllElem(uiaElem, True, UIAClient.UIA_IsEnabledPropertyId, SCOPE_CHILDREN)
			logging.info('--------- 222 ---------')
			set = []
			for x in range(0, all.Length):
				logging.info('--------- 223 ---------')
				item = all.GetElement(x)
				if isCustom(item): # variable(others, Enum, BitEnum)
					logging.info('--------- 224 ---------')
					elem = self.createParam(item)
					logging.info('--------- 225 ---------')
					elem.ctrlType = 'Custom'
					elem.rectangle = item.CurrentBoundingRectangle
					set.append(elem)
					logging.info('--------- 226 ---------')
				elif isButton(item): # method
					logging.info('--------- 227 ---------')
					elem = RMethod(RRTE.getElemSubName(item))
					logging.info('--------- 228 ---------')
					elem.ctrlType = 'Button'
					elem.rectangle = item.CurrentBoundingRectangle
					set.append(elem)
					logging.info('--------- 229 ---------')
				elif isGroup(item): # group
					logging.info('--------- 230 ---------')
					elem = RGroup(item.CurrentName)
					logging.info('--------- 231 ---------')
					elem.ctrlType = 'Group'
					elem.rectangle = item.CurrentBoundingRectangle
					set.append(elem)
					logging.info('--------- 232 ---------')
				elif isTab(item): # page
					logging.info('--------- 233 ---------')
					tabs = self.createPage(item)
					logging.info('--------- 234 ---------')
					set.extend(tabs)
					logging.info('--------- 235 ---------')
				else:
					logging.info('--------- 236 ---------')
					#pass
					logging.info('Ignore one element')
			del all
			return set
		else:
			logging.info('--------- 240 ---------')
			all = findAllElemByControlType(uiaElem, UIAClient.UIA_TreeItemControlTypeId, SCOPE_CHILDREN)
			logging.info('--------- 241 ---------')
			set = []
			for x in range(0, all.Length):
				logging.info('--------- 242 ---------')
				item = all.GetElement(x)
				logging.info('--------- 243 ---------')
				name = RRTE.getElemSubName(item)
				logging.info('--------- 244 ---------')
				if isTreeLeaf(item):
					logging.info('--------- 245 ---------')
					elem = RWindow(name)
				else:
					logging.info('--------- 246 ---------')
					elem = RMenu(name)
				logging.info('--------- 247 ---------')
				elem.ctrlType = 'TreeItem'
				elem.rectangle = item.CurrentBoundingRectangle
				set.append(elem)
				logging.info('--------- 248 ---------')
			logging.info('--------- 249 ---------')
			return set

class RRoot(RElement):
	def select(self, uiaElem):
		logging.info('--------- 301 ---------')
		assert isUIAElem(uiaElem)
		'''
		assert isUIAElem(uiaElem)
		# wait dialog close
		desktop = IUIA.GetRootElement()
		assert isUIAElem(desktop)
		internal = findFirstElemByAutomationId(desktop, 'DD_ExplorerView')
		while not isUIAElem(internal):
			time.sleep(1.5)
			internal = findFirstElemByAutomationId(DesktopRoot, 'DD_ExplorerView')
		'''
		time.sleep(1)
		# get main uia element
		all = findAllElemByControlType(uiaElem, UIAClient.UIA_CustomControlTypeId, SCOPE_CHILDREN)
		logging.info('--------- 302 ---------')
		workRoot = all.GetElement(all.Length-1)
		logging.info('--------- 303 ---------')
		assert isUIAElem(workRoot)
		topTAB = findFirstElemByName(workRoot, 'Fdi.Client.DeviceUi.ViewModel.DeviceUiHostContainerItemViewModel')
		logging.info('--------- 304 ---------')
		assert isUIAElem(topTAB)
		topTABX = findFirstElemByName(topTAB, 'X')
		logging.info('--------- 305 ---------')
		assert isUIAElem(topTABX)
		topRoot = findNextSiblingElem(topTABX)
		logging.info('--------- 306 ---------')
		assert isUIAElem(topRoot)
		# return top root(right side)
		return topRoot
	
	def children(self, uiaElem):
		logging.info('--------- 251 ---------')
		assert isUIAElem(uiaElem)
		set = []
		# get offline root menu item
		offline = findFirstElemBySubText(uiaElem, 'Offline root menu')
		logging.info('--------- 253 ---------')
		assert isUIAElem(offline)
		menu = RRootMenu('Offline root menu')
		logging.info('--------- 254 ---------')
		menu.ctrlType = 'Button'
		menu.rectangle = offline.CurrentBoundingRectangle
		set.append(menu) # for debug
		logging.info('--------- 255 ---------')
		# get online root menu items
		onlineRoot = findFirstElemByAutomationId(uiaElem, 'OnlineParameters')
		logging.info('--------- 256 ---------')
		assert isUIAElem(onlineRoot)
		pane = findFirstElemByControlType(onlineRoot, UIAClient.UIA_PaneControlTypeId)
		logging.info('--------- 257 ---------')
		assert isUIAElem(pane)
		all = findAllElemByControlType(pane, UIAClient.UIA_ButtonControlTypeId, SCOPE_CHILDREN)
		logging.info('--------- 258 ---------')
		for x in range(0, all.Length):
			logging.info('--------- 259 ---------')
			item = all.GetElement(x)
			label = RRTE.getElemSubName(item)
			logging.info('--------- 260 ---------')
			if label == 'Online': continue # TODO
			#if label == 'Device root menu': continue # TODO
			#if label == 'Diagnostic root menu': continue # TODO
			#if label == 'Maintenance root menu': continue # TODO
			#if label == 'Process variables root menu': continue # TODO
			elem = RRootMenu(label)
			logging.info('--------- 261 ---------')
			elem.ctrlType = 'Button'
			elem.rectangle = item.CurrentBoundingRectangle
			set.append(elem)
			logging.info('--------- 262 ---------')
		return set

class RRootMenu(RElement):
	def __init__(self, label):
		super(RRootMenu, self).__init__(label)
		self.current = None
		
	def select(self, uiaElem):
		logging.info('--------- 311 ---------')
		assert isUIAElem(uiaElem)
		# search root menu button
		if not self.label == 'Offline root menu':
			logging.info('--------- 312 ---------')
			onlineRoot = findFirstElemByAutomationId(uiaElem, 'OnlineParameters')
			logging.info('--------- 313 ---------')
			assert isUIAElem(onlineRoot)
			pane = findFirstElemByControlType(onlineRoot, UIAClient.UIA_PaneControlTypeId)
			logging.info('--------- 314 ---------')
			assert isUIAElem(pane)
			btn = findFirstElemBySubText(pane, self.label)
			logging.info('--------- 315 ---------')
		else:
			logging.info('--------- 316 ---------')
			btn = findFirstElemBySubText(uiaElem, self.label)
			logging.info('--------- 317 ---------')
		# push root menu button
		assert isUIAElem(btn)
		logging.info('--------- 318 ---------')
		if not self.label == self.current:
			logging.info('--------- 319 ---------')
			pushButton(btn)
			logging.info('--------- 320 ---------')
			self.current = self.label
			RRTE.waitDialogClose()
			logging.info('--------- 321 ---------')
			#time.sleep(4)
		logging.info('--------- 322 ---------')
		explorer = findFirstElemByAutomationId(uiaElem, 'DD_ExplorerView')
		assert isUIAElem(explorer)
		logging.info('--------- 323 ---------')
		elem = findNextSiblingElem(explorer)
		logging.info('--------- 324 ---------')
		assert isUIAElem(elem)
		return elem
	
class RMenu(RElement):
	def select(self, uiaElem):
		logging.info('--------- 331 ---------')
		assert isUIAElem(uiaElem)
		tree = findFirstElemBySubText(uiaElem, self.label)
		logging.info('--------- 332 ---------')
		assert isUIAElem(tree)
		expandTree(tree)
		logging.info('--------- 333 ---------')
		time.sleep(2)
		return tree

class RWindow(RElement):
	def select(self, uiaElem):
		logging.info('--------- 341 ---------')
		assert isUIAElem(uiaElem)
		leaf = findFirstElemBySubText(uiaElem, self.label)
		logging.info('--------- 342 ---------')
		assert isUIAElem(leaf)
		pushLeaf(leaf)
		logging.info('--------- 343 ---------')
		time.sleep(2)
		curr = leaf
		while not isTree(curr):
			logging.info('--------- 343 ---------')
			curr = findParentElem(curr)
			logging.info('--------- 344 ---------')
			assert isUIAElem(curr)
		logging.info('--------- 345 ---------')
		pane = findNextSiblingElem(curr)
		logging.info('--------- 346 ---------')
		assert isUIAElem(pane)
		return pane

class RPage(RElement):
	def select(self, uiaElem):
		logging.info('--------- 351 ---------')
		assert isUIAElem(uiaElem)
		#pdb.set_trace()
		tabs = findFirstElemByControlType(uiaElem, UIAClient.UIA_TabControlTypeId, SCOPE_CHILDREN)
		logging.info('--------- 352 ---------')
		tab = findFirstElemByName(tabs, self.label)
		logging.info('--------- 353 ---------')
		assert isUIAElem(tab)
		selectTab(tab)
		logging.info('--------- 354 ---------')
		time.sleep(2)
		return tab

class RGroup(RElement):
	def select(self, uiaElem):
		logging.info('--------- 361 ---------')
		assert isUIAElem(uiaElem)
		group = findFirstElemByName(uiaElem, self.label, SCOPE_CHILDREN)
		logging.info('--------- 362 ---------')
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

if __name__ == '__main__':
	#pdb.set_trace()
	logging.basicConfig(level = logging.INFO)
	top = RRoot('root')
	top.ctrlType = ''
	top.rectangle = None
	root = TreeNode(top)
	rrte = RRTE(root)
	rrte.startUp()
	rrte.createTree(rrte.root)
