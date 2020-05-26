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

DELAY_OPEN_RRTE		= 6
DELAY_SET_TO_DEV	= 4
DELAY_OPT_RRTE		= 3
NAME_RRTE_APP		= 'Reference Run-time Environment'
NAME_TOP_TAB		= 'Fdi.Client.DeviceUi.ViewModel.DeviceUiHostContainerItemViewModel'
NAME_X_BTN			= 'X'
NAME_TREE_ROOT		= 'DD_ExplorerView'
NAME_APPLY_BTN		= 'Apply'
NAME_REVERT_BTN		= 'Revert'
NAME_ONLINE_BTN		= 'Online'
NAME_OK_BTN			= 'OK'

#pdb.set_trace()
logging.basicConfig(level = logging.ERROR)
# Start UI Automation
logging.info('')
logging.info('***********************************************************')
logging.info('****** Start UI Automation')
logging.info('***********************************************************')
UIAClient = GetModule('UIAutomationCore.dll')
IUIA = CreateObject('{ff48dba4-60ef-4201-aa87-54103eef594e}', interface=UIAClient.IUIAutomation)

def FindAllElem(start, key, type, flag=UIAClient.PropertyConditionFlags_None, scope=UIAClient.TreeScope_Descendants):
	cnd = IUIA.CreatePropertyConditionEx(type, key, flag)
	all = start.FindAll(scope, cnd)
	logging.info('Element Array size = %d' % all.Length)
	for x in range(0, all.Length):
		element = all.GetElement(x)
		logging.info('Element[%s] is searched.' % element.CurrentName)
	return all

def FindOneElem(start, key, type, flag=UIAClient.PropertyConditionFlags_None, scope=UIAClient.TreeScope_Descendants):
	cnd = IUIA.CreatePropertyConditionEx(type, key, flag)
	element = start.FindFirst(scope, cnd)
	#logging.info('Element[%s] is searched.' % element.CurrentName)
	return element

def GetParentElem(elem):
	walker = IUIA.ControlViewWalker
	parent = walker.GetParentElement(elem)
	return parent

def GetNextSiblingElem(elem):
	walker = IUIA.ControlViewWalker
	element = walker.GetNextSiblingElement(elem)
	return element

def GetPreviousSiblingElem(elem):
	walker = IUIA.ControlViewWalker
	element = walker.GetPreviousSiblingElement(elem)
	return element

def FindElemBySubText(start, name, flag=UIAClient.PropertyConditionFlags_None, scope=UIAClient.TreeScope_Descendants):
	cnd = IUIA.CreatePropertyConditionEx(UIAClient.UIA_NamePropertyId, name, flag)
	child = start.FindFirst(scope, cnd)
	element = GetParentElem(child)
	return element

def GetTextboxCurrentVal(elem):
	text = FindOneElem(elem, UIAClient.UIA_TextControlTypeId, UIAClient.UIA_ControlTypePropertyId)
	return text.CurrentName

def isFoundElem(elem):
	try:
		temp = elem.CurrentName
		return 1
	except Exception as e:
		return 0

def isSetError(textbox, setVal):
	currVal = GetTextboxCurrentVal(textbox)
	#pdb.set_trace()
	if not currVal == setVal:
		return 1
	else:
		# Push [Apply] button
		paneRoot = GetParentElem(GetParentElem(textbox))
		revertBtn = GetNextSiblingElem(paneRoot)
		applyBtn = GetNextSiblingElem(revertBtn)
		pattern = applyBtn.GetCurrentPattern(UIAClient.UIA_InvokePatternId)
		ctrlApplyBtn = cast(pattern, POINTER(UIAClient.IUIAutomationInvokePattern))
		ctrlApplyBtn.Invoke()
		time.sleep(DELAY_SET_TO_DEV)
		# Test error dialog
		root = IUIA.GetRootElement()
		rrteRoot = FindOneElem(root, NAME_RRTE_APP, UIAClient.UIA_NamePropertyId)
		win = FindOneElem(rrteRoot, UIAClient.UIA_WindowControlTypeId, UIAClient.UIA_ControlTypePropertyId)
		if isFoundElem(win):
			OKBtn = FindOneElem(win, NAME_OK_BTN, UIAClient.UIA_NamePropertyId)
			pattern = OKBtn.GetCurrentPattern(UIAClient.UIA_InvokePatternId)
			ctrl = cast(pattern, POINTER(UIAClient.IUIAutomationInvokePattern))
			ctrl.Invoke()
			time.sleep(DELAY_SET_TO_DEV)
			return 1
		else:
			return 0

