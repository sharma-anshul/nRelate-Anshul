from bs4 import BeautifulSoup
from bs4.element import Tag
from download import get


"""Usage: >>> domSimilarity.getSimilarityValue("http://cnn.com", "http://bbc.co.uk")
          >>> 0.625
"""

#Helper function for getSimilarity
def getSimilarityValue(url1, url2):
		page1 = get(url1)
		page2 = get(url2)

		dom1 = BeautifulSoup(page1.text, "html5lib")
		dom2 = BeautifulSoup(page2.text, "html5lib")
		
		return getSimilarity(dom1, dom2)

#Returns a value between 0 and 1 indicating similarity
def getSimilarity(dom1, dom2):
		dom1Children = getChildren(dom1)
		dom2Children = getChildren(dom2)

		if len(dom1Children) == 0 and len(dom2Children) == 0 and dom1.name == dom2.name:
				return 1.0
		else:
				match = matchTags(dom1Children, dom2Children)
				#print float(len(match))/len(dom1Children), float(len(match))/len(dom2Children)
				if (len(dom1Children) == 0 or len(dom2Children) == 0) or len(match) == 0:
						return 0.0
				
				#print float(len(match))/len(dom1Children), float(len(match))/len(dom2Children)
				else: 
						similarity = 0.0 
						for child1, child2 in match:
								similarity = similarity + getSimilarity(child1, child2)
								#print similar, child1.name, child2.name
						return similarity/len(match)

#Gets immediate children of the node
def getChildren(dom):
		children = [child for child in dom.contents if type(child) == Tag]
		#children = sorted(children, key=lambda x: x.name)
		return children

#Returns a list of pair of matching tags(in order)
def matchTags(tags1, tags2):
		smaller, larger, match = tags1, tags2, []
		if len(smaller) > len(larger):
				smaller, larger = larger, smaller
		
		lastIndex = 0
		for tag in smaller:
				for ind in range(lastIndex, len(larger)):
						if tag.name == larger[ind].name:
								match += [(tag, larger[ind])]
								lastIndex = ind+1
								break
		return match
