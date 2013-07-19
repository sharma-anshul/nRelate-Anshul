from domSimilarity1 import getSimilarityValue
from download import get
import threading
import Queue
import time
import multiprocessing
import sys

workQueue = Queue.Queue()
returnQueue = Queue.Queue()
queueLock = threading.Lock()
pages = {}

class processThread(threading.Thread):
		def __init__(self,links, workQueue, returnQueue, name):
				threading.Thread.__init__(self)
				self.links = links
				self.name = name
				self.workQueue = workQueue
				self.returnQueue = returnQueue
		
		def run(self):
				global workQueue
				global queueLock
				global returnQueue
				while True:
						queueLock.acquire()
						if not workQueue.empty():
								link = self.workQueue.get()
								print self.name, link
								queueLock.release()
								returnQueue.put(getDistMat(link, self.links))
						else:
								queueLock.release()
								break
						time.sleep(1)


def getDistanceMatrix(links):
		global workQueue
		global returnQueue
		global pages
		pages = getPages(links)
		
		for link in links:
				workQueue.put(link)

		threads = []

		for i in range(10):
				thread = processThread(links, workQueue, returnQueue, "Thread " + str(i))
				thread.start()
				threads += [thread]

		for thread in threads:
				thread.join()

		return returnQueue

def getPages(links):
		pages = {}
		for link in links:
				pages[link] = get(link)
		return pages

def getDistMat(links):
		distmat = []
		cache = {}
		#global pages
		pages = getPages(links)
		for link1 in links:
				row = []
				for link2 in links:
						if link1 == link2:
								row += [0.0]
								continue
						if (link1, link2) in cache:
								row += [cache[(link1, link2)]]
						else:
								temp = getSimilarityValue(pages[link1], pages[link2])
								cache[(link1, link2)] = temp
								row += [temp]
				distmat += [row]
				print link1
		return distmat
