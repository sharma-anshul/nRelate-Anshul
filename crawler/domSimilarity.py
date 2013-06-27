from bs4 import BeautifulSoup
from bs4.element import Tag

def areSimilar(graph1, graph2):
		dom1 = BeautifulSoup(graph1.text, "html5lib")
		dom2 = BeautifulSoup(graph2.text, "html5lib")
		
		return getSimilarity(dom1, dom2)

def getSimilarity(dom1, dom2):
		dom1Children = getChildren(dom1)
		dom2Children = getChildren(dom2)

		if len(dom1Children) == 0 and len(dom2Children) == 0:
				return True
		else:
				match = matchTags(dom1Children, dom2Children)
				#print float(len(match))/len(dom1Children), float(len(match))/len(dom2Children)
				if (len(dom1Children) == 0 or len(dom2Children) == 0) or len(match) == 0:
						return True
				
				#print float(len(match))/len(dom1Children), float(len(match))/len(dom2Children)

				if float(len(match))/len(dom1Children) >= 0.5 or float(len(match))/len(dom2Children) >= 0.5:
						similar = True
						for child1, child2 in match:
								similar = similar and getSimilarity(child1, child2)
								#print similar, child1.name, child2.name
						return similar
				else:
						return False

def getChildren(dom):
		children = [child for child in dom.contents if type(child) == Tag]
		#children = sorted(children, key=lambda x: x.name)
		return children

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
