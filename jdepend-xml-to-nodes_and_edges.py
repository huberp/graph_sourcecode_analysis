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

## CONFIGURATION - PLEASE EDIT
## 1.) Input file
cfg_yourJDependInputFile = "<your path to file>/examples/junit/jdepend-on-junit.xml"
## 2.) Common Package, will be stripped of node lables to make them better readable
## The real package name will be kept in the node attribute "package"
cfg_stripCommonBasePackage = ["org.junit.","junit."]
 
 #
 # PASS 4: Handle Cycles
 # let's see how we can get the cycles information into it
 #
def checkOrAddCycle(gephiNode, cycleNumber):
	packageTag = ("<%d>" % (cycleNumber))
	currentCycles = gephiNode.javaCycles
	if currentCycles.find(packageTag) == -1:
		gephiNode.javaCycles=currentCycles+packageTag
		gephiNode.javaCyclesNumber = gephiNode.javaCyclesNumber+1
		print gephiNode.javaCycles
 
def fctPass4HandleCycles(cyclesXMLElem, gephiNodesByPackageLabel):
	#first prepare all "cycles" variables on the nodes
	#if this is left out, some values won't be set correctly
	for node in gephiNodesByPackageLabel.values(): 
		node.javaCycles = ""
		node.javaCyclesNumber = 0
		
	i = 0;
	for xmlElem in cyclesXMLElem.childNodes: 
		if xmlElem.nodeType==dom.Node.ELEMENT_NODE and xmlElem.nodeName=="Package":
			currentGephiNodeName = xmlElem.getAttribute("Name")
			currentPackageGephiNode = gephiNodesByPackageLabel[currentGephiNodeName]
			checkOrAddCycle(currentPackageGephiNode,i)
			cycleMembersXMLElems = xmlElem.getElementsByTagName("Package")
			if(len(cycleMembersXMLElems) != 0):
				for memberXMLElem in cycleMembersXMLElems:
					memberPackageName = memberXMLElem.childNodes.item(0).data
					memberPackageGephiNode = gephiNodesByPackageLabel[memberPackageName]
					print "Cycle %d, member: %s" % (i, memberPackageName)
					checkOrAddCycle(memberPackageGephiNode,i)
					#now treat the corresponding edge
					edges = currentPackageGephiNode -> memberPackageGephiNode
					#be aware that the special "->" edge selector returns a set!
					#in our case with just one member
					edge = edges.pop()
					edge.color=red 
					edge.weight = edge.weight+0.05 ##another sound value would be 0.05
					edge.isInCycle = bool(True) 
					#don't forget we are in a lop here, the next edge starts
					#from out current end
					currentPackageGephiNode = memberPackageGephiNode
		i = i+1
 #
 # PASS 3: Go over all Package-Gephi-Nodes and resizes them according to their
 # indegree
 #
def fctPass3ResizeNodesByIndegree(gephiNodesByPackageLabel):
	for node in gephiNodesByPackageLabel.values(): 
		node.size = 5.0 + (node.indegree)## optional divide by / 4)
		
	 
 #
 # PASS 2: Go over all Package-Elements and read their "DependsUpon"
 # We need this for later wiring dependencies thru edges
 #
def fctPass2ReadDependsOnCreateEdges(packagesXMLElem, gephiNodesByPackage):
	for xmlElem in packagesXMLElem.childNodes: 
		if xmlElem.nodeType==dom.Node.ELEMENT_NODE and xmlElem.nodeName=="Package":
			thisGephiNodeName = xmlElem.getAttribute("name")
			thisPackageGephiNode = gephiNodesByPackage[thisGephiNodeName]
			###getElementsByTagName works here because there's ONLY one single DependsUpon
			###per Package elem, whereas there are Package Elems wrapped in Package Elems...;-(
			theSingleDependsUponXMLElem = xmlElem.getElementsByTagName("DependsUpon")
			#could be that packagees don't have DependsUpon-Section
			if(len(theSingleDependsUponXMLElem) != 0):
				theDepPackages= theSingleDependsUponXMLElem.item(0).getElementsByTagName("Package")
				for depPackageXMLElem in theDepPackages:
					#oh, wow, this DOM-API is really some kind of deep nested ;-)
					otherGephiNodeName = depPackageXMLElem.childNodes.item(0).data
					otherPackageGephiNode = gephiNodesByPackage[otherGephiNodeName]
					print "Edge: %s -> %s" % (thisPackageGephiNode, otherPackageGephiNode)
					nuEdge = g.addDirectedEdge(thisPackageGephiNode, otherPackageGephiNode)
					#seems gephi has a bug that sometimes claims the new 
					#created edge is a NoneType for whatever reason
					#workaround is to read the edge from gephis store...
					reReadEdge = thisPackageGephiNode -> otherPackageGephiNode
					#...and set attributes on that object 
					reReadEdge.label="Source-DependsUpon-Target"
					#set the boolean here to false for all nodes.
					#will be set in Pass 4, see fctPass4HandleCycles
					reReadEdge.isInCycle = bool(False)
	
 #
 # PASS 1: Go over all Package-Elements and create a gephi Node for them
 # We need this for later wiring dependencies thru edges
 # result will be a mapping of "full package name" (node attrib 'package') -> node
 #
