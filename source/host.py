import pdb
import logging
import os
import sys
import time
import subprocess
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
	logging.info('Parent\t: %s (%s)' % (node.elem.name, node.elem.ctrlType))
	if node.left:
		logging.info('Child[0]\t: %s (%s)' % (node.left.elem.name, node.left.elem.ctrlType))
	curr = node.left.right
	cnt = 1
	while not curr is None:
		logging.info('Child[%d]\t: %s (%s)' % (cnt, curr.elem.name, curr.elem.ctrlType))
		cnt += 1
		curr = curr.right

# It's EDD's host application's abstract class.
class Host:
	def __init__(self, root=None):
		self.root = root
		self.host = None
	
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
		#assert not root.elem.name == 'Online'
		assert not root.isLeafNode()
		path = root.getPath()
		#for item in path:
		#	logging.info(item.elem.name)
		# push button sequence to getting into current tree node
		uiaElem = self.host
		for item in path:
			uiaElem = item.select(uiaElem)
			if item.isEqual(root):
				item.appendChildren(uiaElem)
				logTreeItem(item)
				currNode = item.left
				if not currNode.isLeafNode(): self.createTree(currNode)
				currNode = currNode.right
				while not currNode == None:
					if not currNode.isLeafNode(): self.createTree(currNode)
					currNode = currNode.right
		time.sleep(2)
	
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
		time.sleep(10)
		logging.info('execCmd = %s' % execCmd)
		self.host = findFirstElemByName(DesktopRoot, 'Reference Run-time Environment', SCOPE_CHILDREN)
		assert isUIAElem(self.host)

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
			if node1.elem.name == node2.elem.name:
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
		#path.remove(self.root)
		path.reverse()
		return path
	
	def select(self, uiaElem):
		return self.elem.select(uiaElem)
	
	def appendChildren(self, uiaElem):
		elems = self.elem.children(uiaElem)
		if len(elems) > 0:
			self.left = TreeNode(elems[0], self)
			currNode = self.left
			for x in range(1, len(elems)):
				currNode.right = TreeNode(elems[x], self)
				currNode = currNode.right
'''
class Tree: # It's logic tree, not control view tree in ui automation 
	def __init__(self, root=None, curr=None):
		self.root = root
		self.curr = curr
'''

class Element: # abstract class
	def __init__(self, name):
		self.name = name
		self.ctrlType = None
		self.rectangle = None
	
	def select(self, uiaElem): # extend a node, for example, group, its processing may be inconsistent on different hosts
		pass
	
	def children(self, uiaElem):
		pass

class RElement(Element):
	def createParam(self, uiaElem):
		editbox = uia2.findFirstElem(uiaElem, 'Value', uia2.Client.UIA_AutomationIdPropertyId, scope=uia2.Client.TreeScope_Children)
		if not uia2.isUIAElem(editbox):
			group = uia2.findFirstElem(uiaElem, uia2.Client.UIA_GroupControlTypeId, uia2.Client.UIA_ControlTypePropertyId, scope=uia2.Client.TreeScope_Children)
			return BitEnum(uia2.getElemSubText(group))
		elif editbox.CurrentControlType == uia2.Client.UIA_EditControlTypeId:
			return Data(uia2.getElemSubText(uiaElem))
		elif editbox.CurrentControlType == uia2.Client.UIA_ComboBoxControlTypeId:
			return Enum(uia2.getElemSubText(uiaElem))
	
	def children(self, uiaElem):
		assert isTree(uiaElem) or isPane(uiaElem)
		if isTree(uiaElem):
			all = findAllElemByControlType(uiaElem, UIAClient.UIA_TreeItemControlTypeId, SCOPE_CHILDREN)
			set = []
			for x in range(0, all.Length):
				item = all.GetElement(x)
				name = getElemSubName(item)
				if isLeaf(item):
					elem = Window(name)
				else:
					elem = Menu(name)
				elem.ctrlType = 'TreeItem'
				elem.rectangle = item.CurrentBoundingRectangle
				set.append(elem)
			return set
		else:
			all = findAllElem4ORCond(uiaElem, UIAClient.UIA_CustomControlTypeId, UIAClient.UIA_ButtonControlTypeId, UIAClient.UIA_GroupControlTypeId, UIAClient.UIA_TabControlTypeId, UIAClient.UIA_ControlTypePropertyId, SCOPE_CHILDREN)
			set = []
			for x in range(0, all.Length):
				item = all.GetElement(x)
				if isCustom(item): # variable(ASCII, Enum, BitEnum)
					elem = self.createParam(item)
					elem.ctrlType = 'Custom'
				elif isButton(item): # method
					elem = Method(uia2.getElemSubText(item))
					elem.ctrlType = 'Button'
				elif isGroup(item): # group or bit-enum
					elem = Group(uia2.getElemSubText(item))
					elem.ctrlType = 'Group'
				elif isTab(item): # page
					elem = Page('')
					elem.ctrlType = 'Tab'
				elem.rectangle = item.CurrentBoundingRectangle
				set.append(elem)
			return set

