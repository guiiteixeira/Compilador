import string
from token import Token
from symbol_table import SymbolTable
from bufferedFileReader import BufferedFileReader
from bufferedFileReader import EndOfFileException
from bufferedFileReader import EndOfBufferException

class AnalisadorLexico:
	def __init__(self, fileName):
		self.lexemes = {

			'>': 'MAIOR',
			'<': 'MENOR',
			'>=': 'MAIOR_IGUAL',
			'<=': 'MENOR_IGUAL',
			'!=': 'DIFERENTE',
			'==': 'IGUAL',
			'=': 'ATRIBUICAO',
			'+': 'SOMA',
			'-': 'SUBTRACAO',
			'*': 'MULTIPLICACAO',
			'/': 'DIVISAO',
			',': 'VIRGULA', 
			'.': 'PONTO', 
			';': 'PONTO_VIRGULA',
			'(': 'ABRE_PARENTESE',
			')': 'FECHA_PARENTESE',
			'{': 'ABRE_CHAVE',
			'}': 'FECHA_CHAVE',
			'[': 'ABRE_COLCHETE',
			']': 'FECHA_COLCHETE'
		}
		self.symbolTable = SymbolTable()
		self.tokens = []
		self.errors = []
		self.reserved = ["int", "float", "struct", "if", "else", "while", "void", "return"]
		self.operators = ["=", "<=", "<", ">", ">=", "==", "!=", "+", "-", "*", "/"]
		self.separators = [",", ".", "[", "{", "(", ")", "}", "]", ";"]
		self.skip = ['\t', ' ','\n','\r']
		self.letters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
		self.digits = "0123456789"
		self.reader = BufferedFileReader(fileName)

	def analisar(self):
		try:
			current_character = self.reader.getChar()
			self.reader.goForward()
			next_character = self.reader.getChar()
			lexeme = ""

			#Comentarios
			if current_character == '/' and next_character == '*':
				self.reader.goForward()
				current_character = self.reader.getChar()
				self.reader.goForward()
				next_character = self.reader.getChar()				
				while not (next_character == '/' and current_character == '*'):
					current_character = self.reader.getChar()
					self.reader.goForward()
					next_character = self.reader.getChar()
				self.reader.goForward()		

			#Ids e reservadas
			elif(current_character in self.letters):
				location = [self.reader.getLine(),self.reader.getColumn()]
				while (current_character in self.letters) or (current_character in self.digits):
					lexeme += current_character
					current_character = self.reader.getChar()
					self.reader.goForward()
				self.reader.goBackwards()
				if lexeme in self.reserved:
					self.tokens.append(Token("RESERVADO",lexeme,location,None))
				else:
					self.tokens.append(Token("ID",None,location,self.symbolTable.add(lexeme)))

			#Operadores
			elif current_character in self.operators or current_character == '!':
				joint = ''
				joint += current_character
				current_character = self.reader.getChar()
				self.reader.goForward()
				if current_character in self.operators:
					joint += current_character
					if joint in self.operators:
						self.tokens.append(Token(self.lexemes[joint],joint,[self.reader.getLine(),self.reader.getColumn()],None))
					else:
						#PanicMode
						self.tokens.append(Token(self.lexemes[joint[0]],joint[0],[self.reader.getLine(),self.reader.getColumn()],None))
						self.tokens.append(Token(self.lexemes[joint[1]],joint[1],[self.reader.getLine(),self.reader.getColumn()],None))
						self.errors.append("Warning -> Dois operandos diferentes juntos que nao agem em conjunto. Linha: " + str(self.reader.getLine()) + " Coluna: " + str(self.reader.getColumn()))
				elif joint in self.operators:
					self.tokens.append(Token(self.lexemes[joint],joint,[self.reader.getLine(),self.reader.getColumn()],None))
					self.reader.goBackwards()
				else:
					#PanicMode
					self.errors.append("Warning -> exclamacao ignorada. Linha: " + str(self.reader.getLine()) + " Coluna: " + str(self.reader.getColumn() - 1))

			#Constantes Numericas
			elif current_character in self.digits:
				floating = False
				exponencial = False
				notIncluded = True
				number = ''
				while current_character in self.digits or current_character == '.' or current_character == 'E':
					if current_character in self.digits:
						number += current_character
					elif current_character == '.' and ((not floating) and (not exponencial)):
						floating = True
						number += current_character
					elif current_character == '.' and (floating or exponencial):
						self.errors("Error -> Constante numerica invalida. Linha: " + str(self.reader.getLine()) + " Coluna: " + str(self.reader.getColumn()))		
					elif current_character == 'E' and (not exponencial):
						if number[len(number) - 1] == '.':
							#PanicMode
							number += '0' + current_character
							exponencial = True
							self.errors.append("Warning -> Constante numerica convergida. Linha: " +  str(self.reader.getLine()) + " Coluna: " + str(self.reader.getColumn()))
						else:	
							number += current_character
							exponencial = True
						current_character = self.reader.getChar()
						self.reader.goForward()
						if current_character == '+' or current_character == '-':
							self.tokens.append(Token("CONSTANTE NUMERICA",None,[self.reader.getLine(),self.reader.getColumn()],self.symbolTable.add(number)))
							self.tokens.append(Token(self.lexemes[current_character],current_character,[self.reader.getLine(),self.reader.getColumn()],None))
							notIncluded = False
							break;
						elif current_character in self.digits:
							number += current_character
					current_character = self.reader.getChar()
					self.reader.goForward()

				if current_character in self.letters and current_character != 'E':
					#PanicMode					
					self.reader.goBackwards();
					self.errors.append("Warning -> Digitos ignorados no inicio de um identificador. Linha: " +  str(self.reader.getLine()) + " Coluna: " + str(self.reader.getColumn()))
				elif notIncluded:
					self.reader.goBackwards();
					self.tokens.append(Token("CONSTANTE NUMERICA",None,[self.reader.getLine(),self.reader.getColumn()],self.symbolTable.add(number)))
		
			#Separadores
			elif current_character in self.separators:
			    self.tokens.append(Token(self.lexemes[current_character], current_character, [self.reader.getLine(),self.reader.getColumn()],None))

			elif current_character not in self.skip:
			    self.errors.append("Error -> Caractere nao suportado. Linha: " +  str(self.reader.getLine()) + " Coluna: " + str(self.reader.getColumn()))

			self.analisar()

		except EndOfBufferException as e:
				self.errors.append(str(e))
		except EndOfFileException as e:
				pass			


	def imprimir_tokens(self):
		print("\nTokens (<tipo, valor/id, linha, coluna>):")
		for t in self.tokens:
		    print(t)

	def imprimir_tabela_simbolos(self):
		print("\nTabela de Simbolos:")
		print(self.symbolTable)

	def imprimir_erros(self):
		if not self.errors:
		    return
		print("Errors:")
		for e in self.errors:
		    print(e)
