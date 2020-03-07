import io
from simhash import Simhash
from indexer import tokenizeText
from indexer import docIDMappingFilePath

"""
TODO:

Simhash--DONE

Important text score multiplier (Bold, heading, etc)

Page rank

Cosine ranking
- Only consider documents with scores above a certain threshold

"""

def getPostings(token, tokenLocations):
	if token in tokenLocations:
		file = open("../finalIndex/index" + str(tokenLocations[token][0]) + ".txt")
		file.seek(int(tokenLocations[token][1]))
		line = file.readline()
		postings = {}
		for posting in line.split(":")[1].split("|")[0:-1]:
			temp = posting.split()
			postings[temp[0]] = temp[2]
		return postings


def getTokenLocations():
	locations = {}
	indexOffsets = open("../finalIndex/indexOffset.txt")
	for line in indexOffsets:
		temp = line.split()
		locations[temp[0]] = (temp[1],temp[2])
	return locations


def getDocIDMapping():
	docIDFile = open(docIDMappingFilePath+".txt","r")
	docIDMapping = {}

	fileName = (docIDFile.readline()).rstrip()

	currID = 0
	while fileName:
		docIDMapping[currID] = fileName
		fileName = (docIDFile.readline()).rstrip()
		currID += 1

	docIDFile.close()

	return docIDMapping


if __name__ == '__main__':
	docIDMapping = getDocIDMapping()
	tokenLocations = getTokenLocations()

	print("___________Assignment 3 Search Engine_____________")
	while True:
		query = input('Enter a search, or just hit enter to exit: ')
		query = query.lower()
		if query == "" or query == "q":
			break
		# print("query: " + query)

		tokens = tokenizeText(query)
		# print("tokens: " + str(tokens))

		postings = []
		for token in tokens:
			postings.append(getPostings(token, tokenLocations))

		postings.sort(key= lambda x : len(x))

		docIDs = []
		for i in range(len(postings)):
			docIDs.append(set())
			for posting in postings[i]:
				docIDs[i].add(posting)

		finalSet = docIDs[0]

		for i in range(len(docIDs)-1):
			finalSet = docIDs[i].intersection(docIDs[i+1])

		docScores = {}
		for docID in finalSet:
			docScores[docID] = 0
			for tokenPosting in postings:
				if docID in tokenPosting:
					docScores[docID] += int(tokenPosting[docID])

		print("Top 10 results:")
		i = 0
		for doc in sorted(docScores, key = lambda x : -docScores[x]):
			print(docIDMapping[int(doc)] + " " + str(docScores[doc]))
			i += 1
			if i == 10:
				break
		print("__________________________________________________")