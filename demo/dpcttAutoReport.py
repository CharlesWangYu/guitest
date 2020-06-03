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
		time.sleep(CTT.DELAY_SET_TO_DEV)
		# get part's node from dialog
		dialog = UIA.findFirstElem(self.CTTRoot, CTT.NAME_NEW_COMPAIGN, UIA.Client.UIA_NamePropertyId)
		if UIA.isUIAElem(dialog):
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
		time.sleep(CTT.DELAY_FOR_DEMO) # test script in process
		# reprot info dialog
		dialog = self.wait()
		assert UIA.isUIAElem(dialog)
		reportUser = UIA.findFirstElem(dialog, CTT.NAME_REPORT_USER, UIA.Client.UIA_AutomationIdPropertyId)
		assert UIA.isUIAElem(reportUser)
		all = UIA.findAllElem(reportUser, UIA.Client.UIA_ButtonControlTypeId, UIA.Client.UIA_ControlTypePropertyId)
		acceptBtn = all.GetElement(all.Length-1)
		assert UIA.isUIAElem(acceptBtn)
		UIA.pushButton(acceptBtn)
		time.sleep(CTT.DELAY_FOR_DEMO) # fake death
		# reprot preview dialog
		dialog = self.wait()
		assert UIA.isUIAElem(dialog)
		saveBtn = UIA.findFirstElem(dialog, 'Save', UIA.Client.UIA_NamePropertyId)
		assert UIA.isUIAElem(saveBtn)
		UIA.pushButton(saveBtn)
		time.sleep(CTT.DELAY_FOR_DEMO) #  display process bar
		# reprot created dialog
		#dlgName = CTT.NAME_DPCTT_APP + ' - ' + self.campaign
		#dialog = UIA.findFirstElem(self.CTTRoot, dlgName, UIA.Client.UIA_NamePropertyId)
		dialog = self.wait()
		assert UIA.isUIAElem(dialog)
		confirmBtn = UIA.findFirstElem(dialog, '2', UIA.Client.UIA_AutomationIdPropertyId)
		assert UIA.isUIAElem(confirmBtn)
		UIA.pushButton(confirmBtn)
		time.sleep(CTT.DELAY_FOR_DEMO)

if __name__ == '__main__':
	#pdb.set_trace()
	logging.basicConfig(level = logging.INFO)
	# get hart register report from DPCTT 
	dpctt = CTT()
	dpctt.start(False)
	dpctt.newCampaign()
	dpctt.assignPackage()
	logging.info('Please deactive same test suits.')
	pdb.set_trace()
	dpctt.execute()
	#dpctt.setReportInfo()
