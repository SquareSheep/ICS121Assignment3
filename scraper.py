import re
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import io
import os
import json
from posting import Posting

rootFolderName = "DEV"
docIDFileName = "docIDs.txt"
wantedTags = {"p","span","blockquote","code","br","a","ol","ins","sub","sup","h1","h2","h3","h4","h5","h6","li","ul","title","b","strong","em","i","small","sub","sup","ins","del","mark","pre"}


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
					tokens.append(currWord)
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


def stem(word):
	pass


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
	filesPerIndex = 10;
	numofFiles = 0;
 
	# Key: Token Value: List of postings
	partialIndex = {}

	for subdir in subdirs:
		subdirectoryName = rootFolderName+"/"+subdir

		for filename in os.listdir(subdirectoryName):
			filename = subdirectoryName+"/"+ filename

			print("____________________________________FILE NAME: " + filename)

			pageTextString = getPageTextString(filename)

			tokens = {}
			for token in tokenizeText(pageTextString):
				if token not in tokens:
					tokens[token] = 1
				else:
					tokens[token] += 1
			print(tokens)

			for token in tokens:
				if token not in partialIndex:
					partialIndex[token] = []
				partialIndex[token].append(Posting(docIDMapping[filename],tokens[token]))

		numofFiles += 1
		if numofFiles == filesPerIndex:
			# Write to partial index
			numofFiles = 0
			partialIndexNum += 1
			
		print("PARTIAL INDEX__________________________________________")
		print(partialIndex)

		break # REMOVE THIS
			

	# Step 3: Merge the partial indexes
		# Index should be split into files, sorted alphabetically