if __name__ == '__main__':
	# Define const and parameter
	MENU_ITEM_TYPE_COLUMN		= 6
	MENU_ITEM_RW_COLUMN			= 7
	MENU_ITEM_DATA_TYPE_COLUMN	= 8
	MENU_ITEM_FORMAT_COLUMN		= 9
	MENU_ITEM_MIN_COLUMN		= 10
	MENU_ITEM_MAX_COLUMN		= 11
	MAX_MENU_ITEM_NUM			= 28
	label						= [''] * MAX_MENU_ITEM_NUM
	itemType					= [''] * MAX_MENU_ITEM_NUM
	rw							= ['RO'] * MAX_MENU_ITEM_NUM
	dataType					= ['INT'] * MAX_MENU_ITEM_NUM
	max							= [float('inf')] * MAX_MENU_ITEM_NUM
	min							= [float('-inf')] * MAX_MENU_ITEM_NUM
	
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
	execCmd = '\"' + hostApp + '\" -l \"' + testFile + '\"'
	logging.info('execCmd = %s' % execCmd)
	subprocess.Popen(execCmd, shell=True, stdout=subprocess.PIPE)
	time.sleep(DELAY_OPEN_RRTE)
	
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
		itemType[currRow-1] = sheet.cell(currRow, MENU_ITEM_TYPE_COLUMN).value;
		rw[currRow-1] = sheet.cell(currRow, MENU_ITEM_RW_COLUMN).value;
		dataType[currRow-1] = sheet.cell(currRow, MENU_ITEM_DATA_TYPE_COLUMN).value;
		if (not sheet.cell(currRow, MENU_ITEM_MIN_COLUMN).value == ''):
			min[currRow-1] = float(sheet.cell(currRow, MENU_ITEM_MIN_COLUMN).value);
		if (not sheet.cell(currRow, MENU_ITEM_MAX_COLUMN).value == ''):
			max[currRow-1] = float(sheet.cell(currRow, MENU_ITEM_MAX_COLUMN).value);
		logging.info('No.%d, (Label = %s, Item Type = %s, RW = %s, Data Type = %s, Min = %.2f, Max = %.2f)' % (currRow-1, label[currRow-1], itemType[currRow-1], rw[currRow-1], dataType[currRow-1], min[currRow-1], max[currRow-1]))

	# Get root node
	logging.info('')
	logging.info('***********************************************************')
	logging.info('****** Get crucial part tree node')
	logging.info('***********************************************************')
	root = IUIA.GetRootElement()
	rrteRoot = FindOneElem(root, NAME_RRTE_APP, UIAClient.UIA_NamePropertyId)
	logging.info('RRTE window root: Class name = %s, Name = %s, Bounding Rectangle = %s, Process ID = %d' % (rrteRoot.CurrentClassName, rrteRoot.CurrentName, rrteRoot.CurrentBoundingRectangle, rrteRoot.CurrentProcessId))
	
	# Push "Online" TAB
	logging.info('')
	logging.info('***********************************************************')
	logging.info('****** Push [Online] TAB')
	logging.info('***********************************************************')
	#txt = FindOneElem(root, 'Online', UIAClient.UIA_NamePropertyId)
	#btnOnline = GetParentElem(txt)
	onlineBtn = FindElemBySubText(root, NAME_ONLINE_BTN)
	pattern = onlineBtn.GetCurrentPattern(UIAClient.UIA_InvokePatternId)
	ctrl = cast(pattern, POINTER(UIAClient.IUIAutomationInvokePattern))
	ctrl.Invoke()
	time.sleep(DELAY_SET_TO_DEV)
	
	# Get the menu tree node
	logging.info('')
	logging.info('***********************************************************')
	logging.info('****** Get the menu tree root node')
	logging.info('***********************************************************')
	all			= FindAllElem(rrteRoot, UIAClient.UIA_CustomControlTypeId, UIAClient.UIA_ControlTypePropertyId, scope=UIAClient.TreeScope_Children)
	workRoot	= all.GetElement(all.Length-1)
	topTAB		= FindOneElem(workRoot, NAME_TOP_TAB, UIAClient.UIA_NamePropertyId)
	topTABX		= FindOneElem(topTAB, NAME_X_BTN, UIAClient.UIA_NamePropertyId)
	topRoot		= GetNextSiblingElem(topTABX)
	explorer	= FindOneElem(topRoot, NAME_TREE_ROOT, UIAClient.UIA_AutomationIdPropertyId)
	treeRoot	= GetNextSiblingElem(explorer)
	paneRoot	= GetNextSiblingElem(treeRoot)
	applyBtn	= FindOneElem(topRoot, NAME_APPLY_BTN, UIAClient.UIA_NamePropertyId)
	revertBtn	= FindOneElem(topRoot, NAME_REVERT_BTN, UIAClient.UIA_NamePropertyId)
	
	# Check menu and parameter labels
	logging.info('')
	logging.info('***********************************************************')
	logging.info('****** Check menu and parameter labels')
	logging.info('***********************************************************')
	print('--- Check menu and parameter labels. ---')
	for currRow in range(1, totalRow):
		if (itemType[currRow] == 'Menu' and itemType[currRow+1] == 'Menu'):
			logging.info('Comparing the menu label[%s].' % label[currRow])
			txt = None
			txt = FindOneElem(treeRoot, label[currRow], UIAClient.UIA_NamePropertyId)
			if (txt is None):
				print('!!! Failed: Menu label [%s] does not exist!' % label[currRow])
			else:
				parent = GetParentElem(txt)
				toggle = FindOneElem(parent, UIAClient.UIA_ButtonControlTypeId, UIAClient.UIA_ControlTypePropertyId)
				pattern = toggle.GetCurrentPattern(UIAClient.UIA_TogglePatternId)
				ctrl = cast(pattern, POINTER(UIAClient.IUIAutomationTogglePattern))
				ctrl.Toggle()
				time.sleep(DELAY_OPT_RRTE)
		elif (itemType[currRow] == 'Menu' and itemType[currRow+1] != 'Menu'):
			logging.info('Comparing the menu label[%s].' % label[currRow])
			paramStartRow = currRow + 1;
			txt = None
			txt = FindOneElem(treeRoot, label[currRow], UIAClient.UIA_NamePropertyId)
			if (txt is None):
				print('!!! Failed: Menu label [%s] does not exist!' % label[currRow])
			else:
				item = GetParentElem(txt)
				pattern = item.GetCurrentPattern(UIAClient.UIA_SelectionItemPatternId)
				ctrl = cast(pattern, POINTER(UIAClient.IUIAutomationSelectionItemPattern))
				ctrl.Select()
				time.sleep(DELAY_OPT_RRTE)
				logging.info('Comparing labels under menu item[%s].' % label[currRow])
				line = FindOneElem(rrteRoot, 'Fdi.Ui.ViewModel.Content.NumericParameterViewModel', UIAClient.UIA_NamePropertyId)
				pane = GetParentElem(line)
				logging.info('paramStartRow = %d' % paramStartRow)
				all = FindAllElem(pane, 'Label', UIAClient.UIA_AutomationIdPropertyId)
				for x in range(paramStartRow, totalRow):
					if (itemType[x] == 'Menu'):
						break;
					if not label[x] == all.GetElement(x-paramStartRow).CurrentName:
						print('!!! Failed: Param label [%s] does not exist!' % label[x])
		#else:
	
	# Check data limits. (Hi/Lo alarm hysteresis : Max=10, Min=0)
	logging.info('')
	logging.info('***********************************************************')
	logging.info('****** Check data limits')
	logging.info('***********************************************************')
	print('--- Check data limits (Hi/Lo alarm hysteresis) ---')
	for currRow in range(1, totalRow):
		if (itemType[currRow] == 'Menu'):
			txt = None
			txt = FindOneElem(treeRoot, label[currRow], UIAClient.UIA_NamePropertyId)
			if (txt is None):
				pass
			else:
				item = GetParentElem(txt)
				pattern = item.GetCurrentPattern(UIAClient.UIA_ExpandCollapsePatternId)
				ctrl = cast(pattern, POINTER(UIAClient.IUIAutomationExpandCollapsePattern))
				state = ctrl.value.CurrentExpandCollapseState
				#pdb.set_trace()
				if state == UIAClient.ExpandCollapseState_Collapsed:
					toggle = FindOneElem(item, UIAClient.UIA_ButtonControlTypeId, UIAClient.UIA_ControlTypePropertyId)
					pattern = toggle.GetCurrentPattern(UIAClient.UIA_TogglePatternId)
					ctrl = cast(pattern, POINTER(UIAClient.IUIAutomationTogglePattern))
					ctrl.Toggle()
					time.sleep(DELAY_OPT_RRTE)
				elif state == UIAClient.ExpandCollapseState_LeafNode:
					pattern = item.GetCurrentPattern(UIAClient.UIA_SelectionItemPatternId)
					ctrl = cast(pattern, POINTER(UIAClient.IUIAutomationSelectionItemPattern))
					ctrl.Select()
					time.sleep(DELAY_OPT_RRTE)
		else: # param
			if rw[currRow] == 'RW':
				#pdb.set_trace()
				paneRoot = GetNextSiblingElem(treeRoot)
				paramLine = FindElemBySubText(paneRoot, label[currRow])
				textbox = FindOneElem(paramLine, 'Value', UIAClient.UIA_AutomationIdPropertyId)
				pattern = textbox.GetCurrentPattern(UIAClient.UIA_ValuePatternId)
				ctrl = cast(pattern, POINTER(UIAClient.IUIAutomationValuePattern))
				# Test max value
				target = int(max[currRow]) # In fact, the floating point type should be combined with the format string to judge its reasonable input.
				logging.info('Test max.  value : %s' % str(target))
				textbox.SetFocus()
				ctrl.SetValue(str(target))
				paneRoot.SetFocus()
				if isSetError(textbox, str(target)):
					print('!!! Failed: Input Data (%s) overflow!' % str(target))
				time.sleep(DELAY_OPT_RRTE)
				# Test min value
				target = int(min[currRow]) # In fact, the floating point type should be combined with the format string to judge its reasonable input.
				logging.info('Test min.  value : %s.' % str(target))
				textbox.SetFocus()
				ctrl.SetValue(str(target))
				paneRoot.SetFocus()
				if isSetError(textbox, str(target)):
					print('!!! Failed: Input Data (%s) overflow!' % str(target))
				time.sleep(DELAY_OPT_RRTE)
	