"""
Muharram Language Parser
Parses tokens into an Abstract Syntax Tree (AST)
"""

from dataclasses import dataclass
from typing import List, Optional
from enum import Enum, auto
from lexer import Token, TokenType

class NodeType(Enum):
    PROGRAM = auto()
    VAR_DECL = auto()
    CLASS_DECL = auto()
    PROPERTY = auto()
    METHOD = auto()
    BLOCK = auto()
    IF_STMT = auto()
    WHILE_STMT = auto()
    RETURN_STMT = auto()
    EXPR_STMT = auto()
    BINARY_OP = auto()
    UNARY_OP = auto()
    CALL = auto()
    GET_PROPERTY = auto()
    SET_PROPERTY = auto()
    IDENTIFIER = auto()
    LITERAL = auto()

@dataclass
class ASTNode:
    node_type: NodeType
    value: Optional[str] = None
    children: List['ASTNode'] = None
    properties: dict = None

    def __post_init__(self):
        if self.children is None:
            self.children = []
        if self.properties is None:
            self.properties = {}

class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0

    def parse(self) -> ASTNode:
        statements = []
        while not self._is_at_end():
            self._skip_newlines()
            if not self._is_at_end():
                stmt = self._parse_statement()
                if stmt:
                    statements.append(stmt)
        return ASTNode(NodeType.PROGRAM, children=statements)

    def _parse_statement(self) -> Optional[ASTNode]:
        self._skip_newlines()
        
        if self._check(TokenType.VAR):
            return self._parse_var_declaration()
        elif self._check(TokenType.CLASS):
            return self._parse_class_declaration()
        elif self._check(TokenType.IF):
            return self._parse_if_statement()
        elif self._check(TokenType.WHILE):
            return self._parse_while_statement()
        elif self._check(TokenType.RETURN):
            return self._parse_return_statement()
        else:
            return self._parse_expression_statement()

    def _parse_var_declaration(self) -> ASTNode:
        self._advance()  # consume 'var'
        name = self._advance().lexeme
        self._consume(TokenType.EQUAL, "Expected '=' in variable declaration")
        expr = self._parse_expression()
        self._skip_newlines()
        return ASTNode(NodeType.VAR_DECL, value=name, children=[expr])

    def _parse_class_declaration(self) -> ASTNode:
        self._advance()  # consume 'class'
        name = self._advance().lexeme
        self._skip_newlines()
        
        members = []
        while not self._check(TokenType.END) and not self._is_at_end():
            self._skip_newlines()
            if self._check(TokenType.PROPERTY):
                members.append(self._parse_property())
            elif self._check(TokenType.METHOD):
                members.append(self._parse_method())
            else:
                self._advance()
        
        self._consume(TokenType.END, "Expected 'end' after class body")
        self._skip_newlines()
        
        node = ASTNode(NodeType.CLASS_DECL, value=name, children=members)
        return node

    def _parse_property(self) -> ASTNode:
        self._advance()  # consume 'property'
        name = self._advance().lexeme
        self._skip_newlines()
        return ASTNode(NodeType.PROPERTY, value=name)

    def _parse_method(self) -> ASTNode:
        self._advance()  # consume 'method'
        name = self._advance().lexeme
        
        params = []
        if self._check(TokenType.LPAREN):
            self._advance()  # consume '('
            while not self._check(TokenType.RPAREN):
                params.append(self._advance().lexeme)
                if self._check(TokenType.COMMA):
                    self._advance()
            self._consume(TokenType.RPAREN, "Expected ')'")
        
        self._skip_newlines()
        
        body = []
        while not self._check(TokenType.END) and not self._is_at_end():
            self._skip_newlines()
            if not self._check(TokenType.END):
                stmt = self._parse_statement()
                if stmt:
                    body.append(stmt)
        
        self._consume(TokenType.END, "Expected 'end' after method body")
        self._skip_newlines()
        
        node = ASTNode(NodeType.METHOD, value=name, children=body)
        node.properties['params'] = params
        return node

    def _parse_if_statement(self) -> ASTNode:
        self._advance()  # consume 'if'
        condition = self._parse_expression()
        self._skip_newlines()
        
        then_body = []
        while not self._check(TokenType.ELSE) and not self._check(TokenType.END):
            self._skip_newlines()
            if not self._check(TokenType.ELSE) and not self._check(TokenType.END):
                stmt = self._parse_statement()
                if stmt:
                    then_body.append(stmt)
        
        else_body = []
        if self._check(TokenType.ELSE):
            self._advance()
            self._skip_newlines()
            while not self._check(TokenType.END):
                self._skip_newlines()
                if not self._check(TokenType.END):
                    stmt = self._parse_statement()
                    if stmt:
                        else_body.append(stmt)
        
        self._consume(TokenType.END, "Expected 'end' after if statement")
        self._skip_newlines()
        
        node = ASTNode(NodeType.IF_STMT, children=[condition] + then_body + else_body)
        node.properties['then_count'] = len(then_body)
        return node

    def _parse_while_statement(self) -> ASTNode:
        self._advance()  # consume 'while'
        condition = self._parse_expression()
        self._skip_newlines()
        
        body = []
        while not self._check(TokenType.END):
            self._skip_newlines()
            if not self._check(TokenType.END):
                stmt = self._parse_statement()
                if stmt:
                    body.append(stmt)
        
        self._consume(TokenType.END, "Expected 'end' after while body")
        self._skip_newlines()
        
        return ASTNode(NodeType.WHILE_STMT, children=[condition] + body)

    def _parse_return_statement(self) -> ASTNode:
        self._advance()  # consume 'return'
        expr = self._parse_expression()
        self._skip_newlines()
        return ASTNode(NodeType.RETURN_STMT, children=[expr])

    def _parse_expression_statement(self) -> ASTNode:
        expr = self._parse_expression()
        self._skip_newlines()
        return ASTNode(NodeType.EXPR_STMT, children=[expr])

    def _parse_expression(self) -> ASTNode:
        return self._parse_assignment()

    def _parse_assignment(self) -> ASTNode:
        expr = self._parse_or()
        
        if self._check(TokenType.EQUAL):
            self._advance()
            value = self._parse_assignment()
            if expr.node_type == NodeType.IDENTIFIER:
                expr.node_type = NodeType.VAR_DECL
                expr.children = [value]
            elif expr.node_type == NodeType.GET_PROPERTY:
                expr.node_type = NodeType.SET_PROPERTY
                expr.children.append(value)
        
        return expr

    def _parse_or(self) -> ASTNode:
        expr = self._parse_and()
        return expr

    def _parse_and(self) -> ASTNode:
        expr = self._parse_equality()
        return expr

    def _parse_equality(self) -> ASTNode:
        expr = self._parse_comparison()
        
        while self._check(TokenType.EQUAL_EQUAL) or self._check(TokenType.BANG_EQUAL):
            op = self._advance().lexeme
            right = self._parse_comparison()
            expr = ASTNode(NodeType.BINARY_OP, value=op, children=[expr, right])
        
        return expr

    def _parse_comparison(self) -> ASTNode:
        expr = self._parse_addition()
        
        while self._check(TokenType.LESS) or self._check(TokenType.LESS_EQUAL) or \
              self._check(TokenType.GREATER) or self._check(TokenType.GREATER_EQUAL):
            op = self._advance().lexeme
            right = self._parse_addition()
            expr = ASTNode(NodeType.BINARY_OP, value=op, children=[expr, right])
        
        return expr

    def _parse_addition(self) -> ASTNode:
        expr = self._parse_multiplication()
        
        while self._check(TokenType.PLUS) or self._check(TokenType.MINUS):
            op = self._advance().lexeme
            right = self._parse_multiplication()
            expr = ASTNode(NodeType.BINARY_OP, value=op, children=[expr, right])
        
        return expr

    def _parse_multiplication(self) -> ASTNode:
        expr = self._parse_postfix()
        
        while self._check(TokenType.STAR) or self._check(TokenType.SLASH) or self._check(TokenType.PERCENT):
            op = self._advance().lexeme
            right = self._parse_postfix()
            expr = ASTNode(NodeType.BINARY_OP, value=op, children=[expr, right])
        
        return expr

    def _parse_postfix(self) -> ASTNode:
        expr = self._parse_primary()
        
        while True:
            if self._check(TokenType.DOT):
                self._advance()
                name = self._advance().lexeme
                if self._check(TokenType.LPAREN):
                    # Method call
                    self._advance()
                    args = []
                    while not self._check(TokenType.RPAREN):
                        args.append(self._parse_expression())
                        if self._check(TokenType.COMMA):
                            self._advance()
                    self._consume(TokenType.RPAREN, "Expected ')'")
                    expr = ASTNode(NodeType.CALL, value=name, children=[expr] + args)
                else:
                    # Property access
                    expr = ASTNode(NodeType.GET_PROPERTY, value=name, children=[expr])
            elif self._check(TokenType.LPAREN):
                # Function call
                self._advance()
                args = []
                while not self._check(TokenType.RPAREN):
                    args.append(self._parse_expression())
                    if self._check(TokenType.COMMA):
                        self._advance()
                self._consume(TokenType.RPAREN, "Expected ')'")
                expr = ASTNode(NodeType.CALL, value='call', children=[expr] + args)
            else:
                break
        
        return expr

    def _parse_primary(self) -> ASTNode:
        if self._check(TokenType.INTEGER) or self._check(TokenType.FLOAT):
            return ASTNode(NodeType.LITERAL, value=self._advance().lexeme)
        
        if self._check(TokenType.STRING):
            return ASTNode(NodeType.LITERAL, value=self._advance().literal)
        
        if self._check(TokenType.TRUE):
            self._advance()
            return ASTNode(NodeType.LITERAL, value='true')
        
        if self._check(TokenType.FALSE):
            self._advance()
            return ASTNode(NodeType.LITERAL, value='false')
        
        if self._check(TokenType.NIL):
            self._advance()
            return ASTNode(NodeType.LITERAL, value='nil')
        
        if self._check(TokenType.IDENTIFIER):
            return ASTNode(NodeType.IDENTIFIER, value=self._advance().lexeme)
        
        if self._check(TokenType.LPAREN):
            self._advance()
            expr = self._parse_expression()
            self._consume(TokenType.RPAREN, "Expected ')'")
            return expr
        
        raise Exception(f"Unexpected token: {self._peek()}")

    def _check(self, token_type: TokenType) -> bool:
        if self._is_at_end():
            return False
        return self._peek().type == token_type

    def _advance(self) -> Token:
        if not self._is_at_end():
            self.pos += 1
        return self._previous()

    def _is_at_end(self) -> bool:
        return self._peek().type == TokenType.EOF

    def _peek(self) -> Token:
        return self.tokens[self.pos]

    def _previous(self) -> Token:
        return self.tokens[self.pos - 1]

    def _consume(self, token_type: TokenType, message: str) -> Token:
        if self._check(token_type):
            return self._advance()
        raise Exception(message + f" Got: {self._peek()}")

    def _skip_newlines(self):
        while self._check(TokenType.NEWLINE):
            self._advance()
