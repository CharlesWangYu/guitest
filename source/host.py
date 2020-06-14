import pdb
import logging
import os
import sys
import time
import subprocess
import xlrd
import win32gui
import win32api
import win32con
import uia2
#import comtypes
from configparser import ConfigParser
from comtypes.client import *
from ctypes import *

# It's EDD's host application's abstract class.
class Host:
	def __init__(self):
		self.root = None
	
	def startUp(self):
		pass
	
	def shutDown(self):
		pass
	
	def load(self, ddfdi):
		pass
	
	def unload(self):
		pass
		
	def createTree(self, root):
		assert not root == None
		#assert not root.elem.name == 'Online'
		assert not root.isLeafNode()
		path = root.getPath()
		#for item in path:
		#	logging.info(item.elem.name)
		# push button sequence to getting into current tree node
		for item in path:
			item.select()
			if item.isEqual(root):
				item.appendChildren()
				#logTreeItem(item)
				currNode = item.left
				if not currNode.isLeafNode(): self.createTree(currNode)
				currNode = currNode.right
				while not currNode == None:
					if not currNode.isLeafNode(): self.createTree(currNode)
					currNode = currNode.right
		time.sleep(2)
	
	def traversal(self, root):
		pass

# It's logic tree, not control view tree in ui automation.
class TreeNode:
	def __init__(self, elem, parent=None, left=None, right=None):
		self.elem = elem
		self.parent = parent # It's logic parent node in tree, not in binary tree
		self.left = left
		self.right = right
	
	def isEqual(self, ref):
		node1 = self
		node2 = ref
		while not (node1 == None and node2 == None):
			if node1.elem.name == node2.elem.name:
				node1 = node1.parent
				node2 = node2.parent
			else:
				return False
		return True
	
	def isLeafNode(self):
		return isinstance(currNode.elem, Leaf)

	def getPath(self):
		path = []
		path.append(self)
		currNode = self
		while not currNode.parent == None:
			currNode = currNode.parent
			path.append(currNode)
		#path.remove(self.root)
		path.reverse()
		return path
	
	def select(self):
		self.elem.select()
	
	def appendChildren(self):
		elems = self.elem.children()
		if len(elems) > 0:
			self.left = TreeNode(elems[0], self)
			currNode = self.left
			for x in range(1, len(elems)):
				currNode.right = TreeNode(elems[x], self)
				currNode = currNode.right
'''
class Tree: # It's logic tree, not control view tree in ui automation 
	def __init__(self, root=None, curr=None):
		self.root = root
		self.curr = curr
'''

class Element: # abstract class
	def __init__(self, name):
		self.name = name
		self.ctrlType = None
		self.rectangle = None
	
	def select(self): # extend a node, for example, group, its processing may be inconsistent on different hosts
		pass
		
	def children(self):
		pass

