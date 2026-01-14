from typing import Optional, List, Any
from dataclasses import dataclass
from src.types import Type

@dataclass
class SourceLocation:
    line: int
    column: int
    file: Optional[str] = None

    def __repr__(self) -> str: 
        if self.file: 
            return f"{self.file}:{self.line}:{self.column}"
        return f"{self.line}:{self.column}"
    
class ASTNode: 
    def __init__(self, location=None): 
        self.location = location

    def accept(self, visitor) -> Any: 
        method_name = f"visit_{self.__class__.__name__}"
        method = getattr(visitor, method_name, visitor.generic_visit)
        return method(self)
    
    def __repr__(self) -> str: 
        return f"{self.__class__.__name__}()"

# Declarations
    
class Declaration(ASTNode): 
    pass

@dataclass
class Program(Declaration): 
    declarations: List[Declaration]

    def __repr__(self) -> str:
        return f"Program(declarations={len(self.declarations)})"
    
@dataclass
class Parameter: 
    type: Type
    name: str
    default_value: Optional["Expression"] = None 

    def __repr__(self) -> str: 
        return f"Parameter({self.type.to_c()} {self.name})"
    
@dataclass 
class FunctionDecl(Declaration):
    return_type: Type
    name: str
    params: List[Parameter]
    body: Optional["Block"] 
    attributes: List[str]

    def __repr__(self) -> str:
        return f"FunctionDecl({self.return_type.to_c()} {self.name})"

@dataclass
class MethodDecl(FunctionDecl): 
    class_name: str
    is_constructor: bool = False

    def __repr__(self) -> str: 
        return f"MethodDecl({self.class_name}::{self.name})"
    
@dataclass
class VarDecl(Declaration): 
    type: Type
    name: str
    initializer: Optional["Expression"] 
    is_global: bool = False
    is_static: bool = False
    attributes: List[str] = None

    def __post_init__(self): 
        if self.attributes is None: 
            self.attributes = []

    def __repr__(self) -> str: 
        return f"VarDecl({self.type.to_c()} {self.name})"
        
@dataclass
class ClassDecl(Declaration): 
    name: str
    members: List[VarDecl]
    methods: List[MethodDecl]
    base_class: Optional[str] = None

    def __repr__(self) -> str: 
        base = f" : {self.base_class}" if self.base_class else ""
        return f"ClassDecl({self.name}{base})"

@dataclass
class UnionDecl(Declaration): 
    name: str
    members: List[VarDecl]
    type_prefix: Optional[str] = None

    def __repr__(self) -> str:
        return f"UnionDecl({self.name})"

@dataclass
class ExternDecl(Declaration): 
    return_type: Type
    name: str
    params: List[Parameter]
    external_name: Optional[str] = None
    is_import: bool = False

    def __repr__(self) -> str: 
        kind = "import" if self.is_import else "extern"
        ext = f" as {self.external_name}" if self.external_name else ""
        return f"ExternDecl({kind} {self.name}{ext})"
    
# Statements

class Statement(ASTNode): 
    pass

@dataclass
class Block(Statement):
    statements: List[Statement]

    def __repr__(self) -> str: 
        return f"Block({len(self.statements)} statements)"
    
@dataclass
class ExpressionStmt(Statement): 
    expression: "Expression" 

    def __repr__(self) -> str: 
        return f"ExpressionStmt({self.expression})"

@dataclass
class IfStmt(Statement): 
    condition: "Expression" 
    then_block: Block
    else_block: Optional[Block] = None

    def __repr__(self) -> str: 
        return "IfStmt(if/else)" if self.else_block else "IfStmt(if)"
    
@dataclass
class WhileStmt(Statement): 
    condition: "Expression" 
    body: Block

    def __repr__(self) -> str: 
        return "WhileStmt()"
    
@dataclass
class ForStmt(Statement): 
    init: Optional[Statement]
    condition: Optional["Expression"] 
    increment: Optional["Expression"] 
    body: Block

    def __repr__(self) -> str: 
        return "ForStmt()"

