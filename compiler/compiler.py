import sys
import os
import re


class Tokenizer:
    def __init__(self, input_stream):
        # opens the jack file stream and gets ready to tokenize it
        self.file = input_stream
        self.tokens = []
        self.curTokenIdx = 0

        self.symbols = {
            "{", "}", "(", ")", "[", "]", ".", ",", ";",
            "+", "-", "*", "/", "&", "|", "<", ">", "=", "~"
        }
        self.keywords = {
            "class", "constructor", "function", "method", "field",
            "static", "var", "int", "char", "boolean", "void",
            "true", "false", "null", "this", "let", "do",
            "if", "else", "while", "return"
        }
        
        # process raw file input to list of lines of text w/extra whitespace & comments removed
        self.clean_text = self.read_and_clean()
        self.tokens = self.text_to_jack_tkns(self.clean_text)

        # print(self.tokens)
        # for t, type in self.tokens:
        #     print(f'token: {t}, type: {type}')

        return

    """
    helper to determine token type
    """
    def ttype(self, token):
        if token in self.keywords:
            return "keyword"
        elif token in self.symbols:
            return "symbol"
        elif token.isdigit():
            return "integerConstant"
        elif token.startswith('"') and token.endswith('"'):
            return "stringConstant"
        else:
            return "identifier"

    """
    takes in string of a file line and outputs list of strings that are jack tokens
    """
    def text_to_jack_tkns(self, text: str) -> list[str]:
        ret = []

        curString = ""
        isInStringFlag = False
        for i in range(len(text)):
            c = text[i]

            if c == " " and not isInStringFlag:
                if curString:
                    ret.append([curString, self.ttype(curString)])
                curString = ""
                continue
            if c in self.symbols and not isInStringFlag:
                if curString:
                    ret.append([curString, self.ttype(curString)])
                ret.append([c, self.ttype(c)])
                curString = ""
                continue
            if c == '"':
                if isInStringFlag:
                    # end of current jack string
                    ret.append([curString, self.ttype('"' + curString + '"')])
                    curString = ""
                    isInStringFlag = not isInStringFlag
                else:
                    if curString:
                        ret.append([curString, self.ttype(curString)])
                    isInStringFlag = not isInStringFlag
                continue
            
            curString += c
            
        
        return ret


    def read_and_clean(self):
        with open(self.file, "r") as f:
            data = f.read()  # read entire file into one string

        # Remove block comments
        data = re.sub(r"/\*.*?\*/", "", data, flags=re.DOTALL)

        # Remove inline comments
        data = re.sub(r"//.*", "", data)

        
        # Strip leading/trailing whitespace and collapse extra newlines/spaces
        data = data.strip()
        data = re.sub(r"\s+", " ", data)  # optional: replace multiple spaces/newlines with a single space

        return data
    
    """
    returns whether or not there are more tokens left to process from input
    """
    def hasMoreTokens(self):
        return True if self.curTokenIdx < len(self.tokens) else False


    """
    move to next token
    """
    def advance(self):
        # advance token index
        self.curTokenIdx += 1
        return

    """
    returns current token type
    """
    def getCurTokenType(self):
        return self.tokens[self.curTokenIdx][1]
    
    """
    returns current token value
    """
    def getCurTokenValue(self):
        return self.tokens[self.curTokenIdx][0]
    
    """
    call only if the current token type is KEYWORD
    """
    def curKeyWord(self):

        return
    
    """
    call only if the current token type is SYMBOL
    """
    def curSymbol(self):

        return
    
    """
    call only if the current token type is IDENTIFIER
    """
    def curIdentifier(self):

        return
    
    """
    call only if the current token type is INT_CONST
    """
    def curIntVal(self):

        return
    
    """
    call only if the current token type is STRING_CONST
    """
    def curStringVal(self):

        return




