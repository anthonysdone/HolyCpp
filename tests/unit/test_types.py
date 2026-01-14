import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pytest
from src.types import *

def test_primitive_types_exist():
    assert all([U0, I8, U8, I16, U16, I32, U32, I64, U64, F64])

def test_primitive_properties():
    assert I64.name == "I64" and I64.c_type == "int64_t" and I64.size == 8
    assert U8.is_signed == False and F64.is_floating == True
    assert U0.is_void() and not I64.is_void()

def test_primitive_helpers():
    assert I64.is_integer() and U32.is_integer()
    assert F64.is_float() and not I64.is_float()
    assert U0.is_void() and not F64.is_void()

def test_primitive_c_types():
    assert I64.to_c() == "int64_t"
    assert U8.to_c() == "uint8_t"
    assert F64.to_c() == "double"

def test_pointer_single_level():
    ptr = PointerType(I64, 1)
    assert ptr.pointee == I64 and ptr.levels == 1
    assert ptr.is_pointer and ptr.to_c() == "int64_t*"

def test_pointer_multi_level():
    ptr2 = PointerType(I64, 2)
    ptr3 = PointerType(U8, 3)
    assert ptr2.to_c() == "int64_t**" and ptr3.to_c() == "uint8_t***"

def test_pointer_equivalence(): 
    ptr1 = PointerType(I64, 1)
    ptr2 = PointerType(I64, 1)
    assert ptr1 == ptr2
    assert ptr1 != PointerType(U64, 1)
    assert ptr1 != PointerType(I64, 2)

def test_array_single_dimension(): 
    arr = ArrayType(I64, [10])
    assert arr.element_type == I64 and arr.dimensions == [10]
    assert arr.to_c() == "int64_t[10]"

def test_array_multi_dimensional():
    arr = ArrayType(U8, [5, 10])
    assert arr.element_type == U8 and arr.dimensions == [5, 10]
    assert arr.to_c() == "uint8_t[5][10]"

def test_array_unsized(): 
    arr = ArrayType(F64, [None])
    assert arr.to_c() == "double[]"

def test_array_equivalence():
    arr1 = ArrayType(I64, [10])
    arr2 = ArrayType(I64, [10])
    assert arr1 == arr2 and arr1 != ArrayType(I64, [20])

def test_class_simple():
    cls = ClassType("MyClass")
    assert cls.name == "MyClass" and cls.base_class is None
    assert cls.to_c() == "MyClass"

def test_class_inheritance():
    cls = ClassType("DerivedClass", "BaseClass")
    assert cls.base_class == "BaseClass" and cls.to_c() == "DerivedClass"

def test_class_equivalence():
    cls1 = ClassType("MyClass")
    cls2 = ClassType("MyClass")
    assert cls1 == cls2 and cls1 != ClassType("OtherClass")

def test_union_simple():
    union = UnionType("MyUnion")
    assert union.name == "MyUnion" and union.to_c() == "MyUnion"

def test_union_with_prefix():
    union = UnionType("MyUnion", "I64i")
    assert union.type_prefix == "I64i"

def test_function_type():
    func = FunctionType(U0, [I64, U8])
    assert func.return_type == U0 and func.param_types == [I64, U8]
    assert func.to_c() == "void (*)(int64_t, uint8_t)"

def test_function_equivalence():
    func1 = FunctionType(U0, [I64, U8])
    func2 = FunctionType(U0, [I64, U8])
    assert func1 == func2 and func1 != FunctionType(I64, [U8])

def test_type_map():
    assert "I64" in {k for k in ["U0", "I8", "U8", "I16", "U16", "I32", "U32", "I64", "U64", "F64"] if k in {"I64"}}
    assert get_type("I64") == I64 and get_type("NonExistent") is None
    assert is_primitive_type("I64") and not is_primitive_type("MyClass")