class RRoot(RElement):
	def select(self, uiaElem):
		all = findAllElemByControlType(uiaElem, UIAClient.UIA_CustomControlTypeId, SCOPE_CHILDREN)
		workRoot = all.GetElement(all.Length-1)
		assert isUIAElem(workRoot)
		topTAB = findFirstElemByName(workRoot, 'Fdi.Client.DeviceUi.ViewModel.DeviceUiHostContainerItemViewModel')
		assert isUIAElem(topTAB)
		topTABX = findFirstElemByName(topTAB, 'X')
		assert isUIAElem(topTABX)
		topRoot = findNextSiblingElem(topTABX)
		assert isUIAElem(topRoot)
		return topRoot
	
	def children(self, uiaElem):
		set = []
		# get offline root menu item
		offline = findFirstElemBySubText(uiaElem, 'Offline root menu')
		assert isUIAElem(offline)
		elem = RRootMenu('Offline root menu')
		elem.ctrlType = 'Button'
		elem.rectangle = offline.CurrentBoundingRectangle
		set.append(elem)
		# get online root menu items
		onlineRoot = findFirstElemByAutomationId(uiaElem, 'OnlineParameters')
		assert isUIAElem(onlineRoot)
		pane = findFirstElemByControlType(onlineRoot, UIAClient.UIA_PaneControlTypeId)
		assert isUIAElem(pane)
		all = findAllElemByControlType(pane, UIAClient.UIA_ButtonControlTypeId, SCOPE_CHILDREN)
		for x in range(0, all.Length):
			item = all.GetElement(x)
			name = getElemSubName(item)
			elem = RRootMenu(name)
			elem.ctrlType = 'Button'
			elem.rectangle = item.CurrentBoundingRectangle
			set.append(elem)
		return set

class RRootMenu(RElement):
	def select(self, uiaElem):
		# search root menu button
		if not self.name == 'Offline root menu':
			onlineRoot = findFirstElemByAutomationId(uiaElem, 'OnlineParameters')
			assert isUIAElem(onlineRoot)
			pane = findFirstElemByControlType(onlineRoot, UIAClient.UIA_PaneControlTypeId)
			assert isUIAElem(pane)
			btn = findFirstElemBySubText(pane, self.name)
		else:
			btn = findFirstElemBySubText(uiaElem, self.name)
		# push root menu button
		assert isUIAElem(btn)
		pushButton(btn)
		time.sleep(4)
		explorer = findFirstElemByAutomationId(uiaElem, 'DD_ExplorerView')
		assert isUIAElem(explorer)
		elem = findNextSiblingElem(explorer)
		assert isUIAElem(elem)
		return elem
	
class RMenu(RElement):
	def select(self, uiaElem):
		tree = findFirstElemBySubText(uiaElem, self.name)
		assert isUIAElem(tree)
		expandTree(tree)
		time.sleep(2)
		#explorer = findFirstElemByAutomationId(uiaElem, 'DD_ExplorerView')
		#assert isUIAElem(explorer)
		#tree = findNextSiblingElem(explorer)
		return tree

class RWindow(RElement):
	def select(self, uiaElem):
		leaf = findFirstElemByAutomationId(uiaElem, self.name)
		assert isUIAElem(leaf)
		pushLeaf(leaf)
		time.sleep(2)
		explorer = findFirstElemByAutomationId(uiaElem, 'DD_ExplorerView')
		assert isUIAElem(explorer)
		tree = findNextSiblingElem(explorer)
		assert isTree(explorer)
		pane = findNextSiblingElem(tree)
		assert isPane(explorer)
		return pane

class RVariable(RElement):
	pass

if __name__ == '__main__':
	#pdb.set_trace()
	logging.basicConfig(level = logging.INFO)
	top = RRoot('root')
	top.ctrlType = None
	top.rectangle = None
	root = TreeNode(top)
	rrte = RRTE(root)
	rrte.startUp()
	rrte.createTree(rrte.root)