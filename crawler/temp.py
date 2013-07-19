import classifier
import distmat
import patternify

def compute_classifier_domain_info():
		patterns = set()
		
		# Gets a sample of links from the website starting from the homepage
		already_analyzed = set()
		links = self._get_all_internal_links(self._start_url)
		
		for i in range(depth - 1):
				if len(links) > 3000:
						break
				sub_links = set()
				cpt = 0
				for link in links:
						print "link %d/%d [%s]" % (cpt, len(links), link)
						cpt += 1
						if (len(sub_links) > 3000):
								break
						if not link in already_analyzed:
								sub_links = sub_links.union(self._get_all_internal_links(link))
								already_analyzed.add(link)
				links = links.union(sub_links)

		self.log("Finished. Got %d sublinks on %d levels" % (len(links), depth))
		
		# Identifies links pointing to content and generates patterns
		ones, zeros = classifier.testSVM(links)
		mean, distMat = distmat.getDistanceMatrix(ones)
		content = []
		for link in distMat:
				if sum(distMat[link])/len(distMat) >= mean:
						content += [link]
		patterns = patternify.getPatterns(content)

		return patterns
