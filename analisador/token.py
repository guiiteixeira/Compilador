class Token:
    def __init__(self, lexemeType, lexeme, location, symbolTableIndex):
        self.lexemeType = lexemeType
        self.lexeme = lexeme
        self.symbolTableIndex = symbolTableIndex
        self.location = location 

    def __str__(self):
        if self.symbolTableIndex is not None:
            return "<{}, {}, {}, {}>".format(self.lexemeType, self.symbolTableIndex, self.location[0],self.location[1])
        else:
            return "<{}, '{}', {}, {}>".format(self.lexemeType, self.lexeme, self.location[0],self.location[1])