class CompilationEngine:
    """
    Skeleton for the Nand2Tetris CompilationEngine.

    The engine consumes tokens from a JackTokenizer (input_stream)
    and writes VM commands or XML (depending on your project phase) to output_stream.
    Only method names and brief descriptions are provided here.
    """

    """
    Creates a new compilation engine with the given input and output streams.
    Typically: keep references to the tokenizer and the writer.
    """
    def __init__(self, tknzr, indent_level, file):
        self.tknzr = tknzr
        self.indent_level = indent_level
        self.f = file
        self.specialOutput = {'<': '&lt;', '>': '&gt;', '"': '&quot;', '&': '&amp;'}
        self.indents = ""
        self.opList = {'+', '-', '*', '/', '&', '|', '<', '>', '='}
        self.unaryOpList = {'-', '~'}
        self.subroutineKeywordList = {'constructor', 'function', 'method'}
        
        return

    def updateIndents(self, change):
        self.indent_level += change
        self.indents = self.indent_level * "  "

    # ------------------------------------------------------------
    # Top-level and declarations
    # ------------------------------------------------------------

    """
    
    """
    def eat(self, expected=[]):
        currentToken = self.tknzr.getCurTokenValue()
        currentTokenType = self.tknzr.getCurTokenType()
        # if (currentTokenType is str) and (currentToken in expected if len(expected) > 0 else True):
        if (type(currentToken) is str) and (currentToken in expected if len(expected) > 0 else True):
            self.f.write(f'{self.indents}<{currentTokenType}> {currentToken} </{currentTokenType}>\n')
            # print(f'<{currentTokenType}> {currentToken} </{currentTokenType}>')
        else:
            print(f'syntax error from eat: current token value: "{currentToken}", current token type: "{currentTokenType}"')
            self.f.write("syntax error\n")

        if self.tknzr.hasMoreTokens():
            self.tknzr.advance()

        return True

    """
    Compiles a complete class.
    Entry point called by the analyzer; handles 'class ... { ... }'.
    """
    def compileClass(self):
        
        """
        class: 'class' className '{' classVarDec* subroutineDec* '}'
        
        """

        self.f.write(f'{self.indents}<class>\n')

        self.updateIndents(1)
        self.eat(["class"])

        # how to handle className?? --> indentifier, just eat w/identifier tags?
        # will be handled in eat if nothing passed directly
        self.eat()

        self.eat(["{"])

        # need checks for how many (if any) of classVarDec & subroutineDec
        self.compileClassVarDec()

        while self.tknzr.hasMoreTokens() and self.tknzr.getCurTokenValue() in self.subroutineKeywordList:
            self.compileSubroutineDec()

        self.eat(["}"])
        self.updateIndents(-1)

        self.f.write(f'{self.indents}</class>\n')
        
        # while self.tknzr.hasMoreTokens():
        #     token = self.tknzr.getCurTokenValue()
        #     tokenType = self.tknzr.getCurTokenType()
        #     # compile type: (recursive calls, advance/eat at leaf (also write to file))
        #     if token in ["if", "let"]:
        #         self.compileStatements()
        #     else:
        #         line = f'<{tokenType}> {self.specialOutput[token] if token in self.specialOutput else token} </{tokenType}>\n'
            
        #     # print(line)
        #     self.f.write(line)
        #     if self.tknzr.hasMoreTokens():
        #         self.tknzr.advance()

        return

    """
    Compiles a static variable declaration or a field declaration.
    Handles sequences like: ('static'|'field') type varName (',' varName)* ';'
    """
    def compileClassVarDec(self):
        """
        classVarDec: ('static'|'field') type varName (','varName)* ';'
        type: 'int'|'char'|'boolean'|className
        """

        self.f.write(f'{self.indents}<classVarDec>\n')
        self.updateIndents(1)


        self.eat(["static", "field"])
        # how to handle className ?? -> just eat as is
        self.eat()
        # self.eat(["int", "char", "boolean", "className"])
        # how to handle varName(s) --> just eat as is
        while self.tknzr.getCurTokenValue() != ";":
            self.eat()
        
        self.eat([";"])

        self.updateIndents(-1)
        self.f.write(f'{self.indents}</classVarDec>\n')

        return

    """
    Compiles a complete method, function, or constructor declaration.
    Handles header ('constructor'|'function'|'method' ...) and delegates body.
    """
    def compileSubroutineDec(self):
        """
        subroutineDec: ('constructor'|'function'|'method') ('void'|type) subroutineName '(' parameterList ')' subRoutineBody
        """

        self.f.write(f'{self.indents}<subroutineDec>\n')
        self.updateIndents(1)


        self.eat(["constructor", "function", "method"])
        self.eat()
        self.eat()
        self.eat(['('])

        self.compileParameterList()
        
        self.eat([')'])

        self.compileSubroutineBody()
        
        self.updateIndents(-1)
        self.f.write(f'{self.indents}</subroutineDec>\n')

        return

    """
    Compiles a (possibly empty) parameter list.
    Does not handle the enclosing parentheses tokens '(' and ')'.
    """
    def compileParameterList(self):
        """
        parameterList: ( (type varName) (','type varName)*)?
        """
        self.f.write(f'{self.indents}<parameterList>\n')
        
        self.updateIndents(1)
        while self.tknzr.getCurTokenValue() != ')':
            self.eat()

        self.updateIndents(-1)
        self.f.write(f'{self.indents}</parameterList>\n')

        return

    """
    Compiles a subroutine's body.
    Handles '{' varDec* statements '}'.
    """
    def compileSubroutineBody(self):
        """
        subroutineBody: '{' varDec* statements '}'
        """

        self.f.write(f'{self.indents}<subroutineBody>\n')
        self.updateIndents(1)

        self.eat(["{"])
        
        self.compileVarDec()

        self.compileStatements()
        
        self.eat(["}"])

        self.updateIndents(-1)
        self.f.write(f'{self.indents}</subroutineBody>\n')

        return

    """
    Compiles a local variable declaration.
    Handles 'var' type varName (',' varName)* ';'
    """
    def compileVarDec(self):
        """
        varDec: 'var' type varName (','varName)* ';'
        """
        self.f.write(f'{self.indents}<varDec>\n')
        self.updateIndents(1)

        self.eat(["var"])
        
        while self.tknzr.getCurTokenValue() != ';':
            self.eat()

        self.eat([";"])

        self.updateIndents(-1)
        self.f.write(f'{self.indents}</varDec>\n')
        
        return

    """
    Compiles a sequence of statements.
    Does not handle the enclosing curly braces '{' and '}'.
    """
    def compileStatements(self):
        """
        statements: statement*
        statement: letStatement | ifStatement | whileStatement | doStatement | returnStatement
        """

        self.f.write(f'{self.indents}<statements>\n')
        self.updateIndents(1)

        # needs looped for if more than one statement
        while self.tknzr.getCurTokenType() == "keyword": 
            if self.tknzr.getCurTokenType() == "keyword":
                # print("compile statements, statement starts with keyword check passed")
                curToken = self.tknzr.getCurTokenValue()
                # print(curToken)
                if curToken == 'if':
                    self.compileIf()
                elif curToken == 'while':
                    self.compileWhile()
                elif curToken == 'do':
                    self.compileDo()
                elif curToken == 'let':
                    self.compileLet()
                elif curToken == 'return':
                    self.compileReturn()
                else:
                    print("syntax error: no keyword found for statement")
            else:
                print("compile statements, statement starts with keyword check failed")
                print(f'compile statements, statement expected to start with keyword: current token: "{self.tknzr.getCurTokenValue()}" current token type: "{self.tknzr.getCurTokenType()}"')

        self.updateIndents(-1)
        self.f.write(f'{self.indents}</statements>\n')
        
        return

    # ------------------------------------------------------------
    # Statements
    # ------------------------------------------------------------

    """
    Compiles a let statement.
    Handles: 'let' varName ('[' expression ']')? '=' expression ';'
    """
    def compileLet(self):
        """
        letStatement: 'let' varName ('[' expression ']')? '=' expression ';'
        """

        self.f.write(f'{self.indents}<letStatement>\n')
        self.updateIndents(1)

        self.eat(["let"])
        self.eat()

        if self.tknzr.getCurTokenValue() == '[':
            self.eat()
            self.compileExpression()
            self.eat()
        
        self.eat(["="])
        
        self.compileExpression()
        
        self.eat([";"])

        self.updateIndents(-1)
        self.f.write(f'{self.indents}</letStatement>\n')

        return

    """
    Compiles an if statement, possibly with a trailing else clause.
    Handles: 'if' '(' expression ')' '{' statements '}' ('else' '{' statements '}')?
    """
    def compileIf(self):
        """
        'if' '(' expressions ')' '{' statements '}' ('else''{' statements '}' )?
        """

        self.f.write(f'{self.indents}<ifStatement>\n')
        self.updateIndents(1)

        self.eat(["if"])
        self.eat(["("])
        self.compileExpression()
        self.eat([")"])
        self.eat(["{"])
        self.compileStatements()
        self.eat(["}"])

        # check for else statement
        if self.tknzr.getCurTokenValue() == "else":
            self.eat(["else"])
            self.eat(["{"])
            self.compileStatements()
            self.eat(["}"])

        self.updateIndents(-1)
        self.f.write(f'{self.indents}</ifStatement>\n')

        return

    """
    Compiles a while statement.
    Handles: 'while' '(' expression ')' '{' statements '}'
    """
    def compileWhile(self):
        # while statement: 'while' '(' 'expression' ')' '{' 'statements '}'

        self.f.write(f'{self.indents}<whileStatement>\n')
        self.updateIndents(1)
        
        self.eat(["while"])
        self.eat(["("])
        self.compileExpression()
        self.eat([")"])
        self.eat(["{"])
        self.compileStatements()
        self.eat(["}"])

        self.updateIndents(-1)
        self.f.write(f'{self.indents}</whileStatement>\n')

        return

    """
    Compiles a do statement (a subroutine call used as a statement).
    Handles: 'do' subroutineCall ';'
    """
    def compileDo(self):
        """
        doSatement: 'do' subroutineCall ';'
        """

        self.f.write(f'{self.indents}<doStatement>\n')
        self.updateIndents(1)

        self.eat(["do"])

        self.compileSubroutineCall()
        
        self.eat([";"])
        
        self.updateIndents(-1)
        self.f.write(f'{self.indents}</doStatement>\n')
        
        return

    """
    Compiles a return statement.
    Handles: 'return' expression? ';'
    """
    def compileReturn(self):
        """
        returnStatement: 'return' expression? ';'
        """

        self.f.write(f'{self.indents}<returnStatement>\n')
        self.updateIndents(1)

        self.eat(["return"])

        if self.tknzr.getCurTokenValue() != ';':
            self.compileExpression()

        self.eat([";"])

        self.updateIndents(-1)
        self.f.write(f'{self.indents}</returnStatement>\n')

        return

    # ------------------------------------------------------------
    # Expressions
    # ------------------------------------------------------------

    """
    Compiles an expression.
    Handles: term (op term)*
    """
    def compileExpression(self):
        
        # expression: term (op term)*

        self.f.write(f'{self.indents}<expression>\n')
        self.updateIndents(1)

        # handle expression
        self.compileTerm()

        while (self.tknzr.getCurTokenType() == 'symbol') and (self.tknzr.getCurTokenValue() in self.opList):
            self.eat()
            self.compileTerm()

        self.updateIndents(-1)
        self.f.write(f'{self.indents}</expression>\n')
        
        return

    """
    Compiles a term.
    If the current token is an identifier, resolves whether it's a varName,
    an array entry, or a subroutine call. Also handles constants, unary ops,
    and parenthesized expressions.
    """
    def compileTerm(self):

        # term: intergerConstant | stringConstant | keywordConstant | varName | varName '[' expression ']' 
        # | subroutineCall | '( expression ')' | unaryOp term

        self.f.write(f'{self.indents}<term>\n')
        self.updateIndents(1)
        
        self.eat()
        
        self.updateIndents(-1)
        self.f.write(f'{self.indents}</term>\n')
        
        return

    """
    Compiles a (possibly empty) comma-separated list of expressions.
    Returns the number of expressions in the list (per the book’s API).
    """
    def compileExpressionList(self):
        # expression list

        self.f.write(f'{self.indents}<expressionList>\n')
        self.updateIndents(1)



        self.updateIndents(-1)
        self.f.write(f'{self.indents}</expressionList>\n')

        return
    

    """
    Compiles subroutine call
    """
    def compileSubroutineCall(self):
        # subroutineName '(' expressionList ')' | (className | varName) '.' subroutineName '(' expressionList ')'

        self.eat()

        if self.tknzr.getCurTokenValue() == '.':
            self.eat(['.'])
            self.eat()

        self.eat(['('])

        self.compileExpressionList()

        self.eat([')'])

        return

