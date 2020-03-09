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
	postings = {}
	if token in tokenLocations:
		file = open("../finalIndex/index" + str(tokenLocations[token][0]) + ".txt")
		file.seek(int(tokenLocations[token][1]))
		line = file.readline()
		for posting in line.split(":")[1].split("|")[0:-1]:
			temp = posting.split()
			listofPositions = []
			for i in range(int(temp[1])):
				listofPositions.append(int(temp[i+2]))
			postings[int(temp[0])] = (int(temp[int(temp[1])+2]),listofPositions)
			#		docID 		tf-idf score 	 list of positions
			print("POSTING: " + str(temp[0]) + " " + str(postings[int(temp[0])]))
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
		if query == "":
			break

		tokens = tokenizeText(query)

		"""
		1: Get a dictionary of the documents that contain all of the query tokens
			a. Initialize each value to the tf-idf score
			- documents[docID] = 

		2: For each document:
			a. Find the minimum distance between any two query tokens
			- minWordDist[docID] = minDist

		3. Find the highest minimum distance and normalize
			a. minWordDist[docID] = (highestMinDist-minDist)/highestMinDist

		4. For every docID in documents:
			a. Multiply it by the normalized minimum distance
			- documents[docID] *= minWordDist[docID]

		5. Print the URLs of the documents in order by score
		"""
		postings = []
		for token in tokens:
			postings.append(getPostings(token, tokenLocations))

		postings.sort(key= lambda x : len(x))

		docIDs = []
		for i in range(len(postings)):
			docIDs.append(set())
			for posting in postings[i]:
				docIDs[i].add(int(posting))

		finalSet = docIDs[0]

		for i in range(len(docIDs)-1):
			finalSet = docIDs[i].intersection(docIDs[i+1])

		docScores = {}
		for docID in finalSet:
			docScores[docID] = 0
			for tokenPosting in postings:
				print(tokenPosting)
				# if docID in tokenPosting:
				# 	print("AAAA: " + str(tokenPosting[docID]))
				# 	docScores[docID] += tokenPosting[docID][0]

		for docID in docScores:
			print("DOCID: " + str(docScores[docID]))

		if len(finalSet) > 0:
			print("FINAL SET: " + str(finalSet))
			print("Top 10 results:")
			i = 0
			for doc in sorted(docScores, key = lambda x : -docScores[x]):
				print(docIDMapping[int(doc)] + "|" + str(docScores[doc]))
				i += 1
				if i == 10:
					break
		else:
			print("No results")
		print("__________________________________________________")