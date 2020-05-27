import pdb
import logging
import sys
import time
import subprocess
import xlrd
import win32api
import win32con
#import comtypes
from configparser import ConfigParser
from comtypes.client import *
from ctypes import *

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
	IUIA = CreateObject('{ff48dba4-60ef-4201-aa87-54103eef594e}', interface=Client.IUIAutomation)
	DesktopRoot = IUIA.GetRootElement()

	@staticmethod
	def findAllElem(start, key, type, flag=Client.PropertyConditionFlags_None, scope=Client.TreeScope_Descendants):
		cnd = UIA.IUIA.CreatePropertyConditionEx(type, key, flag)
		all = start.FindAll(scope, cnd)
		for x in range(0, all.Length):
			element = all.GetElement(x)
			logging.info('Element[%s] is searched.' % element.CurrentName)
		return all

	@staticmethod
	def findFirstElem(start, key, type, flag=Client.PropertyConditionFlags_None, scope=Client.TreeScope_Descendants):
		cnd = UIA.IUIA.CreatePropertyConditionEx(type, key, flag)
		element = start.FindFirst(scope, cnd)
		#logging.info('Element[%s] is searched.' % element.CurrentName)
		return element

	def getParentElem(elem):
		walker = UIA.IUIA.ControlViewWalker
		parent = walker.GetParentElement(elem)
		return parent

	@staticmethod
	def getNextSiblingElem(elem):
		walker = UIA.IUIA.ControlViewWalker
		element = walker.GetNextSiblingElement(elem)
		return element

	@staticmethod
	def getPreviousSiblingElem(elem):
		walker = UIA.IUIA.ControlViewWalker
		element = walker.GetPreviousSiblingElement(elem)
		return element
	
	@staticmethod
	def findElemBySubText(start, name, flag=Client.PropertyConditionFlags_None, scope=Client.TreeScope_Descendants):
		child = UIA.findFirstElem(start, name, UIA.Client.UIA_NamePropertyId)
		element = UIA.getParentElem(child)
		return element
	
	@staticmethod
	def isUIAElem(elem):
		try:
			temp = elem.CurrentName
			return True
		except Exception as e:
			return False
	
	@staticmethod
	def setEditbox(elem, text):
		pattern = elem.GetCurrentPattern(UIA.Client.UIA_ValuePatternId)
		ctrl = cast(pattern, POINTER(UIA.Client.IUIAutomationValuePattern))
		elem.SetFocus()
		ctrl.SetValue(text)

	@staticmethod
	def pushButton(elem):
		pattern = elem.GetCurrentPattern(UIA.Client.UIA_InvokePatternId)
		ctrl = cast(pattern, POINTER(UIA.Client.IUIAutomationInvokePattern))
		ctrl.Invoke()

