'''
@File		: host.py
@Date		: 2020/05/30
@Author		: Wang.Yu
@Version	: 1.0
@Contact	: yu.wang@cn.yokogawa.com
@License	: (C)Copyright 2020 Yokogawa China Co., Ltd.
'''
#import pdb
import logging
import os
import csv
import pickle
from uia2 import *
from uiaRRTE import *

# It's EDD's host application's abstract class.
class Host:
	def __init__(self, root=None):
		self.root = root
		self.host = None
	
	@staticmethod
	def logTreeItem(node):
		logging.info('----------------------------------------------------------')
		logging.info('Parent\t: %s (%s)' % (node.elem.label, node.elem.ctrlType))
		if not node.left is None:
			logging.info('Child[0]\t: %s (%s)' % (node.left.elem.label, node.left.elem.ctrlType))
			curr = node.left.right
			cnt = 1
			while not curr is None:
				logging.info('Child[%d]\t: %s (%s)' % (cnt, curr.elem.label, curr.elem.ctrlType))
				cnt = cnt + 1
				curr = curr.right
	
	def startUp(self):
		pass
	
	def shutDown(self):
		pass
	
	def load(self, ddfdi):
		pass
	
	def unload(self):
		pass
	
	def createTree(self, target):
		assert not target == None
		assert not target.elem.isLeaf()
		path = target.getPath()
		for node in path:
			node.select()
			if not node.isEqual(target): continue
			node.getChildren()
			Host.logTreeItem(node)
			currNode = node.left
			if currNode is None:
				continue
			if not currNode.elem.isLeaf():
				self.createTree(currNode)
			currNode = currNode.right
			while not currNode == None:
				if not currNode.elem.isLeaf():
					self.createTree(currNode)
				currNode = currNode.right
	
	def serialize(self):
		f = open('./tree.bin', 'wb')
		pickle.dump(self.root, f)
	
	def restore(self):
		f = open('./tree.bin', 'rb')
		self.root = pickle.load(f)
		
	def traverse(self, root, func):
		pass

# It's logic tree, not control view tree in ui automation.
class TreeNode:
	def __init__(self, elem, parent=None, left=None, right=None):
		self.elem	= elem
		self.parent	= parent # It's logic parent node in tree, not in binary tree
		self.left	= left
		self.right	= right
	
	def isEqual(self, ref):
		node1 = self
		node2 = ref
		while not (node1 == None and node2 == None):
			if node1.elem.label == node2.elem.label:
				node1 = node1.parent
				node2 = node2.parent
			else:
				return False
		return True
	
	def getPath(self):
		path = []
		path.append(self)
		currNode = self
		while not currNode.parent == None:
			currNode = currNode.parent
			path.append(currNode)
		path.reverse()
		return path
	
	def select(self):
		return self.elem.select()
	
	def getChildren(self):
		elems = self.elem.getChildren()
		# set path info into element object
		for elem in elems:
			path = []
			path.extend(self.elem.path)
			path.append(elem) # append self to oneself's path
			elem.path = path
		# append children node into tree
		if len(elems) > 0:
			curr = None
			for x in range(0, len(elems)):
				node = TreeNode(elems[x])
				node.parent = self
				if x == 0:
					self.left = node
					curr = self.left
				else :
					curr.right = node
					curr = curr.right
	
class Element: # abstract class
	def __init__(self, label):
		self.path		= None # parent node path
		self.label		= label
		self.ctrlType	= ''
		self.rectangle	= None
		
	def isLeaf(self):
		return False
	
	def isEnum(self):
		return False
	
	def isBitEnum(self):
		return False
	
	def getSelfScope(self, scope):
		pass
	
	def getScopeAfterSelect(self):
		scope = DesktopRoot
		for elem in self.path:
			scope = elem.getSelfScope(scope)
		return scope
	
	def select(self): # extend a node, for example, group, its processing may be inconsistent on different hosts
		pass
	
	def getChildren(self):
		pass

