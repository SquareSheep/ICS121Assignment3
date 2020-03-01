from urllib.parse import urlparse
from bs4 import BeautifulSoup
import nltk
import io
import os
import json
import math

rootFolderName = "../DEV"
docIDFileName = "../docIDs.txt"
partialIndexFileName = "../index/partialIndex"
realIndexFileName = "../index/realIndex"

stemmer = nltk.stem.PorterStemmer()


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
					# print(currWord, stemmer.stem(currWord))
					tokens.append(stemmer.stem(currWord))
					currWord = ""
		except:
			continue
	tokens.append(stemmer.stem(currWord))
	return tokens


def getPageTextString(filename):
	'''Returns a string of a file's text, given the filename'''
	file = open(filename)
	d = json.load(file)
	if d["content"]:
		return parseHTML(d["content"])


def getDocIDMapping():
	docIDFile = open(docIDFileName,"r")
	docIDMapping = {}

	filename = (docIDFile.readline()).rstrip()

	currID = 0
	while filename:
		docIDMapping[filename] = currID
		filename = (docIDFile.readline()).rstrip()
		currID += 1

	docIDFile.close()

	return docIDMapping

# Not needed anymore, index already built---------
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


def createDocIDMapping(subdirs):
	'''Creates the docID file given a list of the subdirectories'''
	docIDFile = open(docIDFileName,"w")
	for subdir in subdirs:
		for filename in os.listdir(rootFolderName+"/"+subdir):
			docIDFile.write(rootFolderName+"/"+subdir+"/"+filename+"\n")
	docIDFile.close()


def writePartialIndexToFile(index, filename):
	indexFile = open(filename + ".txt","w")
	indexOffsetFile = open(filename+"offset.txt","w")
	offset = 0
	prevOffset = 0
	for word in sorted(index):
		tempStr = word+":"
		offset = len(word) + 1 # word:

		for posting in index[word]:
			tempStr += str(posting[0]) + " " + str(posting[1])+"|"
			offset += 2 + len(str(posting[0])) + len(str(posting[1]))

			# 			docID length	  " "	frequency length   "|"

		tempStr += "\n"
		offset += 2
		indexOffsetFile.write(word + " " + str(prevOffset+len(word)+1) + " " + str(offset-len(word)-2) + "\n")
		indexFile.write(tempStr)
		prevOffset += offset

	indexFile.close()
	indexOffsetFile.close()


def getPartialIndexOffset(filename):
	'''Returns a dictionary of offsets for each word in the partial index'''
	# offset[token] = (offset, length)
	indexFile = open(filename + ".txt","r")
	offset = {}
	line = indexFile.readline().split()
	while line:
		offset[line[0]] = (line[1],line[2])
		line = indexFile.readline().split()

	return offset


def mergeIndexes(numofindexes, uniqueTokens):
	# Order: docID, frequency, tf-idf score
	# | 0 1 2 |
	partialIndexes = []
	partialIndexOffsets = []

	finalIndex = open("../index/finalIndex.txt","w")

	for i in range(0,numofindexes):
		partialIndexes.append(open(partialIndexFileName + str(i) + ".txt","r"))
		partialIndexOffsets.append(getPartialIndexOffset(partialIndexFileName+str(i)+"offset"))

	for token in sorted(uniqueTokens):
		tempStr = token+":"
		for i in range(0,numofindexes):
			if token in partialIndexOffsets[i]:
				partialIndexes[i].seek(int(partialIndexOffsets[i][token][0]))
				tempOut = partialIndexes[i].readline().rstrip() #partialIndexes[i].read(int(partialIndexOffsets[i][token][1])).rstrip()
				print("TEMP" + tempOut)
				tempStr += tempOut
		tempStr += "\n"
		finalIndex.write(tempStr)
#-------------------------------------------------

if __name__ == '__main__':
	# subdirs = os.listdir(rootFolderName)
	# createDocIDMapping(subdirs)
	# docIDMapping = getDocIDMapping()

	# Step 2: For each subdirectory:
		# Tokenize each file
		# Create a partial index for every X files
	"""
	partialIndexNum = 0
	numofFiles = 0
	numofPostings = 0
	partialIndex = {}
	uniqueTokens = {}
	
	for subdir in subdirs:
		subdirectoryName = rootFolderName+"/"+subdir

		for filename in os.listdir(subdirectoryName):
			filename = subdirectoryName+"/"+ filename

			numofFiles += 1
			print(str(numofPostings)+" " + str(numofFiles) + "____________________________________FILE NAME: " + filename)

			pageTextString = getPageTextString(filename)

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
				partialIndex[token].append((docIDMapping[filename],tokens[token]))
				numofPostings += 1

			if numofPostings > 3000000:
				writePartialIndexToFile(partialIndex, partialIndexFileName + str(partialIndexNum))
				numofPostings = 0
				partialIndexNum += 1
				partialIndex = {}


	if numofPostings > 0:
		writePartialIndexToFile(partialIndex, partialIndexFileName + str(partialIndexNum))
		numofPostings = 0
		partialIndexNum += 1
		partialIndex = {}

	print("________________________DONE_________________________")
	print("uniqueTokens:"+str(len(uniqueTokens)))
	print("numofFiles:"+str(numofFiles))

	i = 0
	for token in sorted(uniqueTokens,key = lambda x: -uniqueTokens[x]):
		print(token,uniqueTokens[token])
		i += 1
		if i == 100:
			break

	# Step 3: Merge the partial indexes
	mergeIndexes(partialIndexNum, uniqueTokens)
	"""

	index = open("../index/finalIndex.txt","r")

	indexNumber = 0
	firstChar = "0"
	offset = 0
	N = 55393 # Total number of documents
	finalIndex = open("../finalIndex/index0.txt","w")
	offsetIndex = open("../finalIndex/indexOffset.txt","w")
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