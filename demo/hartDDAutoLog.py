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

class TreeNode:
	def __init__(self, elem, parent=None, left=None, right=None):
		self.elem = elem
		self.parent = parent # It's logic parent node in tree, not in binary tree
		self.left = left
		self.right = right
	
	def setChildren(self, rrte):
		elems = self.elem.children(rrte)
		if len(elems) > 0:
			self.left = TreeNode(elems[0], self)
			currNode = self.left
			for x in range(1, len(elems)):
				currNode.right = TreeNode(elems[x], self)
				currNode = currNode.right
	
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
		#for x in range(0, all.Length):
			#element = all.GetElement(x)
			#logging.info('Element[%s] is searched.' % element.CurrentName)
		return all

	@staticmethod
	def findFirstElem(start, key, type, flag=Client.PropertyConditionFlags_None, scope=Client.TreeScope_Descendants):
		cnd = UIA.IUIA.CreatePropertyConditionEx(type, key, flag)
		element = start.FindFirst(scope, cnd)
		#logging.info('Element[%s] is searched.' % element.CurrentName)
		return element

	@staticmethod
	def findFirstElem2And(start, key1, type1, key2, type2, flag=Client.PropertyConditionFlags_None, scope=Client.TreeScope_Descendants):
		cnd1 = UIA.IUIA.CreatePropertyConditionEx(type1, key1, flag)
		cnd2 = UIA.IUIA.CreatePropertyConditionEx(type2, key2, flag)
		combine = UIA.IUIA.CreateAndCondition(cnd1, cnd2)
		element = start.FindFirst(scope, combine)
		#logging.info('Element[%s] is searched.' % element.CurrentName)
		return element
	
	@staticmethod
	def findAllElem2Or(start, key1, type1, key2, type2, flag=Client.PropertyConditionFlags_None, scope=Client.TreeScope_Descendants):
		cnd1 = UIA.IUIA.CreatePropertyConditionEx(type1, key1, flag)
		cnd2 = UIA.IUIA.CreatePropertyConditionEx(type2, key2, flag)
		combine = UIA.IUIA.CreateOrCondition(cnd1, cnd2)
		all = start.FindAll(scope, combine)
		#for x in range(0, all.Length):
			#element = all.GetElement(x)
			#logging.info('Element[%s] is searched.' % element.CurrentName)
		return all
	
	@staticmethod
	def findAllElem4Or(start, key1, key2, key3, key4, type, flag=Client.PropertyConditionFlags_None, scope=Client.TreeScope_Descendants):
		cnd1 = UIA.IUIA.CreatePropertyConditionEx(type, key1, flag)
		cnd2 = UIA.IUIA.CreatePropertyConditionEx(type, key2, flag)
		cnd3 = UIA.IUIA.CreatePropertyConditionEx(type, key3, flag)
		cnd4 = UIA.IUIA.CreatePropertyConditionEx(type, key4, flag)
		combine1 = UIA.IUIA.CreateOrCondition(cnd1, cnd2)
		combine2 = UIA.IUIA.CreateOrCondition(cnd3, cnd4)
		combine = UIA.IUIA.CreateOrCondition(combine1, combine2)
		all = start.FindAll(scope, combine)
		#for x in range(0, all.Length):
			#element = all.GetElement(x)
			#logging.info('Element[%s] is searched.' % element.CurrentName)
		return all

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
	def getElemSubText(elem):
		text = UIA.findFirstElem(elem, UIA.Client.UIA_TextControlTypeId, UIA.Client.UIA_ControlTypePropertyId, scope=UIA.Client.TreeScope_Children)
		return text.CurrentName
	
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
		assert UIA.isUIAElem(elem)
		pattern = elem.GetCurrentPattern(UIA.Client.UIA_ValuePatternId)
		ctrl = cast(pattern, POINTER(UIA.Client.IUIAutomationValuePattern))
		elem.SetFocus()
		ctrl.SetValue(text)

	@staticmethod
	def expandTree(elem):
		assert UIA.isUIAElem(elem)
		pattern = elem.GetCurrentPattern(UIA.Client.UIA_ExpandCollapsePatternId)
		ctrl = cast(pattern, POINTER(UIA.Client.IUIAutomationExpandCollapsePattern))
		if ctrl.value.CurrentExpandCollapseState == UIA.Client.ExpandCollapseState_Collapsed:
			ctrl.Select()
	
	@staticmethod
	def collapseTree(elem):
		assert UIA.isUIAElem(elem)
		pattern = elem.GetCurrentPattern(UIA.Client.UIA_ExpandCollapsePatternId)
		ctrl = cast(pattern, POINTER(UIA.Client.IUIAutomationExpandCollapsePattern))
		if ctrl.value.CurrentExpandCollapseState == UIA.Client.ExpandCollapseState_Expanded:
			ctrl.Select()
	
	@staticmethod
	def isLeaf(elem):
		assert UIA.isUIAElem(elem)
		pattern = elem.GetCurrentPattern(UIA.Client.UIA_ExpandCollapsePatternId)
		ctrl = cast(pattern, POINTER(UIA.Client.IUIAutomationExpandCollapsePattern))
		return ctrl.value.CurrentExpandCollapseState == UIA.Client.ExpandCollapseState_LeafNode
	
	@staticmethod
	def pushLeaf(elem):
		assert UIA.isUIAElem(elem)
		pattern1 = elem.GetCurrentPattern(UIA.Client.UIA_ExpandCollapsePatternId)
		ctrl1 = cast(pattern1, POINTER(UIA.Client.IUIAutomationExpandCollapsePattern))
		pattern2 = elem.GetCurrentPattern(UIA.Client.UIA_SelectionItemPatternId)
		ctrl2 = cast(pattern2, POINTER(UIA.Client.IUIAutomationSelectionItemPattern))
		if ctrl1.value.CurrentExpandCollapseState == UIA.Client.ExpandCollapseState_LeafNode:
			ctrl2.Select()
	
	@staticmethod
	def pushButton(elem):
		assert UIA.isUIAElem(elem)
		pattern = elem.GetCurrentPattern(UIA.Client.UIA_InvokePatternId)
		ctrl = cast(pattern, POINTER(UIA.Client.IUIAutomationInvokePattern))
		ctrl.Invoke()
		
	@staticmethod
	def selectTab(elem):
		assert UIA.isUIAElem(elem)
		pattern = elem.GetCurrentPattern(UIA.Client.UIA_SelectionItemPatternId)
		ctrl = cast(pattern, POINTER(UIA.Client.IUIAutomationSelectionItemPattern))
		if not ctrl.value.CurrentIsSelected:
			ctrl.Select()
	
	@staticmethod
	def selectCheckbox(elem):
		assert UIA.isUIAElem(elem)
		pattern = elem.GetCurrentPattern(UIA.Client.UIA_TogglePatternId)
		ctrl = cast(pattern, POINTER(UIA.Client.IUIAutomationTogglePattern))
		if not ctrl.value.CurrentToggleState:
			ctrl.Toggle()
	
	@staticmethod
	def unselectCheckbox(elem):
		assert UIA.isUIAElem(elem)
		pattern = elem.GetCurrentPattern(UIA.Client.UIA_TogglePatternId)
		ctrl = cast(pattern, POINTER(UIA.Client.IUIAutomationTogglePattern))
		if ctrl.value.CurrentToggleState:
			ctrl.Toggle()
	
	@staticmethod
	def setDirInCommonDialog(dialog, path):
		assert UIA.isUIAElem(dialog)
		#logging.info('Reference file is %s.' % path)
		edit = UIA.findFirstElem2And(dialog, UIA.Client.UIA_EditControlTypeId, UIA.Client.UIA_ControlTypePropertyId, 'Edit', UIA.Client.UIA_ClassNamePropertyId)
		assert UIA.isUIAElem(edit)
		okBtn = UIA.findFirstElem(dialog, '1', UIA.Client.UIA_AutomationIdPropertyId, scope=UIA.Client.TreeScope_Children)
		assert UIA.isUIAElem(okBtn)
		UIA.setEditbox(edit, path)
		time.sleep(1)
		UIA.pushButton(okBtn)
		time.sleep(1)

