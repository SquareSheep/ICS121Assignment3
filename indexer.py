from bs4 import BeautifulSoup
import os
import json
import math
import nltk
from simhash import Simhash


rootFolderName = "../DEV"

docIDMappingFilePath = "../docIDs"

partialIndexFilePath = "../TemporaryIndexes/partialIndex"
partialIndexOffsetFilePath = "../TemporaryIndexes/partialIndexOffset"

tempIndexFilePath = "../TemporaryIndexes/temporaryIndex"

finalIndexFilePath = "../FinalIndex/index"
finalIndexOffsetFilePath = "../FinalIndex/indexOffset"

stemmer = nltk.stem.PorterStemmer()
importantTags = ("title","h1","h2","h3","b")
importantWordsFilePath = "../importantWords"
importantWordsOffsetFilePath = "../importantWordsOffset"


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
					tempWord = stemmer.stem(currWord)
					if tempWord != "":
						tokens.append(tempWord)
					currWord = ""
		except:
			continue
	tempWord = stemmer.stem(currWord)
	if tempWord != "":
		tokens.append(tempWord)
	return tokens


def	recordImportantWords(importantWords, pageSoup, numofFiles):
	importantWords.append({})
	for tagType in importantTags:
		for tag in pageSoup(tagType):
			for token in tokenizeText(tag.text):
				if token in importantWords[numofFiles]:
					importantWords[numofFiles][token] += 1
				else:
					importantWords[numofFiles][token] = 1


def writeImportantWordsToFile(importantWords):
	file = open(importantWordsFilePath + ".txt","w")
	offsetFile = open(importantWordsOffsetFilePath + ".txt","w")
	offset = 0
	for page in importantWords:
		tempStr = ""
		for token in page:
			tempStr += token + " " + str(page[token]) + "|"
		file.write(tempStr + "\n")
		offsetFile.write(str(offset)+"\n")
		offset += len(tempStr)+1
	file.close()
	offsetFile.close()


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
		if pageHash.distance(hashedPage) < 3:
			skipPage = True
			break
	else:
		pageHashes.add(pageHash)
	return skipPage


def parseHTML(html):
	'''Returns string of text given an HTML string'''
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
	for token in sorted(partialIndex):

		tokenStr = token+":"

		for posting in partialIndex[token]:
			tokenStr += str(posting[0]) + " " + str(posting[1]) + "|"

		tokenStr += "\n"
		
		partialIndexOffsetFile.write(token + " " + str(offset+len(token)+1) + " " + "0" + "\n")
		partialIndexFile.write(tokenStr)
		offset += len(tokenStr)+1

	partialIndexFile.close()
	partialIndexOffsetFile.close()


def getPartialIndexOffset(indexNumber):
	'''Returns a dictionary of offsets for each word in the partial index'''
	offsetFile = open(partialIndexOffsetFilePath+str(indexNumber)+".txt","r")
	offset = {}
	line = offsetFile.readline().split()
	while line:
		offset[line[0]] = (line[1],line[2])
		line = offsetFile.readline().split()

	return offset


def createTemporaryIndex(numofindexes, uniqueTokens):
	# Order: docID, frequency, tf-idf score
	partialIndexes = []
	partialIndexOffsets = []

	tempIndex = open(tempIndexFilePath+".txt","w")

	for i in range(0,numofindexes):
		partialIndexes.append(open(partialIndexFilePath + str(i) + ".txt","r"))
		partialIndexOffsets.append(getPartialIndexOffset(i))

	for token in sorted(uniqueTokens):
		tokenStr = token+":"
		for i in range(0,numofindexes):
			if token in partialIndexOffsets[i]:
				partialIndexes[i].seek(int(partialIndexOffsets[i][token][0]))
				tokenStr += partialIndexes[i].readline().rstrip()
		tokenStr += "\n"
		tempIndex.write(tokenStr)


def createFinalIndex():
	index = open(tempIndexFilePath+".txt","r")

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

		tempPostings = temp[1].split("|")[0:-1]
		postings = []

		DFt = len(tempPostings) # Number of documents containing this token
		for posting in tempPostings:
			TFd = int(posting.split()[1]) # Number of occurences of this token in the document
			score = int(TFd*math.log(N/DFt, 3))
			postings.append((posting,score))
			

		tokenAndPostings = token + ":"
		for posting in sorted(postings, key = lambda x : -x[1]):
			tokenAndPostings += posting[0] + " " + str(posting[1]) + "|"
		tokenAndPostings += "\n"

		offsetIndex.write(token + " " + str(indexNumber) + " " + str(offset) + "\n")
		offset += len(tokenAndPostings)+1

		finalIndex.write(tokenAndPostings)


if __name__ == '__main__':
	partialIndexNum = 0
	numofFiles = 0
	numofPostings = 0
	partialIndex = {}
	uniqueTokens = {}
	pageHashes = set()
	importantWords = []
	# importantWords[docID][token] = occurences (number of times this token was in <title>,<h1>,<h2>,<h3>,<b>)

	subdirs = os.listdir(rootFolderName)

	docIDFile = open(docIDMappingFilePath + ".txt","w")

	for subdir in subdirs:
		subdirectoryName = rootFolderName+"/"+subdir

		for filePath in os.listdir(subdirectoryName):

			filePath = subdirectoryName+"/"+ filePath
			print(str(numofPostings)+" " + str(numofFiles) + filePath)

			file = open(filePath)
			fileJSON = json.load(file)
			file.close()

			pageURL = fileJSON["url"]
			pageSoup = BeautifulSoup(fileJSON["content"],'lxml')
			pageTextString = getPageTextString(pageSoup)

			if len(pageTextString) < 700 or len(pageTextString) > 70000000:
				continue
			try:
				if isPageTooSimilar(pageTextString, pageHashes):
					continue
			except:
				continue
			
			recordImportantWords(importantWords, pageSoup, numofFiles)

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

				partialIndex[token].append((numofFiles, tokens[token]))
				numofPostings += 1

			if numofPostings > 2000000:
				writePartialIndexToFile(partialIndex, partialIndexNum)
				numofPostings = 0
				partialIndexNum += 1
				partialIndex = {}

			docIDFile.write(pageURL + "\n")
			numofFiles += 1


	if numofPostings > 0:
		writePartialIndexToFile(partialIndex, partialIndexNum)
		numofPostings = 0
		partialIndexNum += 1
		partialIndex = {}

	writeImportantWordsToFile(importantWords)

	createTemporaryIndex(partialIndexNum, uniqueTokens)

	createFinalIndex()