class CTT:
	DELAY_DPCTT_START		= 6
	DELAY_SET_TO_DEV		= 4
	DELAY_FOR_DEMO			= 3
	NAME_DPCTT_APP			= 'FDI Package CTT'
	NAME_REPORT_INFO		= 'Test Report Information'
	NAME_REPORT_USER		= 'me'
	NAME_REPORT_FILLIN		= 'Please fill in Name'
	NAME_TITLE_BAR			= 'TitleBar'
	NAME_OVERFLOW_BTN		= 'OverflowButton'
	
	def __init__(self):
		self.CTTRoot		= None
		# layer2
		self.NewTestDialog	= None
		self.ReportDialog	= None
		self.TitleBar		= None
		self.MenuBar		= None
		self.ToolBar		= None
		self.CampaignView	= None
		self.PropertyView	= None
		self.LogView		= None
		self.StatusBar		= None
		# layer3(Main window)
		self.OverflowBtn	= None
		self.Thumb			= None
		self.ExecuteBtn		= None
		# layer3(Test Report Infomation)
		self.ReportUser		= None
		# layer2(Test Report Infomation)
		self.FillLabel		= None
		self.GivenName		= None
		self.GivenNameEdit	= None
		self.LastName		= None
		self.LastNameEdit	= None
		self.TestLab		= None
		self.TestLabEdit	= None
		self.DevManu		= None
		self.DevManuEdit	= None
		self.DevName		= None
		self.DevNameEdit	= None
		self.VerRRTE		= None
		self.VerRRTEEdit	= None
		self.VerCTT			= None
		self.VerCTTEdit		= None
		self.VerFDI			= None
		self.VerFDIEdit		= None
		self.TestEnv		= None
		self.TestEnvEdit	= None
		self.CancelBtn		= None
		self.AcceptBtn		= None

	def start(self, auto=True):
		# start DPCTT
		config = ConfigParser()
		config.read('test.conf', encoding='UTF-8')
		hostApp	= config['MISC']['HOST_APP_PATH'].strip("'") + '\FDI Package CTT\FDIPackageCTT.exe'
		testFile = config['MISC']['TEST_FILE'].strip("'")
		campaign = config['MISC']['HOST_APP_PATH'].strip("'") + '\FDI Package CTT\Campaigns\HART Testcampaign\hart.testcampaign.xml'
		#outPath = config['MISC']['OUTPUT_PATH'].strip("'")
		execCmd = '\"' + hostApp + '\"'
		if auto: pass
			# the following command can not load correct test suit
			#execCmd += ' --create \"' + testFile + '\" \"' + campaign + '\" --report'
		subprocess.Popen(execCmd, shell=True, stdout=subprocess.PIPE)
		time.sleep(CTT.DELAY_DPCTT_START)
		logging.info('execCmd = %s' % execCmd)
		# get part's node from screen
		self.CTTRoot 		= UIA.findFirstElem(UIA.DesktopRoot, CTT.NAME_DPCTT_APP, UIA.Client.UIA_NamePropertyId)
		'''
		# popup dialog
		self.ReportDialog 	= UIA.findFirstElem(self.CTTRoot, UIA.Client.UIA_WindowControlTypeId, UIA.Client.UIA_ControlTypePropertyId)
		self.ReportUser		= UIA.findFirstElem(self.ReportDialog, CTT.NAME_REPORT_USER, UIA.Client.UIA_AutomationIdPropertyId)
		self.FillLabel 		= UIA.findFirstElem(self.ReportUser, CTT.NAME_REPORT_FILLIN, UIA.Client.UIA_NamePropertyId)
		self.GivenName		= UIA.getNextSiblingElem(self.FillLabel)
		self.GivenNameEdit	= UIA.getNextSiblingElem(self.GivenName)
		self.LastName		= UIA.getNextSiblingElem(self.GivenNameEdit)
		self.LastNameEdit	= UIA.getNextSiblingElem(self.LastName)
		self.TestLab		= UIA.getNextSiblingElem(self.LastNameEdit)
		self.TestLabEdit	= UIA.getNextSiblingElem(self.TestLab)
		self.DevManu		= UIA.getNextSiblingElem(self.TestLabEdit)
		self.DevManuEdit	= UIA.getNextSiblingElem(self.DevManu)
		self.DevName		= UIA.getNextSiblingElem(self.DevManuEdit)
		self.DevNameEdit	= UIA.getNextSiblingElem(self.DevName)
		self.VerRRTE		= UIA.getNextSiblingElem(self.DevNameEdit)
		self.VerRRTEEdit	= UIA.getNextSiblingElem(self.VerRRTE)
		self.VerCTT			= UIA.getNextSiblingElem(self.VerRRTEEdit)
		self.VerCTTEdit		= UIA.getNextSiblingElem(self.VerCTT)
		self.VerFDI			= UIA.getNextSiblingElem(self.VerCTTEdit)
		self.VerFDIEdit		= UIA.getNextSiblingElem(self.VerFDI)
		self.TestEnv		= UIA.getNextSiblingElem(self.VerFDIEdit)
		self.TestEnvEdit	= UIA.getNextSiblingElem(self.TestEnv)
		self.CancelBtn		= UIA.getNextSiblingElem(self.TestEnvEdit)
		self.AcceptBtn		= UIA.getNextSiblingElem(self.CancelBtn)
		'''
		# main window
		self.TitleBar		= UIA.findFirstElem(self.CTTRoot, UIA.Client.UIA_TitleBarControlTypeId, UIA.Client.UIA_ControlTypePropertyId)
		self.MenuBar		= UIA.getNextSiblingElem(self.TitleBar)
		self.ToolBar		= UIA.getNextSiblingElem(self.MenuBar)
		self.CampaignView	= UIA.getNextSiblingElem(self.ToolBar)
		self.PropertyView	= UIA.getNextSiblingElem(self.CampaignView)
		self.LogView		= UIA.getNextSiblingElem(self.PropertyView)
		self.OverflowBtn	= UIA.findFirstElem(self.ToolBar, CTT.NAME_OVERFLOW_BTN, UIA.Client.UIA_AutomationIdPropertyId)
		self.Thumb			= UIA.getNextSiblingElem(self.OverflowBtn)
		self.ExecuteBtn		= UIA.getNextSiblingElem(self.Thumb)
		# assert
		assert UIA.isUIAElem(self.CTTRoot)
		'''
		assert UIA.isUIAElem(self.ReportDialog)
		assert UIA.isUIAElem(self.ReportUser)
		assert UIA.isUIAElem(self.FillLabel)
		assert UIA.isUIAElem(self.GivenName)
		assert UIA.isUIAElem(self.GivenNameEdit)
		assert UIA.isUIAElem(self.LastName)
		assert UIA.isUIAElem(self.LastNameEdit)
		assert UIA.isUIAElem(self.TestLab)
		assert UIA.isUIAElem(self.TestLabEdit)
		assert UIA.isUIAElem(self.DevManu)
		assert UIA.isUIAElem(self.DevManuEdit)
		assert UIA.isUIAElem(self.DevName)
		assert UIA.isUIAElem(self.DevNameEdit)
		assert UIA.isUIAElem(self.VerRRTE)
		assert UIA.isUIAElem(self.VerRRTEEdit)
		assert UIA.isUIAElem(self.VerCTT)
		assert UIA.isUIAElem(self.VerCTTEdit)
		assert UIA.isUIAElem(self.VerFDI)
		assert UIA.isUIAElem(self.VerFDIEdit)
		assert UIA.isUIAElem(self.TestEnv)
		assert UIA.isUIAElem(self.TestEnvEdit)
		assert UIA.isUIAElem(self.CancelBtn)
		assert UIA.isUIAElem(self.AcceptBtn)
		'''
		assert UIA.isUIAElem(self.TitleBar)
		assert UIA.isUIAElem(self.MenuBar)
		assert UIA.isUIAElem(self.ToolBar)
		assert UIA.isUIAElem(self.CampaignView)
		assert UIA.isUIAElem(self.PropertyView)
		assert UIA.isUIAElem(self.LogView)
		assert UIA.isUIAElem(self.OverflowBtn)
		assert UIA.isUIAElem(self.Thumb)
		assert UIA.isUIAElem(self.ExecuteBtn)

	def newCampaign(self):
		hwnd = win32gui.FindWindow(NAME_DPCTT_APP, None)
		win32api.PostMessage(hwnd, win32con.WM_KEYDOWN, win32con.VK_CTRL, 0)
		win32api.PostMessage(hwnd, win32con.WM_KEYDOWN, win32con.VK_N, 0)
		win32api.PostMessage(hwnd, win32con.WM_KEYUP, win32con.VK_N, 0)
		win32api.PostMessage(hwnd, win32con.WM_KEYUP, win32con.VK_CTRL, 0)
	
	def assignPackage(self):
		pass
		
	def setReportInfo(self):
		# get report info
		config = ConfigParser()
		config.read('test.conf', encoding='UTF-8')
		givenName	= config['MISC']['CTT_TESTER_GIVEN_NAME'].strip("'")
		lastName	= config['MISC']['CTT_TESTER_LAST_NAME'].strip("'")
		testLab		= config['MISC']['CTT_TEST_LAB'].strip("'")
		testEnv		= config['MISC']['CTT_TEST_ENV'].strip("'")
		# set report info
		UIA.setEditbox(self.GivenNameEdit, givenName)
		UIA.setEditbox(self.LastNameEdit, lastName)
		UIA.setEditbox(self.TestLabEdit, testLab)
		UIA.setEditbox(self.TestEnvEdit, testEnv)
		time.sleep(CTT.DELAY_FOR_DEMO)
		# push accept button
		UIA.pushButton(self.AcceptBtn)
		time.sleep(CTT.DELAY_SET_TO_DEV)
	
	def execute(self):
		# push execute button
		UIA.pushButton(self.ExecuteBtn)
		time.sleep(CTT.DELAY_SET_TO_DEV)
	