class CTT:
	DELAY_DPCTT_START		= 6
	DELAY_SET_TO_DEV		= 4
	DELAY_FOR_DEMO			= 3
	DELAY_WAIT_DLG			= 3
	DELAY_LONG_TIME			= 10
	DELAY_LONG_LONG			= 100
	# Name or AutomationId (main window)
	NAME_DPCTT_APP			= 'FDI Package CTT'
	NAME_OVERFLOW_BTN		= 'OverflowButton'
	# Name or AutomationId ("Test Report Information" dialog)
	NAME_REPORT_INFO		= 'Test Report Information'
	NAME_REPORT_USER		= 'me'
	NAME_REPORT_FILLIN		= 'Please fill in Name'
	# Name or AutomationId ("New Test Campaign" dialog)
	NAME_NEW_COMPAIGN		= 'New Test Campaign'
	NAME_COMPAIGN_PATH		= 'nameBox'
	NAME_COMPAIGN_CHECK		= 'cb'
	NAME_COMPAIGN_OTHER		= 'otherSelectButton'
	NAME_COMPAIGN_CANCEL	= 'Cancel'
	NAME_COMPAIGN_ACCEPT	= 'Accept'
	NAME_REPLACE_BTN		= 'Replace existing campaign'
	
	def __init__(self):
		self.hostApp		= None
		self.testFile 		= None
		self.campaignRef 	= None
		self.outPath 		= None
		self.campaign	 	= None
		# layer1
		self.CTTRoot		= None
		# layer2
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

	def start(self, auto=True):
		# start DPCTT
		config = ConfigParser()
		config.read('test.conf', encoding='UTF-8')
		self.hostApp	= config['MISC']['HOST_APP_PATH'].strip("'") + '\FDI Package CTT\FDIPackageCTT.exe'
		self.testFile = config['MISC']['TEST_FILE'].strip("'")
		self.campaignRef = config['MISC']['HOST_APP_PATH'].strip("'") + '\FDI Package CTT\Campaigns\HART Testcampaign\hart.testcampaign.xml'
		self.campaign = config['MISC']['CTT_COMPAIGN_FILE'].strip("'")
		self.outPath = config['MISC']['OUTPUT_PATH'].strip("'") + '\dpctt'
		execCmd = '\"' + self.hostApp + '\"'
		if auto: pass
			# the following command can not load correct test suit
			#execCmd += ' --create \"' + self.testFile + '\" \"' + self.campaignRef + '\" --report'
		subprocess.Popen(execCmd, shell=True, stdout=subprocess.PIPE)
		time.sleep(CTT.DELAY_DPCTT_START)
		logging.info('execCmd = %s' % execCmd)
		# get part's node from screen
		self.CTTRoot 		= UIA.findFirstElem(UIA.DesktopRoot, CTT.NAME_DPCTT_APP, UIA.Client.UIA_NamePropertyId)
		assert UIA.isUIAElem(self.CTTRoot)
		self.TitleBar = UIA.findFirstElem(self.CTTRoot, UIA.Client.UIA_TitleBarControlTypeId, UIA.Client.UIA_ControlTypePropertyId)
		assert UIA.isUIAElem(self.TitleBar)
		self.MenuBar = UIA.getNextSiblingElem(self.TitleBar)
		assert UIA.isUIAElem(self.MenuBar)
		self.ToolBar = UIA.getNextSiblingElem(self.MenuBar)
		assert UIA.isUIAElem(self.ToolBar)
		self.CampaignView = UIA.getNextSiblingElem(self.ToolBar)
		assert UIA.isUIAElem(self.CampaignView)
		self.PropertyView = UIA.getNextSiblingElem(self.CampaignView)
		assert UIA.isUIAElem(self.PropertyView)
		self.LogView = UIA.getNextSiblingElem(self.PropertyView)
		assert UIA.isUIAElem(self.LogView)
		self.OverflowBtn = UIA.findFirstElem(self.ToolBar, CTT.NAME_OVERFLOW_BTN, UIA.Client.UIA_AutomationIdPropertyId)
		assert UIA.isUIAElem(self.OverflowBtn)
		self.Thumb = UIA.getNextSiblingElem(self.OverflowBtn)
		assert UIA.isUIAElem(self.Thumb)
		self.ExecuteBtn = UIA.getNextSiblingElem(self.Thumb)
		assert UIA.isUIAElem(self.ExecuteBtn)

	def newCampaign(self, campaign=None, ref=None):
		# open "New Test Campaign" dialog
		hwnd = win32gui.FindWindow(None, CTT.NAME_DPCTT_APP)
		win32gui.SetForegroundWindow(hwnd)
		win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)
		win32api.keybd_event(78, 0, 0, 0) # key code(N) : 78
		win32api.keybd_event(78, 0, win32con.KEYEVENTF_KEYUP, 0)
		win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)
		time.sleep(CTT.DELAY_FOR_DEMO)
		# get part's node from dialog
		dialog = UIA.findFirstElem(self.CTTRoot, CTT.NAME_NEW_COMPAIGN, UIA.Client.UIA_NamePropertyId)
		assert UIA.isUIAElem(dialog)
		pathEdit = UIA.findFirstElem(dialog, CTT.NAME_COMPAIGN_PATH, UIA.Client.UIA_AutomationIdPropertyId)
		assert UIA.isUIAElem(pathEdit)
		checkbox = UIA.findFirstElem(dialog, CTT.NAME_COMPAIGN_CHECK, UIA.Client.UIA_AutomationIdPropertyId)
		assert UIA.isUIAElem(checkbox)
		refBtn = UIA.findFirstElem(dialog, CTT.NAME_COMPAIGN_OTHER, UIA.Client.UIA_AutomationIdPropertyId)
		assert UIA.isUIAElem(refBtn)
		cancelBtn = UIA.findFirstElem(dialog, CTT.NAME_COMPAIGN_CANCEL, UIA.Client.UIA_NamePropertyId)
		assert UIA.isUIAElem(cancelBtn)
		acceptBtn = UIA.getNextSiblingElem(cancelBtn)
		assert UIA.isUIAElem(acceptBtn)
		# set campaign information and accept
		UIA.selectCheckbox(checkbox)
		time.sleep(CTT.DELAY_FOR_DEMO)
		#UIA.setEditbox(CompaignCombo, 'Official HART Test Campaign') # Readonly
		UIA.pushButton(refBtn) # It will call common dialog
		time.sleep(CTT.DELAY_FOR_DEMO)
		commonDialog = UIA.findFirstElem(dialog, UIA.Client.UIA_WindowControlTypeId, UIA.Client.UIA_ControlTypePropertyId)
		assert UIA.isUIAElem(commonDialog)
		if not ref:
			ref = self.campaignRef
		UIA.setDirInCommonDialog(commonDialog, ref)
		time.sleep(CTT.DELAY_FOR_DEMO)
		if not campaign:
			campaign = self.outPath + '\\' + self.campaign + '.xml'
		#logging.info('Output file is %s.' % campaign)
		UIA.setEditbox(pathEdit, campaign)
		time.sleep(CTT.DELAY_FOR_DEMO)
		UIA.pushButton(acceptBtn)
		time.sleep(CTT.DELAY_FOR_DEMO)
		# get part's node from dialog
		dialog = UIA.findFirstElem(self.CTTRoot, CTT.NAME_NEW_COMPAIGN, UIA.Client.UIA_NamePropertyId)
		assert UIA.isUIAElem(dialog)
		replaceBtn = UIA.findFirstElem(dialog, CTT.NAME_REPLACE_BTN, UIA.Client.UIA_NamePropertyId)
		assert UIA.isUIAElem(replaceBtn)
		UIA.pushButton(replaceBtn)
		time.sleep(CTT.DELAY_FOR_DEMO)
		dialog = UIA.findFirstElem(self.CTTRoot, CTT.NAME_NEW_COMPAIGN, UIA.Client.UIA_NamePropertyId)
		assert UIA.isUIAElem(dialog)
		yesBtn = UIA.findFirstElem(dialog, UIA.Client.UIA_ButtonControlTypeId, UIA.Client.UIA_ControlTypePropertyId)
		assert UIA.isUIAElem(yesBtn)
		UIA.pushButton(yesBtn)
		time.sleep(CTT.DELAY_SET_TO_DEV)
		
	def assignPackage(self, assignFile=None):
		# open common dialog (Assign Package) and set FDI package file
		appName = CTT.NAME_DPCTT_APP + ' - ' + self.campaign
		hwnd = win32gui.FindWindow(None, appName)
		win32gui.SetForegroundWindow(hwnd)
		win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)
		win32api.keybd_event(80, 0, 0, 0) # key code(P) : 80
		win32api.keybd_event(80, 0, win32con.KEYEVENTF_KEYUP, 0)
		win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)
		time.sleep(CTT.DELAY_FOR_DEMO)
		commonDialog = UIA.findFirstElem(self.CTTRoot, UIA.Client.UIA_WindowControlTypeId, UIA.Client.UIA_ControlTypePropertyId)
		assert UIA.isUIAElem(commonDialog)
		if not assignFile:
			assignFile = self.testFile
		UIA.setDirInCommonDialog(commonDialog, assignFile)
		time.sleep(CTT.DELAY_FOR_DEMO)
		
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
	
	def wait(self, dlgFindType=UIA.Client.UIA_ControlTypePropertyId, dlgFindKey=UIA.Client.UIA_WindowControlTypeId):
		dialog = UIA.findFirstElem(self.CTTRoot, dlgFindKey, dlgFindType)
		while not UIA.isUIAElem(dialog):
			time.sleep(CTT.DELAY_WAIT_DLG)
			dialog = UIA.findFirstElem(self.CTTRoot, dlgFindKey, dlgFindType)
		return dialog
	
	def execute(self):
		# push execute button
		UIA.pushButton(self.ExecuteBtn)
		time.sleep(CTT.DELAY_FOR_DEMO)
		# verify dialog1
		dialog = self.wait()
		assert UIA.isUIAElem(dialog)
		yesBtn = UIA.findFirstElem(dialog, '6', UIA.Client.UIA_AutomationIdPropertyId)
		assert UIA.isUIAElem(yesBtn)
		UIA.pushButton(yesBtn)
		time.sleep(CTT.DELAY_FOR_DEMO)
		# verify dialog2
		dialog = self.wait()
		assert UIA.isUIAElem(dialog)
		yesBtn = UIA.findFirstElem(dialog, '6', UIA.Client.UIA_AutomationIdPropertyId)
		assert UIA.isUIAElem(yesBtn)
		UIA.pushButton(yesBtn)
		time.sleep(CTT.DELAY_LONG_TIME) # test script in process
		# reprot info dialog
		dialog = self.wait()
		assert UIA.isUIAElem(dialog)
		reportUser = UIA.findFirstElem(dialog, CTT.NAME_REPORT_USER, UIA.Client.UIA_AutomationIdPropertyId)
		assert UIA.isUIAElem(reportUser)
		all = UIA.findAllElem(reportUser, UIA.Client.UIA_ButtonControlTypeId, UIA.Client.UIA_ControlTypePropertyId)
		acceptBtn = all.GetElement(all.Length-1)
		assert UIA.isUIAElem(acceptBtn)
		UIA.pushButton(acceptBtn)
		time.sleep(CTT.DELAY_LONG_TIME) # fake death
		# reprot preview dialog
		dialog = self.wait()
		assert UIA.isUIAElem(dialog)
		saveBtn = UIA.findFirstElem(dialog, 'Save', UIA.Client.UIA_NamePropertyId)
		assert UIA.isUIAElem(saveBtn)
		UIA.pushButton(saveBtn)
		time.sleep(CTT.DELAY_LONG_TIME) #  display process bar
		# reprot created dialog
		#dlgName = CTT.NAME_DPCTT_APP + ' - ' + self.campaign
		#dialog = UIA.findFirstElem(self.CTTRoot, dlgName, UIA.Client.UIA_NamePropertyId)
		dialog = self.wait()
		assert UIA.isUIAElem(dialog)
		confirmBtn = UIA.findFirstElem(dialog, '2', UIA.Client.UIA_AutomationIdPropertyId)
		assert UIA.isUIAElem(confirmBtn)
		UIA.pushButton(confirmBtn)
		time.sleep(CTT.DELAY_FOR_DEMO)
	
