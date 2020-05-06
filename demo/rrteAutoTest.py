import pdb
import logging
import time
import subprocess
import xlrd
#import comtypes
from configparser import ConfigParser
from comtypes.client import *
from ctypes import *
#from comtypes.gen.UIAutomationClient import *
#from ctypes.wintypes import tagPOINT

# Define global parameter
DELAY_OPEN_RRET			= 6
DELAY_PUSH_ONLINE		= 4
MAX_MENU_ITEM_NUM		= 30
MENU_ITEM_TPE_COLUMN	= 6
label					= [''] * MAX_MENU_ITEM_NUM
type					= [''] * MAX_MENU_ITEM_NUM
viewLabel				= [''] * MAX_MENU_ITEM_NUM

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
sheet = excel.sheet_by_name('Label')
totalRow = sheet.nrows

for currRow in range(totalRow):
  for currCol in range(MENU_ITEM_TPE_COLUMN):
    label[currRow] += sheet.cell(currRow, currCol).value
  type[currRow] = sheet.cell(currRow, MENU_ITEM_TPE_COLUMN).value;
  logging.info('No.%d, (Label = %s, Type = %s)' % (currRow, label[currRow], type[currRow]))

# Start UI Automation
logging.info('')
logging.info('***********************************************************')
logging.info('****** Start UI Automation')
logging.info('***********************************************************')
UIAutomationClient = GetModule('UIAutomationCore.dll')
IUIAutomation = CreateObject('{ff48dba4-60ef-4201-aa87-54103eef594e}', interface=UIAutomationClient.IUIAutomation)
walker = IUIAutomation.ControlViewWalker

# Push "Online" TAB
logging.info('')
logging.info('***********************************************************')
logging.info('****** Push [Online] TAB')
logging.info('***********************************************************')
root = IUIAutomation.GetRootElement()
cnd = IUIAutomation.CreatePropertyConditionEx(UIAutomationClient.UIA_NamePropertyId,
                                                'Online',
												UIAutomationClient.PropertyConditionFlags_None)
txt = root.FindFirst(UIAutomationClient.TreeScope_Descendants, cnd)
btnOnline = walker.GetParentElement(txt)
pattern = btnOnline.GetCurrentPattern(UIAutomationClient.UIA_InvokePatternId)
ctrl = cast(pattern, POINTER(UIAutomationClient.IUIAutomationInvokePattern))
ctrl.Invoke()
time.sleep(DELAY_PUSH_ONLINE)

# Get the menu tree root node (ControlType:"ControlType.Tree")
logging.info('')
logging.info('***********************************************************')
logging.info('****** Get the menu tree root node')
logging.info('***********************************************************')
root = IUIAutomation.GetRootElement()
cnd = IUIAutomation.CreatePropertyConditionEx(UIAutomationClient.UIA_NamePropertyId,
                                                'download_to_device_root_menu',
												UIAutomationClient.PropertyConditionFlags_None)
menuLabel = root.FindFirst(UIAutomationClient.TreeScope_Descendants, cnd)
parent = walker.GetParentElement(menuLabel)
menuTreeRoot = walker.GetParentElement(parent)

# Find and push menu item
logging.info('')
logging.info('***********************************************************')
logging.info('****** Find and push menu item')
logging.info('***********************************************************')
#for currRow in range(2, totalRow):
for currRow in range(2, 3):
  if (type[currRow] == 'Menu'):
    ctrl = None
    cnd = IUIAutomation.CreatePropertyConditionEx(UIAutomationClient.UIA_NamePropertyId,
                                                label[currRow],
												UIAutomationClient.PropertyConditionFlags_None)
    menuLabel = menuTreeRoot.FindFirst(UIAutomationClient.TreeScope_Descendants, cnd)
    logging.info('menuLabel part[%s] is [%s].' % (menuLabel.CurrentProcessId, menuLabel.CurrentName))
    if (menuLabel is None):
      print('!!! Failed: Menu label [%s] does not exist!' % label[currRow])
    else:
      logging.info('Menu label [%s] exist!' % label[currRow])
      parent = walker.GetParentElement(menuLabel)
      cnd = IUIAutomation.CreatePropertyConditionEx(UIAutomationClient.UIA_ControlTypePropertyId,
                                                UIAutomationClient.UIA_ButtonControlTypeId,
												UIAutomationClient.PropertyConditionFlags_None)
      toggle = parent.FindFirst(UIAutomationClient.TreeScope_Descendants, cnd)
      pattern = toggle.GetCurrentPattern(UIAutomationClient.UIA_TogglePatternId)
      ctrl = cast(pattern, POINTER(UIAutomationClient.IUIAutomationTogglePattern))
      ctrl.Toggle()
  #else: # 'Param' and 'Method'
    #sortedLabel = getParamMethodLabel(container)
