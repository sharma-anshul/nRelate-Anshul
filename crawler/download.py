import requests

def get(url):
		if not url.startswith('http'):
				url = 'http://' + url
		return requests.get(url, headers={'User-Agent': 'nrelate fp 2.0.0'})