class RRTE:
	DELAY_RRET_START			= 8
	DELAY_WAIT_DLG				= 3
	NAME_RRTE_APP				= 'Reference Run-time Environment'
	NAME_TRACE_LEVEL			= 'Microsoft.Windows.Controls.Ribbon.RibbonGallery Items.Count:1'
	NAME_BROWSER_MODEL			= 'Fdi.Client.Catalog.DeviceCatalogBrowserModel'
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
		self.config = ConfigParser()
		self.config.read('test.conf', encoding='UTF-8')
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
		#config = ConfigParser()
		#config.read('test.conf', encoding='UTF-8')
		#inputMode = self.config['MISC']['TEST_FILE_TYPE'].strip("'")
		hostApp	= self.config['MISC']['HOST_APP_PATH'].strip("'") + '\Reference Run-time Environment\Fdi.Reference.Client.exe'
		testFile = self.config['MISC']['TEST_FILE'].strip("'")
		#outPath = self.config['MISC']['OUTPUT_PATH'].strip("'")
		execCmd = '\"' + hostApp + '\" -l \"' + testFile + '\"'
		subprocess.Popen(execCmd, shell=True, stdout=subprocess.PIPE, close_fds=True)
		time.sleep(RRTE.DELAY_RRET_START)
		logging.info('execCmd = %s' % execCmd)
		# find layer1 element
		self.RRTERoot = UIA.findFirstElem(UIA.DesktopRoot, RRTE.NAME_RRTE_APP, UIA.Client.UIA_NamePropertyId, scope=UIA.Client.TreeScope_Children)
		assert UIA.isUIAElem(self.RRTERoot)
		self.RRTECurr = self.RRTERoot
		# find layer2 element(work area)
		all = UIA.findAllElem(self.RRTERoot, UIA.Client.UIA_CustomControlTypeId, UIA.Client.UIA_ControlTypePropertyId, scope=UIA.Client.TreeScope_Children)
		self.WorkRoot = all.GetElement(all.Length-1)
		assert UIA.isUIAElem(self.WorkRoot)
		# find layer3 element
		self.TopTAB = UIA.findFirstElem(self.WorkRoot, RRTE.NAME_TOP_TAB, UIA.Client.UIA_NamePropertyId)
		assert UIA.isUIAElem(self.TopTAB)
		self.TopTABX = UIA.findFirstElem(self.TopTAB, RRTE.NAME_X_BTN, UIA.Client.UIA_NamePropertyId)
		assert UIA.isUIAElem(self.TopTABX)
		self.TopRoot = UIA.getNextSiblingElem(self.TopTABX)
		assert UIA.isUIAElem(self.TopRoot)
		# find layer4 element
		self.Offline = UIA.findElemBySubText(self.TopRoot, RRTE.NAME_OFFLINE_TAB)
		assert UIA.isUIAElem(self.Offline)
		self.OfflineX = UIA.findFirstElem(self.Offline, RRTE.NAME_X_BTN, UIA.Client.UIA_NamePropertyId)
		assert UIA.isUIAElem(self.OfflineX)
		self.TABRoot = UIA.findFirstElem(self.TopRoot, RRTE.NAME_ONLINE_PARAMS, UIA.Client.UIA_AutomationIdPropertyId)
		assert UIA.isUIAElem(self.TABRoot)
		self.Health = UIA.getNextSiblingElem(self.TABRoot)
		assert UIA.isUIAElem(self.Health)
		self.Explorer = UIA.findFirstElem(self.TopRoot, RRTE.NAME_TREE_ROOT, UIA.Client.UIA_AutomationIdPropertyId)
		assert UIA.isUIAElem(self.Explorer)
		#self.TreeRoot	= UIA.getNextSiblingElem(self.Explorer)
		#self.PaneRoot	= UIA.getNextSiblingElem(self.TreeRoot)
		self.Apply = UIA.findFirstElem(self.TopRoot, RRTE.NAME_APPLY_BTN, UIA.Client.UIA_NamePropertyId)
		assert UIA.isUIAElem(self.Apply)
		self.Revert = UIA.findFirstElem(self.TopRoot, RRTE.NAME_REVERT_BTN, UIA.Client.UIA_NamePropertyId)
		assert UIA.isUIAElem(self.Revert)
		# layer5
		self.Online = UIA.findElemBySubText(self.TABRoot, RRTE.NAME_ONLINE_TAB)
		assert UIA.isUIAElem(self.Online)
		self.OnlineX = UIA.findFirstElem(self.Online, RRTE.NAME_X_BTN, UIA.Client.UIA_NamePropertyId)
		assert UIA.isUIAElem(self.OnlineX)
		self.Device = UIA.findElemBySubText(self.TABRoot, RRTE.NAME_DEVICE_ROOT_MENU)
		assert UIA.isUIAElem(self.Device)
		self.DeviceX = UIA.findFirstElem(self.Device, RRTE.NAME_X_BTN, UIA.Client.UIA_NamePropertyId)
		assert UIA.isUIAElem(self.DeviceX)
		self.Diagnose = UIA.findElemBySubText(self.TABRoot, RRTE.NAME_DIAGNOSTIC_ROOT_MENU)
		assert UIA.isUIAElem(self.Diagnose)
		self.DiagnoseX = UIA.findFirstElem(self.Diagnose, RRTE.NAME_X_BTN, UIA.Client.UIA_NamePropertyId)
		assert UIA.isUIAElem(self.DiagnoseX)
		self.Maintena = UIA.findElemBySubText(self.TABRoot, RRTE.NAME_MAINT_ROOT_MENU)
		assert UIA.isUIAElem(self.Maintena)
		self.MaintenaX = UIA.findFirstElem(self.Maintena, RRTE.NAME_X_BTN, UIA.Client.UIA_NamePropertyId)
		assert UIA.isUIAElem(self.MaintenaX)
		self.Process = UIA.findElemBySubText(self.TABRoot, RRTE.NAME_PROCESS_ROOT_MENU)
		assert UIA.isUIAElem(self.Process)
		self.ProcessX = UIA.findFirstElem(self.Process, RRTE.NAME_X_BTN, UIA.Client.UIA_NamePropertyId)
		assert UIA.isUIAElem(self.ProcessX)
		# create basic root menu node
		onlineElem = Top('Online')
		onlineElem.ctrlType = 'Top'
		processElem = Top('Process variables root menu')
		processElem.ctrlType = 'Top'
		DiagElem = Top('Diagnostic root menu')
		DiagElem.ctrlType = 'Top'
		MaintElem = Top('Maintenance root menu')
		MaintElem.ctrlType = 'Top'
		DevElem = Top('Device root menu')
		DevElem.ctrlType = 'Top'
		rootNode = TreeNode(onlineElem)
		processNode = TreeNode(processElem)
		DiagNode = TreeNode(DiagElem)
		MaintNode = TreeNode(MaintElem)
		DevNode = TreeNode(DevElem)
		rootNode.left = processNode
		processNode.right = DiagNode
		DiagNode.right = MaintNode
		MaintNode.right = DevNode
		rootNode.parent = None
		processNode.parent = rootNode
		DiagNode.parent = rootNode
		MaintNode.parent = rootNode
		DevNode.parent = rootNode
		self.tree = Tree(rootNode, rootNode)

	def createNodeTree(self, selectedNode): # can't be 'Online' item
		if selectedNode == None:
			return
		assert not selectedNode.elem.name == 'Online'
		assert isinstance(selectedNode.elem, SelectableElement)
		# get current node's path
		path = []
		path.append(selectedNode)
		currNode = selectedNode
		while not currNode.parent == None:
			currNode = currNode.parent
			path.append(currNode)
		path.remove(self.tree.root)
		path.reverse()
		#for item in path:
		#	logging.info(item.elem.name)
		# push button sequence to getting into current tree node
		for item in path:
			if isinstance(item.elem, SelectableElement):
				item.elem.select(self)
			if item.isEqual(selectedNode):
				item.setChildren(self)
				logTreeItem(item)
				currNode = item.left
				if isinstance(currNode.elem, SelectableElement):
					self.createNodeTree(currNode)
				currNode = currNode.right
				while not currNode == None:
					if isinstance(currNode.elem, SelectableElement):
						self.createNodeTree(currNode)
					currNode = currNode.right
	
	def loadPackage(self):
		browser = UIA.findFirstElem(self.RRTERoot, RRTE.NAME_BROWSER_MODEL, UIA.Client.UIA_NamePropertyId)
		assert UIA.isUIAElem(browser)
		UIA.selectTab(browser)
		time.sleep(2)
		all = UIA.findAllElem(browser, UIA.Client.UIA_CustomControlTypeId, UIA.Client.UIA_ControlTypePropertyId, scope=UIA.Client.TreeScope_Children)
		custom = all.GetElement(all.Length-1)
		loadBtn = UIA.findFirstElem(custom, UIA.Client.UIA_ButtonControlTypeId, UIA.Client.UIA_ControlTypePropertyId)
		assert UIA.isUIAElem(loadBtn)
		UIA.pushButton(loadBtn)
		logging.info('Load FDI package')
		self.wait()
	
	def closeMenu(self):
		# find layer2 element(work area)
		all = UIA.findAllElem(self.RRTERoot, UIA.Client.UIA_CustomControlTypeId, UIA.Client.UIA_ControlTypePropertyId, scope=UIA.Client.TreeScope_Children)
		self.WorkRoot = all.GetElement(all.Length-1)
		assert UIA.isUIAElem(self.WorkRoot)
		# find layer3 element
		self.TopTAB = UIA.findFirstElem(self.WorkRoot, RRTE.NAME_TOP_TAB, UIA.Client.UIA_NamePropertyId)
		assert UIA.isUIAElem(self.TopTAB)
		self.TopTABX = UIA.findFirstElem(self.TopTAB, RRTE.NAME_X_BTN, UIA.Client.UIA_NamePropertyId)
		assert UIA.isUIAElem(self.TopTABX)
		UIA.pushButton(self.TopTABX)
		logging.info('Close Menu')
		time.sleep(6)
		self.wait()
	
	def close(self):
		'''
		titleBar = UIA.findFirstElem(self.RRTERoot, UIA.Client.UIA_TitleBarControlTypeId, UIA.Client.UIA_ControlTypePropertyId, scope=UIA.Client.TreeScope_Children)
		pdb.set_trace()
		assert UIA.isUIAElem(titleBar)
		closeBtn = UIA.findFirstElem(titleBar, 'Close', UIA.Client.UIA_AutomationIdPropertyId, scope=UIA.Client.TreeScope_Children)
		assert UIA.isUIAElem(closeBtn)
		UIA.pushButton(closeBtn)
		'''
		hwnd = win32gui.FindWindow(None, RRTE.NAME_RRTE_APP)
		win32gui.SetForegroundWindow(hwnd)
		win32api.keybd_event(win32con.VK_MENU, 0, 0, 0)
		win32api.keybd_event(win32con.VK_F4, 0, 0, 0)
		win32api.keybd_event(win32con.VK_F4, 0, win32con.KEYEVENTF_KEYUP, 0)
		win32api.keybd_event(win32con.VK_MENU, 0, win32con.KEYEVENTF_KEYUP, 0)
		logging.info('Close RRTE')
		time.sleep(3)
	
	def setTraceLevel(self, level):
		item = UIA.findFirstElem2And(self.RRTERoot, level, UIA.Client.UIA_NamePropertyId,UIA.Client.UIA_ListItemControlTypeId, UIA.Client.UIA_ControlTypePropertyId)
		assert UIA.isUIAElem(item)
		UIA.selectTab(item)
		logging.info('Set trace level')
		time.sleep(1)
	
	def clearRegistLog(self):
		#config = ConfigParser()
		#config.read('test.conf', encoding='UTF-8')
		#logPath = config['MISC']['RRTE_LOG_PATH'].strip("'")
		logPath = 'C:\ProgramData\FDI\Logs'
		execCmd = 'del /F /S /Q ' + logPath + '\*.*'
		os.system(execCmd)
		logging.info('Clear register log files')
		time.sleep(1)
	
	def traversal(self, targetNode):
		if not targetNode is None:
			if isinstance(targetNode.elem, Window): # TODO: Page
				self.createRegistLog(targetNode)
			self.traversal(targetNode.left)
			self.traversal(targetNode.right)
	
	def createRegistLog(self, node):
		assert not node.elem.name == 'Online'
		assert isinstance(node.elem, Window)
		# get path
		logPath = 'C:\ProgramData\FDI\Logs'
		outPath = 'D:\Work\source\guitest\demo\output'
		path = []
		path.append(node)
		currNode = node
		while not currNode.parent == None:
			currNode = currNode.parent
			path.append(currNode)
		path.remove(path[len(path)-1])
		path.reverse()
		# start RRTE and go into target window item
		self.start()
		self.setTraceLevel('Information') # Verbose
		pathName = outPath + '\\rrte'
		for item in path:
			item.elem.select(self)
			pathName += '\\' + item.elem.name
			execCmd = 'mkdir "' + pathName + '"'
			os.system(execCmd)
		time.sleep(1) # wait question mark dispear (create log)
		# make folder and copy log files
		execCmd = 'copy "' + logPath + '\\*.*" "' + pathName + '"'
		os.system(execCmd)
		time.sleep(1)
		self.close()
		self.clearRegistLog()
	
	def wait(self, dlgFindType=UIA.Client.UIA_ControlTypePropertyId, dlgFindKey=UIA.Client.UIA_WindowControlTypeId):
		dialog = UIA.findFirstElem(self.RRTERoot, dlgFindKey, dlgFindType)
		while not UIA.isUIAElem(dialog):
			time.sleep(RRTE.DELAY_WAIT_DLG)
			dialog = UIA.findFirstElem(self.RRTERoot, dlgFindKey, dlgFindType)
		return dialog

