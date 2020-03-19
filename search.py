import math
import time
from simhash import Simhash
from indexer import tokenizeText
from indexer import docIDMappingFilePath
from indexer import importantWordsFilePath

stopWords = {"a","about","above","after","again","against","all","am","an","and","any","are","aren't","as","at","be","because","been","before","being","below","between","both","but","by","can't","cannot","could","couldn't","did","didn't","do","does","doesn't","doing","don't","down","during","each","few","for","from","further","had","hadn't","has","hasn't","have","haven't","having","he","he'd","he'll","he's","her","here","here's","hers","herself","him","himself","his","how","how's","i","i'd","i'll","i'm","i've","if","in","into","is","isn't","it","it's","its","itself","let's","me","more","most","mustn't","my","myself","no","nor","not","of","off","on","once","only","or","other","ought","our","ours ourselves","out","over","own","same","shan't","she","she'd","she'll","she's","should","shouldn't","so","some","such","than","that","that's","the","their","theirs","them","themselves","then","there","there's","these","they","they'd","they'll","they're","they've","this","those","through","to","too","under","until","up","very","was","wasn't","we","we'd","we'll","we're","we've","were","weren't","what","what's","when","when's","where","where's","which","while","who","who's","whom","why","why's","with","won't","would","wouldn't","you","you'd","you'll","you're","you've","your","yours","yourself","yourselves"}
pageRankFilePath = "../pageRanks"


def getQueryIDFScore(queryTokens):
	N = 55393


def getPostings(token, tokenLocations, threshold=50000):
	postings = {}
	if token in tokenLocations:
		file = open("../finalIndex/index" + str(tokenLocations[token][0]) + ".txt")
		file.seek(int(tokenLocations[token][1]))
		line = file.readline()

		i = 0
		for posting in line.split(":")[1].split("|")[0:-1]:
			temp = posting.split()
			postings[int(temp[0])] = (int(temp[1]),int(temp[2]))
			i += 1
			if i == threshold:
				break
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
		#print(docSets[i])

	finalSet = set()
	for docID in docSets[0]:
		flag = True
		for i in range(1,len(docSets)):
			if docID not in docSets[i]:
				flag = False
		if flag:
			finalSet.add(docID)
			
	return finalSet


def getPageRankScores():
	pageRankScores = {}
	file = open(pageRankFilePath + ".txt")
	file.readline()
	line = file.readline()
	while line:
		pageRankScores[line.split()[0]] = float(line.split()[1])
		line = file.readline()
	return pageRankScores


if __name__ == '__main__':
	docIDMapping = getDocIDMapping()
	tokenLocations = getTokenLocations()
	importantWords = getImportantWords()
	pageRankScores = getPageRankScores()

	print("___________Assignment 3 Search Engine_____________")
	while True:
		query = input('Enter a search, or just hit enter to exit: ')
		query = query.lower()
		startTime = time.time()
		if query == "":
			break

		queryTokens = tokenizeText(query)
		# print("QUERY: " + str(query) + " " + str(queryTokens))

		numofStopWords = 0
		for token in queryTokens:
			if token in stopWords:
				numofStopWords += 1

		if numofStopWords < len(queryTokens)*0.7 and numofStopWords > 0:
			i = 0
			while i < len(queryTokens):
				if queryTokens[i] in stopWords:
					del queryTokens[i]
					i -= 1
				i += 1

		postings = {}
		if numofStopWords == len(queryTokens):
			for token in queryTokens:
				postings[token] = (getPostings(token, tokenLocations,5000))
		else:
			for token in queryTokens:
				postings[token] = getPostings(token, tokenLocations, 50000 - min(len(queryTokens),10)*2000)

		if len(postings) > 0:
			docSet = getBoolDocs(postings)

		# MAIN SECTION ####################################################
		if len(postings) > 0:

			# TF-IDF SCORING #############################
			N = 55393
			queryIDFScores = {}
			for token in queryTokens:
				DFt = len(postings[token])
				TFd = 1
				queryIDFScores[token] = TFd*math.log(N/DFt,3)


			docScores = {}
			for docID in docSet:
				docScores[docID] = 0
				for token in postings:
					if docID in postings[token]:
						docScores[docID] += postings[token][docID][1]*queryIDFScores[token]


			# IMPORTANT WORD SCORING #####################
			for docID in docScores:
				for token in queryTokens:
					if token in importantWords[docID]:
						docScores[docID] *= (importantWords[docID][token]+1)*25
						# print(token)


			# COSINE SCORING #############################
			queryVector = {}
			for token in queryTokens:
				queryVector[token] = queryTokens.count(token)

			docVectors = {}
			for docID in docSet:
				docVectors[docID] = {}
				for token in queryTokens:
					docVectors[docID][token] = 0
					if docID in postings[token]:
						docVectors[docID][token] += postings[token][docID][0]

			QJ2 = 0
			for token in queryVector:
				QJ2 += queryVector[token]*queryVector[token]

			DIJ2 = {}
			DIJQJ = {}
			for docID in docSet:
				DIJ2[docID] = 0
				DIJQJ[docID] = 0
				for token in docVectors[docID]:
					DIJ2[docID] += docVectors[docID][token]*docVectors[docID][token]
					DIJQJ[docID] += docVectors[docID][token]*queryVector[token]

			cosineScores = {}
			for docID in docSet:
				cosineScores[docID] = DIJQJ[docID] / math.sqrt(DIJ2[docID]*QJ2)

			for docID in docScores:
				docScores[docID] *= cosineScores[docID]**3

			#PAGE RANKING SCORING################################
			for docID in docScores:
				if docID in pageRankScores:
					docScores[docID] *= pageRankScores[docID]
				else:
					docScores[docID] *= 1/N
					
		queryTime = time.time()-startTime
		###################################################################

		if len(postings) > 0 and len(docSet) > 0:
			print("Top 25 results:")
			i = 0
			for docID in sorted(docScores, key = lambda x : -docScores[x]):
				if docID in docIDMapping:
					print(docIDMapping[docID].split("#")[0])
				i += 1
				if i == 25:
					break
		else:
			print("No results")
		print("Time: " + str(queryTime))
		print("__________________________________________________")