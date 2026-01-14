from typing import Optional, List, Dict
from dataclasses import dataclass

class Type:
    def __eq__(self, other) -> bool: 
        if not isinstance(other, Type):
            return False
        return type(self) == type(other)
    
    def __hash__(self) -> int: 
        return hash(type(self).__name__)
    
    def to_c(self) -> str:
        raise NotImplementedError
    
    def is_integer(self) -> bool:
        return False
    
    def is_float(self) -> bool:
        return False
    
    def is_pointer(self) -> bool:
        return False
    
    def is_void(self) -> bool:
        return False
    
@dataclass
class PrimitiveType(Type): 
    name: str
    c_type: str
    size: int
    is_signed: bool
    is_floating: bool

    def __eq__(self, other) -> bool:
        if not isinstance(other, PrimitiveType):
            return False
        return self.name == other.name
    
    def __hash__(self) -> int: 
        return hash(self.name)
    
    def to_c(self) -> str: 
        return self.c_type
    
    def is_integer(self) -> bool: 
        return not self.is_floating and self.name != "U0"
    
    def is_float(self) -> bool: 
        return self.is_floating
    
    def is_void(self) -> bool: 
        return self.name == "U0"
    
@dataclass
class PointerType(Type):
    pointee: Type
    levels: int = 1

    def __eq__(self, other) -> bool: 
        if not isinstance(other, PointerType): 
            return False
        return self.pointee == other.pointee and self.levels == other.levels
    
    def __hash__(self) -> int:
        return hash((self.pointee, self.levels))
    
    def to_c(self) -> str: 
        return self.pointee.to_c() + "*" * self.levels
    
    def is_pointer(self) -> bool: 
        return True
    
@dataclass 
class ArrayType(Type): 
    element_type: Type
    dimensions: List[Optional[int]]

    def __eq__(self, other) -> bool: 
        if not isinstance(other, ArrayType): 
            return False
        return (self.element_type == other.element_type and self.dimensions == other.dimensions)
    
    def __hash__(self) -> int: 
        return hash((self.element_type, tuple(self.dimensions)))
    
    def to_c(self) -> str: 
        base = self.element_type.to_c()
        dims = "".join(f"[{d if d is not None else ''}]" for d in self.dimensions)
        return base + dims
    
@dataclass
class ClassType(Type): 
    name: str
    base_class: Optional[str] = None

    def __eq__(self, other) -> bool: 
        if not isinstance(other, ClassType): 
            return False
        return self.name == other.name
    
    def __hash__(self) -> int: 
        return hash(self.name)
    
    def to_c(self) -> str: 
        return self.name
    
@dataclass
class UnionType(Type):
    name: str
    type_prefix: Optional[str] = None

    def __eq__(self, other) -> bool: 
        if not isinstance(other, UnionType):
            return False
        return self.name == other.name
    
    def __hash__(self) -> int:
        return hash(self.name)
    
    def to_c(self) -> str: 
        return self.name
    
@dataclass
class FunctionType(Type): 
    return_type: Type
    param_types: List[Type]

    def __eq__(self, other) -> bool: 
        if not isinstance(other, FunctionType):
            return False
        return (self.return_type == other.return_type and self.param_types == other.param_types)
    
    def __hash__(self) -> int: 
        return hash((self.return_type, tuple(self.param_types)))
    
    def to_c(self) -> str: 
        params = ", ".join(t.to_c() for t in self.param_types)
        return f"{self.return_type.to_c()} (*)({params})"
    
U0 = PrimitiveType("U0", "void", 0, False, False)
I8 = PrimitiveType("I8", "int8_t", 1, True, False)
U8 = PrimitiveType("U8", "uint8_t", 1, False, False)
I16 = PrimitiveType("I16", "int16_t", 2, True, False)
U16 = PrimitiveType("U16", "uint16_t", 2, False, False)
I32 = PrimitiveType("I32", "int32_t", 4, True, False)
U32 = PrimitiveType("U32", "uint32_t", 4, False, False)
I64 = PrimitiveType("I64", "int64_t", 8, True, False)
U64 = PrimitiveType("U64", "uint64_t", 8, False, False)
F64 = PrimitiveType("F64", "double", 8, True, True)

HOLYC_TYPES: Dict[str, Type] = {
    "U0": U0,
    "I8": I8,
    "U8": U8,
    "I16": I16,
    "U16": U16,
    "I32": I32,
    "U32": U32,
    "I64": I64,
    "U64": U64,
    "F64": F64,
}

def get_type(name) -> Optional[Type]:
    return HOLYC_TYPES.get(name)

def is_primitive_type(name) -> bool: 
    return name in HOLYC_TYPES