class Element: # abstract class
	def __init__(self, name):
		self.name = name
		self.ctrlType = None
		self.rectangle = None
		
	def children(self, rrte):
		pass
		
# RRTE element class
class RRTEElement(Element): # abstract class (not used in demo)
	pass

class SelectableElement(Element): # abstract class
	def select(self, rrte):
		pass

class Top(SelectableElement):
	def select(self, rrte):
		btn = UIA.findElemBySubText(rrte.TABRoot, self.name)
		UIA.pushButton(btn)
		time.sleep(3)
		rrte.Explorer = UIA.findFirstElem(rrte.TopRoot, RRTE.NAME_TREE_ROOT, UIA.Client.UIA_AutomationIdPropertyId)
		rrte.TreeRoot = UIA.getNextSiblingElem(rrte.Explorer)
		rrte.RRTECurr = rrte.TreeRoot
	
	def children(self, rrte):
		all = UIA.findAllElem(rrte.RRTECurr, UIA.Client.UIA_TreeItemControlTypeId, UIA.Client.UIA_ControlTypePropertyId, scope=UIA.Client.TreeScope_Children)
		set = []
		for x in range(0, all.Length):
			item = all.GetElement(x)
			name = UIA.getElemSubText(item)
			if UIA.isLeaf(item):
				elem = Window(name)
			else:
				elem = Menu(name)
			elem.ctrlType = 'TreeItem'
			elem.rectangle = item.CurrentBoundingRectangle
			set.append(elem)
		return set
	
