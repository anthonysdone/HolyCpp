from typing import List, Optional
from src.lexer import *
from src.ast_nodes import *
from src.types import *

class ParseError(Exception): 
    def __init__(self, message, token): 
        self.message = message
        self.token = token
        super().__init__(f"Parse error at {token.line}:{token.column}: {message}")

class Parser: 
    PRECEDENCE = {
        TokenType.EQUAL: 14,
        TokenType.PLUS_EQUAL: 14,
        TokenType.MINUS_EQUAL: 14,
        TokenType.STAR_EQUAL: 14,
        TokenType.SLASH_EQUAL: 14,
        TokenType.PERCENT_EQUAL: 14,
        TokenType.AMP_EQUAL: 14,
        TokenType.PIPE_EQUAL: 14,
        TokenType.CARET_EQUAL: 14,
        TokenType.LEFT_SHIFT_EQUAL: 14,
        TokenType.RIGHT_SHIFT_EQUAL: 14,
        
        TokenType.PIPE_PIPE: 13,
        TokenType.CARET_CARET: 12,
        TokenType.AMP_AMP: 11,
        
        TokenType.PIPE: 10,
        TokenType.CARET: 9,
        TokenType.AMPERSAND: 8,
        
        TokenType.EQUAL_EQUAL: 7,
        TokenType.BANG_EQUAL: 7,
        
        TokenType.LESS: 6,
        TokenType.GREATER: 6,
        TokenType.LESS_EQUAL: 6,
        TokenType.GREATER_EQUAL: 6,
        
        TokenType.LEFT_SHIFT: 5,
        TokenType.RIGHT_SHIFT: 5,
        
        TokenType.PLUS: 4,
        TokenType.MINUS: 4,
        
        TokenType.STAR: 3,
        TokenType.SLASH: 3,
        TokenType.PERCENT: 3,
        
        TokenType.BACKTICK: 2,
    }

    TYPE_TOKENS = {
        TokenType.U0, TokenType.I8, TokenType.U8, 
        TokenType.I16, TokenType.U16, TokenType.I32, 
        TokenType.U32, TokenType.I64, TokenType.U64,
        TokenType.F64
    }

    def __init__(self, tokens): 
        self.tokens = tokens
        self.pos = 0

    def parse(self, offset) -> Token: 
        pos = self.pos + offset
        if pos < len(self.tokens): 
            return self.tokens[pos]
        return self.tokens[-1]
    
    def peek_ahead(self, n) -> Token: 
        return self.peek(n)
    
    def advance(self) -> Token: 
        token = self.peek()
        if token.type != TokenType.EOF: 
            self.pos += 1
        return token
    
    def expect(self, token_type) -> Token: 
        token = self.peek()
        if token.type != token_type: 
            self.error(f"Expected {token_type.name}, got {token.type.name}")
        return self.advance()
    
    def match(self, *token_types) -> bool: 
        return self.peek().type in token_types
    
    def error(self, message) -> None: 
        token = self.peek()
        raise ParseError(message, token)
    
    def is_type(self) -> bool: 
        token = self.peek()

        if token.type in self.TYPE_TOKENS:
            return True
        
        return False
    
    def is_declaration_start(self) -> bool: 
        token = self.peek()

        if token.type in (TokenType.STATIC, TokenType.EXTERN, TokenType.IMPORT, 
                          TokenType._EXTERN, TokenType._IMPORT): 
            return True
        
        if token.type in (TokenType.PUBLIC, TokenType.REG, TokenType.NOREG): 
            return True
        
        if token.type in (TokenType.CLASS, TokenType.UNION): 
            return True
        
        if self.is_type():
            return True
        
    def synchronize(self) -> None: 
        self.advance()

        while not self.match(TokenType.EOF):
            if self.peek(-1).type == TokenType.SEMICOLON:
                return
            
            if self.peek().type in (TokenType.CLASS, TokenType.UNION, TokenType.FN, 
                                    TokenType.IF, TokenType.WHILE, TokenType.FOR, 
                                    TokenType.RETURN, TokenType.BREAK, TokenType.CONTINUE):
                return
            
            if self.is_type():
                return 
            
            self.advance()

    def get_precedence(self, token_type) -> int:
        return self.PRECEDENCE.get(token_type, 999)
    
    def is_assignment_op(self) -> bool:
        return self.match(
            TokenType.EQUAL,
            TokenType.PLUS_EQUAL,
            TokenType.MINUS_EQUAL,
            TokenType.STAR_EQUAL,
            TokenType.SLASH_EQUAL,
            TokenType.PERCENT_EQUAL,
            TokenType.AMP_EQUAL,
            TokenType.PIPE_EQUAL,
            TokenType.CARET_EQUAL,
            TokenType.LEFT_SHIFT_EQUAL,
            TokenType.RIGHT_SHIFT_EQUAL
        )
    
    def is_comparison_op(self) -> bool:
        return self.match(
            TokenType.LESS,
            TokenType.GREATER,
            TokenType.LESS_EQUAL,
            TokenType.GREATER_EQUAL,
            TokenType.EQUAL_EQUAL,
            TokenType.BANG_EQUAL
        )
    
    def parse_expression(self) -> Expression:
        return self.parse_assignment()
    
    def parse_assignment(self) -> Expression: 
        expr = self.parse_logical_or()

        if self.is_assignment_op():
            op_token = self.advance()
            op = op_token.value
            right = self.parse_assignment()
            return BinaryOp(op, expr, right)
        
    def parse_logical_or(self) -> Expression:
        left = self.parse_logical_xor()

        while self.match(TokenType.PIPE_PIPE):
            op_token = self.advance()
            right = self.parse_logical_xor()
            left = BinaryOp(op_token.value, left, right)
        
        return left

    def parse_logical_xor(self) -> Expression:
        left = self.parse_logical_and()

        while self.match(TokenType.CARET_CARET):
            op_token = self.advance()
            right = self.parse_logical_and()
            left = BinaryOp(op_token.value, left, right)

        return left
    
    def parse_logical_and(self) -> Expression:
        left = self.parse_bitwise_or()

        while self.match(TokenType.AMP_AMP):
            op_token = self.advance()
            right = self.parse_bitwise_or()
            left = BinaryOp(op_token.value, left, right)

        return left
    
    def parse_bitwise_or(self) -> Expression:
        left = self.parse_bitwise_xor()

        while self.match(TokenType.PIPE):
            op_token = self.advance()
            right = self.parse_bitwise_xor()
            left = BinaryOp(op_token.value, left, right)

        return left
    
    def parse_bitwise_xor(self) -> Expression:
        left = self.parse_bitwise_and()

        while self.match(TokenType.CARET):
            op_token = self.advance()
            right = self.parse_bitwise_and()
            left = BinaryOp(op_token.value, left, right)

        return left
    
    def parse_bitwise_and(self) -> Expression:
        left = self.parse_equality()

        while self.match(TokenType.AMPERSAND):
            op_token = self.advance()
            right = self.parse_equality()
            left = BinaryOp(op_token.value, left, right)

        return left
    
    def parse_equality(self) -> Expression:
        left = self.parse_comparison()

        while self.match(TokenType.EQUAL_EQUAL, TokenType.BANG_EQUAL):
            op_token = self.advance()
            right = self.parse_comparison()
            left = BinaryOp(op_token.value, left, right)

        return left
    
    def parse_comparison(self) -> Expression:
        left = self.parse_shift()

        if not self.is_comparison_op():
            return left
        
        comparisons = []
        operands = [left]

        while self.is_comparison_op():
            op_token = self.advance()
            right = self.parse_shift()
            comparisons.append(op_token.value)
            operands.append(right)

        if len(comparisons) == 1:
            return BinaryOp(comparisons[0], operands[0], operands[1])
        
        result = BinaryOp(comparisons[0], operands[0], operands[1])

        for i in range(1, len(comparisons)):
            next_comp = BinaryOp(comparisons[i], operands[i], operands[i + 1])
            result = BinaryOp("&&", result, next_comp)
        
        return result
    
    def parse_shift(self) -> Expression:
        left = self.parse_additive()

        while self.match(TokenType.LEFT_SHIFT, TokenType.RIGHT_SHIFT):
            op_token = self.advance()
            right = self.parse_additive()
            left = BinaryOp(op_token.value, left, right)

        return left
    
    def parse_additive(self) -> Expression:
        left = self.parse_multiplicative()

        while self.match(TokenType.PLUS, TokenType.MINUS):
            op_token = self.advance()
            right = self.parse_multiplicative()
            left = BinaryOp(op_token.value, left, right)

        return left
    
    def parse_multiplicative(self) -> Expression:
        left = self.parse_power()

        while self.match(TokenType.STAR, TokenType.SLASH, TokenType.PERCENT):
            op_token = self.advance()
            right = self.parse_power()
            left = BinaryOp(op_token.value, left, right)
        
        return left
    
    def parse_power(self) -> Expression:
        left = self.parse_unary()

        while self.match(TokenType.BACKTICK):
            op_token = self.advance()
            right = self.parse_unary()
            left = BinaryOp(op_token.value, left, right)
        
        return left
    
    def parse_unary(self) -> Expression:
        if self.match(TokenType.BANG, TokenType.TILDE, TokenType.MINUS,
                      TokenType.PLUS_PLUS, TokenType.MINUS_MINUS, TokenType.STAR, 
                      TokenType.AMPERSAND): 
            op_token = self.advance()
            operand = self.parse_unary()

            if op_token.type == TokenType.STAR: 
                return PointerDeref(operand)
            
            if op_token.type == TokenType.AMPERSAND:
                return AddressOf(operand)
            
            return UnaryOp(op_token.value, operand)
        
        return self.parse_postfix()

    def parse_postfix(self) -> Expression: 
        expr = self.parse_primary()

        while True: 
            if self.match(TokenType.LBRACKET):
                self.advance()
                index = self.parse_expression()
                self.expect(TokenType.RBRACKET)
                expr = ArrayAccess(expr, index)

            elif self.match(TokenType.ARROW): 
                self.advance()
                member_token = self.expect(TokenType.IDENTIFIER)
                member = member_token.value

                if self.match(TokenType.LPAREN):
                    self.advance()
                    args = self.parse_argument_list()
                    self.expect(TokenType.RPAREN)
                    expr = MethodCall(expr, member, args)
                else:
                    expr = MemberAccess(expr, member, True)
            
            elif self.match(TokenType.DOT): 
                self.advance()
                member_token = self.expect(TokenType.IDENTIFIER)
                member = member_token.value

                if self.match(TokenType.LPAREN):
                    self.advance()
                    args = self.parse_argument_list()
                    self.expect(TokenType.RPAREN)
                    expr = MethodCall(expr, member, args)
                else:
                    expr = MemberAccess(expr, member, False)
            
            elif self.match(TokenType.LPAREN): 
                self.advance()
                args = self.parse_argument_list()
                self.expect(TokenType.RPAREN)
                expr = CallExpr(expr, args)

            elif self.match(TokenType.PLUS_PLUS, TokenType.MINUS_MINUS):
                op_token = self.advance()
                expr = UnaryOp(op_token.value, expr, True)

            else: 
                break
        
        return expr
    
    def parse_argument_list(self) -> List[Expression]:
        args = []

        if self.match(TokenType.RPAREN):
            return args
        
        args.append(self.parse_expression())

        while self.match(TokenType.COMMA):
            self.advance()
            args.append(self.parse_expression())

        return args
    
    def parse_primary(self) -> Expression:
        token = self.peek()

        if token.type == TokenType.INTEGER: 
            self.advance()
            return Literal(token.value, I64)
        
        if token.type == TokenType.FLOAT:
            self.advance()
            return Literal(token.value, F64)
        
        if token.type == TokenType.STRING:
            self.advance()
            return Literal(token.value, PointerType(U8))
        
        if token.type == TokenType.CHAR: 
            self.advance()
            return Literal(token.value, U64)
        
        if token.type == TokenType.LPAREN:
            self.advance()
            expr = self.parse_expression()
            self.expect(TokenType.RPAREN)
            return expr
        
        if token.type == TokenType.THIS:
            self.advance()
            return ThisExpr()
        
        if token.type == TokenType.SIZEOF:
            self.advance()
            self.expect(TokenType.LPAREN)
            type_expr = self.parse_type()
            self.expect(TokenType.RPAREN)
            return SizeofExpr(type_expr)
        
        if token.type == TokenType.OFFSET: 
            self.advance()
            self.expect(TokenType.LPAREN)
            class_token = self.expect(TokenType.IDENTIFIER)
            self.expect(TokenType.COMMA)
            member_token = self.expect(TokenType.IDENTIFIER)
            self.expect(TokenType.RPAREN)
            return OffsetExpr(class_token.value, member_token.value)
        
        if token.type == TokenType.IDENTIFIER:
            self.advance()
            return Identifier(token.value)
        
        if token.type in self.TYPE_TOKENS:
            self.advance()
            return Identifier(token.value)
        
    def parse_type(self) -> Type:
        token = self.peek()

        if token.type in self.TYPE_TOKENS:
            type_name = token.value
            self.advance()
            base_type = get_type(type_name)
            if base_type is None: 
                self.error(f"Unknown type: {type_name}")
        elif token.type == TokenType.IDENTIFIER:
            type_name = token.value
            self.advance()
            base_type = ClassType(type_name)
        else:
            self.error(f"Expected type, got {token.type.name}")

        pointer_count = 0
        while self.match(TokenType.STAR):
            self.advance()
            pointer_count += 1

        if pointer_count > 0: 
            base_type = PointerType(base_type, pointer_count)

        dimensions = []
        while self.match(TokenType.LBRACKET):
            self.advance()
            if self.match(TokenType.RBRACKET):
                dimensions.append(None)
                self.advance()
            else: 
                size_token = self.peek()
                if size_token.type != TokenType.INTEGER:
                    self.error("Expected array size")
                dimensions.append(size_token.value)
                self.advance()
                self.expect(TokenType.RBRACKET)
        
        if dimensions:
            base_type = ArrayType(base_type, dimensions)

        return base_type
    
    