import sys
import os
import re
from collections import defaultdict


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
    def text_to_jack_tkns(self, text):
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
    
    def peek(self):
        if self.curTokenIdx + 1 < len(self.tokens):
            return [True, self.tokens[self.curTokenIdx + 1]]
        else:
            return [False, None]


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
    def __init__(self, tknzr, indent_level, xmlFile, vmFile):
        self.tknzr = tknzr
        self.indent_level = indent_level
        self.f = xmlFile
        self.vmFile = vmFile
        self.specialOutput = {'<': '&lt;', '>': '&gt;', '"': '&quot;', '&': '&amp;'}
        self.indents = ""
        self.opList = {'+', '-', '*', '/', '&', '|', '<', '>', '='}
        self.unaryOpList = {'-', '~'}
        self.subroutineKeywordList = {'constructor', 'function', 'method'}
        self.kwdConstList = {'true', 'false', 'null', 'this'}

        self.classSymbolTable = SymbolTable()
        self.subroutineSymbolTable = SymbolTable()
        self.inSubroutine = False

        self.VMWriter = VMWriter(self.vmFile)
        
        return


    def updateIndents(self, change):
        self.indent_level += change
        self.indents = self.indent_level * "  "

    # ------------------------------------------------------------
    # Top-level and declarations
    # ------------------------------------------------------------

    """
    
    """
    def eat(self, expected=[], skip_st_def=False):
        currentToken = self.tknzr.getCurTokenValue()
        currentTokenType = self.tknzr.getCurTokenType()
        # if (currentTokenType is str) and (currentToken in expected if len(expected) > 0 else True):
        if (type(currentToken) is str) and (currentToken in expected if len(expected) > 0 else True):
            if currentTokenType == "identifier":
                if (self.inSubroutine) and (currentToken not in self.subroutineSymbolTable.scopeTable) and (currentToken not in self.classSymbolTable.scopeTable) and (not skip_st_def):
                    # check for curtype again?
                    self.subroutineSymbolTable.define(currentToken, self.subroutineSymbolTable.curType, self.subroutineSymbolTable.curKind)
                if (not self.inSubroutine) and (currentToken not in self.classSymbolTable.scopeTable) and (not skip_st_def):
                    self.classSymbolTable.define(currentToken, self.classSymbolTable.curType, self.classSymbolTable.curKind)
                    # if currentToken != self.classSymbolTable.curType:
                    #     self.classSymbolTable.define(currentToken, self.classSymbolTable.curType, self.classSymbolTable.curKind)

                # xml tag info for id in symbol table
                if self.inSubroutine:
                    if currentToken in self.subroutineSymbolTable.scopeTable:
                        st_info = [self.subroutineSymbolTable.typeOf(currentToken), self.subroutineSymbolTable.kindOf(currentToken), self.subroutineSymbolTable.indexOf(currentToken)]  if currentToken in self.subroutineSymbolTable.scopeTable else None
                    elif currentToken in self.classSymbolTable.scopeTable:
                        st_info = [self.classSymbolTable.typeOf(currentToken), self.classSymbolTable.kindOf(currentToken), self.classSymbolTable.indexOf(currentToken)]  if currentToken in self.classSymbolTable.scopeTable else None
                    else:
                        st_info = None
                else:
                    st_info = [self.classSymbolTable.typeOf(currentToken), self.classSymbolTable.kindOf(currentToken), self.classSymbolTable.indexOf(currentToken)]  if currentToken in self.classSymbolTable.scopeTable else None
                self.f.write(f'{self.indents}<{currentTokenType}> {currentToken if currentToken not in self.specialOutput else self.specialOutput[currentToken]}, {st_info} </{currentTokenType}>\n')
                
                # term write for const? -> just push to stack?
                # st_info = [type, king(segment), index]
                # if st_info:
                #     self.VMWriter.f.write(f'{currentToken}\n')
                #     self.VMWriter.writePush(st_info[1], st_info[2])

            else:
                self.f.write(f'{self.indents}<{currentTokenType}> {currentToken if currentToken not in self.specialOutput else self.specialOutput[currentToken]} </{currentTokenType}>\n')
                
            
        else:
            print(f'syntax error from eat: current token value: "{currentToken}", current token type: "{currentTokenType}"')
            print(expected)
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
        self.eat(expected=["class"])

        # how to handle className?? --> indentifier, just eat w/identifier tags?
        # will be handled in eat if nothing passed directly
        self.classSymbolTable.updateScopeName(self.tknzr.getCurTokenValue())
        self.eat(skip_st_def=True)

        self.eat(expected=["{"])

        # need checks for how many (if any) of classVarDec & subroutineDec
        while self.tknzr.getCurTokenValue() in ["static", "field"]:
            self.compileClassVarDec()

        self.inSubroutine = True
        while self.tknzr.hasMoreTokens() and self.tknzr.getCurTokenValue() in self.subroutineKeywordList:
            self.compileSubroutineDec()
            print(f'showing symbol table for subroutine: "{self.subroutineSymbolTable.scopeName}"')
            print(f'{self.subroutineSymbolTable.scopeTable}\n')
            self.subroutineSymbolTable.reset()

        self.eat(expected=["}"])
        self.updateIndents(-1)

        self.f.write(f'{self.indents}</class>\n')

        print(f'showing symbol table for class: "{self.classSymbolTable.scopeName}"')
        print(self.classSymbolTable.scopeTable)

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

        self.classSymbolTable.curKind = self.tknzr.getCurTokenValue()
        self.eat(expected=["static", "field"], skip_st_def=True)
        # how to handle className ?? -> just eat as is
        self.classSymbolTable.curType = self.tknzr.getCurTokenValue()
        self.eat(skip_st_def=True)
        # self.eat(expected=["int", "char", "boolean", "className"])
        # how to handle varName(s) --> just eat as is
        while self.tknzr.getCurTokenValue() != ";":
            self.eat()
        
        self.eat(expected=[";"])

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

        # subroutine type:
        self.eat(expected=["constructor", "function", "method"])
        
        # return type
        self.eat(skip_st_def=True)
        
        # subroutine name
        self.subroutineSymbolTable.updateScopeName(self.tknzr.getCurTokenValue())
        self.eat(skip_st_def=True)
        
        # subroutine arguments
        self.eat(expected=['('])
        self.compileParameterList()
        self.eat(expected=[')'])

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

        self.subroutineSymbolTable.curKind = "argument"
        while self.tknzr.getCurTokenValue() != ')':
            # kind for all will be arg
            # type name ','? until token == ')'
            self.subroutineSymbolTable.curType = self.tknzr.getCurTokenValue()
            self.eat(skip_st_def=True)
            self.eat()
            if self.tknzr.getCurTokenValue() != ')':
                self.eat(expected=[','])

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

        self.eat(expected=["{"])
        
        while self.tknzr.getCurTokenValue() in ["static", "field", "var"]:
            self.compileVarDec()

        self.compileStatements()
        
        self.eat(expected=["}"])

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

        # var
        self.eat(expected=["var"])
        
        # type
        self.subroutineSymbolTable.curType = self.tknzr.getCurTokenValue()
        self.eat(skip_st_def=True)
        
        self.subroutineSymbolTable.curKind = "local"
        while self.tknzr.getCurTokenValue() != ';':
            self.eat()

        self.eat(expected=[";"])

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
                    break
            else:
                print("compile statements, statement starts with keyword check failed")
                print(f'compile statements, statement expected to start with keyword: current token: "{self.tknzr.getCurTokenValue()}" current token type: "{self.tknzr.getCurTokenType()}"')
                break

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

        self.eat(expected=["let"])

        # this is where you pop the expression result to:
        dest = self.tknzr.getCurTokenValue()
        self.eat()
        if self.tknzr.getCurTokenValue() == '[':
            self.eat()
            self.compileExpression()
            self.eat()
        
        self.eat(expected=["="])
        
        # this should result in value on top of stack that will be popped to varName you are assigning
        self.compileExpression()

        if dest in self.subroutineSymbolTable.scopeTable:
            st_info = [self.subroutineSymbolTable.typeOf(dest), self.subroutineSymbolTable.kindOf(dest), self.subroutineSymbolTable.indexOf(dest)]  if dest in self.subroutineSymbolTable.scopeTable else None
        elif dest in self.classSymbolTable.scopeTable:
            st_info = [self.classSymbolTable.typeOf(dest), self.classSymbolTable.kindOf(dest), self.classSymbolTable.indexOf(dest)]  if dest in self.classSymbolTable.scopeTable else None
        else:
            st_info = None
        if st_info:
            # self.VMWriter.f.write(f'{dest}\n')
            self.VMWriter.writePop(st_info[1], st_info[2])
        else:
            print("let statement assignment error, no symbol table info")
        
        self.eat(expected=[";"])

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

        self.eat(expected=["if"])
        self.eat(expected=["("])
        self.compileExpression()
        self.eat(expected=[")"])
        self.eat(expected=["{"])
        self.compileStatements()
        self.eat(expected=["}"])

        # check for else statement
        if self.tknzr.getCurTokenValue() == "else":
            self.eat(expected=["else"])
            self.eat(expected=["{"])
            self.compileStatements()
            self.eat(expected=["}"])

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
        
        self.eat(expected=["while"])
        self.eat(expected=["("])
        self.compileExpression()
        self.eat(expected=[")"])
        self.eat(expected=["{"])
        self.compileStatements()
        self.eat(expected=["}"])

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

        self.eat(expected=["do"])

        self.compileSubroutineCall()
        
        self.eat(expected=[";"])
        
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

        self.eat(expected=["return"])

        # if have expression here, need to push result of that to stack (so it can be returned)
        # if no value/expression --> push constant 0, then return that
        if self.tknzr.getCurTokenValue() != ';':
            self.compileExpression()
        else:
            self.VMWriter.writePush('constant', 0)

        self.VMWriter.writeReturn()
        self.eat(expected=[";"])

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
            op = self.tknzr.getCurTokenValue()
            self.eat()
            self.compileTerm()
            self.VMWriter.writeArithmetic(op)

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

        # term: intergerConstant | stringConstant | keywordConstant | varName | 
        # varName '[' expression ']' | subroutineCall | '( expression ')' | 
        # unaryOp term

        self.f.write(f'{self.indents}<term>\n')
        self.updateIndents(1)
        
        # get token type?  keyword, symbol, string_constant, int_constant, identifier

        # how to id subroutine, unary op?

        cur = self.tknzr.getCurTokenValue()
        hasNext, nx = self.tknzr.peek()
        next, nextType = nx
        
        if cur == '(':
            self.eat(expected=['('])
            self.compileExpression()
            self.eat(expected=[')'])
        elif hasNext and next == '[':
            self.eat()
            self.eat('[')
            self.compileExpression()
            self.eat(']')
        elif cur in self.unaryOpList:
            self.eat()
            self.compileTerm()
        elif cur in self.kwdConstList:
            self.eat()
        elif hasNext and next == '(':
            self.compileSubroutineCall()
        elif hasNext and next == '.':
            # self.eat(skip_st_def=True)
            # self.eat(expected=['.'])
            self.compileSubroutineCall()
        else:
            # print(f'next: {next}, cur: {self.tknzr.getCurTokenValue()}')
            currentToken = cur
            if currentToken in self.subroutineSymbolTable.scopeTable:
                st_info = [self.subroutineSymbolTable.typeOf(currentToken), self.subroutineSymbolTable.kindOf(currentToken), self.subroutineSymbolTable.indexOf(currentToken)]  if currentToken in self.subroutineSymbolTable.scopeTable else None
            elif currentToken in self.classSymbolTable.scopeTable:
                st_info = [self.classSymbolTable.typeOf(currentToken), self.classSymbolTable.kindOf(currentToken), self.classSymbolTable.indexOf(currentToken)]  if currentToken in self.classSymbolTable.scopeTable else None
            else:
                st_info = None
            if st_info:
                # self.VMWriter.f.write(f'{cur}\n')
                self.VMWriter.writePush(st_info[1], st_info[2])
            else:
                # either string/value const -> can just push value directly to stack -> how?
                # self.VMWriter.f.write(f'{cur}\n')
                self.VMWriter.writePush('constant', cur)

            self.eat()
        
        self.updateIndents(-1)
        self.f.write(f'{self.indents}</term>\n')
        
        return

    """
    Compiles a (possibly empty) comma-separated list of expressions.
    Returns the number of expressions in the list (per the book’s API).
    """
    def compileExpressionList(self):
        # expression list: (expression (',' expression)* )?

        self.f.write(f'{self.indents}<expressionList>\n')
        self.updateIndents(1)

        # while self.tknzr.getCurTokenValue() != ')':
        #     self.compileExpression()
        #     if self.tknzr.getCurTokenValue() != ')':
        #         self.eat(expected=[','])

        # is there an expression? if not exit w/o expression tags
        # if cur token is an a term (then is expression else skip)
        # term: identifier, unaryOp, '('
        count = 0
        while (self.tknzr.getCurTokenType() in ['identifier', 'stringConstant', 'integerConstant']) or (self.tknzr.getCurTokenValue() in self.kwdConstList) or (self.tknzr.getCurTokenValue() in self.unaryOpList) or (self.tknzr.getCurTokenValue() == '('):
            # is term, else skip 
            self.compileExpression()
            count += 1
            if self.tknzr.getCurTokenValue() == ',':
                self.eat(expected=[','])
            else:
                break

        self.updateIndents(-1)
        self.f.write(f'{self.indents}</expressionList>\n')

        return count
    

    """
    Compiles subroutine call
    """
    def compileSubroutineCall(self):
        # subroutineName '(' expressionList ')' | (className | varName) '.' subroutineName '(' expressionList ')'

        # eat subroutine name w/o adding to symbol table
        name = self.tknzr.getCurTokenValue()
        self.eat(skip_st_def=True)

        if self.tknzr.getCurTokenValue() == '.':
            self.eat(expected=['.'])
            name = name + "."
            name = name + self.tknzr.getCurTokenValue()
            self.eat(skip_st_def=True)

        self.eat(expected=['('])

        # need to pull nArgs from here
        nArgs = self.compileExpressionList()

        self.eat(expected=[')'])

        # for testing:
        # nArgs = 1
        self.VMWriter.writeCall(name, nArgs)

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
        outputFileName = baseName + "_test" + ".xml"
        vmOutputFileName = baseName + ".vm"
        print(f'\nXML Output File: {outputFileName}\nVM OutputFile: {vmOutputFileName}\n')
        
        indent_level = 0
        with open(outputFileName, "w") as f, open(vmOutputFileName, "w") as f_vm:
            self.compilation_engine = CompilationEngine(self.tokenizer, indent_level, f, f_vm)
            
            self.compilation_engine.compileClass()


