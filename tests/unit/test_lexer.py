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
    lexer = Lexer("++ -- << >> <= >= == != && || ^^ += -= *= /= -> ...")
    tokens = lexer.tokenize()
    expected = [
        TokenType.PLUS_PLUS, TokenType.MINUS_MINUS, TokenType.LEFT_SHIFT,
        TokenType.RIGHT_SHIFT, TokenType.LESS_EQUAL, TokenType.GREATER_EQUAL,
        TokenType.EQUAL_EQUAL, TokenType.BANG_EQUAL, TokenType.AMP_AMP,
        TokenType.PIPE_PIPE, TokenType.CARET_CARET, TokenType.PLUS_EQUAL,
        TokenType.MINUS_EQUAL, TokenType.STAR_EQUAL, TokenType.SLASH_EQUAL,
        TokenType.ARROW, TokenType.ELLIPSIS, TokenType.EOF
    ]
    assert [t.type for t in tokens] == expected

def test_keywords_vs_identifiers():
    lexer = Lexer("I64 if else myVar U0 class _myVar2")
    tokens = lexer.tokenize()
    assert tokens[0].type == TokenType.I64
    assert tokens[1].type == TokenType.IF
    assert tokens[2].type == TokenType.ELSE
    assert tokens[3].type == TokenType.IDENTIFIER and tokens[3].value == "myVar"
    assert tokens[4].type == TokenType.U0
    assert tokens[5].type == TokenType.CLASS
    assert tokens[6].type == TokenType.IDENTIFIER and tokens[6].value == "_myVar2"
    
def test_number_literals():
    lexer = Lexer("42 0xFF 3.14 2.5e10 0x1A2B")
    tokens = lexer.tokenize()
    assert tokens[0].type == TokenType.INTEGER and tokens[0].value == 42
    assert tokens[1].type == TokenType.INTEGER and tokens[1].value == 0xFF
    assert tokens[2].type == TokenType.FLOAT and tokens[2].value == 3.14
    assert tokens[3].type == TokenType.FLOAT and tokens[3].value == 2.5e10
    assert tokens[4].type == TokenType.INTEGER and tokens[4].value == 0x1A2B

def test_string_literals():
    lexer = Lexer(r'"Hello\nWorld" "Tab\there" "Quote\"Test"')
    tokens = lexer.tokenize()
    assert tokens[0].type == TokenType.STRING and tokens[0].value == "Hello\nWorld"
    assert tokens[1].type == TokenType.STRING and tokens[1].value == "Tab\there"
    assert tokens[2].type == TokenType.STRING and tokens[2].value == 'Quote"Test'

def test_char_literals():
    lexer = Lexer("'A' 'ABC' '\\n' '\\t'")
    tokens = lexer.tokenize()
    assert tokens[0].type == TokenType.CHAR and tokens[0].value == 0x41
    assert tokens[1].type == TokenType.CHAR and tokens[1].value == 0x434241
    assert tokens[2].type == TokenType.CHAR and tokens[2].value == ord('\n')
    assert tokens[3].type == TokenType.CHAR and tokens[3].value == ord('\t')

def test_comments():
    lexer = Lexer("x // line comment\ny /* block */ z")
    tokens = lexer.tokenize()
    assert [t.value for t in tokens if t.type == TokenType.IDENTIFIER] == ["x", "y", "z"]

def test_whitespace_handling():
    lexer = Lexer("  x\t\ty  \n\n  z  ")
    tokens = lexer.tokenize()
    assert [t.value for t in tokens if t.type == TokenType.IDENTIFIER] == ["x", "y", "z"]

def test_sample_program():
    source = """
    class Circle {
        F64 x, y, radius;
    };

    U0 Circle->Area() { // Calculate area
        return 3.14 * this->radius`2; 
    }

    Circle c;
    c.radius = 5.0;
    "Area: %f\\n", c.Area();
    """
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    
    token_types = [t.type for t in tokens]
    assert TokenType.CLASS in token_types
    assert TokenType.LBRACE in token_types
    assert TokenType.RBRACE in token_types
    assert TokenType.F64 in token_types
    assert TokenType.IDENTIFIER in token_types
    assert TokenType.ARROW in token_types
    assert TokenType.BACKTICK in token_types  # power operator
    assert TokenType.STAR in token_types
    assert TokenType.STRING in token_types
    assert TokenType.FLOAT in token_types
    assert TokenType.LPAREN in token_types
    assert TokenType.RPAREN in token_types
    assert TokenType.SEMICOLON in token_types
    assert TokenType.RETURN in token_types
    assert TokenType.THIS in token_types
    assert TokenType.DOT in token_types
    assert TokenType.COMMA in token_types
    assert TokenType.EOF in token_types
    
    identifiers = [t.value for t in tokens if t.type == TokenType.IDENTIFIER]
    assert "Circle" in identifiers
    assert "x" in identifiers
    assert "y" in identifiers
    assert "radius" in identifiers
    assert "Area" in identifiers
    assert "c" in identifiers

    floats = [t.value for t in tokens if t.type == TokenType.FLOAT]
    assert 3.14 in floats
    assert 5.0 in floats
    integers = [t.value for t in tokens if t.type == TokenType.INTEGER]
    assert 2 in integers  # from radius`2
    strings = [t.value for t in tokens if t.type == TokenType.STRING]
    assert "Area: %f\n" in strings
    
    assert any(t.type == TokenType.CLASS for t in tokens)
    assert any(t.type == TokenType.U0 for t in tokens)
    assert any(t.type == TokenType.F64 for t in tokens)
    assert any(t.type == TokenType.RETURN for t in tokens)
    assert any(t.type == TokenType.THIS for t in tokens)

