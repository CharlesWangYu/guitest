import pdb
import logging
import time
import subprocess
import xlrd
#import comtypes
from configparser import ConfigParser
from comtypes.client import *
from ctypes import *

#UIAutomationClient = GetModule('UIAutomationCore.dll')
#IUIAutomation = CreateObject('{ff48dba4-60ef-4201-aa87-54103eef594e}', interface=UIAutomationClient.IUIAutomation)
	
class Tree:
	"""Tree Class"""
	def __init__(self, name=None):
		#self.style = style	# MENU/WINDOW/PAGE,GROUP/PARAM/METHOD
		#elf.mode = mode	# RO or RW
		#self.type = type	# Parameter type (INT,Float,Enum,BitEnum)
		self.name = name	# Node name
		self.parent = None
		self.lchild = None
		self.rchild = None

	def __search(self, name):
		currNode = self
		while(currNode is not None and not name == currNode.name):
			if(not name == currNode.name and not currNode.lchild == None):
				currNode = currNode.lchild.__search(name)
			if(not name == currNode.name and not currNode.rchild == None):
				currNode = currNode.rchild.__search(name)
		return currNode

	def search(self, name):
		return self.__search(name)

	def insert(self, parentName=None, name=None):
		"""Insert tree node under parent node"""
		parentNode = self.__search(parentName)
		logging.info('Current node name = %s' % parentNode.name)
		if parentName == None:
			self.name = name
		else:
			if parentNode != None:
				node = Tree(name)
				if parentNode.lchild == None:
					parentNode.lchild = node
				else:
					currNode = parentNode.lchild
					while (not currNode.rchild == None):
						currNode = currNode.rchild
					currNode.rchild = node
	
	def addChildNode(self, name=None):
		"""Add tree node under current node"""
		if self.name == None:
			self.name = name
			self.parent = None
			return self
		else:
			node = Tree(name)
			node.parent = self
			if self.lchild == None:
				self.lchild = node
			else:
				currNode = self.lchild
				while (not currNode.rchild == None):
					currNode = currNode.rchild
				currNode.rchild = node
			return self

	def traverse(self):
		if self == None:
			return
		if not self.lchild == None:
			self.lchild.traverse()
		if not self.rchild == None:
			self.rchild.traverse()

	def dump(self):
		if self == None:
			return
		if self.parent == None:
			str = 'None'
		else:
			str = self.parent.name
		print ('node = %s, parent = %s' %(self.name, str))
		if not self.lchild == None:
			self.lchild.dump()
		if not self.rchild == None:
			self.rchild.dump()

#pdb.set_trace()
logging.basicConfig(level = logging.INFO)

tree = Tree()
#tree.insert(name='Online')
#tree.insert('Online', 'Process variables root menu')
#tree.insert('Online', 'Diagnostic root menu')
#tree.insert('Online', 'Maintenance root menu')
#tree.insert('Online', 'Device root menu')
#tree.insert('Process variables root menu', 'Dynamic variables')
#tree.insert('Process variables root menu', 'Device variables')
#tree.insert('Process variables root menu', 'Dynamic variables status')
#tree.insert('Process variables root menu', 'Totalizer count')
#tree.insert('Process variables root menu', 'View outputs')
curr = tree.addChildNode('Online')
curr.addChildNode('Process variables root menu')
curr.addChildNode('Diagnostic root menu')
curr.addChildNode('Maintenance root menu')
curr.addChildNode('Device root menu')
curr = curr.lchild
curr.addChildNode('Dynamic variables')
curr.addChildNode('Device variables')
curr.addChildNode('Dynamic variables status')
curr.addChildNode('Totalizer count')
curr.addChildNode('View outputs')
tree.dump()