class SymbolTable():
    def __init__(self):
        """
        key: "name"  values: type, kind, # of kind
        sub dict with count of kind?
        kind: static, field, argument, var
        """

        self.scopeName = None

        self.scopeTable = {}
        self.scopeTableKindCount = defaultdict(int)
        
        self.curType = None
        self.curKind = None

        return
    
    def reset(self):
        self.scopeTable = {}
        self.scopeTableKindCount = defaultdict(int)


    def updateScopeName(self, scope_name):
        self.scopeName = scope_name


    def define(self, name, type, kind):
        """
        adds new variable to symbol table
        
        :param self: current symbol table object
        :param name: new variabel name
        :param type: new variable's type
        :param kind: new variable's kind (static, field, argument, var)
        :param isSubRoutineVar: boolean if new var should be added to subroutine or class table
        """
        if name != self.scopeName:        
            count = self.scopeTableKindCount[kind]
            self.scopeTable[name] = {"type": type, "kind": kind, "index": count}
            self.scopeTableKindCount[kind] += 1

        return


    def varCount(self, kind):
        return self.scopeTableKindCount[kind]
    

    def kindOf(self, name):
        return self.scopeTable[name]["kind"] if name in self.scopeTable else None


    def typeOf(self, name):
        return self.scopeTable[name]["type"]


    def indexOf(self, name):
        return self.scopeTable[name]["index"]


