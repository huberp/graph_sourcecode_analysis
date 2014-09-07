####################################################################################################
# Python file to be used in gephi. It creates Edges from Nodes based on node attributes, 
# i.e. child-parent-relations
# (c) 2013 - 2014  Peter Huber, Munich
# 
# You can use this script as is or modify it and redistribute. Redistributing original or
# changed version is only allowed with giving credits to the original author
####################################################################################################
# START WITH: execfile("<your path to file>/child-parent-to-nodes_and_edges.py")
#
import sys
import inspect

## CONFIGURATION-SECTION
## 
#cfg_nameIDAttribute = "rid"
#cfg_nameParentIDAttribute = "parent_rid"
cfg_nameIDAttribute = "nid"
cfg_nameParentIDAttribute = "parent"
#
# Accessors for ChildNodeID 
def accessorNodeID(gephiNode):
	#coerce every thing to string in order to be safe later when using parent_id lists
	return str(gephiNode.__findattr_ex__(cfg_nameIDAttribute))

#
# Accessor for ParentNodeID	
def accessorParentNodeID(gephiNode):
	return gephiNode.__findattr_ex__(cfg_nameParentIDAttribute) 

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
	#"active" = false will finally be set for all "double nodes" which
	#are infact only a edge definition, i.e. node is twice or more
	#in node list, because a specific node n has more than one parent
	#and the parent node attribute is only single valued
	for node in g.nodes:
		node.active = True
	
	for node in g.nodes:
		indexKeyValue = indexFunct(node)
		#do we allready have a mapped node?
		#this could be in cases where we have a node-edge mixture imported
		#like a node with a indexID has two lines which are used to define two edges
		if not gephiNodesIndex.has_key(indexKeyValue):
			gephiNodesIndex[indexKeyValue] = node
			#print "Mapped '%s' (%s)" % ( indexKeyValue, type(indexKeyValue) )
		else:
			node.active = False
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
				strParentIndexKeyValue = str(parentIndexKeyValue)
				if not gephiNodeIndex.has_key(indexKeyValue):
					print "NodeIndex value has no node mapped '%s'" % (indexKeyValue)
				if not gephiNodeIndex.has_key(strParentIndexKeyValue):
					print "ParentIndex value has no node mapped '%s' (%s)" % (strParentIndexKeyValue, type(strParentIndexKeyValue))
				if gephiNodeIndex.has_key(indexKeyValue) and gephiNodeIndex.has_key(strParentIndexKeyValue):
					nuEdge = g.addDirectedEdge(gephiNodeIndex[indexKeyValue], gephiNodeIndex[strParentIndexKeyValue])
					#if nuEdge == None:
					#	print "%s -> %s" % (indexKeyValue, parentIndexKeyValue)
					lableValue = "%s -> %s" % (indexKeyValue, strParentIndexKeyValue)
					accessEdge = gephiNodeIndex[indexKeyValue] -> gephiNodeIndex[strParentIndexKeyValue]
					accessEdge.label = lableValue


def removeDoubleNodes(gephiNodeIndex):
	deleteList = []
	for node in g.nodes:
		indexKeyValue = indexFunct(node)
		if not gephiNodeIndex.has_key(indexKeyValue):
			deleteList.add(node)	
	#for node in deleteList:
	#	g.nodes.remove(node)

def postProcessNodes():
	for n in g.nodes: 
		if 0==n.degree:
			n.active = False
		else:
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