def fctPass1ReadPackageCreateNodes(packagesXMLElem):
	gephiNodesByPackage = {}
	##print packagesElem
	##print packagesElem.childNodes
	for xmlElem in packagesXMLElem.childNodes: 
		if xmlElem.nodeType==dom.Node.ELEMENT_NODE and xmlElem.nodeName=="Package":
			gephiNodeNameFull = xmlElem.getAttribute("name")
			gephiNodeLabel = fctStrippedNodeName(gephiNodeNameFull)
			print "%d, %s = %s" % (xmlElem.nodeType, xmlElem.nodeName, gephiNodeLabel)
			nuGephiNode = g.addNode(label=gephiNodeLabel,color=blue, size=5.0)
			#add the full name of the package as a separate column
			nuGephiNode.package = gephiNodeNameFull
			fctAddStats(xmlElem, nuGephiNode)
			gephiNodesByPackage[gephiNodeNameFull] = nuGephiNode
	return gephiNodesByPackage	

#
# Add statistics per package
# xmlElem points to a <package> element of JDepend file
# nuGephiNode points to the newly created gephi node which
# corresponds to the xmlElem
#	
def fctAddStats(packageXmlElem, nuGephiNode):
	#loop though just on element
	for statsXmlNode in packageXmlElem.getElementsByTagName('Stats'):
		for xmlElem in statsXmlNode.childNodes:
			if not xmlElem.nodeType==dom.Node.ELEMENT_NODE:
				continue
			print "Attribute %s = %f" % (xmlElem.nodeName,float(xmlElem.firstChild.nodeValue))
			nuGephiNode.__setattr__(xmlElem.nodeName,float(xmlElem.firstChild.nodeValue))
	
	#
	# Use a Package name as coming from the JDepend-File
	# Strip of a common base Package, given by the String cfg_stripCommonBasePackage
	# But only strip if the Packagename starts with the common part
	# This is usefull for having shorter Labels on the nodes
	#
def fctStrippedNodeName(originalPackageName):
	for aPrefix in cfg_stripCommonBasePackage:
		if originalPackageName.startswith(aPrefix):
			return originalPackageName[len(aPrefix):]
	
	return originalPackageName

	
#
# very simple layout based on Instabilty/Abstractnes values
#	
def fctIALayout():
	for n in g.nodes:
		if not (n.I == None or n.A==None):
			n.x = n.I * 800.0
			n.y = n.A * 800.0
		else:
			n.x = 400.0
			n.y = 400.0
		
#
# MAIN FUNCTION
# Running all the different Passes
#
def main():

	#now parse the xml 
	jdependDOM = dom.parse(cfg_yourJDependInputFile)
 
	# NODES AND EDGES
	# 
	#Create Nodes which represent a Java-Package each
	#get access to the package element in the xml 
	packageElement = jdependDOM.childNodes.item(0).childNodes.item(1)
	gephiNodesByPackageLabel = fctPass1ReadPackageCreateNodes(packageElement)

	#now wire the packages, i.e. we have to go over the xml again :-(
	fctPass2ReadDependsOnCreateEdges(packageElement, gephiNodesByPackageLabel)

	#resize by indegree
	fctPass3ResizeNodesByIndegree(gephiNodesByPackageLabel)
	
	# CYCLES
	#
	cyclesElement  = jdependDOM.childNodes.item(0).childNodes.item(3)
	fctPass4HandleCycles(cyclesElement, gephiNodesByPackageLabel)
	
	# Lyout
	#
	fctIALayout()
	
	# Paths - Floyd Warshall
	#
	nodeLen = int(len(gephiNodesByPackageLabel))
	minId = int((min(g.nodes,key=lambda n: int(n.id))).id)
	d = [[sys.maxint for x in xrange(nodeLen)] for x in xrange(nodeLen)]
	print "Nodes: %d" % nodeLen
	for e in g.edges:
		d[int(e.edge.source.id)-minId][int(e.edge.target.id)-minId] = int(1)
		
	for k in xrange(0, nodeLen-1):
		for i in xrange(0, nodeLen-1):
			for j in xrange(0, nodeLen-1):
				d[i][j] = min(d[i][j], d[i][k]+d[k][j])
		
	
	for n in gephiNodesByPackageLabel.values():
		z = int(n.id) - minId
		maxVal = 0
		for s in xrange(0, nodeLen-1):
			if d[z][s]!=sys.maxint and d[z][s]>maxVal:
				maxVal = d[z][s]
		
		print "z %d -> %d" % (z,maxVal)
		n.longestPath = maxVal		
	
main()	
##
#Access to Modularity Class attribute after haviing it computed - int(n.__findattr_ex__("Modularity Class")) * 100
	
##
#Some calls for try out thing in console
#pElem=jdependDOM.childNodes.item(0).childNodes.item(1)
#>>> pElem.childNodes.item(3).getAttribute("name")

