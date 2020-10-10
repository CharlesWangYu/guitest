'''
@File		: uiaRRTE.py
@Date		: 2020/08/30
@Author		: Wang.Yu
@Version	: 1.0
@Contact	: yu.wang@cn.yokogawa.com
@License	: (C)Copyright 2020 Yokogawa China Co., Ltd.
'''
#import pdb
#import logging
from uia2 import *
from comtypes.client import *
from ctypes import *

def waitProgressBarClose():
	desktop = IUIA.GetRootElement()
	assert isUIAElem(desktop)
	rrte = findFirstElemByName(desktop, 'Reference Run-time Environment', SCOPE_CHILDREN)
	assert isUIAElem(rrte)
	process = findFirstElemByControlType(rrte, UIAClient.UIA_WindowControlTypeId, SCOPE_CHILDREN)
	while isUIAElem(process):
		time.sleep(0.1)
		process = findFirstElemByControlType(rrte, UIAClient.UIA_WindowControlTypeId, SCOPE_CHILDREN)
	time.sleep(0.1)
			
def isContentNameString(uiaElem):
	return 'Fdi.Ui.ViewModel.Content.StringParameterViewModel' == uiaElem.CurrentName

def isContentNameDate(uiaElem):
	return 'Fdi.Ui.ViewModel.Content.DateTimeParameterViewModel' == uiaElem.CurrentName

def isContentNameTime(uiaElem):
	return 'Fdi.Ui.ViewModel.Content.UidTimeSpanViewModel' == uiaElem.CurrentName

def isContentNameNumeric(uiaElem):
	return 'Fdi.Ui.ViewModel.Content.NumericParameterViewModel' == uiaElem.CurrentName

def isContentNameEnum(uiaElem):
	return 'Fdi.Ui.ViewModel.Content.EnumerationViewModel' == uiaElem.CurrentName

def isContentNameBitEnum(uiaElem):
	return 'Fdi.Ui.ViewModel.Content.BitEnumerationViewModel' == uiaElem.CurrentName

def isLayoutNameMethod(uiaElem): # in menu tree
	return 'Fdi.Ui.ViewModel.Layout.ActionMenuItemViewModel' == uiaElem.CurrentName

def isLayoutNameMenu(uiaElem): # in menu tree, include menu and window
	return 'Fdi.Ui.ViewModel.Layout.RootMenuViewModel' == uiaElem.CurrentName

def isEditboxEnabled(uiaElem):
	assert isUIAElem(uiaElem)
	edit = findFirstElemByControlType(uiaElem, UIAClient.UIA_EditControlTypeId)
	pattern = edit.GetCurrentPattern(UIAClient.UIA_ValuePatternId)
	status = cast(pattern, POINTER(UIAClient.IUIAutomationValuePattern))
	return status.CurrentIsReadOnly
	assert isUIAElem(edit)
	return edit.CurrentIsEnabled

def isComboboxEnabled(uiaElem):
	assert isUIAElem(uiaElem)
	combo = findFirstElemByControlType(uiaElem, UIAClient.UIA_ComboBoxControlTypeId)
	assert isUIAElem(combo)
	return combo.CurrentIsEnabled

def isBitEnumGroupEnabled(uiaElem):
	checkBox = findFirstElemByControlType(uiaElem, UIAClient.UIA_CheckBoxControlTypeId)
	return checkBox.CurrentIsEnabled

def isRootMenuPushed(uiaElem):
	assert isUIAElem(uiaElem)
	btnX = findFirstElemByName(uiaElem, 'X', SCOPE_CHILDREN)
	return btnX.CurrentIsOffscreen == 0 # 0:isOffScreen=False, 1:isOffScreen=True
	
def isTreeItemExpand(uiaElem):
	assert isUIAElem(uiaElem)
	btn = findFirstElemByControlType(uiaElem, UIAClient.UIA_ButtonControlTypeId, SCOPE_CHILDREN)
	assert isUIAElem(btn)
	pattern = btn.GetCurrentPattern(UIAClient.UIA_TogglePatternId)
	ctrl = cast(pattern, POINTER(UIAClient.IUIAutomationTogglePattern))
	return ctrl.value.CurrentToggleState

