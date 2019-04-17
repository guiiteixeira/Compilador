class EndOfBufferException(Exception):
	pass

class EndOfFileException(Exception):
	pass

class BufferedFileReader(object):
	
	def __init__(self,fileName):
		self.inputFile = open(fileName,'r')
		self.current_line = self.inputFile.readline()
		self.last_line = ''
		self.using_last = False
		self.pointer = 0
		self.line = 0

	def getChar(self):
		if self.using_last:
			return self.last_line[self.pointer]
		return self.current_line[self.pointer]

	def goForward(self):
		if self.using_last:
			if (self.pointer + 1) < len(self.last_line):
				self.pointer += 1
			else:
				self.pointer = 0
				self.using_last = False
		else:
			if (self.pointer + 1) < len(self.current_line):
				self.pointer += 1
			else:
				self.last_line = self.current_line
				self.current_line = self.inputFile.readline()
				if not self.current_line:
					raise EndOfFileException("Impossible to go forward")
				self.pointer = 0
				self.line += 1

	def goBackwards(self):
		if self.using_last:
			if (self.pointer - 1) > 0:
				self.pointer -= 1
			else:
				raise EndOfBufferException("Impossible to go backwards")
		else:
			if (self.pointer - 1) > 0:
				self.pointer -= 1
			else:
				self.using_last = True
				self.pointer = (len(self.last_line) - 1)
	
	def getLine(self):
		if self.using_last:
			return self.line
		return self.line + 1

	def getColumn(self):
		return self.pointer
