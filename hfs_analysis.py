# -*- coding:CP949 -*-
from struct import *
import sys
import math


p2 = lambda x, y : pack_from('>H', x, y)
up1 = lambda x, y : unpack_from('@c', x, y)[0]
up2 = lambda x, y : unpack_from('>H', x, y)[0]
up4 = lambda x, y : unpack_from('>L', x, y)[0]
up8 = lambda x, y : unpack_from('>Q', x, y)[0]

def CalcOffset(target, nodesize, blocksize, catalog):
	return  (target*nodesize)+(catalog*blocksize)

def LeafNode(catalog, offset, blocksize, nodesize):
	nodeoffset = offset+14
	f.seek(nodeoffset)
	keylengthtemp = f.read(2)
	keylength = up2(keylengthtemp, 0x00)
	keyinfotemp = f.read(keylength)
	keytypetemp = f.read(2)
	keytype = up2(keytypetemp, 0x00)
	if keytype == 1 :
		print ("Type : File!!")
	elif keytype == 2:
		print ("Type : Directory!!")
	
	return

def IndexNode(catalog, offset, blocksize, nodesize):
	keylength = 0
	i = 0
	print ("[*] IndexNode =====================================")
	while(1):
		offset = offset + 6*i + keylength 
		f.seek(offset)	
		lengthtemp = f.read(2)
		keylength = up2(lengthtemp, 0x00)
		if keylength == 0:
			break
		keyinfo = f.read(4)
		parentid = up4(keyinfo, 0x00)
		print ("ParentID : ", parentid)
		keynamelengthtemp = f.read(2)
		keynamelength = up2(keynamelengthtemp, 0x00)
		keyname = f.read(keylength-6)
		print ('Name : ', keyname.decode('unicode-escape'))	
		targetleaftemp = f.read(4)
		targetleaf = up4(targetleaftemp, 0x00)

		print ("TargetLeaf Node : ", targetleaf)
		targetleafoffset = CalcOffset(targetleaf, nodesize, blocksize, catalog)
		print ("TargetLeaf Offset : ", targetleafoffset)
		LeafNode(catalog, targetleafoffset, blocksize, nodesize)
		i = 1
	
def BTHeaderNode(catalog, offset, blocksize):

	print ("[*] BTHeaderRecord ============================")
	f.seek(offset)
	btheader = f.read(106)

	rootnode = up4(btheader, 0x02)
	print ("Root Node : ", rootnode)

	nodenum = up4(btheader, 0x16)
	print ("Number of Node : ", nodenum)

	leafnum = up4(btheader, 0x06)
	print ("Number of Leaf Node : ", leafnum)

	nodesize = up2(btheader, 0x12)
	print ("Size of a Node Page : ", nodesize)

	firstleaf = up4(btheader, 0x0A)
	print ("First Leaf Node : ", firstleaf )

	lastleaf = up4(btheader, 0x0E)
	print ("Last Leaf Node : ", lastleaf)

	rootnodeoffset = CalcOffset(rootnode, nodesize, blocksize, catalog)
	print ("Root Node Offset : ", rootnodeoffset)

	CheckNodeType(int(rootnodeoffset), blocksize, nodesize, catalog)

def CheckNodeType(offset, blocksize, nodesize, catalog):
	f.seek(offset)
	nodedescriptor = f.read(14)

	flink = up4(nodedescriptor, 0x00)
	blink = up4(nodedescriptor, 0x04)
	nodetype = up1(nodedescriptor, 0x08)
	print ('fLink : ', flink)
	print ('bLink : ', blink)
	if nodetype == b'\xff':
		print ('NodeType : LeafNode')
	elif nodetype == b'\x00':
		print ('NodeType : IndexNode')
		IndexNode(catalog, offset+14, blocksize, nodesize)
	elif nodetype == b'\x01':
		print ('NodeType : BTHeaderNode')
	elif nodetype == b'\x02':
		print ('NodeType : BTMapNode')

def CatalogCheckNodeType(catalog, blocksize):
	for keys in catalog.keys():
		offset = keys*blocksize
		f.seek(offset)
		nodedescriptor = f.read(14)

		flink = up4(nodedescriptor, 0x00)
		print ('fLink : ', flink)
		blink = up4(nodedescriptor, 0x04)
		print ('bLink : ', blink)
		nodetype = up1(nodedescriptor, 0x08)
		if nodetype == b'\xff':
			print ('NodeType : LeafNode')
		elif nodetype == b'\x00':
			print ('NodeType : IndexNode')
		elif nodetype == b'\x01':	
			print ('NodeType : BTHeaderNode')
			BTHeaderNode(keys, offset+14, blocksize)
		elif nodetype == b'\x02':
			print ('NodeType : BTMapNode')

f = open("hfsx_image", 'rb')

f.seek(1024)
volumeheader = f.read(1024)

print ("[*]Volume Header  ================================")

signature = up2(volumeheader, 0x0)
print ('Magic Signature : ', hex(signature))

blocksize = up4(volumeheader, 0x28)
print ('Block Size : ', blocksize)

totalblocks = up4(volumeheader, 0x2c)
volumesize = totalblocks * blocksize
print ('Volume Size : ', volumesize)

countblock = 0
i = 0

f.seek(1296)
forkdata = f.read(16)

print ("[*]Catalog Files  =================================")

catalogblock = {}

logical_size = up8(forkdata, 0x0)
print('Logical Size : ', logical_size)

clump_size = up4(forkdata,0x8)
print('Clump Size : ', clump_size)

total_blocks = up4(forkdata, 0xC)
print('Total Blocks : ', total_blocks)


for i in range(0, 8):
	
	descriptor = f.read(8)
	startblock = up4(descriptor, 0x00)
	if startblock == 0x00000000 :
		break

	print('Start Block : ', startblock)
	

	blockcount = up4(descriptor, 0x04)
	print('Block Count : ', blockcount)
	catalogblock[startblock] = blockcount

CatalogCheckNodeType(catalogblock, blocksize)



