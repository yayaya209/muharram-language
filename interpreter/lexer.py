"""
Muharram Language Lexer
Tokenizes Muharram source code into tokens
"""

from enum import Enum, auto
from dataclasses import dataclass
from typing import List, Optional

class TokenType(Enum):
    # Literals
    INTEGER = auto()
    FLOAT = auto()
    STRING = auto()
    BOOL = auto()
    NIL = auto()
    
    # Keywords
    VAR = auto()
    CLASS = auto()
    PROPERTY = auto()
    METHOD = auto()
    IF = auto()
    ELSE = auto()
    WHILE = auto()
    FOR = auto()
    RETURN = auto()
    END = auto()
    TRUE = auto()
    FALSE = auto()
    
    # Identifiers and operators
    IDENTIFIER = auto()
    PLUS = auto()
    MINUS = auto()
    STAR = auto()
    SLASH = auto()
    PERCENT = auto()
    EQUAL = auto()
    EQUAL_EQUAL = auto()
    BANG_EQUAL = auto()
    LESS = auto()
    LESS_EQUAL = auto()
    GREATER = auto()
    GREATER_EQUAL = auto()
    DOT = auto()
    COMMA = auto()
    LPAREN = auto()
    RPAREN = auto()
    
    # Special
    EOF = auto()
    NEWLINE = auto()

@dataclass
class Token:
    type: TokenType
    lexeme: str
    literal: Optional[str] = None
    line: int = 1
    column: int = 1

