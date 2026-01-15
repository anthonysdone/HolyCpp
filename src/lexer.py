from enum import Enum, auto
from dataclasses import dataclass
from typing import Optional, List

class TokenType(Enum): 
    
    INTEGER = auto()
    FLOAT = auto()
    STRING = auto()
    CHAR = auto()

    IDENTIFIER = auto()

    U0 = auto()
    I8 = auto()
    U8 = auto()
    I16 = auto()
    U16 = auto()
    I32 = auto()
    U32 = auto()
    I64 = auto()
    U64 = auto()
    F64 = auto()

    IF = auto()
    ELSE = auto()
    WHILE = auto()
    FOR = auto()
    SWITCH = auto()
    CASE = auto()
    DEFAULT = auto()
    BREAK = auto()
    GOTO = auto()
    RETURN = auto()
    TRY = auto()
    CATCH = auto()
    THROW = auto()

    CLASS = auto()
    UNION = auto()
    PUBLIC = auto()
    EXTERN = auto()
    IMPORT = auto()
    _EXTERN = auto()
    _IMPORT = auto()

    SIZEOF = auto()
    OFFSET = auto()
    STATIC = auto()
    NOREG = auto()
    REG = auto()
    THIS = auto()
    START = auto()
    END = auto()
    LOCK = auto()
    LASTCLASS = auto()

    PLUS = auto()
    MINUS = auto()
    STAR = auto()
    SLASH = auto()
    PERCENT = auto()
    AMPERSAND = auto()
    PIPE = auto()
    CARET = auto()
    TILDE = auto()
    BANG = auto()
    LESS = auto()
    GREATER = auto()
    EQUAL = auto()
    BACKTICK = auto()

    PLUS_PLUS = auto()
    MINUS_MINUS = auto()
    LEFT_SHIFT = auto()
    RIGHT_SHIFT = auto()
    LESS_EQUAL = auto()
    GREATER_EQUAL = auto()
    EQUAL_EQUAL = auto()
    BANG_EQUAL = auto()
    AMP_AMP = auto()
    PIPE_PIPE = auto()
    CARET_CARET = auto()
    PLUS_EQUAL = auto()
    MINUS_EQUAL = auto()
    STAR_EQUAL = auto()
    SLASH_EQUAL = auto()
    PERCENT_EQUAL = auto()
    AMP_EQUAL = auto()
    PIPE_EQUAL = auto()
    CARET_EQUAL = auto()
    LEFT_SHIFT_EQUAL = auto()
    RIGHT_SHIFT_EQUAL = auto()
    ARROW = auto()
    ELLIPSIS = auto()

    LPAREN = auto()
    RPAREN = auto()
    LBRACE = auto()
    RBRACE = auto()
    LBRACKET = auto()
    RBRACKET = auto()
    SEMICOLON = auto()
    COMMA = auto()
    DOT = auto()
    COLON = auto()
    QUESTION = auto()

    EOF = auto()
    NEWLINE = auto()

@dataclass 
class Token: 
    type: TokenType
    value: any
    line: int
    column: int

    def __repr__(self) -> str:
        return f"Token({self.type.name}, {self.value!r}, {self.line}:{self.column})"

class LexerError(Exception):
    def __init__(self, message, line, column): 
        self.message = message 
        self.line = line
        self.column = column
        super().__init__(f"Lexer error at {line}:{column}: {message}")

