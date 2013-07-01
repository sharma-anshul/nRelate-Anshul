import numpy
from boilerpipe.extract import Extractor
from nltk import sent_tokenize
from sklearn import svm
import urllib2
import httplib
import pickle
import re
import requests
from sklearn import preprocessing
from urlparse import urlparse
from os.path import exists

boilerplate = set(['privacy', 'contact-us', 'contact', 'video', 'videos', 'help', 'about', 'feedback', 'tag', 'tags', 'category', 'user', 'by_tag', 'by_date', 'author', 'taxonomy', 'comments', 'label', 'terms-of-service', 'privacy-policy', 'printmail', 'print', 'about-us', 'about_us', 'sitemap','?author', '?tag', '?category', '?replytocom', 'rss.'])

def checkBoilerplate(link):
	global boilerplate
	linkParts = set([part.lower() for part in link.split("/")])
	if len(linkParts.intersection(boilerplate)) > 0:
		return False
	return True

#Downloads page
def get(url):
	if not url.startswith('http'):
		url = 'http://' + url
	return requests.get(url, headers={'User-Agent': 'nrelate fp 2.0.0'})

#Trains the classifier
def trainSVM(patterns = None):
    if not patterns == None:
    	print "\nPatterns\n"
    	for pattern in patterns:
			print pattern

	if patterns == None and not exists("svm-classifier"):
		links, trainVectors, trainLabels, pageLinks = [], [], [], []
		content = [line[:-1] for line in open("content")]
		notcontent = [line[:-1] for line in open("notcontent")]
		cont, ncont = [], []

		print "\nTraining\n"
		for link in content:
			vec = getFeatures(link, patterns)
			trainVectors += [vec]
			trainLabels += [1.0]
		
		for link in notcontent:
			vec = getFeatures(link, patterns)
			trainVectors += [vec]
			trainLabels += [0.0]
		
		classifier = svm.SVC()
		classifier.fit(trainVectors, trainLabels)
		if patterns == None:
			pickle.dump(classifier, open("svm-classifier", "w+"))
		else:
			pickle.dump(classifier, open("svm-classifier2", "w+"))
	else:
		print "\nPreliminary classifier already trained.\n"

#Tests the classifier
def testSVM(linkSet, patterns = None):
    cont, ncont, vectors = [], [], []
    print "\nTesting\n"
    classifier = None
    if patterns == None:
		classifier = pickle.load(open("svm-classifier", "r"))
    else:
		classifier = pickle.load(open("svm-classifier2", "r"))
    
    for link in linkSet:	
		vec = getFeatures(link, patterns)
		vectors += [vec]
		result = classifier.predict(vec)
		if result == 1.0:
			cont += [link]
		else:
			ncont += [link]
	
    cont = [link for link in cont if checkBoilerplate(link)]

    print "\nCorrelation Matrix\n"
    print numpy.corrcoef(numpy.transpose(numpy.array(vectors)))
    return sorted(cont, key=lambda x: len(x)), sorted(ncont, key=lambda x: len(x))

#Gets features from URLs
def getFeatures(link, patterns):
	"""
	notFound = False
	numLinks = 0.0
	page = ""
	try:
		page = get(link).text
		numLinks = len(re.findall("(<(a|A) (href|HREF)=.*?>.*?</\\2>)", page))
		numLinks = float(numLinks)
	except httplib.IncompleteRead, e:
	   pass
	"""
	if link.endswith(".htm"):
		link += "l"
	print link
	
	text = getText(link)
	totNumWords, capitalWords, numFullStops = 0.0, 0.0, 0.0
	
	sentences = sent_tokenize(text)
	for sentence in sentences:
		words = sentence.split()
		totNumWords += len(words)
		for word in words:
			if 'A' <= word[0] <= 'Z': capitalWords += 1
		if sentence.endswith('.'): numFullStops += 1
	
	capWordRat = 1.0
	fullStopRat = 1.0
	numSent 	= len(sentences)
	avgSentLen 	= totNumWords/numSent
	
	if totNumWords != 0.0:
		capWordRat 	= capitalWords/totNumWords
		fullStopRat = numFullStops/totNumWords
	
	vec = []
	vec += [numSent]
	vec += [totNumWords]
	vec += [avgSentLen]
	vec += [capWordRat]
	vec += [fullStopRat]
	if not patterns == None:
		matches = False
		for pattern in patterns:
			if re.match(pattern, urlparse(link).path):
				matches = True
				break
		if matches:
			vec += [1]
		else:
			vec += [0]
		numeric = 0
		for part in link.split("/"):
			if part.isdigit():
				numeric += 1
		vec += [numeric]
		vec += [len(link.split("/"))]
		vec += [len(link)]
		isBoiler = 1 if checkBoilerplate(link) else 0
		vec += [isBoiler]

	"""
	if numSent == 0 and numLinks == 0:
	    vec += [100.0]
	elif numSent == 0:
	    vec += [numLinks]
	else:
	    vec += [numLinks/numSent]
	    print numLinks/numSent
	"""
	return vec

def getText(link):
	extractor = None
	try:
		extractor = Extractor(url=link)
	except urllib2.HTTPError, e:
		if e.code == 404:
			print "not found"
			notFound = True
	except urllib2.URLError, e:
		print "timed out"
	except httplib.BadStatusLine, e:
		print "bad status"
	except:
		print "Error"
	text = ""
	if extractor != None:
		text = extractor.getText()
	return text
