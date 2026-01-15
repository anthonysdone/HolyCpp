import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pytest
from src.types import I64, U8, F64
from src.ast_nodes import *

def test_source_location():
    loc = SourceLocation(10, 5, "test.HC")
    assert loc.line == 10 and loc.column == 5
    assert str(loc) == "test.HC:10:5"

def test_declaration_nodes():
    prog = Program([])
    assert isinstance(prog, Program) and len(prog.declarations) == 0

    var = VarDecl(I64, "x", None, False, False)
    assert var.name == "x" and var.type == I64

    cls = ClassDecl("MyClass", [], [], "BaseClass")
    assert cls.name == "MyClass" and cls.base_class == "BaseClass"

def test_function_nodes():
    param = Parameter(I64, "x", None)
    assert param.type == I64 and param.name == "x"

    func = FunctionDecl(I64, "Add", [param], None, [])
    assert func.name == "Add" and func.return_type == I64
    
    method = MethodDecl(I64, "Process", [], None, [], "MyClass")
    assert method.class_name == "MyClass"

def test_statement_nodes():
    block = Block([])
    assert isinstance(block, Block) and len(block.statements) == 0

    ret = ReturnStmt(Literal(42, I64))
    assert ret.value.value == 42

    if_stmt = IfStmt(Literal(1, I64), Block([]), None)
    assert if_stmt.condition.value == 1

def test_control_flow_nodes(): 
    while_stmt = WhileStmt(Literal(1, I64), Block([]))
    assert isinstance(while_stmt.body, Block)

    for_stmt = ForStmt(None, None, None, Block([]))
    assert isinstance(for_stmt.body, Block)

def test_switch_case_nodes():
    case1 = CaseStmt([1, 2], False, False, [])
    assert case1.values == [1, 2] and not case1.is_range

    case2 = CaseStmt([5, 10], True, False, [])
    assert case2.is_range

    switch = SwitchStmt(Identifier("x"), [case1])
    assert len(switch.cases) == 1

def test_expression_nodes(): 
    lit = Literal(42, I64)
    ident = Identifier("x")
    assert lit.value == 42 and ident.name == "x"

    binop = BinaryOp("+", lit, ident)
    assert binop.op == "+" and binop.left == lit

    unary = UnaryOp("-", lit, False)
    assert unary.op == "-" and not unary.is_postfix

def test_call_and_member_nodes(): 
    call = CallExpr(Identifier("func"), [Literal(1, I64)])
    assert len(call.arguments) == 1

    member = MemberAccess(Identifier("obj"), "field", False)
    assert member.member == "field" and not member.is_arrow

    method = MethodCall(Identifier("obj"), "Method", [])
    assert method.method == "Method"

def test_pointer_nodes(): 
    dref = PointerDeref(Identifier("ptr"))
    assert isinstance(dref.operand, Identifier)

    addr = AddressOf(Identifier("x"))
    assert isinstance(addr.operand, Identifier)

    arr_access = ArrayAccess(Identifier("arr"), Literal(5, I64))
    assert isinstance(arr_access.index, Literal)

def test_special_expr_nodes():
    this = ThisExpr()
    assert isinstance(this, ThisExpr)

    sizeof = SizeofExpr(I64)
    assert sizeof.type == I64

    offset = OffsetExpr("MyClass", "field")
    assert offset.class_name == "MyClass" and offset.member == "field"

def test_exception_nodes():
    try_catch = TryCatchStmt(Block([]), Block([]))
    assert isinstance(try_catch.try_block, Block)

    throw = ThrowStmt(Literal(0x4552524F, I64))
    assert throw.value.value == 0x4552524F

def test_extern_nodes():
    ext = ExternDecl(I64, "ExtFunc", [], "C_FUNC", False)
    assert ext.external_name == "C_FUNC" and not ext.is_import

def test_visitor_pattern():
    class TestVisitor(ASTVisitor):
        def __init__(self):
            self.visited = []
        
        def visit_Literal(self, node):
            self.visited.append(node.value)
            return node.value
        
        def visit_Identifier(self, node):
            self.visited.append(node.name)
            return node.name
    
    visitor = TestVisitor()
    lit = Literal(42, I64)
    ident = Identifier("x")

    lit.accept(visitor)
    ident.accept(visitor)

    assert visitor.visited == [42, "x"]

def test_ast_tree_construction():
    param = Parameter(I64, "x")
    body = Block([ReturnStmt(BinaryOp("*", Identifier("x"), Literal(2, I64)))])
    func = FunctionDecl(I64, "Double", [param], body, [])
    prog = Program([func])
    
    assert len(prog.declarations) == 1
    assert prog.declarations[0].name == "Double"
    assert isinstance(prog.declarations[0].body.statements[0], ReturnStmt)