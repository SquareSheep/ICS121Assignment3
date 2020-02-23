from urllib.parse import urlparse
from bs4 import BeautifulSoup
import nltk
import io
import os
import json
from posting import Posting

rootFolderName = "../DEV"
docIDFileName = "../docIDs.txt"
partialIndexFileName = "../index/partialIndex"
realIndexFileName = "../index/realIndex"

stemmer = nltk.stem.PorterStemmer()

uniqueTokens = {}

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
	return tokens


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


def getPageTextString(filename):
	'''Returns a string of a file's text, given the filename'''
	file = open(filename)
	d = json.load(file)
	if d["content"]:
		return parseHTML(d["content"])


def writeIndexToFile(index, filename):
	indexFile = open(filename,"w")
	for word, postings in index.items():
		tempStr = word
		for posting in postings:
			tempStr += "|" + str(posting[0]) + " " + str(posting[1])
		tempStr += "\n"
		indexFile.write(tempStr)


def mergeIndexes(numofindexes):
	partialIndexes = []
	for i in range(0,numofindexes):
		partialIndexes[i] = open(partialIndexFileName + str(i) + ".txt","r")

	# for token in sorted(uniqueTokens):
	# 	for partialIndex in partialIndexes:
	# 		if token in partialIndex:

# Part 1 of assignment
# Creating the inverted index and docID mapping
if __name__ == '__main__':

	# Step 1: Map all the documents to integers
		# Put this mapping in a file
	subdirs = os.listdir(rootFolderName)
	# createDocIDMapping(subdirs)
	docIDMapping = getDocIDMapping()

	# Step 2: For each subdirectory:
		# Tokenize each file
		# Create a partial index for every X files

	partialIndexNum = 0
	numofFiles = 0
	numofPostings = 0
	stop = False
	partialIndex = {}

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

			if numofPostings >= 5000000:
				writeIndexToFile(partialIndex, partialIndexFileName + str(partialIndexNum) + ".txt")
				numofPostings = 0
				partialIndexNum += 1
				partialIndex = {}
				# stop = True
				# break
		if stop:
			break
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
	# mergeIndexes(partialIndexNum)