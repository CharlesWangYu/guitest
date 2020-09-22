'''
@File		: uia2.py
@Date		: 2020/05/30
@Author		: Wang.Yu
@Version	: 1.0
@Contact	: yu.wang@cn.yokogawa.com
@License	: (C)Copyright 2020 Yokogawa China Co., Ltd.
'''
#import pdb
#import logging
from comtypes.client import *
from ctypes import *

# This is the operation of UIA initialization, they need to be executed 
# immediately when starting this module.
UIA_CORE_NAME			= 'UIAutomationCore.dll'
UIA_OBJ_ID				= '{ff48dba4-60ef-4201-aa87-54103eef594e}'

UIAClient = GetModule(UIA_CORE_NAME)
IUIA = CreateObject(UIA_OBJ_ID, interface=UIAClient.IUIAutomation)
DesktopRoot = IUIA.GetRootElement()

# These are some commonly used UIA constant definitions.
SCOPE_CHILDREN			= UIAClient.TreeScope_Children
SCOPE_DESCENDANTS		= UIAClient.TreeScope_Descendants

# This is a group of functions used to judge the attributes of UIA objects
def isUIAElem(elem):
	NULL = cast(0, POINTER(UIAClient.IUIAutomationElement))
	return not (elem == NULL)

def isTreeLeaf(elem):
	assert isUIAElem(elem)
	pattern = elem.GetCurrentPattern(UIAClient.UIA_ExpandCollapsePatternId)
	ctrl = cast(pattern, POINTER(UIAClient.IUIAutomationExpandCollapsePattern))
	return ctrl.value.CurrentExpandCollapseState == UIAClient.ExpandCollapseState_LeafNode

def isTreeExpanded(elem):
	assert isUIAElem(elem)
	pattern = elem.GetCurrentPattern(UIAClient.UIA_ExpandCollapsePatternId)
	ctrl = cast(pattern, POINTER(UIAClient.IUIAutomationExpandCollapsePattern))
	return ctrl.value.CurrentExpandCollapseState == UIAClient.ExpandCollapseState_Expanded

def isTreeCollapsed(elem):
	assert isUIAElem(elem)
	pattern = elem.GetCurrentPattern(UIAClient.UIA_ExpandCollapsePatternId)
	ctrl = cast(pattern, POINTER(UIAClient.IUIAutomationExpandCollapsePattern))
	return ctrl.value.CurrentExpandCollapseState == UIAClient.ExpandCollapseState_Collapsed

def isTree(elem):
	assert isUIAElem(elem)
	return elem.CurrentControlType == UIAClient.UIA_TreeControlTypeId

def isPane(elem):
	assert isUIAElem(elem)
	return elem.CurrentControlType == UIAClient.UIA_PaneControlTypeId

def isCustom(elem):
	assert isUIAElem(elem)
	return elem.CurrentControlType == UIAClient.UIA_CustomControlTypeId

def isButton(elem):
	assert isUIAElem(elem)
	return elem.CurrentControlType == UIAClient.UIA_ButtonControlTypeId

def isGroup(elem):
	assert isUIAElem(elem)
	return elem.CurrentControlType == UIAClient.UIA_GroupControlTypeId

def isTab(elem):
	assert isUIAElem(elem)
	return elem.CurrentControlType == UIAClient.UIA_TabControlTypeId
	
def isTabItem(elem):
	assert isUIAElem(elem)
	return elem.CurrentControlType == UIAClient.UIA_TabItemControlTypeId

# This is a group of functions for finding UIA objects.
def findAllChildren(root):
	cnd = IUIA.CreateTrueCondition()
	all = root.FindAll(SCOPE_CHILDREN, cnd)
	return all

def findAllElem(root, key, type, scope=SCOPE_DESCENDANTS):
	cnd = IUIA.CreatePropertyConditionEx(type, key, UIAClient.PropertyConditionFlags_None)
	all = root.FindAll(scope, cnd)
	return all

def findAllElemByName(root, type, scope=SCOPE_DESCENDANTS):
	return findAllElem(root, type, UIAClient.UIA_NamePropertyId, scope)

