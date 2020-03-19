from bs4 import BeautifulSoup
from urllib.parse import urlparse
import os
import json
import networkx
from indexer import getPageTextString
from indexer import rootFolderName
from indexer import docIDMappingFilePath
from search import getDocIDMapping


def getDocURLMapping():
	docIDFile = open(docIDMappingFilePath+".txt")
	docIDMapping = {}

	fileName = (docIDFile.readline()).rstrip()

	currID = 0
	while fileName:
		docIDMapping[fileName] = currID
		fileName = (docIDFile.readline()).rstrip()
		currID += 1

	docIDFile.close()

	return docIDMapping


if __name__ == '__main__':
	docURLMapping = getDocURLMapping()
	docIDMapping = getDocIDMapping()

	graph = networkx.DiGraph()

	subdirs = os.listdir(rootFolderName)

	for subdir in subdirs:
		subdirectoryName = rootFolderName+"/"+subdir

		for filePath in os.listdir(subdirectoryName):
			filePath = subdirectoryName+"/"+ filePath
			
			file = open(filePath)
			fileJSON = json.load(file)
			file.close()

			pageURL = fileJSON["url"]
			if pageURL not in docURLMapping:
				continue
			parsedURL = urlparse(pageURL)

			pageSoup = BeautifulSoup(fileJSON["content"],'lxml')

			for a in pageSoup.find_all('a', href=True):
				link = a['href']
				if link == "" or link == "#" or link == "/":
					continue
				elif link[0:3] == "../":
					newlink = link[2:]
					path = parsedURL.path.split("/")
					link = parsedURL.netloc
					for i in range(len(path)-1):
						link += "/" + path[i]
					link += newlink

				if link in docURLMapping:
					graph.add_edge(docURLMapping[pageURL], docURLMapping[link])
					print("FILEPATH: " + pageURL)
					print("LINK: " + link)
				else:
					graph.add_edge(docURLMapping[pageURL], -1)
					
	pageRankFiles = open("../pageRanks.txt","w")
	pageScores = networkx.pagerank(graph)
	for docID in sorted(pageScores):
		pageRankFiles.write(str(pageScores[docID]) + "\n")