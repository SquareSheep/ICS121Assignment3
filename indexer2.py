def createDocIDMapping(subdirs):
	'''Creates the docID file given a list of the subdirectories'''
	docIDFile = open(docIDFileName,"w")
	for subdir in subdirs:
		for filename in os.listdir(rootFolderName+"/"+subdir):
			docIDFile.write(rootFolderName+"/"+subdir+"/"+filename+"\n")
	docIDFile.close()


def createIDURLMapping(subdirs):
	docIDFile = open(docIDFileName,"w")
	for subdir in subdirs:
		for filename in os.listdir(rootFolderName+"/"+subdir):
			print(filename)
			js = open(rootFolderName+"/"+subdir+"/"+filename)
			di = json.load(js)
			docIDFile.write(di["url"]+"\n")
			js.close()
	docIDFile.close()