def findAllElemByControlType(root, type, scope=SCOPE_DESCENDANTS):
	return findAllElem(root, type, UIAClient.UIA_ControlTypePropertyId, scope)

def findAllElemByAutomationId(root, id, scope=SCOPE_DESCENDANTS):
	return findAllElem(root, id, UIAClient.UIA_AutomationIdPropertyId, scope)

def findAllElem2ORCond(root, key1, type1, key2, type2, scope=SCOPE_DESCENDANTS):
	cnd1 = IUIA.CreatePropertyConditionEx(type1, key1, UIAClient.PropertyConditionFlags_None)
	cnd2 = IUIA.CreatePropertyConditionEx(type2, key2, UIAClient.PropertyConditionFlags_None)
	combine = IUIA.CreateOrCondition(cnd1, cnd2)
	all = root.FindAll(scope, combine)
	return all

def findAllElem4ORCond(root, key1, key2, key3, key4, type, scope=SCOPE_DESCENDANTS):
	try:
		cnd1 = IUIA.CreatePropertyConditionEx(type, key1, UIAClient.PropertyConditionFlags_None)
		cnd2 = IUIA.CreatePropertyConditionEx(type, key2, UIAClient.PropertyConditionFlags_None)
		cnd3 = IUIA.CreatePropertyConditionEx(type, key3, UIAClient.PropertyConditionFlags_None)
		cnd4 = IUIA.CreatePropertyConditionEx(type, key4, UIAClient.PropertyConditionFlags_None)
		condArray = [cnd1, cnd2, cnd3, cnd4]
		combine = IUIA.CreateOrConditionFromArray(condArray)
		all = root.FindAll(scope, combine)
		return all
	except e:
		print ('Catch abnormal [%s]' % e)

def findFirstElem(root, key, type, scope=SCOPE_DESCENDANTS):
	cnd = IUIA.CreatePropertyConditionEx(type, key, UIAClient.PropertyConditionFlags_None)
	element = root.FindFirst(scope, cnd)
	return element

def findFirstElem2ANDCond(root, key1, type1, key2, type2, scope=SCOPE_DESCENDANTS):
	cnd1 = IUIA.CreatePropertyConditionEx(type1, key1, UIAClient.PropertyConditionFlags_None)
	cnd2 = IUIA.CreatePropertyConditionEx(type2, key2, UIAClient.PropertyConditionFlags_None)
	combine = IUIA.CreateAndCondition(cnd1, cnd2)
	element = root.FindFirst(scope, combine)
	return element

def findFirstElemByName(root, name, scope=SCOPE_DESCENDANTS):
	return findFirstElem(root, name, UIAClient.UIA_NamePropertyId, scope)

def findFirstElemByControlType(root, type, scope=SCOPE_DESCENDANTS):
	return findFirstElem(root, type, UIAClient.UIA_ControlTypePropertyId, scope)

def findFirstElemByAutomationId(root, Id, scope=SCOPE_DESCENDANTS):
	return findFirstElem(root, Id, UIAClient.UIA_AutomationIdPropertyId, scope)

def findFirstElemBySubText(root, name):
	child = findFirstElemByName(root, name)
	if not isUIAElem(child):
		return cast(0, POINTER(UIAClient.IUIAutomationElement))
	element = findParentElem(child)
	#assert isUIAElem(element)
	return element

def findParentElem(child):
	walker = IUIA.ControlViewWalker
	parent = walker.GetParentElement(child)
	assert isUIAElem(parent)
	return parent

def findFirstChildElem(elem):
	walker = IUIA.ControlViewWalker
	first = walker.GetFirstChildElement(elem)
	assert isUIAElem(first)
	return first

def findLastChildElem(elem):
	walker = IUIA.ControlViewWalker
	last = walker.GetLastChildElement(elem)
	assert isUIAElem(last)
	return last

def findNextSiblingElem(elem):
	walker = IUIA.ControlViewWalker
	next = walker.GetNextSiblingElement(elem)
	assert isUIAElem(next)
	return next

def findPreviousSiblingElem(elem):
	walker = IUIA.ControlViewWalker
	element = walker.GetPreviousSiblingElement(elem)
	assert isUIAElem(next)
	return element

