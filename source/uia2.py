import pdb
import logging
import os
import sys
import time
from configparser import ConfigParser
from comtypes.client import *
from ctypes import *

UIAClient = GetModule('UIAutomationCore.dll')
IUIA = CreateObject('{ff48dba4-60ef-4201-aa87-54103eef594e}', interface=UIAClient.IUIAutomation)
DesktopRoot = IUIA.GetRootElement()

SCOPE_CHILDREN			= UIAClient.TreeScope_Children
SCOPE_DESCENDANTS		= UIAClient.TreeScope_Descendants

def isUIAElem(elem):
	try:
		temp = elem.CurrentName
		return True
	except Exception as e:
		return False

def findAllElem(root, key, type, scope=SCOPE_DESCENDANTS):
	cnd = IUIA.CreatePropertyConditionEx(type, key, UIAClient.PropertyConditionFlags_None)
	all = root.FindAll(scope, cnd)
	#logging.debug('Found %d elements.' % all.Length)
	#for x in range(0, all.Length):
	#	logging.debug('The name of element[%d] is \'%s\'.' % (x, all.GetElement(x).CurrentName))
	return all

def findAllElemByControlType(root, name, scope=SCOPE_DESCENDANTS):
	return findAllElem(root, name, UIAClient.UIA_ControlTypePropertyId, scope)

def findAllElem2ORCond(root, key1, type1, key2, type2, scope=SCOPE_DESCENDANTS):
	cnd1 = IUIA.CreatePropertyConditionEx(type1, key1, UIAClient.PropertyConditionFlags_None)
	cnd2 = IUIA.CreatePropertyConditionEx(type2, key2, UIAClient.PropertyConditionFlags_None)
	combine = IUIA.CreateOrCondition(cnd1, cnd2)
	all = root.FindAll(scope, combine)
	#logging.debug('Found %d elements.' % all.Length)
	#for x in range(0, all.Length):
	#	logging.debug('The name of element[%d] is \'%s\'.' % (x, all.GetElement(x).CurrentName))
	return all

def findAllElem4ORCond(root, key1, key2, key3, key4, type, scope=SCOPE_DESCENDANTS):
	cnd1 = IUIA.CreatePropertyConditionEx(type, key1, UIAClient.PropertyConditionFlags_None)
	cnd2 = IUIA.CreatePropertyConditionEx(type, key2, UIAClient.PropertyConditionFlags_None)
	cnd3 = IUIA.CreatePropertyConditionEx(type, key3, UIAClient.PropertyConditionFlags_None)
	cnd4 = IUIA.CreatePropertyConditionEx(type, key4, UIAClient.PropertyConditionFlags_None)
	combine1 = IUIA.CreateOrCondition(cnd1, cnd2)
	combine2 = IUIA.CreateOrCondition(cnd3, cnd4)
	combine = IUIA.CreateOrCondition(combine1, combine2)
	all = root.FindAll(scope, combine)
	#logging.debug('Found %d elements.' % all.Length)
	#for x in range(0, all.Length):
	#	logging.debug('The name of element[%d] is \'%s\'.' % (x, all.GetElement(x).CurrentName))
	return all

def findFirstElem(root, key, type, scope=SCOPE_DESCENDANTS):
	cnd = IUIA.CreatePropertyConditionEx(type, key, UIAClient.PropertyConditionFlags_None)
	element = root.FindFirst(scope, cnd)
	#logging.debug('Found the 1st element, and it\'s name is \'%s\'' % element.CurrentName)
	return element

def findFirstElem2ANDCond(root, key1, type1, key2, type2, scope=SCOPE_DESCENDANTS):
	cnd1 = IUIA.CreatePropertyConditionEx(type1, key1, UIAClient.PropertyConditionFlags_None)
	cnd2 = IUIA.CreatePropertyConditionEx(type2, key2, UIAClient.PropertyConditionFlags_None)
	combine = IUIA.CreateAndCondition(cnd1, cnd2)
	element = root.FindFirst(scope, combine)
	#logging.debug('Found the 1st element, and it\'s name is \'%s\'' % element.CurrentName)
	return element

def findFirstElemByName(root, name, scope=SCOPE_DESCENDANTS):
	return findFirstElem(root, name, UIAClient.UIA_NamePropertyId, scope)

def findFirstElemByControlType(root, type, scope=SCOPE_DESCENDANTS):
	return findFirstElem(root, type, UIAClient.UIA_ControlTypePropertyId, scope)

def findFirstElemByAutomationId(root, Id, scope=SCOPE_DESCENDANTS):
	return findFirstElem(root, Id, UIAClient.UIA_AutomationIdPropertyId, scope)

def getParentElem(child):
	walker = IUIA.ControlViewWalker
	parent = walker.GetParentElement(child)
	assert isUIAElem(parent)
	return parent

def getNextSiblingElem(elem):
	walker = IUIA.ControlViewWalker
	next = walker.GetNextSiblingElement(elem)
	assert isUIAElem(next)
	return next

def getPreviousSiblingElem(elem):
	walker = IUIA.ControlViewWalker
	element = walker.GetPreviousSiblingElement(elem)
	assert isUIAElem(next)
	return element

def getElemSubName(elem):
	text = findFirstElem(elem, Client.UIA_TextControlTypeId, Client.UIA_ControlTypePropertyId, scope=SCOPE_CHILDREN)
	return text.CurrentName

def findFirstElemBySubText(root, name, flag=Client.PropertyConditionFlags_None, scope=Client.TreeScope_Descendants):
	child = findFirstElem(start, name, Client.UIA_NamePropertyId)
	element = getParentElem(child)
	return element