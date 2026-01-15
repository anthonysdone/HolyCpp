import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pytest
from src.lexer import *

def test_signle_tokens():
    lexer = Lexer("+ - * / % & | ^ ~ ! < > = ` ( ) { } [ ] ; , . : ?")
    tokens = lexer.tokenize()
    expected = [
        TokenType.PLUS, TokenType.MINUS, TokenType.STAR, TokenType.SLASH,
        TokenType.PERCENT, TokenType.AMPERSAND, TokenType.PIPE, TokenType.CARET,
        TokenType.TILDE, TokenType.BANG, TokenType.LESS, TokenType.GREATER,
        TokenType.EQUAL, TokenType.BACKTICK, TokenType.LPAREN, TokenType.RPAREN,
        TokenType.LBRACE, TokenType.RBRACE, TokenType.LBRACKET, TokenType.RBRACKET,
        TokenType.SEMICOLON, TokenType.COMMA, TokenType.DOT, TokenType.COLON,
        TokenType.QUESTION, TokenType.EOF
    ]
    assert [t.type for t in tokens] == expected

def test_double_tokens(): 
    lexer = Lexer("++ -- ")