class Util:
	csvFile = None
	treeDeepth = 0
	csvColumn = 10
	
	@staticmethod
	def preTraverseLabel(node):
		rowElement = []
		if node == None or node.elem == None:
			return
		for x in range(0, Util.csvColumn):
			if(x != Util.treeDeepth):
				rowElement.append('')
			else:
				rowElement.append(node.elem.label)
		rowElement.append(node.elem.label)
		rowElement.append(node.elem.style)
		Util.csvFile.writerow(rowElement)
		Util.treeDeepth += 1
		Util.preTraverseLabel(node.left)
		Util.treeDeepth -= 1
		Util.preTraverseLabel(node.right)
	
	@staticmethod
	def preTraverseEnumOpts(node):
		rowElement = []
		if node == None or node.elem == None:
			return
		if node.elem.isEnum():
			if not node.elem.readonly:
				rowElement.append(node.elem.label)
				Util.csvFile.writerow(rowElement)
				rowElement.clear()
				for item in node.elem.options:
					rowElement.append('')
					rowElement.append(item)
					Util.csvFile.writerow(rowElement)
					rowElement.clear()
			else:
				rowElement.append(node.elem.label + ' (Not Read)')
				Util.csvFile.writerow(rowElement)
				rowElement.clear()
		Util.preTraverseEnumOpts(node.left)
		Util.preTraverseEnumOpts(node.right)
	
	@staticmethod
	def preTraverseBitEnumOpts(node):
		rowElement = []
		if node == None or node.elem == None:
			return
		if node.elem.isBitEnum():
			rowElement.append(node.elem.label)
			Util.csvFile.writerow(rowElement)
			rowElement.clear()
			for item in node.elem.options:
				rowElement.append('')
				rowElement.append(item)
				Util.csvFile.writerow(rowElement)
				rowElement.clear()
		Util.preTraverseBitEnumOpts(node.left)
		Util.preTraverseBitEnumOpts(node.right)
	
	@staticmethod
	def dumpMenuLabel2Csv(root):
		headers = ['ITEM0', 'ITEM1', 'ITEM2', 'ITEM3', 'ITEM4', 'ITEM5', 'ITEM6', 'ITEM7', 'ITEM8', 'ITEM9', 'LABEL', 'STYLE']
		outputPath = os.getcwd() + '\\output\\'
		outputFile = outputPath + 'outputTree.csv'
		if not os.path.exists(outputPath):
			os.makedirs(outputPath)
		with open(outputFile, 'w', newline='', encoding='UTF-8') as Util.csvFile:
			Util.csvFile = csv.writer(Util.csvFile)
			Util.csvFile.writerow(headers)
			Util.preTraverseLabel(root)
	
	@staticmethod
	def dumpEnumOpt2Csv(root):
		headers = ['ENUM', 'OPTION']
		outputPath = os.getcwd() + '\\output\\'
		outputFile = outputPath + 'outputEnumOpts.csv'
		if not os.path.exists(outputPath):
			os.makedirs(outputPath)
		with open(outputFile, 'w', newline='', encoding='UTF-8') as Util.csvFile:
			Util.csvFile = csv.writer(Util.csvFile)
			Util.csvFile.writerow(headers)
			Util.preTraverseEnumOpts(root)
	
	@staticmethod
	def dumpBitEnumOpt2Csv(root):
		headers = ['BITENUM', 'OPTION']
		outputPath = os.getcwd() + '\\output\\'
		outputFile = outputPath + 'outputBitEnumOpts.csv'
		if not os.path.exists(outputPath):
			os.makedirs(outputPath)
		with open(outputFile, 'w', newline='', encoding='UTF-8') as Util.csvFile:
			Util.csvFile = csv.writer(Util.csvFile)
			Util.csvFile.writerow(headers)
			Util.preTraverseBitEnumOpts(root)