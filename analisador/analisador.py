import string
from token import Token
from symbol_table import SymbolTable
from bufferedFileReader import BufferedFileReader
from bufferedFileReader import EndOfFileException
from bufferedFileReader import EndOfBufferException
from arvore_sintatica import Noh
from arvore_sintatica import ArvoreSintatica

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
		self.indice = 0
		self.reserved = ["int", "char", "float", "struct", "if", "else", "while", "void", "return"]
		self.operators = ["=", "<=", "<", ">", ">=", "==", "!=", "+", "-", "*", "/"]
		self.separators = [",", ".", "[", "{", "(", ")", "}", "]", ";"]
		self.skip = ['\t', ' ','\n','\r']
		self.letters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
		self.digits = "0123456789"
		self.reader = BufferedFileReader(fileName)
		self.root = Noh(None,True,'programa')
		self.arvore = ArvoreSintatica(self.root)

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

	def peek_token(self):
		if(self.indice >= len(self.tokens)):
			return None
		return self.tokens[self.indice]

	def peek_second_token(self):
		if((self.indice + 1) >= len(self.tokens)):
			return None
		return self.tokens[self.indice+1]

	def pop_token(self):
		if(self.indice == len(self.tokens)):
			return None
		else:
			self.indice += 1
			return self.tokens[self.indice - 1]

	def analise_sintatica(self):
		self.programa()

	def programa(self):
		if(self.peek_token() is not None):
			noh1 = Noh(self.arvore.root,False,'declaracao_lista')
			self.arvore.root.addFilho(noh1)
			self.declaracao_lista(noh1)

	def declaracao_lista(self,noh):
		if(self.peek_token() is not None):
			noh1 = Noh(noh,False,'declaracao')
			noh.addFilho(noh1)
			self.declaracao(noh1)
			noh2 = Noh(noh,False,'declaracao_lista\'')
			noh.addFilho(noh2)
			self.declaracao_lista1(noh2)

	def declaracao_lista1(self,noh):
		if(self.peek_token() is not None):
			primeiros_declaracao = ['int','float','char','void', 'struct']
			if(self.peek_token().lexeme in primeiros_declaracao):
				noh1 = Noh(noh,False,'declaracao')
				noh.addFilho(noh1)
				self.declaracao(noh1)
				noh2 = Noh(noh,False,'declaracao_lista\'')
				noh.addFilho(noh2)
				self.declaracao_lista1(noh2)
		

	def declaracao(self,noh):
		if(self.peek_token() is not None):
			primeiros_tipo_especificador = ['int','float','char','void']
			if(self.peek_token().lexeme in primeiros_tipo_especificador):
				noh1 = Noh(noh,False,'tipo_especificador')
				noh.addFilho(noh1)
				self.tipo_especificador(noh1)
				self.match(noh,"ID")
				noh2 = Noh(noh,False,'declaracao\'')
				noh.addFilho(noh2)
				self.declaracao1(noh2)
			else:
				noh1 = Noh(noh,False,'estrutura')
				noh.addFilho(noh1)
				self.estrutura(noh1)

	def declaracao1(self,noh):
		if(self.peek_token() is not None):
			if(self.peek_token().lexeme == '('):
				noh1 = Noh(noh,False,'fun_declaracao')
				noh.addFilho(noh1)
				self.fun_declaracao(noh1)
			else:
				noh1 = Noh(noh,False,'var_declaracao')
				noh.addFilho(noh1)
				self.var_declaracao(noh1)

	def var_declaracao(self,noh):
		if(self.peek_token() is not None):
			noh1 = Noh(noh,False,'var_declaracao\'')
			noh.addFilho(noh1)
			self.var_declaracao1(noh1)				


	def var_declaracao1(self,noh):
		if(self.peek_token() is not None):
			if(self.peek_token().lexemeType == self.lexemes['[']):
				self.match(noh,'[')
				self.match(noh,'CONSTANTE NUMERICA')
				self.match(noh,']')
				noh1 = Noh(noh,False,'var_declaracao\'')
				noh.addFilho(noh1)
				self.var_declaracao1(noh1)
			elif(self.peek_token().lexemeType == self.lexemes['=']):
				self.match(noh,'=')
				noh1 = Noh(noh,False,'expressao')
				noh.addFilho(noh1)
				self.expressao(noh1)
				noh2 = Noh(noh,False,'var_declaracao\'')
				noh.addFilho(noh2)
				self.var_declaracao1(noh2)
			else:
				self.match(noh,';')

	def tipo_especificador(self,noh):
		if(self.peek_token() is not None):
			if(self.peek_token().lexeme == "int"):
				self.match(noh,"int")
			elif(self.peek_token().lexeme == "float"):
				self.match(noh,"float")
			elif(self.peek_token().lexeme == "char"):
				self.match(noh,"char")
			else:
				self.match(noh,"void")

	def estrutura(self,noh):
		if(self.peek_token() is not None):
			self.match(noh,'struct')
			self.match(noh,'ID')
			self.match(noh,'{')
			noh1 = Noh(noh,False,'atributos_declaracao')
			noh.addFilho(noh1)
			self.atributos_declaracao(noh1)
			self.match(noh,'}')

	def atributos_declaracao(self,noh):
		if(self.peek_token() is not None):
			primeiros_tipo_especificador = ['int','float','char','void']
			if(self.peek_token().lexeme in primeiros_tipo_especificador):
				noh1 = Noh(noh,False,'tipo_especificador')
				noh.addFilho(noh1)
				self.tipo_especificador(noh1)
				self.match(noh,'ID')
				noh2 = Noh(noh,False,'var_declaracao')
				noh.addFilho(noh2)
				self.var_declaracao(noh2)
				noh3 = Noh(noh,False,'atributos_declaracao\'')
				noh.addFilho(noh3)
				self.atributos_declaracao1(noh3)
			else:
				noh1 = Noh(noh,False,'estrutura')
				noh.addFilho(noh1)
				self.estrutura(noh1)
				noh2 = Noh(noh,False,'declaracao\'')
				noh.addFilho(noh2)
				self.atributos_declaracao1(noh2)

	def atributos_declaracao1(self,noh):
		if(self.peek_token() is not None):
			primeiros_tipo_especificador = ['int','float','char','void']
			if(self.peek_token().lexeme in primeiros_tipo_especificador):
				noh1 = Noh(noh,False,'tipo_especificador')
				noh.addFilho(noh1)
				self.tipo_especificador(noh1)
				self.match(noh,'ID')
				noh2 = Noh(noh,False,'var_declaracao')
				noh.addFilho(noh2)
				self.var_declaracao(noh2)
				noh3 = Noh(noh,False,'atributos_declaracao\'')
				noh.addFilho(noh3)
				self.atributos_declaracao1(noh3)
			elif(self.peek_token().lexeme == 'struct'):
				noh1 = Noh(noh,False,'estrutura')
				noh.addFilho(noh1)
				self.estrutura(noh1)
				noh2 = Noh(noh,False,'atributos_declaracao\'')
				noh.addFilho(noh2)
				self.atributos_declaracao1(noh2)

	def fun_declaracao(self,noh):
		if(self.peek_token() is not None):
			self.match(noh,'(')
			noh1 = Noh(noh,False,'params')
			noh.addFilho(noh1)
			self.params(noh1)
			self.match(noh,')')
			noh2 = Noh(noh,False,'composto_decl')
			noh.addFilho(noh2)
			self.composto_decl(noh2)

	def params(self,noh):
		if(self.peek_token() is not None):
			if(self.peek_token().lexeme == 'void'):
				self.match(noh,'void')
			else:
				noh1 = Noh(noh,False,'param_lista')
				noh.addFilho(noh1)
				self.param_lista(noh1)

	def param_lista(self,noh):
		if(self.peek_token() is not None):
			primeiros_tipo_especificador = ['int','float','char','void']
			if(self.peek_token().lexeme in primeiros_tipo_especificador):
				noh1 = Noh(noh,False,'param')
				noh.addFilho(noh1)
				self.param(noh1)
				noh2 = Noh(noh,False,'param_lista')
				noh.addFilho(noh2)
				self.param_lista(noh2)
			elif(self.peek_token().lexeme == ','):
				self.match(noh,',')
				noh1 = Noh(noh,False,'param')
				noh.addFilho(noh1)
				self.param(noh1)
				noh2 = Noh(noh,False,'param_lista')
				noh.addFilho(noh2)
				self.param_lista(noh2)

	def param(self,noh):
		if(self.peek_token() is not None):
			noh2 = Noh(noh,False,'tipo_especificador')
			noh.addFilho(noh2)
			self.tipo_especificador(noh2)
			self.match(noh,"ID")
			noh1 = Noh(noh,False,'param\'')
			noh.addFilho(noh1)
			self.param1(noh1)

	def param1(self,noh):
		if(self.peek_token() is not None):
			if(self.peek_token().lexemeType == self.lexemes['[']):
				self.match(noh,'[')
				self.match(noh,']')
				noh1 = Noh(noh,False,'param\'')
				noh.addFilho(noh1)
				self.param1(noh1)
	

	def composto_decl(self,noh):
		if(self.peek_token() is not None):
			self.match(noh,"{")
			noh1 = Noh(noh,False,'instrucoes')
			noh.addFilho(noh1)
			self.instrucoes(noh1)
			self.match(noh,"}")

	def instrucoes(self,noh):
		if(self.peek_token() is not None):
			primeiros_comando = ['{','if','while','return','(','ID','CONSTANTE NUMERICA']
			primeiros_local_declaracoes = ["int","char","float","void"]			
			if(self.peek_token().lexeme in primeiros_comando or self.peek_token().lexemeType in primeiros_comando):
				noh2 = Noh(noh,False,'comando_lista')
				noh.addFilho(noh2)
				self.comando_lista(noh2)
				noh1 = Noh(noh,False,'instrucoes')
				noh.addFilho(noh1)
				self.instrucoes(noh1)
			elif(self.peek_token().lexeme in primeiros_local_declaracoes):
				noh2 = Noh(noh,False,'local_declaracoes')
				noh.addFilho(noh2)
				self.local_declaracoes(noh2)
				noh1 = Noh(noh,False,'instrucoes')
				noh.addFilho(noh1)
				self.instrucoes(noh1) 			

	def local_declaracoes(self,noh):
		if(self.peek_token() is not None):
			primeiros_tipo_especificador = ["int","char","float","void"]
			if(self.peek_token().lexeme in primeiros_tipo_especificador):
				noh1 = Noh(noh,False,'tipo_especificador')
				noh.addFilho(noh1)
				self.tipo_especificador(noh1)
				self.match(noh,'ID')
				noh3 = Noh(noh,False,'var_declaracao')
				noh.addFilho(noh3)
				self.var_declaracao(noh3)
				noh2 = Noh(noh,False,'local_declaracoes')
				noh.addFilho(noh2)
				self.local_declaracoes(noh2)
			elif(self.peek_token().lexeme == 'struct'):
				noh1 = Noh(noh,False,'estrutura')
				noh.addFilho(noh1)
				self.estrutura(noh1)
				noh2 = Noh(noh,False,'local_declaracoes')
				noh.addFilho(noh2)
				self.local_declaracoes(noh2)

	def comando_lista(self,noh):
		if(self.peek_token() is not None):
			primeiros_comando = ['{','if','while','return','(','ID','CONSTANTE NUMERICA']
			if(self.peek_token().lexeme in primeiros_comando or self.peek_token().lexemeType in primeiros_comando):
				noh1 = Noh(noh,False,'comando')
				noh.addFilho(noh1)
				self.comando(noh1)
				noh2 = Noh(noh,False,'comando_lista')
				noh.addFilho(noh2)
				self.comando_lista(noh2)

	def comando(self,noh):
		if(self.peek_token() is not None):
			if(self.peek_token().lexemeType == self.lexemes['{']):
				noh1 = Noh(noh,False,'composto_decl')
				noh.addFilho(noh1)
				self.composto_decl(noh1)
			elif(self.peek_token().lexeme == "if"):
				noh1 = Noh(noh,False,'selecao_decl')
				noh.addFilho(noh1)
				self.selecao_decl(noh1)
			elif(self.peek_token().lexeme == "while"):
				noh1 = Noh(noh,False,'iteracao_decl')
				noh.addFilho(noh1)
				self.iteracao_decl(noh1)
			elif(self.peek_token().lexeme == "return"):
				noh1 = Noh(noh,False,'retorno_decl')
				noh.addFilho(noh1)
				self.retorno_decl(noh1)
			else:
				noh1 = Noh(noh,False,'expressao_decl')
				noh.addFilho(noh1)
				self.expressao_decl(noh1)

	def expressao_decl(self,noh):
		if(self.peek_token() is not None):
			if(self.peek_token().lexeme == ';'):
				self.match(noh,';')
			else:
				noh1 = Noh(noh,False,'expressao')
				noh.addFilho(noh1)
				self.expressao(noh1)
				self.match(noh,";")

	def selecao_decl(self,noh):
		if(self.peek_token() is not None):
			self.match(noh,"if")
			self.match(noh,"(")
			noh1 = Noh(noh,False,'expressao')
			noh.addFilho(noh1)
			self.expressao(noh1)
			self.match(noh,")")
			noh2 = Noh(noh,False,'comando')
			noh.addFilho(noh2)
			self.comando(noh2)
			noh3 = Noh(noh,False,'else_decl')
			noh.addFilho(noh3)
			self.else_decl(noh3)

	def else_decl(self,noh):
		if(self.peek_token() is not None):
			if(self.peek_token().lexeme == "else"):
				self.match(noh,"else")
				noh2 = Noh(noh,False,'comando')
				noh.addFilho(noh2)
				self.comando(noh2)

	def iteracao_decl(self,noh):
		if(self.peek_token() is not None):
			self.match(noh,"while")
			self.match(noh,"(")
			noh1 = Noh(noh,False,'expressao')
			noh.addFilho(noh1)
			self.expressao(noh1)
			self.match(noh,")")
			noh2 = Noh(noh,False,'comando')
			noh.addFilho(noh2)
			self.comando(noh2)

	def retorno_decl(self,noh):
		if(self.peek_token() is not None):
			self.match(noh,"return")
			noh2 = Noh(noh,False,'retorno_decl\'')
			noh.addFilho(noh2)
			self.retorno_decl1(noh2)
			self.match(noh,";")

	def retorno_decl1(self,noh):
		if(self.peek_token() is not None):
			if(self.peek_token().lexemeType != self.lexemes[';']):
				noh2 = Noh(noh,False,'expressao')
				noh.addFilho(noh2)
				self.expressao(noh2)
		
	def expressao(self,noh):
		if(self.peek_token() is not None):
			if(self.peek_token().lexemeType == self.lexemes['('] or self.peek_token().lexemeType == 'CONSTANTE NUMERICA'):
				noh2 = Noh(noh,False,'expressao_simples')
				noh.addFilho(noh2)
				self.expressao_simples(noh2)
			else:
				if(self.peek_second_token().lexemeType == self.lexemes['(']):
					noh2 = Noh(noh,False,'ativacao')
					noh.addFilho(noh2)
					self.ativacao(noh2)
					noh1 = Noh(noh,False,'termo\'')
					noh.addFilho(noh1)
					self.termo1(noh1)
					noh3 = Noh(noh,False,'expressao_soma\'')
					noh.addFilho(noh3)
					self.expressao_soma1(noh3)
					noh4 = Noh(noh,False,'expressao_simples\'')
					noh.addFilho(noh4)
					self.expressao_simples1(noh4)
				else:
					noh1 = Noh(noh,False,'var')
					noh.addFilho(noh1)
					self.var(noh1)
					if(self.peek_token().lexemeType == self.lexemes['=']):
						self.match(noh,'=')
						noh2 = Noh(noh,False,'expressao')
						noh.addFilho(noh2)
						self.expressao(noh2)
					else:
						noh2 = Noh(noh,False,'termo\'')
						noh.addFilho(noh2)
						self.termo1(noh2)
						noh3 = Noh(noh,False,'expressao_soma\'')
						noh.addFilho(noh3)
						self.expressao_soma1(noh3)
						noh4 = Noh(noh,False,'expressao_simples\'')
						noh.addFilho(noh4)
						self.expressao_simples1(noh4)

	def var(self,noh):
		if(self.peek_token() is not None):
			self.match(noh,'ID')
			noh1 = Noh(noh,False,'var\'')
			noh.addFilho(noh1)
			self.var1(noh1)
	
	def var1(self,noh):
		if(self.peek_token() is not None):
			if(self.peek_token().lexemeType == self.lexemes['[']):
				self.match(noh,'[')
				noh2 = Noh(noh,False,'expressao')
				noh.addFilho(noh2)
				self.expressao(noh2)
				self.match(noh,']')
				noh1 = Noh(noh,False,'var\'')
				noh.addFilho(noh1)
				self.var1(noh1)


	def expressao_simples(self,noh):
		if(self.peek_token() is not None):
			noh1 = Noh(noh,False,'expressao_soma')
			noh.addFilho(noh1)
			self.expressao_soma(noh1)
			noh2 = Noh(noh,False,'expressao_simples\'')
			noh.addFilho(noh2)
			self.expressao_simples1(noh2)

	def expressao_simples1(self,noh):
		if(self.peek_token() is not None):
			primeiros_relacional = ['<','>','==','!=','<=','>=']
			if(self.peek_token().lexeme in primeiros_relacional):
				noh1 = Noh(noh,False,'relacional')
				noh.addFilho(noh1)
				self.relacional(noh1)
				noh2 = Noh(noh,False,'expressao_soma')
				noh.addFilho(noh2)
				self.expressao_soma(noh2)

	def expressao_soma(self,noh):
		if(self.peek_token() is not None):
			noh1 = Noh(noh,False,'termo')
			noh.addFilho(noh1)
			self.termo(noh1)
			noh2 = Noh(noh,False,'expressao_soma\'')
			noh.addFilho(noh2)
			self.expressao_soma1(noh2)

	def expressao_soma1(self,noh):
		if(self.peek_token() is not None):
			primeiros_soma = ['+','-']
			if(self.peek_token().lexeme in primeiros_soma):
				noh1 = Noh(noh,False,'soma')
				noh.addFilho(noh1)
				self.soma(noh1)
				noh2 = Noh(noh,False,'termo')
				noh.addFilho(noh2)
				self.termo(noh2)
				noh3 = Noh(noh,False,'expressao_soma\'')
				noh.addFilho(noh3)
				self.expressao_soma1(noh3)

	def termo(self,noh):
		if(self.peek_token() is not None):
			noh1 = Noh(noh,False,'fator')
			noh.addFilho(noh1)
			self.fator(noh1)
			noh2 = Noh(noh,False,'termo\'')
			noh.addFilho(noh2)
			self.termo1(noh2)

	def termo1(self,noh):
		if(self.peek_token() is not None):
			primeiros_mult = ['*','/']
			if(self.peek_token().lexeme in primeiros_mult):
				noh1 = Noh(noh,False,'mult')
				noh.addFilho(noh1)
				self.mult(noh1)
				noh2 = Noh(noh,False,'fator')
				noh.addFilho(noh2)
				self.fator(noh2)
				noh3 = Noh(noh,False,'termo\'')
				noh.addFilho(noh3)
				self.termo1(noh3)

	def fator(self,noh):
		if(self.peek_token() is not None):
			if(self.peek_token().lexemeType == self.lexemes['(']):
				self.match(noh,'(')
				noh1 = Noh(noh,False,'expressao')
				noh.addFilho(noh1)
				self.expressao(noh1)
				self.match(noh,')')
			elif(self.peek_token().lexemeType == 'CONSTANTE NUMERICA'):
				self.match(noh,'CONSTANTE NUMERICA')
			elif(self.peek_second_token().lexemeType == self.lexemes['(']):
				noh1 = Noh(noh,False,'ativacao')
				noh.addFilho(noh1)
				self.ativacao(noh1)
			else:
				noh1 = Noh(noh,False,'var')
				noh.addFilho(noh1)
				self.var(noh1)

	def ativacao(self,noh):
		if(self.peek_token() is not None):
			self.match(noh,'ID')
			self.match(noh,'(')
			noh1 = Noh(noh,False,'args')
			noh.addFilho(noh1)
			self.args(noh1)
			self.match(noh,')')

	def args(self,noh):
		if(self.peek_token() is not None):
			noh1 = Noh(noh,False,'arg_lista')
			noh.addFilho(noh1)
			self.arg_lista(noh1)

	def arg_lista(self,noh):
		if(self.peek_token() is not None):
			primeiros_expressao = ['ID','CONSTANTE NUMERICA',self.lexemes['(']]
			if(self.peek_token().lexemeType in primeiros_expressao):
				noh1 = Noh(noh,False,'expressao')
				noh.addFilho(noh1)
				self.expressao(noh1)
				noh2 = Noh(noh,False,'arg_lista')
				noh.addFilho(noh2)
				self.arg_lista(noh2)
			elif(self.peek_token().lexeme == ','):
				self.match(noh,',')
				noh1 = Noh(noh,False,'expressao')
				noh.addFilho(noh1)
				self.expressao(noh1)
				noh2 = Noh(noh,False,'arg_lista')
				noh.addFilho(noh2)
				self.arg_lista(noh2)

	def relacional(self,noh):
		if(self.peek_token() is not None):
			if(self.peek_token().lexemeType == self.lexemes['>']):
				self.match(noh,'>')
			elif(self.peek_token().lexemeType == self.lexemes['<']):
				self.match(noh,'<')
			elif(self.peek_token().lexemeType == self.lexemes['>=']):
				self.match(noh,'>=')
			elif(self.peek_token().lexemeType == self.lexemes['<=']):
				self.match(noh,'<=')
			elif(self.peek_token().lexemeType == self.lexemes['!=']):
				self.match(noh,'!=')
			else:
				self.match(noh,'==')

	def soma(self,noh):
		if(self.peek_token() is not None):		
			if(self.peek_token().lexemeType == self.lexemes['+']):
				self.match(noh,'+')
			else:
				self.match(noh,'-')

	def mult(self,noh):
		if(self.peek_token() is not None):
			if(self.peek_token().lexemeType == self.lexemes['*']):
				self.match(noh,'*')
			else:
				self.match(noh,'/')


	def match(self,noh,lexeme):
		token = self.peek_token()
		if(token is not None): 
			if(lexeme == 'ID' or lexeme == 'CONSTANTE NUMERICA'):
				if(token.lexemeType != lexeme):
					self.errors.append('Syntax Error -> Esperado \'' + lexeme + '\' - encontrado \'' + str(token) + '\'' )
				else:
					noh1 = Noh(noh,False,token)
					noh.addFilho(noh1)
			else:
				if(token.lexeme != lexeme):
					#panic mode
					if(lexeme == ';'):
						self.errors.append('Syntax Error -> Esperado \'' + lexeme + '\' - encontrado \'' + str(token) + '\'\nERRO FOI IGNORADO')
						noh1 = Noh(noh,False,';')
						noh.addFilho(noh1)
						return
					elif(lexeme == 'struct'):
						self.errors.append('Syntax Error -> Esperado \'' + lexeme + '\' - encontrado \'' + str(token) + '\'\n')
						return
					self.errors.append('Syntax Error -> Esperado \'' + lexeme + '\' - encontrado \'' + str(token) + '\'')
				else:
					noh1 = Noh(noh,False,token)
					noh.addFilho(noh1)
		else:
			self.errors.append('Syntax Error -> Esperado \'' + lexeme + '\' - encontrado \'nada\'' )
			return
		self.pop_token()
		
		
#------------------------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------------------------

		

	def imprimir_tabela_simbolos(self):
		print("\nTabela de Simbolos:")
		print(self.symbolTable)

	def imprimir_erros(self):
		if not self.errors:
		    return
		print("Errors:")
		for e in self.errors:
		    print(e)

	def imprimirArvore(self):
		print("Arvore Sintatica:\n")
		print(self.arvore)
