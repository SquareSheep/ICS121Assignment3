import io
import math
from simhash import Simhash
from indexer import tokenizeText
from indexer import docIDMappingFilePath
from indexer import importantWordsFilePath

"""
TODO:

Simhash--DONE

Important text score multiplier (Bold, heading, etc)

Page rank

Cosine ranking
- Only consider documents with scores above a certain threshold

"""

def getQueryIDFScore(queryTokens):
	N = 55393



def getPostings(token, tokenLocations):
	postings = {}
	if token in tokenLocations:
		file = open("../finalIndex/index" + str(tokenLocations[token][0]) + ".txt")
		file.seek(int(tokenLocations[token][1]))
		line = file.readline()
		for posting in line.split(":")[1].split("|")[0:-1]:
			temp = posting.split()
			postings[int(temp[0])] = (int(temp[1]),int(temp[2]))
			#		docID 		tf-idf score 	 list of positions
			# print("POSTING: " + str(temp[0]) + " " + str(postings[int(temp[0])]))
	return postings


def getImportantWords():
	file = open(importantWordsFilePath+".txt")
	importantWords = []
	line = file.readline()
	i = 0
	while line:
		importantWords.append({})
		for word in line.split("|")[:-1]:
			temp = word.split()
			importantWords[i][temp[0]] = int(temp[1])
		line = file.readline()
		i += 1
	file.close()
	return importantWords


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


def getBoolDocs(postings):
	'''Returns a set of docIDs that contain all of the query words'''
	docSets = []
	for i, token in enumerate(postings):
		docSets.append(set())
		for docID in postings[token]:
			docSets[i].add(docID)
		print(docSets[i])

	finalSet = set()
	for docID in docSets[0]:
		flag = True
		for i in range(1,len(docSets)):
			if docID not in docSets[i]:
				flag = False
		if flag:
			finalSet.add(docID)
			
	return finalSet


if __name__ == '__main__':
	docIDMapping = getDocIDMapping()
	tokenLocations = getTokenLocations()
	importantWords = getImportantWords()

	print("___________Assignment 3 Search Engine_____________")
	while True:
		query = input('Enter a search, or just hit enter to exit: ')
		query = query.lower()
		if query == "":
			break

		queryTokens = tokenizeText(query)
		print("QUERY: " + str(query) + " " + str(queryTokens))

		postings = {}
		for token in queryTokens:
			postings[token] = (getPostings(token, tokenLocations))

		if len(postings) > 0:
			for token in postings:
				print("POSTING: " + str(token) + " " + str(postings[token]))

			docSet = getBoolDocs(postings)

		# MAIN SECTION ####################################################
		if len(postings) > 0:

			# TF-IDF SCORING #############################
			docScores = {}
			for docID in docSet:
				docScores[docID] = 0
				for token in postings:
					if docID in postings[token]:
						docScores[docID] += postings[token][docID][1]

			# COSINE SCORING #############################
			queryVector = {}
			for token in queryTokens:
				queryVector[token] = queryTokens.count(token)
			print(queryVector)

			docVectors = {}
			for docID in docSet:
				docVectors[docID] = {}
				for token in queryTokens:
					docVectors[docID][token] = 0
					if docID in postings[token]:
						docVectors[docID][token] += postings[token][docID][0]
			print(docVectors)

			QJ2 = 0
			for token in queryVector:
				QJ2 += queryVector[token]*queryVector[token]
			print("QJ2: " + str(QJ2))

			DIJ2 = {}
			DIJQJ = {}
			for docID in docSet:
				DIJ2[docID] = 0
				DIJQJ[docID] = 0
				for token in docVectors[docID]:
					DIJ2[docID] += docVectors[docID][token]*docVectors[docID][token]
					DIJQJ[docID] += docVectors[docID][token]*queryVector[token]
			print("DOCDIJ: " + str(DIJ2))
			print("DOCDP: " + str(DIJQJ))

			cosineScores = {}
			for docID in docSet:
				cosineScores[docID] = DIJQJ[docID] / math.sqrt(DIJ2[docID]*QJ2)
			print("CONSINE SCORES: " + str(cosineScores))

			for docID in docScores:
				docScores[docID] *= cosineScores[docID]
					
		###################################################################
		if len(postings) > 0 and len(docSet) > 0:
			print("Top 25 results:")
			i = 0
			for doc in sorted(docScores, key = lambda x : -docScores[x]):
				print(docIDMapping[int(doc)] + " |" + str(docScores[doc]))
				i += 1
				if i == 25:
					break
		else:
			print("No results")
		print("__________________________________________________")