class Lexer:
    def __init__(self, source: str):
        self.source = source
        self.pos = 0
        self.line = 1
        self.column = 1
        self.tokens: List[Token] = []
        self.keywords = {
            'var': TokenType.VAR,
            'class': TokenType.CLASS,
            'property': TokenType.PROPERTY,
            'method': TokenType.METHOD,
            'if': TokenType.IF,
            'else': TokenType.ELSE,
            'while': TokenType.WHILE,
            'for': TokenType.FOR,
            'return': TokenType.RETURN,
            'end': TokenType.END,
            'true': TokenType.TRUE,
            'false': TokenType.FALSE,
            'nil': TokenType.NIL,
        }

    def tokenize(self) -> List[Token]:
        while self.pos < len(self.source):
            self._skip_whitespace_and_comments()
            if self.pos >= len(self.source):
                break
            
            char = self.source[self.pos]
            
            if char == '\n':
                self.tokens.append(Token(TokenType.NEWLINE, '\n', line=self.line, column=self.column))
                self.pos += 1
                self.line += 1
                self.column = 1
            elif char.isdigit():
                self._tokenize_number()
            elif char.isalpha() or char == '_':
                self._tokenize_identifier()
            elif char == '"':
                self._tokenize_string()
            elif char == '+':
                self.tokens.append(Token(TokenType.PLUS, '+', line=self.line, column=self.column))
                self.pos += 1
                self.column += 1
            elif char == '-':
                self.tokens.append(Token(TokenType.MINUS, '-', line=self.line, column=self.column))
                self.pos += 1
                self.column += 1
            elif char == '*':
                self.tokens.append(Token(TokenType.STAR, '*', line=self.line, column=self.column))
                self.pos += 1
                self.column += 1
            elif char == '/':
                self.tokens.append(Token(TokenType.SLASH, '/', line=self.line, column=self.column))
                self.pos += 1
                self.column += 1
            elif char == '%':
                self.tokens.append(Token(TokenType.PERCENT, '%', line=self.line, column=self.column))
                self.pos += 1
                self.column += 1
            elif char == '=':
                if self._peek() == '=':
                    self.tokens.append(Token(TokenType.EQUAL_EQUAL, '==', line=self.line, column=self.column))
                    self.pos += 2
                    self.column += 2
                else:
                    self.tokens.append(Token(TokenType.EQUAL, '=', line=self.line, column=self.column))
                    self.pos += 1
                    self.column += 1
            elif char == '!':
                if self._peek() == '=':
                    self.tokens.append(Token(TokenType.BANG_EQUAL, '!=', line=self.line, column=self.column))
                    self.pos += 2
                    self.column += 2
            elif char == '<':
                if self._peek() == '=':
                    self.tokens.append(Token(TokenType.LESS_EQUAL, '<=', line=self.line, column=self.column))
                    self.pos += 2
                    self.column += 2
                else:
                    self.tokens.append(Token(TokenType.LESS, '<', line=self.line, column=self.column))
                    self.pos += 1
                    self.column += 1
            elif char == '>':
                if self._peek() == '=':
                    self.tokens.append(Token(TokenType.GREATER_EQUAL, '>=', line=self.line, column=self.column))
                    self.pos += 2
                    self.column += 2
                else:
                    self.tokens.append(Token(TokenType.GREATER, '>', line=self.line, column=self.column))
                    self.pos += 1
                    self.column += 1
            elif char == '.':
                self.tokens.append(Token(TokenType.DOT, '.', line=self.line, column=self.column))
                self.pos += 1
                self.column += 1
            elif char == ',':
                self.tokens.append(Token(TokenType.COMMA, ',', line=self.line, column=self.column))
                self.pos += 1
                self.column += 1
            elif char == '(':
                self.tokens.append(Token(TokenType.LPAREN, '(', line=self.line, column=self.column))
                self.pos += 1
                self.column += 1
            elif char == ')':
                self.tokens.append(Token(TokenType.RPAREN, ')', line=self.line, column=self.column))
                self.pos += 1
                self.column += 1
            else:
                self.pos += 1
                self.column += 1

        self.tokens.append(Token(TokenType.EOF, '', line=self.line, column=self.column))
        return self.tokens

    def _skip_whitespace_and_comments(self):
        while self.pos < len(self.source):
            char = self.source[self.pos]
            if char in ' \t\r':
                self.pos += 1
                self.column += 1
            elif char == '#':
                # Skip comment until end of line
                while self.pos < len(self.source) and self.source[self.pos] != '\n':
                    self.pos += 1
            else:
                break

    def _tokenize_number(self):
        start = self.pos
        start_col = self.column
        while self.pos < len(self.source) and self.source[self.pos].isdigit():
            self.pos += 1
            self.column += 1

        if self.pos < len(self.source) and self.source[self.pos] == '.':
            self.pos += 1
            self.column += 1
            while self.pos < len(self.source) and self.source[self.pos].isdigit():
                self.pos += 1
                self.column += 1
            literal = self.source[start:self.pos]
            self.tokens.append(Token(TokenType.FLOAT, literal, literal, line=self.line, column=start_col))
        else:
            literal = self.source[start:self.pos]
            self.tokens.append(Token(TokenType.INTEGER, literal, literal, line=self.line, column=start_col))

    def _tokenize_identifier(self):
        start = self.pos
        start_col = self.column
        while self.pos < len(self.source) and (self.source[self.pos].isalnum() or self.source[self.pos] == '_'):
            self.pos += 1
            self.column += 1

        text = self.source[start:self.pos]
        token_type = self.keywords.get(text, TokenType.IDENTIFIER)
        self.tokens.append(Token(token_type, text, line=self.line, column=start_col))

    def _tokenize_string(self):
        start_col = self.column
        self.pos += 1  # Skip opening quote
        self.column += 1
        start = self.pos
        
        while self.pos < len(self.source) and self.source[self.pos] != '"':
            if self.source[self.pos] == '\\':
                self.pos += 2
                self.column += 2
            else:
                self.pos += 1
                self.column += 1

        value = self.source[start:self.pos]
        self.pos += 1  # Skip closing quote
        self.column += 1
        self.tokens.append(Token(TokenType.STRING, f'"{value}"', value, line=self.line, column=start_col))

    def _peek(self) -> str:
        if self.pos + 1 < len(self.source):
            return self.source[self.pos + 1]
        return '\0'
