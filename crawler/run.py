import sys 
import crawl
import classifier
import patternify

"""usage: python run.py http://cnn.com"""

crawler = crawl.crawler() #get a crawler object

urls = crawler.crawl(sys.argv[1], 500) #get URLs, number of URLs to crawl

classifier.trainSVM() #train preliminary classifier using the "content" and "notcontent" files

ones, zeros = classifier.testSVM(urls) #classify using preliminary classifier

patterns = patternify.getPatterns(ones) #get patterns from classified "ones" (content links)

classifier.trainSVM(patterns) #train secondary classifier with pattern features

ones, zeros = classifier.testSVM(urls, patterns) #classify using secondary classifier
