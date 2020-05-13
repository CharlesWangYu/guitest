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

class Node(object):
    """Node Class"""
    def __init__(self, elem=None, type=None, lchild=None, rchild=None):
        self.elem = elem
        self.item = item	# MENU/WINDOW/PAGE,GROUP/PARAM/METHOD
        self.mode = mode	# RO or RW
        self.type = type	# Parameter type (INT,Float,Enum,BitEnum)
        self.lchild = lchild
        self.rchild = rchild

class Tree(object):
    """Tree Class"""
    def __init__(self):
        self.root = Node()
        self.myQueue = []
