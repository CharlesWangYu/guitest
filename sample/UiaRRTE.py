#from comtypes import GUID
from comtypes.client import *
from ctypes import *

# Start ui automation
UIAutomationClient = GetModule("UIAutomationCore.dll")
IUIAutomation = CreateObject("{ff48dba4-60ef-4201-aa87-54103eef594e}", interface=UIAutomationClient.IUIAutomation)

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
ctrl.Invoke()
