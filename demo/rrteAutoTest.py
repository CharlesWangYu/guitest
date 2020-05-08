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
    for x in range(0, totalRow - paramStartRow):
      element = all.GetElement(x)
      logging.info('[%s]Element1[%s] is searched.' % (element.CurrentProcessId, element.CurrentName))
    return all

def seekParentElement(currentElement):
   walker = IUIAutomation.ControlViewWalker
   parent = walker.GetParentElement(currentElement)
   return parent

def compareLabel(specLabel, appLabel):
   #logging.info('specLabel is [%s]. appLabel is [%s]' % (specLabel, appLabel))
   return (specLabel == appLabel)

if __name__ == '__main__':
  # Define const and parameter
  DELAY_OPEN_RRET			= 6
  DELAY_PUSH_BUTTON			= 4
  MAX_MENU_ITEM_NUM			= 30
  MENU_ITEM_TPE_COLUMN		= 6
  label						= [''] * MAX_MENU_ITEM_NUM
  type						= [''] * MAX_MENU_ITEM_NUM
  viewLabel					= [''] * MAX_MENU_ITEM_NUM

  #pdb.set_trace()
  logging.basicConfig(level = logging.ERROR)
  
  # Load and parser config file
  logging.info('***********************************************************')
  logging.info('****** Load and parser config file')
  logging.info('***********************************************************')
  config = ConfigParser()
  config.read('testRrte.conf', encoding='UTF-8')

  inputMode	= config['MISC']['TEST_FILE_TYPE'].strip("'")
  hostApp	= config['MISC']['HOST_APP_FILE'].strip("'")
  specFile	= config['MISC']['INPUT_SPEC_FILE'].strip("'")
  testFile	= config['MISC']['TEST_FILE'].strip("'")
  outPath	= config['MISC']['OUTPUT_PATH'].strip("'")

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
  totalRow = sheet.nrows - 1
  
  for currRow in range(1, sheet.nrows):
    for currCol in range(MENU_ITEM_TPE_COLUMN):
      label[currRow-1] += sheet.cell(currRow, currCol).value
    type[currRow-1] = sheet.cell(currRow, MENU_ITEM_TPE_COLUMN).value;
    logging.info('No.%d, (Label = %s, Type = %s)' % (currRow-1, label[currRow-1], type[currRow-1]))
  
  # Start UI Automation
  logging.info('')
  logging.info('***********************************************************')
  logging.info('****** Start UI Automation')
  logging.info('***********************************************************')
  #UIAutomationClient = GetModule('UIAutomationCore.dll')
  IUIAutomation = CreateObject('{ff48dba4-60ef-4201-aa87-54103eef594e}', interface=UIAutomationClient.IUIAutomation)
  root = IUIAutomation.GetRootElement()
  rrteRoot = searchOneElement(root, 'Reference Run-time Environment', UIAutomationClient.UIA_NamePropertyId)
  
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
  
  # Find and push menu item
  logging.info('')
  logging.info('***********************************************************')
  logging.info('****** Check menu and parameter label')
  logging.info('***********************************************************')
  for currRow in range(1, 3):
    logging.info('Comparing the menu label[%s].' % label[currRow])
    if (type[currRow] == 'Menu' and type[currRow+1] == 'Menu'):
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
    elif (type[currRow] == 'Menu' and type[currRow+1] != 'Menu'):
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
        logging.info('totalRow = %d' % totalRow)
        logging.info('paramStartRow = %d' % paramStartRow)
        all = searchAllElement(pane, 'Label', UIAutomationClient.UIA_AutomationIdPropertyId)
        for x in range(paramStartRow, totalRow):
          if (not compareLabel(label[x], all.GetElement(x-paramStartRow).CurrentName)):
            print('!!! Failed: Param label [%s] does not exist!' % label[x])