class Menu(SelectableElement):
	def select(self, rrte):
		tree = UIA.findElemBySubText(rrte.RRTECurr, self.name)
		UIA.expandTree(tree)
		time.sleep(2)
		rrte.Explorer = UIA.findFirstElem(rrte.TopRoot, RRTE.NAME_TREE_ROOT, UIA.Client.UIA_AutomationIdPropertyId)
		rrte.TreeRoot = UIA.getNextSiblingElem(rrte.Explorer)
		rrte.PaneRoot = UIA.getNextSiblingElem(rrte.TreeRoot)
		rrte.RRTECurr = tree
	
	def children(self, rrte):
		all = findAllElem(rrte.RRTECurr, UIA.Client.UIA_TreeItemControlTypeId, UIA.Client.UIA_ControlTypePropertyId, scope=UIA.Client.TreeScope_Children)
		set = []
		for x in range(0, all.Length):
			item = all.GetElement(x)
			elem = Window(UIA.getElemSubText(item))
			elem.ctrlType = 'TreeItem'
			elem.rectangle = item.CurrentBoundingRectangle
			set.append(elem)
		return set

class Window(SelectableElement):
	def select(self, rrte):
		leaf = UIA.findElemBySubText(rrte.RRTECurr, self.name)
		UIA.pushLeaf(leaf)
		time.sleep(3)
		rrte.Explorer = UIA.findFirstElem(rrte.TopRoot, RRTE.NAME_TREE_ROOT, UIA.Client.UIA_AutomationIdPropertyId)
		rrte.TreeRoot = UIA.getNextSiblingElem(rrte.Explorer)
		rrte.PaneRoot = UIA.getNextSiblingElem(rrte.TreeRoot)
		rrte.RRTECurr = rrte.PaneRoot
	
	def children(self, rrte):
		all = UIA.findAllElem4Or(rrte.RRTECurr, UIA.Client.UIA_CustomControlTypeId, UIA.Client.UIA_ButtonControlTypeId, UIA.Client.UIA_GroupControlTypeId, UIA.Client.UIA_TabControlTypeId, UIA.Client.UIA_ControlTypePropertyId, scope=UIA.Client.TreeScope_Children)
		set = []
		for x in range(0, all.Length):
			item = all.GetElement(x)
			if item.CurrentControlType == UIA.Client.UIA_CustomControlTypeId: # variable
				elem = self.createParam(item)
				elem.ctrlType = 'Custom'
			elif item.CurrentControlType == UIA.Client.UIA_ButtonControlTypeId: # method
				elem = Method(UIA.getElemSubText(item))
				elem.ctrlType = 'Button'
			elif item.CurrentControlType == UIA.Client.UIA_GroupControlTypeId: # group
				elem = Group(UIA.getElemSubText(item))
				elem.ctrlType = 'Group'
			elif item.CurrentControlType == UIA.Client.UIA_TabControlTypeId: # tab
				elem = Page('')
				elem.ctrlType = 'Tab'
			elem.rectangle = item.CurrentBoundingRectangle
			set.append(elem)
		return set
	
	def createParam(self, uiaElem):
		editbox = UIA.findFirstElem(uiaElem, 'Value', UIA.Client.UIA_AutomationIdPropertyId, scope=UIA.Client.TreeScope_Children)
		if not UIA.isUIAElem(editbox):
			group = UIA.findFirstElem(uiaElem, UIA.Client.UIA_GroupControlTypeId, UIA.Client.UIA_ControlTypePropertyId, scope=UIA.Client.TreeScope_Children)
			return BitEnum(UIA.getElemSubText(group))
		elif editbox.CurrentControlType == UIA.Client.UIA_EditControlTypeId:
			return Data(UIA.getElemSubText(uiaElem))
		elif editbox.CurrentControlType == UIA.Client.UIA_ComboBoxControlTypeId:
			return Enum(UIA.getElemSubText(uiaElem))

