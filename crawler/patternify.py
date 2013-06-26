from urlparse import urlparse
import re

boilerplate = set(["privacy", "contact-us", "contact", "video", "help", "about", "feedback"])

def checkBoilerplate(link):
		global boilerplate
		linkParts = set([part.lower() for part in link.split("/")])
		if len(linkParts.intersection(boilerplate)) > 0:
				return False
		return True

def getPatterns(urls):
		paths = []
		for url in urls:
				if not url.startswith("http://"):
						url = "http://" + url[:-1]
				parsedUrl = urlparse(url)
				domain = parsedUrl.hostname
				path = parsedUrl.path
				if path != "" and checkBoilerplate(path):
						paths += [path]
		paths = sorted(paths)
		# form tree using actual components of URL
		pathTree = getPathTree(paths)
		
		tempPath, pathPatterns = "", {}
		# converts components of the tree to regex
		getPaths(tempPath, pathTree, pathPatterns)	
		
		pathCount = {}
		pathDict = {}

		# for each regex counts how many URLs it matches
		for path in pathPatterns:
				temp = formatPath(path)
				temp = temp.replace("-", "\-")
				for url in urls:
						#if temp.startswith("/\\"):
						#		temp = temp[0] + '^' + temp[1:-1] + '$' + temp[-1]
						if re.match(temp, urlparse(url).path):
								if temp not in pathCount:
										pathCount[temp] = 1
										pathDict[temp] = [url]
								else:
										pathCount[temp] += 1
										pathDict[temp] += [url]

		# Only uses those regex which match atleast 10% of the link count
		cutoff = (0.1) * len(paths)
		selectedPaths = []
		for path in pathCount:
				if pathCount[path] >= cutoff and path != "/":
						selectedPaths += [path]
						
		sortedPaths = set([path for path in selectedPaths])
		return sortedPaths


def formatPath(path):
		pathParts = path.split("/")
		newPathParts = ['', pathParts[1]]
		for section in pathParts[2:]:
				newPathParts += [formatSection(section)]

		return "/".join(newPathParts)


def formatSection(section):
		regex = ["[\w\d_]+", "[\w\d-]+", "\w+", "\d+", "[\w_]+", "[\w-]+", "[\d_]+", "[\d-]+", "[\w-_]+", "[\w\d-_]+", "[\d-_]+", "[\w-_]+"]
		if not section in regex:
				separator = getSeparator(section)
				if not separator == None:
						tempValue = ""
						if section.startswith(separator):
								tempValue += separator
						for part in section.split(separator):
								tempPart = "NUM"
								if not part == "NUM":
										tempSeparator = getSeparator(part)
										if not tempSeparator == None:
												tempPart = part
										else:
												tempPart = "WORD"
								if tempValue == "" or tempValue == separator:
										tempValue += tempPart
								else:
										tempValue += separator + tempPart
						section = tempValue
						sectionParts = set(section.split(separator))
						if sectionParts == set(["NUM"]):
								section = "[\d" + separator + "]+"
						elif sectionParts == set(["WORD"]):
								section = "[\w" + separator + "]+"
						elif sectionParts == set(["NUM", "WORD"]):
								section = "[\w\d" + separator + "]+"
						else:
								temp = []
								for part in sectionParts:
										temp += [formatSection(part)]
								regex = [separator]
								for rx in temp:
										regex += getRegexComponents(rx)
								section = "[" + "".join(set(regex))  + "]+"
				else:
						if not section == "NUM" and not section == '':
								section = "\w+"
						elif section == "NUM":
								section = "\d+"

		return section	


def getPathTree(paths):
		pathTree = Node(None)
		for path in paths:
				createPathTree(pathTree, path, 0)
		formattedPathTree = Node(None)
		formatPathTree(pathTree, formattedPathTree)
		return formattedPathTree


def createPathTree(parent, path, index):
		pathParts = path.split("/")
		if index < len(pathParts):
				currValue = pathParts[index]
				separator = getSeparator(currValue)
				
				if not separator == None:
						tempValue = "" 
						if currValue.startswith(separator):
								tempValue += separator
						
						for part in currValue.split(separator):
								if part.isdigit():
										part = "NUM"
								if tempValue == "":
										tempValue += part
								else:
										tempValue += separator + part
						currValue = tempValue
				else:
						if currValue.isdigit():
								currValue = "NUM"
				
				node = None
				children = parent.getChildren()
				if currValue in children:
						node = children[currValue]
				else:
						node = Node(currValue)
						parent.addChild(node)
				
				createPathTree(node, path, index + 1)


def formatPathTree(parent, newParent):
		children = parent.getChildren()
		if len(children) == 0:
				return
		else:
				for child in children:
						section = child
						grandChildren = children[child].getChildren()
						if len(children) > 1 and len(grandChildren) <= 1:
								section = formatSection(section)
						
						if section == "NUM":
								section = "\d+"

						newChild = Node(section)
						newParent.addChild(newChild)
						formatPathTree(children[child], newParent.getChildren()[section])


def getPaths(path, parent, pathPatterns):
		children = parent.getChildren()
		if len(children) == 0:
				if path in pathPatterns:
						pathPatterns[path] += 1
				else:
						pathPatterns[path] = 1
		else:
				for child in children:
						section = child
						if not path == "/":
								getPaths(path + "/"  + section, children[child], pathPatterns)
						else:
								getPaths(path + section, children[child], pathPatterns)


def getSeparator(path):
		separator = None
		maxParts = 1
		for sep in ["_", "-"]:
				parts = len(path.split(sep))
				if parts > maxParts:
						maxParts = parts
						separator = sep
		return separator

def getRegexComponents(regex):
		components = []
		if regex.startswith("["):
				ind = 1
				while not regex[ind] == "]":
						if regex[ind] == "\\":
								components += [regex[ind:ind + 2]]
								ind += 2
						else:
								components += [regex[ind]]
								ind += 1
		elif regex.startswith("\\"):
				components += [regex[:-1]]
		
		return components

class Node():
		def __init__(self, value):
				self.value = value
				self.children = {}

		def getChildren(self):
				return self.children

		def getValue(self):
				return self.value

		def addChild(self, child):
				if child.value not in self.children:
						self.children[child.value] = child