class JackAnalyzer():
    def __init__(self, inputPaths):
        self.filesList = inputPaths
        self.tokenizer = None
        self.compilation_engine = None

    def drive_analyze(self):
        print(f'\nTranslating file(s): {self.filesList}\n')

        for file in self.filesList:
            self.analyze(file)


    def analyze(self, file):

        # single file -- with compilation engine
        print(f'\nTranslating single file: {file}\n')
        self.tokenizer = Tokenizer(file)

        # setup output file
        baseName, _ = os.path.splitext(file)
        outputFileName = baseName + "_test_cmpeng" + ".xml"
        print(f'\nOutput File: {outputFileName}\n')
        
        indent_level = 0
        with open(outputFileName, "w") as f:
            self.compilation_engine = CompilationEngine(self.tokenizer, indent_level, f)
            # line = f'<tokens>\n'
            # f.write(line)
            
            self.compilation_engine.compileClass()

            # line = f'</tokens>\n'
            # f.write(line)

        
        # single file -- no compilation engine

        # print(f'\nTranslating single file: {self.filesList[0]}\n')
        # tokenizer = Tokenizer(self.filesList[0])

        # baseName, _ = os.path.splitext(self.filesList[0])
        # outputFileName = baseName + "_test" + ".xml"
        # print(f'\nOutput File: {outputFileName}\n')

        # with open(outputFileName, "w") as f:
        #     line = f'<tokens>\n'
        #     f.write(line)
        #     while tokenizer.hasMoreTokens():
        #         token = tokenizer.getCurTokenValue()
        #         tokenType = tokenizer.getCurTokenType()
        #         line = f'<{tokenType}> {self.specialOutput[token] if token in self.specialOutput else token} </{tokenType}>\n'
        #         f.write(line)
        #         tokenizer.advance()
        #     line = f'</tokens>\n'
        #     f.write(line)


def main(files):
    print("\nrunning main")

    analyzer = JackAnalyzer(files)
    analyzer.drive_analyze()


    return



def process_path(path):
    # check if the argument is a file
    if os.path.isfile(path):
        print(f"{path} is a file")
        return [path] if path.endswith(".jack") else []
    
    # check if the argument is a directory
    elif os.path.isdir(path):
        print(f"{path} is a directory")
        jack_files = []
        for entry in os.listdir(path):
            full_path = os.path.join(path, entry)
            if full_path.endswith(".jack") and os.path.isfile(full_path):
                jack_files.append(full_path)
        return jack_files
    
    else:
        print(f"{path} does not exist or is not accessible")
        return []

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <path>")
        sys.exit(1)
    
    input_path = sys.argv[1]
    jack_files = process_path(input_path)
    print("Found .jack files:", jack_files)

    main(jack_files)