class Lexer: 
    KEYWORDS = {
        'U0': TokenType.U0,
        'I8': TokenType.I8,
        'U8': TokenType.U8,
        'I16': TokenType.I16,
        'U16': TokenType.U16,
        'I32': TokenType.I32,
        'U32': TokenType.U32,
        'I64': TokenType.I64,
        'U64': TokenType.U64,
        'F64': TokenType.F64,
        'if': TokenType.IF,
        'else': TokenType.ELSE,
        'while': TokenType.WHILE,
        'for': TokenType.FOR,
        'switch': TokenType.SWITCH,
        'case': TokenType.CASE,
        'default': TokenType.DEFAULT,
        'break': TokenType.BREAK,
        'goto': TokenType.GOTO,
        'return': TokenType.RETURN,
        'try': TokenType.TRY,
        'catch': TokenType.CATCH,
        'throw': TokenType.THROW,
        'class': TokenType.CLASS,
        'union': TokenType.UNION,
        'public': TokenType.PUBLIC,
        'extern': TokenType.EXTERN,
        'import': TokenType.IMPORT,
        '_extern': TokenType._EXTERN,
        '_import': TokenType._IMPORT,
        'sizeof': TokenType.SIZEOF,
        'offset': TokenType.OFFSET,
        'static': TokenType.STATIC,
        'noreg': TokenType.NOREG,
        'reg': TokenType.REG,
        'this': TokenType.THIS,
        'start': TokenType.START,
        'end': TokenType.END,
        'lock': TokenType.LOCK,
        'lastclass': TokenType.LASTCLASS,
    }

    def __init__(self, source): 
        self.source = source
        self.pos = 0
        self.line = 1
        self.column = 1
        self.length = len(source)

    def error(self, message) -> None:
        raise LexerError(message, self.line, self.column)
    
    def peek(self, offset=0) -> Optional[str]: 
        pos = self.pos + offset
        if pos < self.length: 
            return self.source[pos]
        return None
    
    def advance(self) -> Optional[str]:
        if self.pos >= self.length: 
            return None
        
        char = self.source[self.pos]
        self.pos += 1

        if char == "\n":
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        
        return char
    
    def skip_whitespace(self) -> None: 
        while self.peek() and self.peek() in " \t\r\n": 
            self.advance()
        
    def skip_line_comment(self) -> None:
        self.advance()
        self.advance()

        while self.peek() and self.peek() != "\n":
            self.advance()

    def skip_block_comment(self) -> None:
        self.advance()
        self.advance()

        while True: 
            if self.peek() is None: 
                self.error("Unterminated block comment")

            if self.peek() == "*" and self.peek(1) == "/":
                self.advance()
                self.advance()
                break

            self.advance()


    def read_number(self) -> Token:
        start_line = self.line
        start_column = self.column
        num_str = ""
        is_hex = False
        is_float = False

        if self.peek() == "0" and self.peek(1) in "xX":
            is_hex = True
            num_str += self.advance()
            num_str += self.advance()

        while self.peek(): 
            char = self.peek()

            if is_hex: 
                if char in "0123456789abcdefABCDEF": 
                    num_str += self.advance()
                else:
                    break
            else:
                if char.isdigit():
                    num_str += self.advance()
                elif char == "." and not is_float:
                    is_float = True
                    num_str += self.advance()
                elif char in "eE":
                    is_float = True
                    num_str += self.advance()
                    if self.peek() in "+-":
                        num_str += self.advance()
                else:
                    break
        
        try: 
            if is_hex: 
                value = int(num_str, 16)
                token_type = TokenType.INTEGER
            elif is_float:
                value = float(num_str)
                token_type = TokenType.FLOAT
            else:
                value = int(num_str)
                token_type = TokenType.INTEGER
        except ValueError:
            self.error(f"Invalid number literal: {num_str}")
        
        return Token(token_type, value, start_line, start_column)
            
    def read_string(self) -> Token: 
        start_line = self.line
        start_column = self.column

        self.advance()

        result = ""
        while True: 
            char = self.peek()
            
            if char is None:
                self.error("Unterminated string literal")
            
            if char == '"': 
                self.advance()
                break
            
            if char == "\\":
                self.advance()
                next_char = self.peek()

                if next_char is None: 
                    self.error("Unterminated string escape sequence")

                escape_map = {
                    'n': '\n',
                    't': '\t',
                    'r': '\r',
                    '\\': '\\',
                    '"': '"',
                    "'": "'",
                    '0': '\0',
                }

                if next_char in escape_map: 
                    result += escape_map[next_char]
                    self.advance()
                else: 
                    result += next_char
                    self.advance()
            else:
                result += char
                self.advance()
        
        return Token(TokenType.STRING, result, start_line, start_column)
    
    def read_char(self) -> Token: 
        start_line = self.line
        start_column = self.column

        self.advance()

        chars = []
        while True: 
            char = self.peek()

            if char is None: 
                self.error("Unterminated char literal")
            
            if char == "'":
                self.advance()
                break

            if char == "\\":
                self.advance()
                next_char = self.peek()

                if next_char is None:
                    self.error("Unterminated char escape sequence")

                escape_map = {
                    'n': '\n',
                    't': '\t',
                    'r': '\r',
                    '\\': '\\',
                    '"': '"',
                    "'": "'",
                    '0': '\0',
                }

                if next_char in escape_map:
                    chars.append(escape_map[next_char])
                    self.advance()
                else:
                    chars.append(next_char)
                    self.advance()
            else: 
                chars.append(char)
                self.advance()

        value = 0
        for i, c in enumerate(chars):
            if i >= 8: 
                break
            value |= (ord(c) & 0xFF) << (i * 8)

        return Token(TokenType.CHAR, value, start_line, start_column)
    
    def read_identifier(self) -> Token: 
        start_line = self.line
        start_column = self.column

        result = ""
        while self.peek() and (self.peek().isalnum() or self.peek() == "_"): 
            result += self.advance()
        
        token_type = self.KEYWORDS.get(result, TokenType.IDENTIFIER)

        return Token(token_type, result, start_line, start_column)
    
    def next_token(self) -> Token: 
        while True: 
            self.skip_whitespace()

            if self.peek() == "/" and self.peek(1) == "/": 
                self.skip_line_comment()
            elif self.peek() == "/" and self.peek(1) == "*":
                self.skip_block_comment()
            else:
                break
        
        if self.pos >= self.length: 
            return Token(TokenType.EOF, "", self.line, self.column)
        
        start_line = self.line
        start_column = self.column
        char = self.peek()

        if char.isdigit():
            return self.read_number()
        
        if char == '"':
            return self.read_string()
        
        if char == "'":
            return self.read_char()
    
        if char.isalpha() or char == "_":
            return self.read_identifier()

        self.advance()

        if char == '.' and self.peek() == '.' and self.peek(1) == '.':
            self.advance()
            self.advance()
            return Token(TokenType.ELLIPSIS, '...', start_line, start_column)
        
        if char == '<' and self.peek() == '<' and self.peek(1) == '=':
            self.advance()
            self.advance()
            return Token(TokenType.LEFT_SHIFT_EQUAL, '<<=', start_line, start_column)
        
        if char == '>' and self.peek() == '>' and self.peek(1) == '=':
            self.advance()
            self.advance()
            return Token(TokenType.RIGHT_SHIFT_EQUAL, '>>=', start_line, start_column)
        
        two_char_ops = {
            '++': TokenType.PLUS_PLUS,
            '--': TokenType.MINUS_MINUS,
            '<<': TokenType.LEFT_SHIFT,
            '>>': TokenType.RIGHT_SHIFT,
            '<=': TokenType.LESS_EQUAL,
            '>=': TokenType.GREATER_EQUAL,
            '==': TokenType.EQUAL_EQUAL,
            '!=': TokenType.BANG_EQUAL,
            '&&': TokenType.AMP_AMP,
            '||': TokenType.PIPE_PIPE,
            '^^': TokenType.CARET_CARET,
            '+=': TokenType.PLUS_EQUAL,
            '-=': TokenType.MINUS_EQUAL,
            '*=': TokenType.STAR_EQUAL,
            '/=': TokenType.SLASH_EQUAL,
            '%=': TokenType.PERCENT_EQUAL,
            '&=': TokenType.AMP_EQUAL,
            '|=': TokenType.PIPE_EQUAL,
            '^=': TokenType.CARET_EQUAL,
            '->': TokenType.ARROW,
        }

        two_char = char + (self.peek() or "")
        if two_char in two_char_ops:
            self.advance()
            return Token(two_char_ops[two_char], two_char, start_line, start_column)
        
        single_char_tokens = {
            '+': TokenType.PLUS,
            '-': TokenType.MINUS,
            '*': TokenType.STAR,
            '/': TokenType.SLASH,
            '%': TokenType.PERCENT,
            '&': TokenType.AMPERSAND,
            '|': TokenType.PIPE,
            '^': TokenType.CARET,
            '~': TokenType.TILDE,
            '!': TokenType.BANG,
            '<': TokenType.LESS,
            '>': TokenType.GREATER,
            '=': TokenType.EQUAL,
            '`': TokenType.BACKTICK,
            '(': TokenType.LPAREN,
            ')': TokenType.RPAREN,
            '{': TokenType.LBRACE,
            '}': TokenType.RBRACE,
            '[': TokenType.LBRACKET,
            ']': TokenType.RBRACKET,
            ';': TokenType.SEMICOLON,
            ',': TokenType.COMMA,
            '.': TokenType.DOT,
            ':': TokenType.COLON,
            '?': TokenType.QUESTION,
        }

        if char in single_char_tokens: 
            return Token(single_char_tokens[char], char, start_line, start_column)
        
        self.error(f"Unknown character: {char!r}")

    def tokenize(self) -> List[Token]: 
        tokens = []

        while True: 
            token = self.next_token()
            tokens.append(token)

            if token.type == TokenType.EOF:
                break

        return tokens