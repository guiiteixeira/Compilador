class Noh:
	
	def __init__(self, pai, isRoot, funcao):
		self.filhos = []
		self.pai = pai
		self.isRoot = isRoot
		self.funcao = funcao

	def addFilho(self,noh):
		self.filhos.append(noh)


class ArvoreSintatica:

	def __init__(self, root):
		self.root = root

	def __str__(self):
		valueOf = self.root.funcao + '\n'
		nohs = [self.root]
		for noh in nohs:
			valueOf += "Filhos de " + str(noh.funcao) + ":\n" 
			for filho in noh.filhos:
				nohs.append(filho)
				valueOf += str(filho.funcao) + " -- "

			valueOf += "\n"

		return valueOf
				
	
