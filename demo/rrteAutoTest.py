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

def FindAllElem(start, key, type, flag=UIAutomationClient.PropertyConditionFlags_None, scope=UIAutomationClient.TreeScope_Descendants):
	cnd = IUIAutomation.CreatePropertyConditionEx(type, key, flag)
	all = start.FindAll(scope, cnd)
	logging.info('Element Array size = %d' % all.Length)
	for x in range(0, all.Length):
		element = all.GetElement(x)
		logging.info('Element[%s] is searched.' % element.CurrentName)
	return all

def FindOneElem(start, key, type, flag=UIAutomationClient.PropertyConditionFlags_None, scope=UIAutomationClient.TreeScope_Descendants):
	cnd = IUIAutomation.CreatePropertyConditionEx(type, key, flag)
	element = start.FindFirst(scope, cnd)
	logging.info('Element[%s] is searched.' % element.CurrentName)
	return element

def GetParentElem(elem):
	walker = IUIAutomation.ControlViewWalker
	parent = walker.GetParentElement(elem)
	return parent

def GetNextSiblingElem(elem):
	walker = IUIAutomation.ControlViewWalker
	element = walker.GetNextSiblingElement(elem)
	return element

def GetPreviousSiblingElem(elem):
	walker = IUIAutomation.ControlViewWalker
	element = walker.GetPreviousSiblingElement(elem)
	return element

def FindElemBySubText(start, name, flag=UIAutomationClient.PropertyConditionFlags_None, scope=UIAutomationClient.TreeScope_Descendants):
	cnd = IUIAutomation.CreatePropertyConditionEx(UIAutomationClient.UIA_NamePropertyId, name, flag)
	child = start.FindFirst(scope, cnd)
	element = GetParentElem(child)
	return element

def GetTextboxCurrentVal(elem):
	text = FindOneElem(elem, UIAutomationClient.UIA_TextControlTypeId, UIAutomationClient.UIA_ControlTypePropertyId)
	return text.CurrentName

def isFoundElem(elem):
	try:
		temp = elem.CurrentName
		return 1
	except Exception as e:
		return 0

def isSetError(textbox, setVal):
	currVal = GetTextboxCurrentVal(textbox)
	if not currVal == setVal:
		return 1
	else:
		# Push [Apply] button
		paneRoot = GetParentElem(GetParentElem(textbox))
		RevertBtn = GetNextSiblingElem(paneRoot)
		ApplyBtn = GetNextSiblingElem(RevertBtn)
		pattern = ApplyBtn.GetCurrentPattern(UIAutomationClient.UIA_InvokePatternId)
		ctrlApplyBtn = cast(pattern, POINTER(UIAutomationClient.IUIAutomationInvokePattern))
		ctrlApplyBtn.Invoke()
		# Test error dialog
		root = IUIAutomation.GetRootElement()
		rrteRoot = FindOneElem(root, 'Reference Run-time Environment', UIAutomationClient.UIA_NamePropertyId)
		win = FindOneElem(rrteRoot, UIAutomationClient.UIA_WindowControlTypeId, UIAutomationClient.UIA_ControlTypePropertyId)
		#pdb.set_trace()
		if isFoundElem(win):
			OKBtn = FindOneElem(win, 'OK', UIAutomationClient.UIA_NamePropertyId)
			pattern = OKBtn.GetCurrentPattern(UIAutomationClient.UIA_InvokePatternId)
			ctrl = cast(pattern, POINTER(UIAutomationClient.IUIAutomationInvokePattern))
			ctrl.Invoke()
			return 1
		else:
			return 0
