import pdb
import logging
import sys
import time
import subprocess
import xlrd
#import comtypes
from configparser import ConfigParser
from comtypes.client import *
from ctypes import *

#UIAutomationClient = GetModule('UIAutomationCore.dll')
#IUIAutomation = CreateObject('{ff48dba4-60ef-4201-aa87-54103eef594e}', interface=UIAutomationClient.IUIAutomation)

class TreeNode:
	def __init__(self, elem, parent=None, left=None, right=None):
		self.elem = elem
		self.parent = parent # It's logic parent node in tree, not in binary tree
		self.left = left
		self.right = right

class Tree: # It's logic tree, not control view tree in ui automation 
	def __init__(self, root=None, curr=None):
		self.root = root
		self.curr = curr

	def addChild(self, child, parent): # insert node under the current node
		if parent == None and self.root == None:
			self.root = child
			child.parent = None
		else:
			child.parent = parent
			if self.curr.left == None:
				self.curr.left = child
			else:
				currNode = self.curr.left
				while (not currNode.right == None):
					currNode = currNode.right
				currNode.right = child

	def preorderScreen(self): # traverse to page node in tree items
		pass

class UIA:
	Client = GetModule('UIAutomationCore.dll')
	IUia = CreateObject('{ff48dba4-60ef-4201-aa87-54103eef594e}', interface=Client.IUIAutomation)
	Root = IUia.GetRootElement()

	@staticmethod
	def FindAllElem(start, key, type, flag=Client.PropertyConditionFlags_None, scope=Client.TreeScope_Descendants):
		cnd = UIA.IUia.CreatePropertyConditionEx(type, key, flag)
		all = start.FindAll(scope, cnd)
		for x in range(0, all.Length):
			element = all.GetElement(x)
		return all

	@staticmethod
	def FindOneElem(start, key, type, flag=Client.PropertyConditionFlags_None, scope=Client.TreeScope_Descendants):
		cnd = UIA.IUia.CreatePropertyConditionEx(type, key, flag)
		element = start.FindFirst(scope, cnd)
		return element

	@staticmethod
	def GetSiblingElem(elem):
		walker = UIA.IUia.ControlViewWalker
		element = walker.GetNextSiblingElement(elem)
		return element

	@staticmethod
	def FindElemBySubText(start, name, flag=Client.PropertyConditionFlags_None, scope=Client.TreeScope_Descendants):
		cnd = UIA.IUia.CreatePropertyConditionEx(UIA.Client.UIA_NamePropertyId, name, flag)
		child = start.FindFirst(scope, cnd)
		walker = UIA.IUia.ControlViewWalker
		element = walker.GetParentElement(child)
		return element

