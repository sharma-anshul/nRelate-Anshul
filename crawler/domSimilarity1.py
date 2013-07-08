from bs4 import BeautifulSoup
from bs4.element import Tag
from download import get

#Helper function for getSimilarity
def getSimilarityValue(url1, url2):
		graph1 = get(url1)
		graph2 = get(url2)
		dom1 = BeautifulSoup(graph1.text, "html5lib")
		dom2 = BeautifulSoup(graph2.text, "html5lib")
		
		return getSimilarity(dom1, dom2)

#Returns boolean value indicating if the DOMs are similar
def getSimilarity(dom1, dom2):
		dom1Children = getChildren(dom1)
		dom2Children = getChildren(dom2)

		if len(dom1Children) == 0 and len(dom2Children) == 0 and dom1.name == dom2.name:
				return 1.0
		else:
				match = matchTags(dom1Children, dom2Children)

				#print float(len(match))/len(dom1Children), float(len(match))/len(dom2Children)
				if not (len(dom1Children) == 0 or len(dom2Children) == 0 or len(match) == 0):
						similarity = 0.0
						for child1, child2 in match:
								similarity = similarity + getSimilarity(child1, child2)		                         
								#print similar, child1.name, child2.name
						return similarity/len(match)
				#print float(len(match))/len(dom1Children), float(len(match))/len(dom2Children)
				else:
						return 0.0

#Returns immediate children of the node 
def getChildren(dom):
		unUsedTags = ["h1", "h2", "h3", "h4", "h5", "h6", "p", "strong", "b", "i", ""]
		children = [child for child in dom.contents if type(child) == Tag and child.name not in unUsedTags]
		#children = sorted(children, key=lambda x: x.name)
		return children

#Gets a list of tuples of matching tags(in order)
def matchTags(tags1, tags2):
		smaller, larger, match, matchedId = tags1, tags2, [], False
		if len(smaller) > len(larger):
				smaller, larger = larger, smaller
				
		smallIndex, largeIndex = 0, 0

		for smallInd in range(len(smaller)):
				tag = smaller[smallInd]
				idMatched = False
				
				tagId, tagName = None, tag.name
				if "id" in tag.attrs:
						tagId = tag["id"]
				for ind in range(largeIndex, len(larger)):
						otherId, otherName = None, larger[ind].name
						if "id" in larger[ind].attrs:
								otherId = larger[ind]["id"]
						if not tagId == None and not otherId == None and tagId == otherId and tagName == otherName:
								match += [(tag, larger[ind])]
								smallIndex = smallInd + 1
								largeIndex = ind + 1
								idMatched = True
								break
				if idMatched:
						matchedId = idMatched
						break

		for smallInd in range(smallIndex, len(smaller)):
				tag = smaller[smallInd]
				idMatched = False

				#Gives matching tag ids preference over tag names
				tagId, tagName = None, tag.name
				if "id" in tag.attrs:
						tagId = tag["id"]
				for ind in range(largeIndex, len(larger)):
						otherId, otherName = None, larger[ind].name
						if "id" in larger[ind].attrs:
						        otherId = larger[ind]["id"]
						if not tagId == None and not otherId == None and tagId == otherId:
								#print tagId, otherId
								match += [(tag, larger[ind])]
								largeIndex = ind + 1
								idMatched = True
								break
				if idMatched:
						matchedId = idMatched
						continue

				#Matches tags by tag name
				for ind in range(largeIndex, len(larger)):
						if tag.name == larger[ind].name:
								match += [(tag, larger[ind])]
								largeIndex = ind+1
								break
		return match
