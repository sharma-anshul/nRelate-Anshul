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
		
		# For each pattern, counts how many URLs it matches
		pathCount, pathDict = countMatchingUrls(pathPatterns, urls)

		#allUnique = [path for path in pathCount if pathCount[path] == 1]
		#if len(allUnique) == len(pathCount):
		#		pathPatterns = []
		#		for path in pathCount:
		#				pathPatterns += [formatPath(path)]
		#		pathCount, pathDict = countMatchingUrls(pathPatterns, urls)

		# Only uses those regex which match atleast 10% of the link count
		cutoff = (0.1) * len(paths)
		selectedPaths = []
		for path in pathCount:
				if pathCount[path] >= cutoff and path != "/":
						selectedPaths += [path]
						
		sortedPaths = collatePatterns(set([path for path in selectedPaths]), pathDict)
		return sortedPaths

def collatePatterns(patterns, pathDict):
		similarPatts = {}
		collated = []
		for pattern in patterns:
				firstPart = pattern.split("/")[1]
				#print firstPart
				if firstPart not in similarPatts:
						similarPatts[firstPart] = [pattern]
				else:
						similarPatts[firstPart] += [pattern]
		
		for firstPart in similarPatts:
				#print firstPart
				unrequired = []
				for pattern1 in similarPatts[firstPart]:
						for pattern2 in similarPatts[firstPart]:
								if pattern1 == pattern2 or pattern1 in unrequired or pattern2 in unrequired:
										break
								urls1 = set(pathDict[pattern1])
								urls2 = set(pathDict[pattern2])
								intersection = urls1.intersection(urls2)
								
								print pattern1, pattern2, len(intersection), len(urls1), len(urls2)

								if len(intersection) == len(urls2) or len(intersection) == len(urls1):
										temp = pattern1 if len(urls2) > len(urls1) else pattern2
										unrequired += [temp]
				print unrequired	
				similarPatts[firstPart] = [patt for patt in similarPatts[firstPart] if patt not in unrequired]
				collated += similarPatts[firstPart]
		return collated

def countMatchingUrls(pathPatterns, urls):
		pathCount, pathDict = {}, {}

		for path in pathPatterns:
				temp = path
				#temp = formatPath(path)
				temp = temp.replace("-", "\-")
				for url in urls:
						#if temp.startswith("/\\"):
						#       temp = temp[0] + '^' + temp[1:-1] + '$' + temp[-1]
						if re.match(temp, urlparse(url).path) and not path == "/":
								if temp not in pathCount:
										pathCount[temp] = 1
										pathDict[temp] = [url]
								else:
										pathCount[temp] += 1
										pathDict[temp] += [url]
		
		return pathCount, pathDict

def formatPath(path):
		pathParts = path.split("/")
		newPathParts = []
		for section in pathParts:
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
						if len(children) > 1 and not parent.value == "":
								section = formatSection(section)
						elif len(children) > 1 and len(grandChildren) < 1 and parent.value == "":
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