def isTreeLeafSelected(uiaElem):
	assert isUIAElem(uiaElem)
	pattern = uiaElem.GetCurrentPattern(UIAClient.UIA_SelectionItemPatternId)
	ctrl = cast(pattern, POINTER(UIAClient.IUIAutomationSelectionItemPattern))
	return ctrl.value.CurrentIsSelected
	
def isTabSelected(uiaElem):
	assert isUIAElem(uiaElem)
	pattern = uiaElem.GetCurrentPattern(UIAClient.UIA_SelectionItemPatternId)
	ctrl = cast(pattern, POINTER(UIAClient.IUIAutomationSelectionItemPattern))
	return ctrl.value.CurrentIsSelected

def getElemSubName(uiaElem):
	textbox = findFirstElemByControlType(uiaElem, UIAClient.UIA_TextControlTypeId, SCOPE_CHILDREN)
	text = textbox.CurrentName
	return text

def getMenuMethodName(uiaElem):
	btns = findAllElemByControlType(uiaElem, UIAClient.UIA_ButtonControlTypeId, SCOPE_CHILDREN)
	btn = btns.GetElement(btns.Length-1)
	text = btn.CurrentName
	return text

def getCurrentValString(uiaElem):
	editItem = findFirstElemByControlType(uiaElem, UIAClient.UIA_EditControlTypeId)
	textbox  = findFirstElemByControlType(editItem, UIAClient.UIA_TextControlTypeId)
	text = textbox.CurrentName
	return text

def setEditboxCurrVal(uiaElem, currVal):
	editor = findFirstElemByControlType(uiaElem, UIAClient.UIA_EditControlTypeId)
	assert isUIAElem(editor)
	setEditbox(editor, '')
	setEditbox(editor, currVal)

def setGroupCheckboxCurrVal(uiaElem):
	custom = findFirstElemByControlType(uiaElem, UIAClient.UIA_CustomControlTypeId)
	assert isUIAElem(custom)
	checkbox = findFirstElemByControlType(custom, UIAClient.UIA_CheckBoxControlTypeId)
	assert isUIAElem(checkbox)
	pattern = checkbox.GetCurrentPattern(UIAClient.UIA_TogglePatternId)
	ctrl = cast(pattern, POINTER(UIAClient.IUIAutomationTogglePattern))
	ctrl.Toggle()
	time.sleep(0.1) # Do not delete this delay. It will cause failure in the interval between two toggle operations.
	ctrl.Toggle()

def setComboboxCurrVal(uiaElem, currVal):
	combo = findFirstElemByControlType(uiaElem, UIAClient.UIA_ComboBoxControlTypeId)
	assert isUIAElem(combo)
	expandCombo(combo)
	opts = findAllElemByControlType(combo, UIAClient.UIA_ListItemControlTypeId)
	for x in range(0, opts.Length):
		opt = opts.GetElement(x)
		txt = findFirstElemByControlType(opt, UIAClient.UIA_TextControlTypeId)
		if not txt.CurrentName == currVal:
			pattern = opt.GetCurrentPattern(UIAClient.UIA_SelectionItemPatternId)
			Selection = cast(pattern, POINTER(UIAClient.IUIAutomationSelectionItemPattern))
			Selection.Select()
			break
	expandCombo(combo)
	for x in range(0, opts.Length):
		opt = opts.GetElement(x)
		txt = findFirstElemByControlType(opt, UIAClient.UIA_TextControlTypeId)
		if txt.CurrentName == currVal:
			pattern = opt.GetCurrentPattern(UIAClient.UIA_SelectionItemPatternId)
			Selection = cast(pattern, POINTER(UIAClient.IUIAutomationSelectionItemPattern))
			Selection.Select()
			break
