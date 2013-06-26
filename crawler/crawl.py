import requests
from bs4 import BeautifulSoup
from urlparse import urlparse
import re

class crawler():


	_total_link_requested = 0
	_links_requested = set()
	_robot_parser = None
	_short_domain = None
	_excluded_patterns = []
	USER_AGENT = 'nrelate fp 2.0.0'	
	prefix = ""

	def crawl(self, url, limit = 200):
		linkSet = set()
		url_components = urlparse(url)
		print url_components.path
		self._short_domain = url_components.hostname
		linkSet.add(url)
		timesSeen = {}
		while len(linkSet) < limit:
			print "%d links crawled" % (len(linkSet)) #prints number of links crawled so far
			if len(linkSet) in timesSeen:
				timesSeen[len(linkSet)] += 1
				if timesSeen[len(linkSet)] >= 5:
					print "Unable to download URLs"
					break
			else:
				timesSeen[len(linkSet)] = 1
			temp_url = linkSet.pop()
			linkSet.update(self._get_all_internal_links(temp_url))
			#print self._get_all_internal_links(temp_url)
		
		return linkSet
	
	def check_numeric(self, val):
		try:
			int(val)
		except:
			return False
		return True	

	def _get(self, url):
        	if not url.startswith('http'):
            		url = 'http://' + url
        	return requests.get(url, headers={'User-Agent': self.USER_AGENT})		

	def _get_all_internal_links(self, url):
		""" Given a URL, this function returns a set of links pointing to other
		pages of the same website

		"""
		if not url.startswith("http://"):
		    url = "http://" + url

		# Downloads the page
		try:
		    response = self._get(url)
		    soup = BeautifulSoup(response.text, "html5lib")
		    self._total_link_requested += 1
		    self._links_requested.add(url)
		except Exception as e:
		    self.log(str(e))
		    self.log("Error with %s. Skipping..." % url)
		    return []

		# Extracts internal links using beautiful soup
		if url.startswith("http://www."):
		    prefix = "http://www."
		elif url.startswith("www."):
		    prefix = "www."
		else:
		    prefix = "http://"

		a_tags = []
		for element in soup.contents:
		    if element.__class__.__name__ == 'Tag':
			a_tags = element.find_all("a", href=True)
			break
		# Removes links to non-pages (images, files, etc)
		link_set = set()
		for a_tag in a_tags:
		    original_case_link = a_tag['href'].strip()
		    a_tag['href'] = a_tag['href'].lower().strip()

		    if a_tag['href'].startswith('#'):
			continue
		    if len(a_tag['href']) > 500:
			continue
		    if (a_tag['href'].startswith('javascript:') or a_tag['href'].startswith('mailto:') or
			    a_tag['href'].startswith('itms')):
				continue
		    if ".css" in a_tag['href'] or ".js" in a_tag['href']:
			continue
		    if ".xml" in a_tag['href']:
			continue
		    if ".jpg" in a_tag['href'] or ".png" in a_tag['href'] or ".gif" in a_tag['href']:
			continue

		    if a_tag['href'].startswith('http') or a_tag['href'].startswith('www.'):
			if not (a_tag['href'].startswith('http://www.%s' % self._short_domain) or
				a_tag['href'].startswith('http://%s' % self._short_domain) or
				a_tag['href'].startswith('www\.%s' % self._short_domain)):
			    continue
		    bad_pattern_found = False
		    for excluded_pattern in self._excluded_patterns:
			if excluded_pattern in a_tag['href']:
			    bad_pattern_found = True
			    break
		    if bad_pattern_found:
			continue
		    if a_tag['href'].endswith(".pdf") or a_tag['href'].endswith(".framedurl"):
			continue

		    a_tag['href'] = original_case_link
		    if a_tag['href'].startswith('/'):
			a_tag['href'] = prefix + self._short_domain + a_tag['href']
		    elif not a_tag['href'].startswith('www') and not a_tag['href'].startswith('http'):
			a_tag['href'] = prefix + self._short_domain + '/' + a_tag['href']
		    a_tag['href'] = re.sub('[^\/]\?.+$', '', a_tag['href'])
		    a_tag['href'] = re.sub('#.+$', '', a_tag['href'])
		    a_tag['href'] = re.sub(';.+$', '', a_tag['href'])
		    if not a_tag['href'] in link_set:
			link_set.add(a_tag['href'])

		return link_set

	def log(self, msg):
		print msg
