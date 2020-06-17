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
		path = root.getPath()
		uiaElem = self.host
		for node in path:
			uiaElem = node.select(uiaElem)
			if node.isEqual(root):
				node.appendChildren(uiaElem)
				logTreeItem(node)
				currNode = node.left
				if currNode is None:
					continue
				if not currNode.isVariableNode():
					self.createTree(currNode)
				currNode = currNode.right
				while not currNode == None:
					if not currNode.isVariableNode():
						self.createTree(currNode)
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
		return self.elem.select(uiaElem)
	
	def appendChildren(self, uiaElem):
		assert isUIAElem(uiaElem)
		elems = self.elem.children(uiaElem)
		elemNum = len(elems)
		#logging.info('%d child nodes will insert tree under the [%s].' % (elemNum, self.elem.label))
		if elemNum == 0: return
		curr = None
		for x in range(0, elemNum):
			logging.info('Add the child[%d] under the node [%s].' % (x+1, self.elem.label))
			elem = elems[x]
			node = TreeNode(elem, self)
			if elem == elems[0]:
				self.left = node
				curr = self.left
			else:
				curr.right = node
				curr = curr.right

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
		uias = findAllElemByControlType(uiaElem, UIAClient.UIA_TabItemControlTypeId, SCOPE_CHILDREN)
		pages = []
		#logging.info('Page count is %d' % uias.Length)
		for x in range(0, uias.Length):
			item = uias.GetElement(x)
			page = RPage(item.CurrentName)
			page.ctrlType = 'TabItem'
			pages.append(page)
		return pages
	
	def children(self, uiaElem):
		assert isUIAElem(uiaElem)
		if isPane(uiaElem) or isTabItem(uiaElem) or isGroup(uiaElem):
			#all = findAllElem4ORCond(uiaElem, UIAClient.UIA_CustomControlTypeId, UIAClient.UIA_ButtonControlTypeId, UIAClient.UIA_GroupControlTypeId, UIAClient.UIA_TabControlTypeId, UIAClient.UIA_ControlTypePropertyId, SCOPE_CHILDREN) # Please attention here!! It will make release IUnKnown object.
			all = findAllElem(uiaElem, True, UIAClient.UIA_IsEnabledPropertyId, SCOPE_CHILDREN)
			set = []
			for x in range(0, all.Length):
				item = all.GetElement(x)
				if isCustom(item): # variable(others, Enum, BitEnum)
					elem = self.createParam(item)
					elem.ctrlType = 'Custom'
					elem.rectangle = item.CurrentBoundingRectangle
					set.append(elem)
				elif isButton(item): # method
					elem = RMethod(RRTE.getElemSubName(item))
					elem.ctrlType = 'Button'
					elem.rectangle = item.CurrentBoundingRectangle
					set.append(elem)
				elif isGroup(item): # group
					elem = RGroup(item.CurrentName)
					elem.ctrlType = 'Group'
					elem.rectangle = item.CurrentBoundingRectangle
					set.append(elem)
				elif isTab(item): # page
					tabs = self.createPage(item)
					set.extend(tabs)
				else:
					#logging.info('Ignore one element')
					pass
			return set
		else:
			all = findAllElemByControlType(uiaElem, UIAClient.UIA_TreeItemControlTypeId, SCOPE_CHILDREN)
			set = []
			for x in range(0, all.Length):
				item = all.GetElement(x)
				name = RRTE.getElemSubName(item)
				if isTreeLeaf(item):
					elem = RWindow(name)
				else:
					elem = RMenu(name)
				elem.ctrlType = 'TreeItem'
				elem.rectangle = item.CurrentBoundingRectangle
				set.append(elem)
			return set

class RRoot(RElement):
	def select(self, uiaElem):
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
		workRoot = all.GetElement(all.Length-1)
		assert isUIAElem(workRoot)
		topTAB = findFirstElemByName(workRoot, 'Fdi.Client.DeviceUi.ViewModel.DeviceUiHostContainerItemViewModel')
		assert isUIAElem(topTAB)
		topTABX = findFirstElemByName(topTAB, 'X')
		assert isUIAElem(topTABX)
		topRoot = findNextSiblingElem(topTABX)
		assert isUIAElem(topRoot)
		# return top root(right side)
		return topRoot
	
	def children(self, uiaElem):
		assert isUIAElem(uiaElem)
		set = []
		# get offline root menu item
		offline = findFirstElemBySubText(uiaElem, 'Offline root menu')
		assert isUIAElem(offline)
		menu = RRootMenu('Offline root menu')
		menu.ctrlType = 'Button'
		menu.rectangle = offline.CurrentBoundingRectangle
		set.append(menu) # for debug
		# get online root menu items
		onlineRoot = findFirstElemByAutomationId(uiaElem, 'OnlineParameters')
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
		
	def select(self, uiaElem):
		assert isUIAElem(uiaElem)
		# search root menu button
		if not self.label == 'Offline root menu':
			onlineRoot = findFirstElemByAutomationId(uiaElem, 'OnlineParameters')
			assert isUIAElem(onlineRoot)
			pane = findFirstElemByControlType(onlineRoot, UIAClient.UIA_PaneControlTypeId)
			assert isUIAElem(pane)
			btn = findFirstElemBySubText(pane, self.label)
		else:
			btn = findFirstElemBySubText(uiaElem, self.label)
		# push root menu button
		assert isUIAElem(btn)
		if not self.label == self.current:
			pushButton(btn)
			self.current = self.label
			RRTE.waitDialogClose()
			#time.sleep(4)
		explorer = findFirstElemByAutomationId(uiaElem, 'DD_ExplorerView')
		assert isUIAElem(explorer)
		elem = findNextSiblingElem(explorer)
		assert isUIAElem(elem)
		return elem
	
class RMenu(RElement):
	def select(self, uiaElem):
		assert isUIAElem(uiaElem)
		tree = findFirstElemBySubText(uiaElem, self.label)
		assert isUIAElem(tree)
		expandTree(tree)
		time.sleep(2)
		return tree

class RWindow(RElement):
	def select(self, uiaElem):
		assert isUIAElem(uiaElem)
		leaf = findFirstElemBySubText(uiaElem, self.label)
		assert isUIAElem(leaf)
		pushLeaf(leaf)
		time.sleep(2)
		curr = leaf
		while not isTree(curr):
			curr = findParentElem(curr)
			assert isUIAElem(curr)
		pane = findNextSiblingElem(curr)
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
		time.sleep(2)
		return tab

class RGroup(RElement):
	def select(self, uiaElem):
		assert isUIAElem(uiaElem)
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

if __name__ == '__main__':
	#pdb.set_trace()
	logging.basicConfig(level = logging.DEBUG)
	top = RRoot('root')
	top.ctrlType = ''
	top.rectangle = None
	root = TreeNode(top)
	rrte = RRTE(root)
	rrte.startUp()
	rrte.createTree(rrte.root)
