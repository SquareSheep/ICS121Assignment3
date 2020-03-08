from urllib.parse import urlparse
from bs4 import BeautifulSoup
import nltk
import io
import os
import json
import math

rootFolderName = "../DEV"
docIDMappingFilePath = "../docIDs"
partialIndexFilePath = "../TemporaryIndexes/partialIndex"
partialIndexOffsetFilePath = "../TemporaryIndexes/partialIndexOffset"
tempIndexFilePath = "../TemporaryIndexes/temporaryIndex"
finalIndexFilePath = "../FinalIndex/TemporaryIndexes"
finalIndexOffsetFilePath = "../FinalIndex/indexOffset"

stemmer = nltk.stem.PorterStemmer()
importantTags = ("title","h1","h2","h3","b")


def tokenizeText(text):
	'''Returns list of tokens given a string of text'''
	tokens = []
	currWord = ""
	for char in text:
		try:
			charOrd = ord(char)
			if (charOrd >= 65 and charOrd <= 90):
				currWord += char.lower()
			elif (charOrd >= 48 and charOrd <= 57) or (charOrd >= 96 and charOrd <= 122):
				currWord += char
			else:
				if currWord != "":
					tokens.append(stemmer.stem(currWord))
					currWord = ""
		except:
			continue
	tokens.append(stemmer.stem(currWord))
	return tokens


def	recordImportantWords(importantWords, pageSoup):
	for tagType in importantTags:
		for tag in pageSoup(tagType):
			if tag in importantWords[numofFiles]:
				importantWords[numofFiles][tag] += 1
			else:
				importantWords[numofFiles][tag] = 1


def getPageTextString(pageSoup):
	'''Returns a string of a file's text, given the page's soup'''
	for script in pageSoup("script"):
			script.decompose()
	pageTextString = ""
	for text in pageSoup.stripped_strings:
		pageTextString += text + " "
	return pageTextString


def isPageTooSimilar(pageTextString, pageHashes):
	pageHash = Simhash(pageTextString)
	minDist = 100000000
	skipPage = False
	for hashedPage in pageHashes:
		if pageHash.distance(hashedPage) <= 3:
			skipPage = True
			break
	else:
		pageHashes.add(pageHash)
	return skipPage


def parseHTML(html):
	'''Returns string of text given an HTML string'''

	# Parse html and tokenize
	# parser = lxml.etree.HTMLParser(encoding=encode)
	soup = BeautifulSoup(html,'lxml')
	for script in soup("script"):
		script.decompose()

	pageTextString = ""
	for text in soup.stripped_strings:
		pageTextString += text + " "

	return pageTextString


def writePartialIndexToFile(partialIndex, partialIndexNum):

	partialIndexFile = open(partialIndexFilePath + str(partialIndexNum) + ".txt","w")
	partialIndexOffsetFile = open(partialIndexOffsetFilePath + str(partialIndexNum) + ".txt","w")
	offset = 0
	prevOffset = 0
	for token in sorted(partialIndex):
		tokenStr = token+":"
		offset = len(token) + 1

		for posting in partialIndex[token]:
			tokenStr += str(posting[0]) + " " + str(posting[1])+"|"
			offset += 2 + len(str(posting[0])) + len(str(posting[1]))

		tokenStr += "\n"
		offset += 2
		partialIndexOffsetFile.write(token + " " + str(prevOffset+len(token)+1) + " " + str(offset-len(token)-2) + "\n")
		partialIndexFile.write(tokenStr)
		prevOffset += offset

	partialIndexFile.close()
	partialIndexOffsetFile.close()


def getPartialIndexOffset(fileName):
	'''Returns a dictionary of offsets for each word in the partial index'''
	# offset[token] = (offset, length)
	offsetFile = open(fileName + ".txt","r")
	offset = {}
	line = offsetFile.readline().split()
	while line:
		offset[line[0]] = (line[1],line[2])
		line = offsetFile.readline().split()

	return offset