'''
def isValidData(img):
	#time.sleep(DELAY_OPEN_RRET)
	#image = GetPreviousSiblingElem(textbox)
	#parent = GetParentElem(image)
	#grand = GetParentElem(parent)
	#parent.SetFocus()
	#grand.SetFocus()
	#textbox.SetFocus()
	#logging.info('textb class name = %s, help text = %s, process id = %s' % (textbox.CurrentClassName, textbox.CurrentHelpText, textbox.CurrentProcessId))
	parent = GetParentElem(img)
	image = FindOneElem(parent, 'Icon', UIAutomationClient.UIA_AutomationIdPropertyId)
	parent = GetParentElem(image)
	image = FindOneElem(parent, 'Icon', UIAutomationClient.UIA_AutomationIdPropertyId)
	parent = GetParentElem(image)
	image = FindOneElem(parent, 'Icon', UIAutomationClient.UIA_AutomationIdPropertyId)
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
	logging.basicConfig(level = logging.ERROR)
	
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
	rrteRoot = FindOneElem(root, 'Reference Run-time Environment', UIAutomationClient.UIA_NamePropertyId)
	logging.info('RRTE window root: Class name = %s, Name = %s, Bounding Rectangle = %s, Process ID = %d' % (rrteRoot.CurrentClassName, rrteRoot.CurrentName, rrteRoot.CurrentBoundingRectangle, rrteRoot.CurrentProcessId))
	
	# Push "Online" TAB
	logging.info('')
	logging.info('***********************************************************')
	logging.info('****** Push [Online] TAB')
	logging.info('***********************************************************')
	txt = FindOneElem(root, 'Online', UIAutomationClient.UIA_NamePropertyId)
	btnOnline = GetParentElem(txt)
	pattern = btnOnline.GetCurrentPattern(UIAutomationClient.UIA_InvokePatternId)
	ctrl = cast(pattern, POINTER(UIAutomationClient.IUIAutomationInvokePattern))
	ctrl.Invoke()
	time.sleep(DELAY_PUSH_BUTTON)
	
	# Get the menu tree root node (ControlType:"ControlType.Tree")
	logging.info('')
	logging.info('***********************************************************')
	logging.info('****** Get the menu tree root node')
	logging.info('***********************************************************')
	txt = FindOneElem(root, 'download_to_device_root_menu', UIAutomationClient.UIA_NamePropertyId)
	parent = GetParentElem(txt)
	menuTreeRoot = GetParentElem(parent)
	
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
			txt = FindOneElem(menuTreeRoot, label[currRow], UIAutomationClient.UIA_NamePropertyId)
			if (txt is None):
				print('!!! Failed: Menu label [%s] does not exist!' % label[currRow])
			else:
				parent = GetParentElem(txt)
				toggle = FindOneElem(parent, UIAutomationClient.UIA_ButtonControlTypeId, UIAutomationClient.UIA_ControlTypePropertyId)
				pattern = toggle.GetCurrentPattern(UIAutomationClient.UIA_TogglePatternId)
				ctrl = cast(pattern, POINTER(UIAutomationClient.IUIAutomationTogglePattern))
				ctrl.Toggle()
				time.sleep(DELAY_FOR_DEMO)
		elif (type[currRow] == 'Menu' and type[currRow+1] != 'Menu'):
			logging.info('Comparing the menu label[%s].' % label[currRow])
			paramStartRow = currRow + 1;
			txt = None
			txt = FindOneElem(menuTreeRoot, label[currRow], UIAutomationClient.UIA_NamePropertyId)
			if (txt is None):
				print('!!! Failed: Menu label [%s] does not exist!' % label[currRow])
			else:
				item = GetParentElem(txt)
				pattern = item.GetCurrentPattern(UIAutomationClient.UIA_SelectionItemPatternId)
				ctrl = cast(pattern, POINTER(UIAutomationClient.IUIAutomationSelectionItemPattern))
				ctrl.Select()
				time.sleep(DELAY_PUSH_BUTTON)
				logging.info('Comparing labels under menu item[%s].' % label[currRow])
				line = FindOneElem(rrteRoot, 'Fdi.Ui.ViewModel.Content.NumericParameterViewModel', UIAutomationClient.UIA_NamePropertyId)
				pane = GetParentElem(line)
				logging.info('paramStartRow = %d' % paramStartRow)
				all = FindAllElem(pane, 'Label', UIAutomationClient.UIA_AutomationIdPropertyId)
				for x in range(paramStartRow, totalRow):
					if (type[x] == 'Menu'):
						break;
					if not label[x] == all.GetElement(x-paramStartRow).CurrentName:
						print('!!! Failed: Param label [%s] does not exist!' % label[x])
		#else:
	
	# Check data limits (Hi/Lo alarm hysteresis : Max=10, Min=0)
	logging.info('')
	logging.info('***********************************************************')
	logging.info('****** Check data limits (Hi/Lo alarm hysteresis : Max=10, Min=0)')
	logging.info('***********************************************************')
	print('--- Check data limits (Hi/Lo alarm hysteresis) ---')
	txt = FindOneElem(menuTreeRoot, 'Maintenance root menu', UIAutomationClient.UIA_NamePropertyId)
	item = GetParentElem(txt)
	pattern = item.GetCurrentPattern(UIAutomationClient.UIA_SelectionItemPatternId)
	ctrl = cast(pattern, POINTER(UIAutomationClient.IUIAutomationSelectionItemPattern))
	ctrl.Select()
	time.sleep(DELAY_FOR_DEMO)
	txt = FindOneElem(item, 'High/Low alarm configuration', UIAutomationClient.UIA_NamePropertyId)
	item = GetParentElem(txt)
	pattern = item.GetCurrentPattern(UIAutomationClient.UIA_SelectionItemPatternId)
	ctrl = cast(pattern, POINTER(UIAutomationClient.IUIAutomationSelectionItemPattern))
	ctrl.Select()
	time.sleep(DELAY_FOR_DEMO)
	# Get editbox value
	paneRoot = GetNextSiblingElem(menuTreeRoot)
	txt = FindOneElem(paneRoot, 'Hi/Lo alarm hysteresis', UIAutomationClient.UIA_NamePropertyId)
	paramLine = GetParentElem(txt)
	textbox = FindOneElem(paramLine, 'Value', UIAutomationClient.UIA_AutomationIdPropertyId)
	pattern = textbox.GetCurrentPattern(UIAutomationClient.UIA_ValuePatternId)
	ctrlTextbox = cast(pattern, POINTER(UIAutomationClient.IUIAutomationValuePattern))
	# Test max value
	target = int(max[totalRow-1])
	logging.info('Test max.  value : %s' % str(target))
	textbox.SetFocus()
	ctrlTextbox.SetValue(str(target))
	paneRoot.SetFocus()
	if isSetError(textbox, str(target)):
		print('!!! Failed: Input Data (%s) overflow!' % str(target))
	time.sleep(DELAY_FOR_DEMO)
	# Test min value
	target = int(min[totalRow-1])
	logging.info('Test min.  value : %s.' % str(target))
	textbox.SetFocus()
	ctrlTextbox.SetValue(str(target))
	paneRoot.SetFocus()
	if isSetError(textbox, str(target)):
		print('!!! Failed: Input Data (%s) overflow!' % str(target))
	time.sleep(DELAY_FOR_DEMO)
	