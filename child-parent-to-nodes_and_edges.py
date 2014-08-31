####################################################################################################
# Python file to be used in gephi. It reads in JDepend XML Files and creates Nodes and Edges from it
# (c) 2013 - 2014  Peter Huber, Munich
# 
# You can use this script as is or modify it and redistribute. Redistributing original or
# changed version is only allowed with giveing reference to the original author
####################################################################################################
# START WITH: execfile("<your path to file>/jdepend-xml-to-nodes_and_edges.py")
#
# Read about Python, german only: http://openbook.galileocomputing.de/python/python_kapitel_08_003.htm#mjfb4d02fccab9edcdc5ad084f35eaeaa6
#
import xml.dom.minidom as dom
import sys
import inspect

## CONFIGURATION
## 1.) Input file
cfg_yourJDependInputFile = "<your path to file>/examples/junit/jdepend-on-junit.xml"
## 2.) Common Package, will be stripped of node lables to make them better readable
## The real package name will be kept in the node attribute "package"
cfg_stripCommonBasePackage = ""

#
# Accessors for ChildNodeID 
def accessorNodeID(gephiNode):
	return gephiNode.__findattr_ex__("rid")

#
# Accessor for ParentNodeID	
def accessorParentNodeID(gephiNode):
	return gephiNode.__findattr_ex__("parent_rid") 

#	
#splits up a list of parentIDs as obtained by accessorParentNodeID
#it might be a comma seperated list of values  
def splitNodeIDs(parentNodeIDValue):
	if isinstance(parentNodeIDValue, str):
		return [x.strip() for x in parentNodeIDValue.split(",")]
	else:
		return [parentNodeIDValue]
 
#
# build a node index by a given index function, for instance "accessorNodeID" 
def buildIndex(indexFunct):
	gephiNodesIndex = {}
	
	#prepare node value
	#"inactive" will be set for all "double nodes" which
	#are infact only a edge definition, i.e. node is twice or more
	#in list, because a specific node n has more than one parent
	for node in g.nodes:
		node.inactive = False
	
	for node in g.nodes:
		indexKeyValue = indexFunct(node)
		#do we allready have a mapped node?
		#this could be in cases where we have a node-edge mixture imported
		#like a node with a indexID has two lines which are used to define two edges
		if not gephiNodesIndex.has_key(indexKeyValue):
			gephiNodesIndex[indexKeyValue] = node
		else:
			node.inactive = True
	return gephiNodesIndex

#
# now build adges from a prebuilt index, with two accessor functions
# a.) indexFunct, same as used for buildIndex, which will be used to get the ID of the node itself
# b.) parentIndexFunct, which is used to get (a list?) the parentIndex of a "node" value
def buildEdges(gephiNodeIndex, indexFunct, parentIndexFunct):
	for node in g.nodes:
		indexKeyValue = indexFunct(node)
		parentIndexKeyValueList = parentIndexFunct(node)
		#it's potentially a list of parent IDs
		for parentIndexKeyValue in splitNodeIDs(parentIndexKeyValueList):
			#print indexKeyValue, parentIndexKeyValue
			#print "ID %s -> ParentID %s" % (indexKeyValue, parentIndexKeyValue)
			if indexKeyValue!=None and parentIndexKeyValue!=None:
				if gephiNodeIndex.has_key(indexKeyValue) and gephiNodeIndex.has_key(parentIndexKeyValue):
					nuEdge = g.addDirectedEdge(gephiNodeIndex[indexKeyValue], gephiNodeIndex[parentIndexKeyValue])
					#if nuEdge == None:
					#	print "%s -> %s" % (indexKeyValue, parentIndexKeyValue)
					lableValue = "%s -> %s" % (indexKeyValue, parentIndexKeyValue)
					accessEdge = gephiNodeIndex[indexKeyValue] -> gephiNodeIndex[parentIndexKeyValue]
					accessEdge.label = lableValue
				else:
					print "Some index value has no node mapped %s %s" % (indexKeyValue, parentIndexKeyValue)


def removeDoubleNodes(gephiNodeIndex):
	deleteList = []
	for node in g.nodes:
		indexKeyValue = indexFunct(node)
		if not gephiNodeIndex.has_key(indexKeyValue):
			deleteList.add(node)	
	#for node in deleteList:
	#	g.nodes.remove(node)

def postProcessNodes()
	for n in g.nodes: 
		n.size = 2 + n.degree*0.2
	
#########################################################################################
# MAIN FUNCTION
# Running all the different Passes
#
def main():

	#1st build up an index of ID values to nodes with a specific accessor
	gephiNodeIndex = buildIndex(accessorNodeID)
	
	#now build edges
	buildEdges(gephiNodeIndex, accessorNodeID, accessorParentNodeID)
	
	#postprocess nodes, i.e. adjust size by degree 
	postProcessNodes()
	
main()	
	
##
#Some calls for try out thing in console
#pElem=jdependDOM.childNodes.item(0).childNodes.item(1)
#>>> pElem.childNodes.item(3).getAttribute("name")

