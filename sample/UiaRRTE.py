#from comtypes import GUID
from comtypes.client import *
from ctypes import *
from comtypes.gen.UIAutomationClient import *
from ctypes.wintypes import tagPOINT
import comtypes

# Start ui automation
UIAutomationClient = GetModule("UIAutomationCore.dll")
IUIAutomation = CreateObject("{ff48dba4-60ef-4201-aa87-54103eef594e}", interface=UIAutomationClient.IUIAutomation)
walker = IUIAutomation.RawViewWalker

# Get root node(desktop)
root = IUIAutomation.GetRootElement()
#print (root)
#print (root.CurrentClassName)
#print (root.CurrentName)
#print (root.CurrentBoundingRectangle)

# Get Import Package/DD button
cnd = IUIAutomation.CreatePropertyConditionEx(UIAutomationClient.UIA_NamePropertyId,
                                                'Import Package/DD',
												UIAutomationClient.PropertyConditionFlags_None)
#print (cnd)
btn = root.FindFirst(UIAutomationClient.TreeScope_Descendants, cnd)
#print (btn.CurrentProcessId)
#print (btn.CurrentName)

# Push Import Package/DD button
pattern = btn.GetCurrentPattern(UIAutomationClient.UIA_InvokePatternId)
#print (pattern)
ctrl = cast(pattern, POINTER(UIAutomationClient.IUIAutomationInvokePattern))
#ctrl.Invoke()

# Get parent & grand element of Import Package/DD button
parent = walker.GetParentElement(btn)
#grand = walker.GetParentElement(parent)
#print(grand.CurrentProcessId)
#print(grand.CurrentName)

# Find "Online" TAB button and push it
cnd = IUIAutomation.CreatePropertyConditionEx(UIAutomationClient.UIA_NamePropertyId,
                                                'Online',
												UIAutomationClient.PropertyConditionFlags_None)
txt = root.FindFirst(UIAutomationClient.TreeScope_Descendants, cnd)
btn_online = walker.GetParentElement(txt)
pattern = btn_online.GetCurrentPattern(UIAutomationClient.UIA_InvokePatternId)
ctrl = cast(pattern, POINTER(UIAutomationClient.IUIAutomationInvokePattern))
ctrl.Invoke()
#print(txt.CurrentName)
#print(btn_online.CurrentName)

# Find TreeView root node
cnd = IUIAutomation.CreatePropertyConditionEx(UIAutomationClient.UIA_NamePropertyId,
                                                'Fdi.Ui.ViewModel.Layout.TableViewModel',
												UIAutomationClient.PropertyConditionFlags_None)
online_root = root.FindFirst(UIAutomationClient.TreeScope_Descendants, cnd)

# Find PV node in online TAB
cnd = IUIAutomation.CreatePropertyConditionEx(UIAutomationClient.UIA_NamePropertyId,
                                                'PV',
												UIAutomationClient.PropertyConditionFlags_None)
pv = online_root.FindFirst(UIAutomationClient.TreeScope_Descendants, cnd)
print(pv.CurrentProcessId)
print(pv.CurrentName)