# This is a group of functions for manipulating UIA objects.
def setEditbox(elem, text):
	assert isUIAElem(elem)
	pattern = elem.GetCurrentPattern(UIAClient.UIA_ValuePatternId)
	ctrl = cast(pattern, POINTER(UIAClient.IUIAutomationValuePattern))
	elem.SetFocus()
	ctrl.SetValue(text)

def expandCombo(elem):
	assert isUIAElem(elem)
	pattern = elem.GetCurrentPattern(UIAClient.UIA_ExpandCollapsePatternId)
	ctrl = cast(pattern, POINTER(UIAClient.IUIAutomationExpandCollapsePattern))
	if ctrl.value.CurrentExpandCollapseState == UIAClient.ExpandCollapseState_Collapsed:
		ctrl.Expand()

def collapseCombo(elem):
	pattern = elem.GetCurrentPattern(UIAClient.UIA_ExpandCollapsePatternId)
	ctrl = cast(pattern, POINTER(UIAClient.IUIAutomationExpandCollapsePattern))
	if ctrl.value.CurrentExpandCollapseState == UIAClient.ExpandCollapseState_Expanded:
		ctrl.Collapse()

def expandTree(elem):
	assert isUIAElem(elem)
	btn = findFirstElemByControlType(elem, UIAClient.UIA_ButtonControlTypeId, SCOPE_CHILDREN)
	assert isUIAElem(btn)
	pattern = btn.GetCurrentPattern(UIAClient.UIA_TogglePatternId)
	ctrl = cast(pattern, POINTER(UIAClient.IUIAutomationTogglePattern))
	if not ctrl.value.CurrentToggleState:
		ctrl.Toggle()

def collapseTree(elem):
	assert isUIAElem(elem)
	btn = findFirstElemByControlType(onlineRoot, UIAClient.UIA_ButtonControlTypeId, SCOPE_CHILDREN)
	assert isUIAElem(btn)
	pattern = btn.GetCurrentPattern(UIAClient.UIA_TogglePatternId)
	ctrl = cast(pattern, POINTER(UIAClient.IUIAutomationTogglePattern))
	if ctrl.value.CurrentToggleState:
		ctrl.Toggle()

def pushLeaf(elem):
	assert isTreeLeaf(elem)
	pattern = elem.GetCurrentPattern(UIAClient.UIA_SelectionItemPatternId)
	ctrl = cast(pattern, POINTER(UIAClient.IUIAutomationSelectionItemPattern))
	ctrl.Select()

def pushButton(elem):
	assert isUIAElem(elem)
	pattern = elem.GetCurrentPattern(UIAClient.UIA_InvokePatternId)
	ctrl = cast(pattern, POINTER(UIAClient.IUIAutomationInvokePattern))
	ctrl.Invoke()
	
def selectTab(elem):
	assert isUIAElem(elem)
	pattern = elem.GetCurrentPattern(UIAClient.UIA_SelectionItemPatternId)
	ctrl = cast(pattern, POINTER(UIAClient.IUIAutomationSelectionItemPattern))
	if not ctrl.value.CurrentIsSelected:
		ctrl.Select()

def selectCheckbox(elem):
	assert isUIAElem(elem)
	pattern = elem.GetCurrentPattern(UIAClient.UIA_TogglePatternId)
	ctrl = cast(pattern, POINTER(UIAClient.IUIAutomationTogglePattern))
	if not ctrl.value.CurrentToggleState:
		ctrl.Toggle()

def unselectCheckbox(elem):
	assert isUIAElem(elem)
	pattern = elem.GetCurrentPattern(UIAClient.UIA_TogglePatternId)
	ctrl = cast(pattern, POINTER(UIAClient.IUIAutomationTogglePattern))
	if ctrl.value.CurrentToggleState:
		ctrl.Toggle()

if __name__ == '__main__':
	all = findAllChildren(DesktopRoot)
	for x in range(0, all.Length):
		item = all.GetElement(x)
		print (item.CurrentClassName)
	#pdb.set_trace()
	#test = findFirstElemByName(DesktopRoot, 'XXXXXXXXX')
	test = findFirstElemByControlType(DesktopRoot, UIAClient.UIA_WindowControlTypeId)
	assert isUIAElem(test)