def createTemporaryIndex(numofindexes, uniqueTokens):
	# Order: docID, frequency, tf-idf score
	# | 0 1 2 |
	partialIndexes = []
	partialIndexOffsets = []

	tempIndex = open(tempIndexFilePath,"w")

	for i in range(0,numofindexes):
		partialIndexes.append(open(partialIndexFilePath + str(i) + ".txt","r"))
		partialIndexOffsets.append(getPartialIndexOffset(partialIndexFilePath+str(i)+"offset"))

	for token in sorted(uniqueTokens):
		tokenStr = token+":"
		for i in range(0,numofindexes):
			if token in partialIndexOffsets[i]:
				partialIndexes[i].seek(int(partialIndexOffsets[i][token][0]))
				tokenStr += partialIndexes[i].readline().rstrip()
		tokenStr += "\n"
		tempIndex.write(tokenStr)


def createFinalIndex():
	index = open("../index/finalIndex.txt","r")

	indexNumber = 0
	firstChar = "0"
	offset = 0
	N = 55393 # Total number of documents
	finalIndex = open(finalIndexFilePath + "0.txt","w")
	offsetIndex = open(finalIndexOffsetFilePath+".txt","w")
	for line in index:
		temp = line.split(":")

		token = temp[0]
		if token[0] != firstChar:
			indexNumber += 1
			finalIndex = open("../finalIndex/index" + str(indexNumber) + ".txt","w")
			firstChar = token[0]
			offset = 0

		postings = temp[1].split("|")[0:-1]

		tokenAndPostings = token + ":"
		
		DFt = len(postings) # Number of documents containing this token
		for posting in postings:
			TFd = int(posting.split()[1]) # Number of occurences of this token in the document
			score = int(TFd*math.log(N/DFt, 3))
			tokenAndPostings += posting + " " + str(score) + "|"
		tokenAndPostings += "\n"

		offsetIndex.write(token + " " + str(indexNumber) + " " + str(offset) + "\n")
		offset += len(tokenAndPostings)+1

		finalIndex.write(tokenAndPostings)


if __name__ == '__main__':
	# Step 1: For each subdirectory:
		# Tokenize each file
		# Create a partial index for every X files

	partialIndexNum = 0
	numofFiles = 0
	numofPostings = 0
	partialIndex = {}
	uniqueTokens = {}
	pageHashes = set()
	importantWords = [] # A list of dictionaries
	# importantWords[docID][token] = occurences (number of times this token was in <title>,<h1>,<h2>,<h3>,<b>)

	subdirs = os.listdir(rootFolderName)
	
	for subdir in subdirs:
		subdirectoryName = rootFolderName+"/"+subdir

		for filePath in os.listdir(subdirectoryName):

			filePath = subdirectoryName+"/"+ filePath
			print(str(numofPostings)+" " + str(numofFiles) + " FILE NAME: " + filePath)

			file = open(filePath)
			fileJSON = json.load(file)
			file.close()

			pageURL = fileJSON["url"]
			pageSoup = BeautifulSoup(fileJSON["content"],'lxml')
			pageTextString = getPageTextString(pageSoup)			
			
			if isPageTooSimilar(pageTextString, pageHashes):
				break
			
			recordImportantWords(importantWords, pageSoup)

			tokens = {}
			for token in tokenizeText(pageTextString):
				if token not in tokens:
					tokens[token] = 1
				else:
					tokens[token] += 1

				if token not in uniqueTokens:
					uniqueTokens[token] = 1
				else:
					uniqueTokens[token] += 1

			for token in tokens:
				if token not in partialIndex:
					partialIndex[token] = []
				partialIndex[token].append((numofFiles,tokens[token]))
				numofPostings += 1

			if numofPostings > 3000000:
				writePartialIndexToFile(partialIndex, partialIndexFilePath + str(partialIndexNum))
				numofPostings = 0
				partialIndexNum += 1
				partialIndex = {}

			docIDFile.write(pageURL + " " + numofFiles + "\n")
			numofFiles += 1


	if numofPostings > 0:
		writePartialIndexToFile(partialIndex, partialIndexNum)
		numofPostings = 0
		partialIndexNum += 1
		partialIndex = {}

	print("uniqueTokens:"+str(len(uniqueTokens) + "\nnumofFiles:"+str(numofFiles)))

	# Step 2: Merge the partial indexes into one temporary index with all of the postings
	createTemporaryIndex(partialIndexNum, uniqueTokens)

	# Step 3: Add scores to all of the postings and write the final index
	# createFinalIndex()