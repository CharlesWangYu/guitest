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
	'''
	count = 0
	while (not isUIAElem(edit)) and (count < 3):
		edit = findFirstElemByControlType(uiaElem, UIAClient.UIA_EditControlTypeId)
		count += 1
		time.sleep(0.1)
	'''
	assert isUIAElem(edit)
	return edit.CurrentIsEnabled

def isComboboxEnabled(uiaElem):
	assert isUIAElem(uiaElem)
	combo = findFirstElemByControlType(uiaElem, UIAClient.UIA_ComboBoxControlTypeId)
	'''
	count = 0
	while (not isUIAElem(combo)) and (count < 3):
		combo = findFirstElemByControlType(uiaElem, UIAClient.UIA_ComboBoxControlTypeId)
		count += 1
		time.sleep(0.1)
	'''
	assert isUIAElem(combo)
	return combo.CurrentIsEnabled

def isBitEnumGroupEnabled(uiaElem):
	checkBox = findFirstElemByControlType(uiaElem, UIAClient.UIA_CheckBoxControlTypeId)
	return checkBox.CurrentIsEnabled

def isRootMenuPushed(uiaElem):
	assert isUIAElem(uiaElem)
	btnX = findFirstElemByName(uiaElem, 'X', SCOPE_CHILDREN)
	return btnX.CurrentIsOffscreen == 0 # 0:isOffScreen=False, 1:isOffScreen=True

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
