class SymbolTable:
	def __init__(self):
		self.table = []

	def add(self, value):
		if value not in self.table:
			self.table.append(value)
		return self.table.index(value)


	def __str__(self):
		lexeme = ''
		for idx in range(len(self.table)):
			lexeme += "ID: " + str(idx) + ", Valor: " + str(self.table[idx]) + "\n"
		return lexeme

