import pdb
import logging
import time
import subprocess
import xlrd
#import comtypes
from configparser import ConfigParser
from comtypes.client import *
from ctypes import *

UIAutomationClient = GetModule('UIAutomationCore.dll')
IUIAutomation = CreateObject('{ff48dba4-60ef-4201-aa87-54103eef594e}', interface=UIAutomationClient.IUIAutomation)

def searchOneElement(startNode, key, type,
					 flag = UIAutomationClient.PropertyConditionFlags_None,
					 scope = UIAutomationClient.TreeScope_Descendants):
	cnd = IUIAutomation.CreatePropertyConditionEx(type, key, flag)
	element = startNode.FindFirst(scope, cnd)
	logging.info('[%s]Element[%s] is searched.' % (element.CurrentProcessId, element.CurrentName))
	return element

def searchAllElement(startNode, key, type,
					 flag = UIAutomationClient.PropertyConditionFlags_None,
					 scope = UIAutomationClient.TreeScope_Descendants):
	cnd = IUIAutomation.CreatePropertyConditionEx(type, key, flag)
	all = startNode.FindAll(scope, cnd)
	size = all.Length
	logging.info('Parameter Array size = %d' % size)
	for x in range(0, size):
	  element = all.GetElement(x)
	  logging.info('[%s]Element1[%s] is searched.' % (element.CurrentProcessId, element.CurrentName))
	return all

def seekParentElement(currentElement):
	walker = IUIAutomation.ControlViewWalker
	parent = walker.GetParentElement(currentElement)
	return parent

def GetNextSiblingElem(elem):
	walker = IUIAutomation.ControlViewWalker
	element = walker.GetNextSiblingElement(elem)
	return element

def GetPreviousSiblingElem(elem):
	walker = IUIAutomation.ControlViewWalker
	element = walker.GetPreviousSiblingElement(elem)
	return element
	
def compareLabel(specLabel, appLabel):
	#logging.info('specLabel is [%s]. appLabel is [%s]' % (specLabel, appLabel))
	return (specLabel == appLabel)
	
def isError():
	root = IUIAutomation.GetRootElement()
	rrteRoot = searchOneElement(root, 'Reference Run-time Environment', UIAutomationClient.UIA_NamePropertyId)
	all = searchAllElement(rrteRoot, UIAutomationClient.UIA_WindowControlTypeId, UIAutomationClient.UIA_ControlTypePropertyId)
	size = all.Length
	logging.info('found windows count = %d' % size)
	pdb.set_trace()
	if win is None:
		pass
	else:
		OKBtn = searchOneElement(win, 'OK', UIAutomationClient.UIA_NamePropertyId)
		pattern = OKBtn.GetCurrentPattern(UIAutomationClient.UIA_InvokePatternId)
		ctrl = cast(pattern, POINTER(UIAutomationClient.IUIAutomationInvokePattern))
		ctrl.Invoke()
		return 1
	
'''
def isValidData(img):
	#time.sleep(DELAY_OPEN_RRET)
	#image = GetPreviousSiblingElem(textbox)
	#parent = seekParentElement(image)
	#grand = seekParentElement(parent)
	#parent.SetFocus()
	#grand.SetFocus()
	#textbox.SetFocus()
	#logging.info('textb class name = %s, help text = %s, process id = %s' % (textbox.CurrentClassName, textbox.CurrentHelpText, textbox.CurrentProcessId))
	parent = seekParentElement(img)
	image = searchOneElement(parent, 'Icon', UIAutomationClient.UIA_AutomationIdPropertyId)
	parent = seekParentElement(image)
	image = searchOneElement(parent, 'Icon', UIAutomationClient.UIA_AutomationIdPropertyId)
	parent = seekParentElement(image)
	image = searchOneElement(parent, 'Icon', UIAutomationClient.UIA_AutomationIdPropertyId)
	logging.info('Image class name = %s, help text = %s, automation id = %s' % (image.CurrentClassName, image.CurrentHelpText, image.CurrentAutomationId))
	pdb.set_trace()
	result = compareLabel(image.CurrentHelpText, '') or compareLabel(image.CurrentHelpText, 'The Value has been modified in the EditContext and is not yet in the Device.')
	return result	
'''