class Page(SelectableElement):
	def select(self, rrte):
		tab = UIA.findElemBySubText(rrte.PaneRoot, self.name)
		UIA.selectTab(tab)
		time.sleep(2)
		rrte.Explorer = UIA.findFirstElem(rrte.TopRoot, RRTE.NAME_TREE_ROOT, UIA.Client.UIA_AutomationIdPropertyId)
		rrte.TreeRoot = UIA.getNextSiblingElem(rrte.Explorer)
		rrte.PaneRoot = UIA.getNextSiblingElem(rrte.TreeRoot)
		rrte.RRTECurr = tab

class Group(Element):
	pass

class Param(Element): # abstract class
	def __init__(self, label, mode='RO', edit='None', unit=''):
		Element.__init__(self, label)
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
	# get hart register log from RRTE 
	rrte = RRTE()
	rrte.start()
	rrte.createNodeTree(rrte.tree.root.left)
	#rrte.closeMenu()
	rrte.close()
	rrte.clearRegistLog()
	rrte.traversal(rrte.tree.root.left)
	# get hart register report from DPCTT 
	dpctt = CTT()
	dpctt.start(False)
	dpctt.newCampaign()
	dpctt.assignPackage()
	logging.info('Please deactive same test suits.')
	pdb.set_trace()
	dpctt.execute()
	#dpctt.setReportInfo()