class RRTECtrl:
	RRET_OPEN_DELAY				= 6
	NAME_RRTE_APP				= 'Reference Run-time Environment'
	NAME_TOP_TAB				= 'Fdi.Client.DeviceUi.ViewModel.DeviceUiHostContainerItemViewModel'
	NAME_X_BTN					= 'X'
	NAME_ONLINE_PARAMS			= 'OnlineParameters'
	NAME_OFFLINE_TAB			= 'Offline root menu'
	NAME_ONLINE_TAB				= 'Online'
	NAME_DEVICE_ROOT_MENU		= 'Device root menu'
	NAME_DIAGNOSTIC_ROOT_MENU	= 'Diagnostic root menu'
	NAME_MAINT_ROOT_MENU		= 'Maintenance root menu'
	NAME_PROCESS_ROOT_MENU		= 'Process variables root menu'
	NAME_HEALTH_TAB				= 'Health'
	NAME_TREE_ROOT				= 'DD_ExplorerView'
	NAME_APPLY_BTN				= 'Apply'
	NAME_REVERT_BTN				= 'Revert'

	def __init__(self):
		self.tree		= None
		self.RRTERoot	= None
		self.RRTECurr	= None
		self.CurrTAB	= None
		# layer2
		self.WorkRoot	= None
		# layer3
		self.TopTAB		= None # TAB for special fdi package 
		self.TopBtnX	= None # button on the right side of top TAB
		self.TopRoot	= None # window to contain tab, menu tree, and param
		# layer4
		self.Offline	= None # offline entry
		self.OfflineX	= None
		self.TABRoot	= None # root TABs' parent
		# layer5
		self.Online		= None # online entry
		self.OnlineX	= None
		self.Device		= None # device root menu entry
		self.DeviceX	= None
		self.Diagnose	= None # diagnostic root menu entry
		self.DiagnoseX	= None
		self.Maintena	= None # maintenance root menu entry
		self.MaintenaX	= None
		self.Process	= None # process variable root menu entry
		self.ProcessX	= None
		# layer4
		self.Health		= None
		self.Explorer	= None
		self.TreeRoot	= None # update after click root menu button
		self.PaneRoot	= None # update after click menu or window item
		self.Apply		= None
		self.Revert		= None

	def start(self):
		config = ConfigParser()
		config.read('testRrte.conf', encoding='UTF-8')
		#inputMode = config['MISC']['TEST_FILE_TYPE'].strip("'")
		hostApp	= config['MISC']['HOST_APP_FILE'].strip("'")
		testFile = config['MISC']['TEST_FILE'].strip("'")
		#outPath = config['MISC']['OUTPUT_PATH'].strip("'")
		execCmd = '\"' + hostApp + '\" -l \"' + testFile + '\"'
		subprocess.Popen(execCmd, shell=True, stdout=subprocess.PIPE)
		time.sleep(RRTECtrl.RRET_OPEN_DELAY)
		# find layer1 element
		self.RRTERoot	= UIA.FindOneElem(UIA.Root, RRTECtrl.NAME_RRTE_APP, UIA.Client.UIA_NamePropertyId)
		self.RRTECurr	= self.RRTERoot
		# find layer2 element(work area)
		all = UIA.FindAllElem(self.RRTERoot, UIA.Client.UIA_CustomControlTypeId, UIA.Client.UIA_ControlTypePropertyId, scope=UIA.Client.TreeScope_Children)
		self.WorkRoot	= all.GetElement(all.Length-1)
		# find layer3 element
		self.TopTAB		= UIA.FindOneElem(self.WorkRoot, RRTECtrl.NAME_TOP_TAB, UIA.Client.UIA_NamePropertyId)
		self.TopTABX	= UIA.FindOneElem(self.TopTAB, RRTECtrl.NAME_X_BTN, UIA.Client.UIA_NamePropertyId)
		self.TopRoot	= UIA.GetSiblingElem(self.TopTABX)
		# find layer4 element
		self.Offline	= UIA.FindElemBySubText(self.TopRoot, RRTECtrl.NAME_OFFLINE_TAB)
		self.OfflineX	= UIA.FindOneElem(self.Offline, RRTECtrl.NAME_X_BTN, UIA.Client.UIA_NamePropertyId)
		self.TABRoot	= UIA.FindOneElem(self.TopRoot, RRTECtrl.NAME_ONLINE_PARAMS, UIA.Client.UIA_AutomationIdPropertyId)
		self.Health		= UIA.GetSiblingElem(self.TABRoot)
		self.Explorer	= UIA.FindOneElem(self.TopRoot, RRTECtrl.NAME_TREE_ROOT, UIA.Client.UIA_AutomationIdPropertyId)
		#self.TreeRoot	= UIA.GetSiblingElem(self.Explorer)
		#self.PaneRoot	= UIA.GetSiblingElem(self.TreeRoot)
		self.Apply		= UIA.FindOneElem(self.TopRoot, RRTECtrl.NAME_APPLY_BTN, UIA.Client.UIA_NamePropertyId)
		self.Revert		= UIA.FindOneElem(self.TopRoot, RRTECtrl.NAME_REVERT_BTN, UIA.Client.UIA_NamePropertyId)
		# layer5
		self.Online		= UIA.FindElemBySubText(self.TABRoot, RRTECtrl.NAME_ONLINE_TAB)
		self.OnlineX	= UIA.FindOneElem(self.Online, RRTECtrl.NAME_X_BTN, UIA.Client.UIA_NamePropertyId)
		self.Device		= UIA.FindElemBySubText(self.TABRoot, RRTECtrl.NAME_DEVICE_ROOT_MENU)
		self.DeviceX	= UIA.FindOneElem(self.Device, RRTECtrl.NAME_X_BTN, UIA.Client.UIA_NamePropertyId)
		self.Diagnose	= UIA.FindElemBySubText(self.TABRoot, RRTECtrl.NAME_DIAGNOSTIC_ROOT_MENU)
		self.DiagnoseX	= UIA.FindOneElem(self.Diagnose, RRTECtrl.NAME_X_BTN, UIA.Client.UIA_NamePropertyId)
		self.Maintena	= UIA.FindElemBySubText(self.TABRoot, RRTECtrl.NAME_MAINT_ROOT_MENU)
		self.MaintenaX	= UIA.FindOneElem(self.Maintena, RRTECtrl.NAME_X_BTN, UIA.Client.UIA_NamePropertyId)
		self.Process	= UIA.FindElemBySubText(self.TABRoot, RRTECtrl.NAME_PROCESS_ROOT_MENU)
		self.ProcessX	= UIA.FindOneElem(self.Process, RRTECtrl.NAME_X_BTN, UIA.Client.UIA_NamePropertyId)
		# assert
		assert not self.RRTERoot == None
		assert not self.WorkRoot == None
		assert not self.TopTAB == None
		assert not self.TopTABX == None
		assert not self.TopRoot == None
		assert not self.Offline == None
		assert not self.OfflineX == None
		assert not self.TABRoot == None
		assert not self.Health == None
		assert not self.Explorer == None
		assert not self.Apply == None
		assert not self.Revert == None
		assert not self.Online == None
		assert not self.OnlineX == None
		assert not self.Device == None
		assert not self.DeviceX == None
		assert not self.Diagnose == None
		assert not self.DiagnoseX == None
		assert not self.Maintena == None
		assert not self.MaintenaX == None
		assert not self.Process == None
		assert not self.ProcessX == None

	def getDescendant(self, node):
		pass

	def select(self, node):
		assert not type(node) == 'Group'
		assert not type(node) == 'Method'
		assert not type(node) == 'Data'
		assert not type(node) == 'Enum'
		assert not type(node) == 'BitEnum'
		path = []
		path.append(node.elem)
		currNode = node
		while not currNode.parent == None:
			currNode = currNode.parent
			path.append(currNode.elem)
		path.reverse()
		self.UIACurr = self.UIARoot
		for item in path:
			self.UIACurr = item.select(self.UIACurr)
		
		

