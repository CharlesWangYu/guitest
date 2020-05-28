import pdb
import logging
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
		assert UIA.isUIAElem(elem)
		pattern = elem.GetCurrentPattern(UIA.Client.UIA_ValuePatternId)
		ctrl = cast(pattern, POINTER(UIA.Client.IUIAutomationValuePattern))
		elem.SetFocus()
		ctrl.SetValue(text)

	@staticmethod
	def pushButton(elem):
		assert UIA.isUIAElem(elem)
		pattern = elem.GetCurrentPattern(UIA.Client.UIA_InvokePatternId)
		ctrl = cast(pattern, POINTER(UIA.Client.IUIAutomationInvokePattern))
		ctrl.Invoke()
	
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
		time.sleep(CTT.DELAY_LONG_LONG) # fake death
		time.sleep(CTT.DELAY_LONG_LONG)
		# reprot preview dialog
		dialog = self.wait()
		assert UIA.isUIAElem(dialog)
		saveBtn = UIA.findFirstElem(dialog, 'Save', UIA.Client.UIA_NamePropertyId)
		assert UIA.isUIAElem(saveBtn)
		UIA.pushButton(saveBtn)
		time.sleep(CTT.DELAY_LONG_LONG) #  display process bar
		time.sleep(CTT.DELAY_LONG_LONG)
		time.sleep(CTT.DELAY_LONG_LONG)
		# reprot created dialog
		#dlgName = CTT.NAME_DPCTT_APP + ' - ' + self.campaign
		#dialog = UIA.findFirstElem(self.CTTRoot, dlgName, UIA.Client.UIA_NamePropertyId)
		dialog = self.wait()
		assert UIA.isUIAElem(dialog)
		confirmBtn = UIA.findFirstElem(dialog, '2', UIA.Client.UIA_AutomationIdPropertyId)
		assert UIA.isUIAElem(confirmBtn)
		UIA.pushButton(confirmBtn)
		time.sleep(CTT.DELAY_FOR_DEMO)
		pdb.set_trace()
	
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
	dpctt.execute()
	#dpctt.setReportInfo()

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