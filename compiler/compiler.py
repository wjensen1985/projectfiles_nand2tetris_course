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
    def __init__(self, input_stream, output_stream):
        self.tokenizer = input_stream
        self.out = output_stream
        
        return

    # ------------------------------------------------------------
    # Top-level and declarations
    # ------------------------------------------------------------

    """
    
    """
    def eat(self):
        currentToken = "test"
        if (currentToken is not str):
            # error
            return False
        else:
            # advance tokenizer

            pass

        return True

    """
    Compiles a complete class.
    Entry point called by the analyzer; handles 'class ... { ... }'.
    """
    def compileClass(self):
        
        return

    """
    Compiles a static variable declaration or a field declaration.
    Handles sequences like: ('static'|'field') type varName (',' varName)* ';'
    """
    def compileClassVarDec(self):
        
        return

    """
    Compiles a complete method, function, or constructor declaration.
    Handles header ('constructor'|'function'|'method' ...) and delegates body.
    """
    def compileSubroutine(self):
        
        return

    """
    Compiles a (possibly empty) parameter list.
    Does not handle the enclosing parentheses tokens '(' and ')'.
    """
    def compileParameterList(self):
        
        return

    """
    Compiles a subroutine's body.
    Handles '{' varDec* statements '}'.
    """
    def compileSubroutineBody(self):
        
        return

    """
    Compiles a local variable declaration.
    Handles 'var' type varName (',' varName)* ';'
    """
    def compileVarDec(self):
        
        return

    """
    Compiles a sequence of statements.
    Does not handle the enclosing curly braces '{' and '}'.
    """
    def compileStatements(self):
        
        return

    # ------------------------------------------------------------
    # Statements
    # ------------------------------------------------------------

    """
    Compiles a let statement.
    Handles: 'let' varName ('[' expression ']')? '=' expression ';'
    """
    def compileLet(self):
        
        return

    """
    Compiles an if statement, possibly with a trailing else clause.
    Handles: 'if' '(' expression ')' '{' statements '}' ('else' '{' statements '}')?
    """
    def compileIf(self):
        
        return

    """
    Compiles a while statement.
    Handles: 'while' '(' expression ')' '{' statements '}'
    """
    def compileWhile(self):
        
        return

    """
    Compiles a do statement (a subroutine call used as a statement).
    Handles: 'do' subroutineCall ';'
    """
    def compileDo(self):
        
        return

    """
    Compiles a return statement.
    Handles: 'return' expression? ';'
    """
    def compileReturn(self):
        
        return

    # ------------------------------------------------------------
    # Expressions
    # ------------------------------------------------------------

    """
    Compiles an expression.
    Handles: term (op term)*
    """
    def compileExpression(self):
       
        return

    """
    Compiles a term.
    If the current token is an identifier, resolves whether it's a varName,
    an array entry, or a subroutine call. Also handles constants, unary ops,
    and parenthesized expressions.
    """
    def compileTerm(self):
        
        return

    """
    Compiles a (possibly empty) comma-separated list of expressions.
    Returns the number of expressions in the list (per the book’s API).
    """
    def compileExpressionList(self):
        
        return


class JackAnalyzer():
    def __init__(self, inputPaths):
        self.filesList = inputPaths
        self.specialOutput = {'<': '&lt;', '>': '&gt;', '"': '&quot;', '&': '&amp;'}


    def analyze(self):
        if len(self.filesList) > 1:
            # folder mode
            print(f'\nTranslating all files: {self.filesList}\n')

            # for each file in list:
            #       Translate
            #           1. tokenizer call
            #           2. compilation engine -> compile class    

        else:
            # single file

            print(f'\nTranslating single file: {self.filesList[0]}\n')
            tokenizer = Tokenizer(self.filesList[0])

            baseName, _ = os.path.splitext(self.filesList[0])
            print(baseName)
            outputFileName = baseName + "_test" + ".xml"



            with open(outputFileName, "w") as f:
                line = f'<tokens>\n'
                f.write(line)
                while tokenizer.hasMoreTokens():
                    token = tokenizer.getCurTokenValue()
                    tokenType = tokenizer.getCurTokenType()
                    line = f'<{tokenType}> {self.specialOutput[token] if token in self.specialOutput else token} </{tokenType}>\n'
                    f.write(line)
                    tokenizer.advance()
                line = f'</tokens>\n'
                f.write(line)


def main(files):
    print("\nrunning main")

    analyzer = JackAnalyzer(files)
    analyzer.analyze()


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