class Element: # abstract class
	def __init__(self, label):
		self.label = label
		self.rectangle = None # label's rectangle
		
# RRTE element class
class RRTEElement(Element): # abstract class (not used in demo)
	pass
	
class Menu(Element):
	pass

class Window(Element):
	pass

class Page(Element):
	pass

class Group(Element):
	pass

class Param(Element): # abstract class
	def __init__(self, label, mode='RO', edit='None', unit=''):
		LeafElement.__init__(self, label)
		self.mode = mode
		self.edit = edit
		self.unit = unit

class Method(Element):
	pass

class Data(Param):
	pass

class Enum(Param):
	pass

class BitEnum(Param):
	pass

if __name__ == '__main__':
	#pdb.set_trace()
	logging.basicConfig(level = logging.INFO)
	
	rrte = RRTECtrl()
	rrte.start()
	

''' TODO : tree --> binary tree
class Tree:
	def __init__(self, name=None):
		#self.style = style	# MENU/WINDOW/PAGE,GROUP/PARAM/METHOD
		#elf.mode = mode	# RO or RW
		#self.type = type	# Parameter type (INT,Float,Enum,BitEnum)
		self.name = name	# Node name
		self.parent = None	# It's logic parent node in tree, not in binary tree
		self.lchild = None
		self.rchild = None

	def __search(self, name):
		currNode = self
		while(currNode is not None and not name == currNode.name):
			if(not name == currNode.name and not currNode.lchild == None):
				currNode = currNode.lchild.__search(name)
			if(not name == currNode.name and not currNode.rchild == None):
				currNode = currNode.rchild.__search(name)
		return currNode

	def search(self, name):
		return self.__search(name)

	def insert(self, parentName=None, name=None):
		parentNode = self.__search(parentName)
		logging.info('Current node name = %s' % parentNode.name)
		if parentName == None:
			self.name = name
		else:
			if parentNode != None:
				node = Tree(name)
				if parentNode.lchild == None:
					parentNode.lchild = node
				else:
					currNode = parentNode.lchild
					while (not currNode.rchild == None):
						currNode = currNode.rchild
					currNode.rchild = node
	
	def addChildNode(self, name=None):
		if self.name == None:
			self.name = name
			self.parent = None
			return self
		else:
			node = Tree(name)
			node.parent = self
			if self.lchild == None:
				self.lchild = node
			else:
				currNode = self.lchild
				while (not currNode.rchild == None):
					currNode = currNode.rchild
				currNode.rchild = node
			return self

	def traverse(self):
		if self == None:
			return
		if not self.lchild == None:
			self.lchild.traverse()
		if not self.rchild == None:
			self.rchild.traverse()

	def dump(self):
		if self == None:
			return
		if self.parent == None:
			str = 'None'
		else:
			str = self.parent.name
		print ('node = %s, parent = %s' %(self.name, str))
		if not self.lchild == None:
			self.lchild.dump()
		if not self.rchild == None:
			self.rchild.dump()
	
	def parent(self):
		return self.parent
	
	def next(self):
		return self.rchild

#pdb.set_trace()
logging.basicConfig(level = logging.INFO)

tree = Tree()
#tree.insert(name='Online')
#tree.insert('Online', 'Process variables root menu')
#tree.insert('Online', 'Diagnostic root menu')
#tree.insert('Online', 'Maintenance root menu')
#tree.insert('Online', 'Device root menu')
#tree.insert('Process variables root menu', 'Dynamic variables')
#tree.insert('Process variables root menu', 'Device variables')
#tree.insert('Process variables root menu', 'Dynamic variables status')
#tree.insert('Process variables root menu', 'Totalizer count')
#tree.insert('Process variables root menu', 'View outputs')
curr = tree.addChildNode('Online')
curr.addChildNode('Process variables root menu')
curr.addChildNode('Diagnostic root menu')
curr.addChildNode('Maintenance root menu')
curr.addChildNode('Device root menu')
curr = curr.lchild
curr.addChildNode('Dynamic variables')
curr.addChildNode('Device variables')
curr.addChildNode('Dynamic variables status')
curr.addChildNode('Totalizer count')
curr.addChildNode('View outputs')
tree.dump()
'''