if __name__ == '__main__':
	# Define const and parameter
	DELAY_OPEN_RRET				= 6
	DELAY_PUSH_BUTTON			= 4
	DELAY_FOR_DEMO				= 3
	MAX_MENU_ITEM_NUM			= 28
	MENU_ITEM_TYPE_COLUMN		= 6
	MENU_ITEM_RW_COLUMN			= 7
	MENU_ITEM_MIN_COLUMN		= 10
	MENU_ITEM_MAX_COLUMN		= 11
	label						= [''] * MAX_MENU_ITEM_NUM
	type						= [''] * MAX_MENU_ITEM_NUM
	rw							= ['RO'] * MAX_MENU_ITEM_NUM
	max							= [float('inf')] * MAX_MENU_ITEM_NUM
	min							= [float('-inf')] * MAX_MENU_ITEM_NUM
	
	#pdb.set_trace()
	logging.basicConfig(level = logging.INFO)
	
	# Load and parser config file
	logging.info('***********************************************************')
	logging.info('****** Load and parser config file')
	logging.info('***********************************************************')
	config = ConfigParser()
	config.read('testRrte.conf', encoding='UTF-8')
	
	inputMode	= config['MISC']['TEST_FILE_TYPE'].strip("'")
	hostApp		= config['MISC']['HOST_APP_FILE'].strip("'")
	specFile	= config['MISC']['INPUT_SPEC_FILE'].strip("'")
	testFile	= config['MISC']['TEST_FILE'].strip("'")
	outPath		= config['MISC']['OUTPUT_PATH'].strip("'")
	
	logging.info('inputMode = %s' % inputMode)
	logging.info('hostApp = %s' % hostApp)
	logging.info('specFile = %s' % specFile)
	logging.info('testFile = %s' % testFile)
	logging.info('outPath = %s' % outPath)
	
	# Startup RRTE and load target FDI package or EDD file
	logging.info('')
	logging.info('***********************************************************')
	logging.info('****** Startup RRTE and load target FDI package or EDD file')
	logging.info('***********************************************************')
	#import os
	#execCmd = '\"\"' + hostApp + '\" -l \"' + testFile + '\" &\"'
	#os.system(execCmd)
	execCmd = '\"' + hostApp + '\" -l \"' + testFile + '\"'
	logging.info('execCmd = %s' % execCmd)
	subprocess.Popen(execCmd, shell=True, stdout=subprocess.PIPE)
	time.sleep(DELAY_OPEN_RRET)
	
	# Read spec. file (Excel, unified format)
	logging.info('')
	logging.info('***********************************************************')
	logging.info('****** Read spec. file (Excel, unified format)')
	logging.info('***********************************************************')
	excel = xlrd.open_workbook(specFile)
	sheet = excel.sheet_by_name('Spec')
	totalRow = sheet.nrows - 1
	logging.info('totalRow = %d' % totalRow)
	
	for currRow in range(1, totalRow+1):
		for currCol in range(MENU_ITEM_TYPE_COLUMN):
			label[currRow-1] += sheet.cell(currRow, currCol).value
		type[currRow-1] = sheet.cell(currRow, MENU_ITEM_TYPE_COLUMN).value;
		rw[currRow-1] = sheet.cell(currRow, MENU_ITEM_RW_COLUMN).value;
		if (not sheet.cell(currRow, MENU_ITEM_MIN_COLUMN).value == ''):
			min[currRow-1] = float(sheet.cell(currRow, MENU_ITEM_MIN_COLUMN).value);
		if (not sheet.cell(currRow, MENU_ITEM_MAX_COLUMN).value == ''):
			max[currRow-1] = float(sheet.cell(currRow, MENU_ITEM_MAX_COLUMN).value);
		logging.info('No.%d, (Label = %s, Type = %s, Min = %.2f, Max = %.2f)' % (currRow-1, label[currRow-1], type[currRow-1], min[currRow-1], max[currRow-1]))

	# Start UI Automation
	logging.info('')
	logging.info('***********************************************************')
	logging.info('****** Start UI Automation')
	logging.info('***********************************************************')
	#UIAutomationClient = GetModule('UIAutomationCore.dll')
	#IUIAutomation = CreateObject('{ff48dba4-60ef-4201-aa87-54103eef594e}', interface=UIAutomationClient.IUIAutomation)
	root = IUIAutomation.GetRootElement()
	rrteRoot = searchOneElement(root, 'Reference Run-time Environment', UIAutomationClient.UIA_NamePropertyId)
	logging.info('RRTE window root: Class name = %s, Name = %s, Bounding Rectangle = %s, Process ID = %d' % (rrteRoot.CurrentClassName, rrteRoot.CurrentName, rrteRoot.CurrentBoundingRectangle, rrteRoot.CurrentProcessId))
	
	# Push "Online" TAB
	logging.info('')
	logging.info('***********************************************************')
	logging.info('****** Push [Online] TAB')
	logging.info('***********************************************************')
	txt = searchOneElement(root, 'Online', UIAutomationClient.UIA_NamePropertyId)
	btnOnline = seekParentElement(txt)
	pattern = btnOnline.GetCurrentPattern(UIAutomationClient.UIA_InvokePatternId)
	ctrl = cast(pattern, POINTER(UIAutomationClient.IUIAutomationInvokePattern))
	ctrl.Invoke()
	time.sleep(DELAY_PUSH_BUTTON)
	
	# Get the menu tree root node (ControlType:"ControlType.Tree")
	logging.info('')
	logging.info('***********************************************************')
	logging.info('****** Get the menu tree root node')
	logging.info('***********************************************************')
	txt = searchOneElement(root, 'download_to_device_root_menu', UIAutomationClient.UIA_NamePropertyId)
	parent = seekParentElement(txt)
	menuTreeRoot = seekParentElement(parent)
	
	# Check menu and parameter labels
	logging.info('')
	logging.info('***********************************************************')
	logging.info('****** Check menu and parameter labels')
	logging.info('***********************************************************')
	print('--- Check menu and parameter labels. ---')
	for currRow in range(1, totalRow - 1):
		if (type[currRow] == 'Menu' and type[currRow+1] == 'Menu'):
			logging.info('Comparing the menu label[%s].' % label[currRow])
			txt = None
			txt = searchOneElement(menuTreeRoot, label[currRow], UIAutomationClient.UIA_NamePropertyId)
			if (txt is None):
				print('!!! Failed: Menu label [%s] does not exist!' % label[currRow])
			else:
				parent = seekParentElement(txt)
				toggle = searchOneElement(parent, UIAutomationClient.UIA_ButtonControlTypeId, UIAutomationClient.UIA_ControlTypePropertyId)
				pattern = toggle.GetCurrentPattern(UIAutomationClient.UIA_TogglePatternId)
				ctrl = cast(pattern, POINTER(UIAutomationClient.IUIAutomationTogglePattern))
				ctrl.Toggle()
				time.sleep(DELAY_FOR_DEMO)
		elif (type[currRow] == 'Menu' and type[currRow+1] != 'Menu'):
			logging.info('Comparing the menu label[%s].' % label[currRow])
			paramStartRow = currRow + 1;
			txt = None
			txt = searchOneElement(menuTreeRoot, label[currRow], UIAutomationClient.UIA_NamePropertyId)
			if (txt is None):
				print('!!! Failed: Menu label [%s] does not exist!' % label[currRow])
			else:
				item = seekParentElement(txt)
				pattern = item.GetCurrentPattern(UIAutomationClient.UIA_SelectionItemPatternId)
				ctrl = cast(pattern, POINTER(UIAutomationClient.IUIAutomationSelectionItemPattern))
				ctrl.Select()
				time.sleep(DELAY_PUSH_BUTTON)
				logging.info('Comparing labels under menu item[%s].' % label[currRow])
				line = searchOneElement(rrteRoot, 'Fdi.Ui.ViewModel.Content.NumericParameterViewModel', UIAutomationClient.UIA_NamePropertyId)
				pane = seekParentElement(line)
				logging.info('paramStartRow = %d' % paramStartRow)
				all = searchAllElement(pane, 'Label', UIAutomationClient.UIA_AutomationIdPropertyId)
				for x in range(paramStartRow, totalRow):
					if (type[x] == 'Menu'):
						break;
					if (not compareLabel(label[x], all.GetElement(x-paramStartRow).CurrentName)):
						print('!!! Failed: Param label [%s] does not exist!' % label[x])
		#else:
	
	# Check data limits (Hi/Lo alarm hysteresis : Max=10, Min=0)
	logging.info('')
	logging.info('***********************************************************')
	logging.info('****** Check data limits (Hi/Lo alarm hysteresis : Max=10, Min=0)')
	logging.info('***********************************************************')
	print('--- Check data limits (Hi/Lo alarm hysteresis) ---')
	txt = searchOneElement(menuTreeRoot, 'Maintenance root menu', UIAutomationClient.UIA_NamePropertyId)
	item = seekParentElement(txt)
	pattern = item.GetCurrentPattern(UIAutomationClient.UIA_SelectionItemPatternId)
	ctrl = cast(pattern, POINTER(UIAutomationClient.IUIAutomationSelectionItemPattern))
	ctrl.Select()
	time.sleep(DELAY_FOR_DEMO)
	txt = searchOneElement(item, 'High/Low alarm configuration', UIAutomationClient.UIA_NamePropertyId)
	item = seekParentElement(txt)
	pattern = item.GetCurrentPattern(UIAutomationClient.UIA_SelectionItemPatternId)
	ctrl = cast(pattern, POINTER(UIAutomationClient.IUIAutomationSelectionItemPattern))
	ctrl.Select()
	time.sleep(DELAY_FOR_DEMO)
	paneRoot = GetNextSiblingElem(menuTreeRoot)
	RevertBtn = GetNextSiblingElem(paneRoot)
	ApplyBtn = GetNextSiblingElem(RevertBtn)
	pattern = ApplyBtn.GetCurrentPattern(UIAutomationClient.UIA_InvokePatternId)
	ctrlApplyBtn = cast(pattern, POINTER(UIAutomationClient.IUIAutomationInvokePattern))
	txt = searchOneElement(paneRoot, 'Hi/Lo alarm hysteresis', UIAutomationClient.UIA_NamePropertyId)
	paramLine = seekParentElement(txt)
	textbox = searchOneElement(paramLine, 'Value', UIAutomationClient.UIA_AutomationIdPropertyId)
	pattern = textbox.GetCurrentPattern(UIAutomationClient.UIA_ValuePatternId)
	ctrlTextbox = cast(pattern, POINTER(UIAutomationClient.IUIAutomationValuePattern))
	# Test max value
	target = int(max[totalRow-1])
	logging.info('Test max.  value : %s' % str(target))
	textbox.SetFocus()
	ctrlTextbox.SetValue(str(target))
	paneRoot.SetFocus()
	ctrlApplyBtn.Invoke()
	if isError():
		print('!!! Failed: Input Data (%s) overflow!' % str(target))
	time.sleep(DELAY_FOR_DEMO)
	# Test min value
	target = int(min[totalRow-1])
	logging.info('Test min.  value : %s.' % str(target))
	textbox.SetFocus()
	ctrlTextbox.SetValue(str(target))
	paneRoot.SetFocus()
	ctrlApplyBtn.Invoke()
	if isError():
		print('!!! Failed: Input Data (%s) overflow!' % str(target))
	time.sleep(DELAY_FOR_DEMO)
		
	'''
	image = GetPreviousSiblingElem(textbox)
	# Test legal value
	value = searchOneElement(textbox, UIAutomationClient.UIA_TextControlTypeId, UIAutomationClient.UIA_ControlTypePropertyId)
	temp = value.CurrentName
	tempValue = str(int(temp) + 1)
	pattern = textbox.GetCurrentPattern(UIAutomationClient.UIA_ValuePatternId)
	ctrlTextbox = cast(pattern, POINTER(UIAutomationClient.IUIAutomationValuePattern))
	#ctrlTextbox.SetValue(tempValue)
	#paneRoot.SetFocus()
	#time.sleep(DELAY_FOR_DEMO)
	target = int((max[totalRow-1] + min[totalRow-1]) / 4)
	logging.info('Test legal value : %s' % str(target))
	ctrlTextbox.SetValue(str(target))
	if isValidData(image):
		paneRoot.SetFocus()
		ctrlApplyBtn.Invoke()
	else:
		print('!!! Failed: Input Data (%s) overflow!' % str(target))
	time.sleep(DELAY_FOR_DEMO)
	# Test max value
	target = int(max[totalRow-1])
	logging.info('Test max.  value : %s' % str(target))
	textbox.SetFocus()
	ctrlTextbox.SetValue(str(target))
	paneRoot.SetFocus()
	if isValidData(image):
		ctrlApplyBtn.Invoke()
	else:
		print('!!! Failed: Input Data (%s) overflow!' % str(target))
	time.sleep(DELAY_FOR_DEMO)
	# Test min value
	target = int(min[totalRow-1])
	logging.info('Test min.  value : %s.' % str(target))
	textbox.SetFocus()
	ctrlTextbox.SetValue(str(target))
	paneRoot.SetFocus()
	if isValidData(image):
		ctrlApplyBtn.Invoke()
	else:
		print('!!! Failed: Input Data (%s) overflow!' % str(target))
	time.sleep(DELAY_FOR_DEMO)
	# Test max value + 1
	target = int(max[totalRow-1])+1
	logging.info('Test max.  value + 1 : %s.' % str(target))
	textbox.SetFocus()
	ctrlTextbox.SetValue(str(target))
	paneRoot.SetFocus()
	if isValidData(image):
		ctrlApplyBtn.Invoke()
	else:
		print('!!! Failed: Input Data (%s) overflow!' % str(target))
	time.sleep(DELAY_FOR_DEMO)
	'''
	