@dataclass
class CaseStmt(ASTNode): 
    values: List[int]
    is_range: bool
    is_auto: bool
    statements: List[Statement]
    is_subswitch: bool = False
    subswitch_start: List[Statement] = None
    subswitch_end: List[Statement] = None

    def __post_init__(self): 
        if self.subswitch_start is None: 
            self.subswitch_start = []
        if self.subswitch_end is None: 
            self.subswitch_end = []
    
    def __repr__(self) -> str: 
        if self.is_auto:
            return "CaseStmt(auto)"
        if self.is_range: 
            return f"CaseStmt({self.values[0]}...{self.values[1]})"
        return f"CaseStmt({self.values})"

@dataclass
class SwitchStmt(Statement):
    expression: "Expression" 
    cases: List[CaseStmt]
    is_unchecked: bool = False

    def __repr__(self) -> str:
        kind = "switch[]" if self.is_unchecked else "switch"
        return f"SwitchStmt({kind}, {len(self.cases)} cases)"
    
@dataclass
class ReturnStmt(Statement):
    value: Optional["Expression"] 

    def __repr__(self) -> str:
        return "ReturnStmt()" if self.value is None else f"ReturnStmt({self.value})"

@dataclass
class TryCatchStmt(Statement):
    try_block: Block
    catch_block: Block

    def __repr__(self) -> str: 
        return "TryCatchStmt()"

@dataclass
class ThrowStmt(Statement): 
    value: "Expression" 

    def __repr__(self) -> str:
        return f"ThrowStmt({self.value})"

@dataclass
class GotoStmt(Statement): 
    label: str

    def __repr__(self) -> str: 
        return f"GotoStmt({self.label})"
    
@dataclass
class LabelStmt(Statement): 
    label: str

    def __repr__(self) -> str: 
        return f"LabelStmt({self.label})"

@dataclass
class LockStmt(Statement): 
    body: Block

    def __repr__(self) -> str: 
        return "LockStmt()"

# Expressions

class Expression(ASTNode):
    pass

@dataclass
class BinaryOp(Expression):
    op: str
    left: Expression
    right: Expression

    def __repr__(self) -> str: 
        return f"BinaryOp({self.left} {self.op} {self.right})"

@dataclass
class UnaryOp(Expression):
    op: str
    operand: Expression
    is_postfix: bool = False

    def __repr__(self) -> str: 
        if self.is_postfix: 
            return f"UnaryOp({self.operand}{self.op})"
        return f"UnaryOp({self.op}{self.operand})"
    
@dataclass
class CallExpr(Expression): 
    function: Expression
    arguments: List[Expression]

    def __repr__(self) -> str: 
        return f"CallExpr({self.function}, {len(self.arguments)} args)"
    
@dataclass
class MethodCall(Expression): 
    object: Expression
    method: str
    arguments: List[Expression]

    def __repr__(self) -> str:
        return f"MethodCall({self.object}.{self.method})"

@dataclass
class MemberAccess(Expression): 
    object: Expression
    member: str
    is_arrow: bool = False

    def __repr__(self) -> str: 
        op = "->" if self.is_arrow else "."
        return f"MemberAccess({self.object}{op}{self.member})"

@dataclass
class ArrayAccess(Expression): 
    array: Expression
    index: Expression

    def __repr__(self) -> str: 
        return f"ArrayAccess({self.array}[{self.index}])"

@dataclass
class PointerDeref(Expression): 
    operand: Expression

    def __repr__(self) -> str:
        return f"PointerDeref(*{self.operand})"

@dataclass
class Literal(Expression): 
    value: Any
    type: Type

    def __repr__(self) -> str: 
        return f"Literal({self.value})"

@dataclass
class Identifier(Expression): 
    name: str

    def __repr__(self) -> str: 
        return f"Identifier({self.name})"
    
@dataclass
class ThisExpr(Expression): 
    def __repr__(self) -> str: 
        return "ThisExpr()"
    
@dataclass
class SizeofExpr(Expression): 
    type: Type

    def __repr__(self) -> str: 
        return f"SizeofExpr({self.type.to_c()})"

@dataclass
class OffsetExpr(Expression): 
    class_name: str
    member: str

    def __repr__(self) -> str: 
        return f"OffsetExpr({self.class_name}, {self.member})"

# Visitor Pattern

class ASTVisitor: 
    def generic_visit(self, node) -> Any: 
        raise NotImplementedError(f"No visit method for {type(node).__name__}")

    