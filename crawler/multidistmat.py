from domSimilarity1 import getSimilarityValue
from download import get
import threading
import Queue
import time
import multiprocessing
import sys

workQueue = multiprocessing.Queue()
returnQueue = multiprocessing.Queue()
queueLock = multiprocessing.Lock()
pages = {}

class process(multiprocessing.Process):
		def __init__(self, links, name):
				multiprocessing.Process.__init__(self)
				self.links = links
				self.name = name
		
		def run(self):
				global workQueue
				global queueLock
				global returnQueue
				while True:
						queueLock.acquire()
						if not workQueue.empty():
								link = workQueue.get()
								print self.name, link
								queueLock.release()
								returnQueue.put(getDistMat(link, self.links))
								time.sleep(1)
						else:
								print "done"
								#multiprocessing.Event
								queueLock.release()
								break


def getDistanceMatrix(links):
		global workQueue
		global returnQueue
		global pages
		pages = getPages(links)
		
		for link in links:
				workQueue.put(link)

		processes = []

		for i in range(10):
				proc = process(links, "Process: " + str(i))
				proc.start()
				processes += [proc]

		while not workQueue.empty():
				time.sleep(1)

		if workQueue.empty():
				for proc in processes:
						proc.terminate()
		returnList = []
		while not returnQueue.empty():
				returnList += [returnQueue.get()]
		return returnList

def getPages(links):
		pages = {}
		for link in links:
				pages[link] = get(link)
				print link
		return pages

def getDistMat(link, links):
		distmat = []
		global pages
		#pages = getPages(links)
		for link2 in links:
				if link == link2:
						distmat += [0.0]
				else:
						temp = getSimilarityValue(pages[link], pages[link2])
						distmat += [temp]
		return (link, distmat)