class RRTE:
	DELAY_RRET_START			= 8
	DELAY_SET_TO_DEV			= 4
	DELAY_FOR_DEMO				= 3
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
		config.read('test.conf', encoding='UTF-8')
		#inputMode = config['MISC']['TEST_FILE_TYPE'].strip("'")
		hostApp	= config['MISC']['HOST_APP_PATH'].strip("'") + '\Reference Run-time Environment\Fdi.Reference.Client.exe'
		testFile = config['MISC']['TEST_FILE'].strip("'")
		#outPath = config['MISC']['OUTPUT_PATH'].strip("'")
		execCmd = '\"' + hostApp + '\" -l \"' + testFile + '\"'
		subprocess.Popen(execCmd, shell=True, stdout=subprocess.PIPE)
		time.sleep(RRTE.DELAY_RRET_START)
		logging.info('execCmd = %s' % execCmd)
		# find layer1 element
		self.RRTERoot	= UIA.findFirstElem(UIA.DesktopRoot, RRTE.NAME_RRTE_APP, UIA.Client.UIA_NamePropertyId)
		self.RRTECurr	= self.RRTERoot
		# find layer2 element(work area)
		all = UIA.findAllElem(self.RRTERoot, UIA.Client.UIA_CustomControlTypeId, UIA.Client.UIA_ControlTypePropertyId, scope=UIA.Client.TreeScope_Children)
		self.WorkRoot	= all.GetElement(all.Length-1)
		# find layer3 element
		self.TopTAB		= UIA.findFirstElem(self.WorkRoot, RRTE.NAME_TOP_TAB, UIA.Client.UIA_NamePropertyId)
		self.TopTABX	= UIA.findFirstElem(self.TopTAB, RRTE.NAME_X_BTN, UIA.Client.UIA_NamePropertyId)
		self.TopRoot	= UIA.getNextSiblingElem(self.TopTABX)
		# find layer4 element
		self.Offline	= UIA.findElemBySubText(self.TopRoot, RRTE.NAME_OFFLINE_TAB)
		self.OfflineX	= UIA.findFirstElem(self.Offline, RRTE.NAME_X_BTN, UIA.Client.UIA_NamePropertyId)
		self.TABRoot	= UIA.findFirstElem(self.TopRoot, RRTE.NAME_ONLINE_PARAMS, UIA.Client.UIA_AutomationIdPropertyId)
		self.Health		= UIA.getNextSiblingElem(self.TABRoot)
		self.Explorer	= UIA.findFirstElem(self.TopRoot, RRTE.NAME_TREE_ROOT, UIA.Client.UIA_AutomationIdPropertyId)
		#self.TreeRoot	= UIA.getNextSiblingElem(self.Explorer)
		#self.PaneRoot	= UIA.getNextSiblingElem(self.TreeRoot)
		self.Apply		= UIA.findFirstElem(self.TopRoot, RRTE.NAME_APPLY_BTN, UIA.Client.UIA_NamePropertyId)
		self.Revert		= UIA.findFirstElem(self.TopRoot, RRTE.NAME_REVERT_BTN, UIA.Client.UIA_NamePropertyId)
		# layer5
		self.Online		= UIA.findElemBySubText(self.TABRoot, RRTE.NAME_ONLINE_TAB)
		self.OnlineX	= UIA.findFirstElem(self.Online, RRTE.NAME_X_BTN, UIA.Client.UIA_NamePropertyId)
		self.Device		= UIA.findElemBySubText(self.TABRoot, RRTE.NAME_DEVICE_ROOT_MENU)
		self.DeviceX	= UIA.findFirstElem(self.Device, RRTE.NAME_X_BTN, UIA.Client.UIA_NamePropertyId)
		self.Diagnose	= UIA.findElemBySubText(self.TABRoot, RRTE.NAME_DIAGNOSTIC_ROOT_MENU)
		self.DiagnoseX	= UIA.findFirstElem(self.Diagnose, RRTE.NAME_X_BTN, UIA.Client.UIA_NamePropertyId)
		self.Maintena	= UIA.findElemBySubText(self.TABRoot, RRTE.NAME_MAINT_ROOT_MENU)
		self.MaintenaX	= UIA.findFirstElem(self.Maintena, RRTE.NAME_X_BTN, UIA.Client.UIA_NamePropertyId)
		self.Process	= UIA.findElemBySubText(self.TABRoot, RRTE.NAME_PROCESS_ROOT_MENU)
		self.ProcessX	= UIA.findFirstElem(self.Process, RRTE.NAME_X_BTN, UIA.Client.UIA_NamePropertyId)
		# assert
		assert UIA.isUIAElem(self.RRTERoot)
		assert UIA.isUIAElem(self.WorkRoot)
		assert UIA.isUIAElem(self.TopTAB)
		assert UIA.isUIAElem(self.TopTABX)
		assert UIA.isUIAElem(self.TopRoot)
		assert UIA.isUIAElem(self.Offline)
		assert UIA.isUIAElem(self.OfflineX)
		assert UIA.isUIAElem(self.TABRoot)
		assert UIA.isUIAElem(self.Health)
		assert UIA.isUIAElem(self.Explorer)
		assert UIA.isUIAElem(self.Apply)
		assert UIA.isUIAElem(self.Revert)
		assert UIA.isUIAElem(self.Online)
		assert UIA.isUIAElem(self.OnlineX)
		assert UIA.isUIAElem(self.Device)
		assert UIA.isUIAElem(self.DeviceX)
		assert UIA.isUIAElem(self.Diagnose)
		assert UIA.isUIAElem(self.DiagnoseX)
		assert UIA.isUIAElem(self.Maintena)
		assert UIA.isUIAElem(self.MaintenaX)
		assert UIA.isUIAElem(self.Process)
		assert UIA.isUIAElem(self.ProcessX)

	def getTreeNodeFromScreen(self, node):
		pass
	
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
	def __init__(self, name):
		self.name = name
		self.ctrlType = None
		self.rectangle = None
		
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
	'''
	rootElement = Menu('Online')
	rootNode = TreeNode(rootElement)
	rrte = RRTE()
	rrte.start()
	rrte.getTreeNodeFromScreen(rootNode)
	rrte.getLog(rootNode)
	'''
	dpctt = CTT()
	dpctt.start(False)
	dpctt.newCampaign()
	dpctt.assignPackage()
	#dpctt.setReportInfo()
	#dpctt.execute()

'''
	def AddAutomationEventHandler(self, eventId, element, scope, cacheRequest, handler):
'''

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