class VMWriter():
    def __init__(self, file):
        self.f = file

        # how to diff sub vs. neg???
        self.command_lookup = {"+": "add", "-": "sub", ">": "gt", "<": "lt", "/": "call Math.divide 2", "*": "call Math.multiply 2"}

        return

    # accessing a value from variable or pushing value to stack for operation
    def writePush(self, segment, index):
        vm_code = [f'push {segment} {index}']        
        # print(vm_code)
        for line in vm_code:
            output = f'{line}\n'
            self.f.write(str(output))

        return

    # taking value from stack and putting to variable, assigning result to var from stack
    def writePop(self, segment, index):
        vm_code = [f'pop {segment} {index}']        
        # print(vm_code)
        for line in vm_code:
            output = f'{line}\n'
            self.f.write(str(output))
        
        return
    

    def writeArithmetic(self, command):
        error = "arithmetic lookup error"
        vm_code = [f'{self.command_lookup[command] if command in self.command_lookup else error}']        
        # print(vm_code)
        for line in vm_code:
            output = f'{line}\n'
            self.f.write(str(output))
        return


    def writeLabel(self, label):

        return


    def writeGoto(self, label):

        return


    def writeIf(self, label):

        return
    

    def writeCall(self, name, nArgs):
        error = "write call error"
        vm_code = [f'call {name} {nArgs}']        
        # print(vm_code)
        for line in vm_code:
            output = f'{line}\n'
            self.f.write(str(output))
        return
    

    def writeFunction(self, name, nArgs):

        return


    def writeReturn(self):
        vm_code = ['return']
        # print(vm_code)
        for line in vm_code:
            output = f'{line}\n'
            self.f.write(str(output))

        return
    

    def close(self):

        return


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