class Posting:
	def __init__(self, docID, frequency):
		self.docID = docID
		self.frequency = frequency

	def __repr__(self):
		return str(self.docID) + ":" + str(self.frequency)
