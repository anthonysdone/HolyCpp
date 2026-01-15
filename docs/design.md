# HolyC to C Transpiler - Design Document

## 1. Overview

### 1.1 Goals
- Create a faithful HolyC to C transpiler that preserves the semantics and behavior of HolyC programs
- Generate clean, readable C code that follows C99/C11 standards
- Implement all key HolyC language features
- Keep the transpiler implementation simple and maintainable
- Written entirely in Python with minimal dependencies

### 1.2 Non-Goals
- Perfect compile-time execution (#exe{}) - will translate to runtime where possible
- Full TempleOS system calls - will provide stubs/wrappers
- Binary compatibility with TempleOS
- Inline assembly support (initially - can be added in later phases)

## 2. Architecture

### 2.1 Pipeline Overview
```
HolyC Source → Lexer → Parser → AST → Semantic Analyzer → Code Generator → C Source
```

### 2.2 Component Structure
```
holyc_transpiler/
├── lexer.py          # Tokenization
├── parser.py         # Syntax analysis and AST construction
├── ast_nodes.py      # AST node definitions
├── semantic.py       # Type checking and symbol resolution
├── codegen.py        # C code generation
├── types.py          # HolyC type system
├── runtime.py        # Generate runtime support header
└── main.py           # CLI entry point
```

## 3. HolyC Type System Translation

### 3.1 Built-in Types Mapping

| HolyC Type | C Type | Notes |
|------------|--------|-------|
| U0 | void | Zero size void |
| I8 | int8_t | char |
| U8 | uint8_t | unsigned char |
| I16 | int16_t | short |
| U16 | uint16_t | unsigned short |
| I32 | int32_t | int |
| U32 | uint32_t | unsigned int |
| I64 | int64_t | long (64-bit) |
| U64 | uint64_t | unsigned long |
| F64 | double | No F32 support |

### 3.2 Sub-integer Access
HolyC allows accessing sub-parts of integers:
```holyc
I64 i = 0x123456780000DEF0;
i.u16[1] = 0x9ABC;
```

**Translation Strategy:**
Generate a union wrapper for each integer variable that needs sub-access:
```c
typedef union {
    int64_t value;
    struct {
        uint8_t u8[8];
        int8_t i8[8];
        uint16_t u16[4];
        int16_t i16[4];
        uint32_t u32[2];
        int32_t i32[2];
    };
} holyc_i64_t;
```

### 3.3 Literal Details

**Multi-char Literal Packing:**
- Up to 8 characters packed into uint64_t
- Little-endian byte order
- Example: 'ABC' → 0x434241 (C=0x43, B=0x42, A=0x41)
- Excess characters beyond 8 are truncated

**Escape Sequences:**
Standard C escape sequences supported:
- `\n` (newline), `\t` (tab), `\r` (carriage return)
- `\\` (backslash), `\"` (quote), `\'` (apostrophe)
- `\0` (null)

## 4. Key Language Features

### 4.1 Function Calls Without Parentheses
**HolyC:**
```holyc
Dir;
Dir();
Dir("*");
```

**Translation:** Always emit parentheses in C:
```c
Dir();
Dir();
Dir("*");
```

**Implementation:** Parser detects bare identifiers in statement context and converts to call expressions.

### 4.2 Default Arguments Not At End
**HolyC:**
```holyc
U0 Test(I64 i=4, I64 j, I64 k=5) {
    Print("%X %X %X\n", i, j, k);
}
Test(,3);  // i=4, j=3, k=5
```

**Translation Strategy:**
- Generate wrapper functions for each calling pattern
- Use sentinel values to detect omitted arguments
```c
void Test_impl(int64_t i, int64_t j, int64_t k) {
    holyc_print("%X %X %X\n", i, j, k);
}

void Test_default_i_k(int64_t j) {
    Test_impl(4, j, 5);
}
```

### 4.3 String/Char Literal Syntax Sugar
**HolyC:**
```holyc
"Hello World\n";           // Calls Print()
"%s age %d\n", name, age;  // Calls Print()
'' drv;                    // Calls PutChars()
'*';                       // Calls PutChars()
```

**Translation:**
```c
holyc_print("Hello World\n");
holyc_print("%s age %d\n", name, age);
holyc_putchars(drv);
holyc_putchars('*');
```

**Implementation:** Parser recognizes string/char expressions in statement context.

### 4.4 Multi-Character Literals
**HolyC:**
```holyc
'ABC'  // equals 0x434241
PutChars('Hello ');
```

**Translation:**
```c
0x434241
holyc_putchars(0x6F6C6C6548ULL);  // 'Hello ' packed
```

**Implementation:** Lexer packs multi-char literals into uint64_t at tokenization.

### 4.5 Postfix Type Casting
**HolyC:** No explicit cast syntax, uses ToI64(), ToBool(), ToF64()

**Translation:** Direct function mapping:
```c
int64_t ToI64(double x) { return (int64_t)x; }
double ToF64(int64_t x) { return (double)x; }
int ToBool(int64_t x) { return x != 0; }
```

### 4.6 No main() - Top-Level Code
**HolyC:**
```holyc
I64 x = 5;
"Hello\n";
```

**Translation Strategy:**
Collect all top-level statements into a generated `_holyc_init()` function:
```c
int64_t x;

void _holyc_init(void) {
    x = 5;
    holyc_print("Hello\n");
}

int main(int argc, char **argv) {
    _holyc_init();
    return 0;
}
```

### 4.7 Variable Argument Count (argc/argv)
**HolyC:**
```holyc
I64 AddNums(...) {
    I64 i, res=0;
    for (i=0; i<argc; i++)
        res += argv[i];
    return res;
}
```

**Translation Strategy:**
Use a struct to pass arguments:
```c
typedef struct {
    int64_t count;
    int64_t *args;
} holyc_varargs_t;

int64_t AddNums(holyc_varargs_t varargs) {
    int64_t argc = varargs.count;
    int64_t *argv = varargs.args;
    int64_t i, res = 0;
    for (i = 0; i < argc; i++)
        res += argv[i];
    return res;
}

// Call site:
int64_t args[] = {1, 2, 3};
AddNums((holyc_varargs_t){3, args});
```

### 4.8 Chained Comparisons
**HolyC:**
```holyc
if (5 < i < j+1 < 20)
```

**Translation:**
```c
if (5 < i && i < j+1 && j+1 < 20)
```

**Implementation:** Parser detects comparison chains and expands to logical AND.

### 4.9 Switch Statement Extensions

#### 4.9.1 Switch [] - Unchecked
**HolyC:**
```holyc
switch [] (i) { ... }
```

**Translation:** Regular switch, document with comment:
```c
// Unchecked switch - assumes i is in range
switch (i) { ... }
```

#### 4.9.2 Range Cases
**HolyC:**
```holyc
case 4...7:
```

**Translation:** Multiple case labels:
```c
case 4: case 5: case 6: case 7:
```

#### 4.9.3 No-Value Cases
**HolyC:**
```holyc
case: "Zero\n"; break;   // Starts at 0
case: "One\n"; break;    // 1
case 10: "Ten\n"; break;
case: "Eleven\n"; break; // 11
```

**Translation:** Track and emit explicit values:
```c
case 0: holyc_print("Zero\n"); break;
case 1: holyc_print("One\n"); break;
case 10: holyc_print("Ten\n"); break;
case 11: holyc_print("Eleven\n"); break;
```

#### 4.9.4 Sub-switches (start/end blocks)
**HolyC:**
```holyc
switch (i) {
    case 0: "Zero "; break;
    start:
        "[";
        case 1: "One"; break;
        case 3: "Three"; break;
    end:
        "] ";
        break;
}
```

**Translation Strategy:**
Use nested blocks and goto for control flow:
```c
switch (i) {
    case 0: 
        holyc_print("Zero "); 
        break;
    case 1:
    case 3: {
        holyc_print("[");
        switch (i) {
            case 1: holyc_print("One"); break;
            case 3: holyc_print("Three"); break;
        }
        holyc_print("] ");
        break;
    }
}
```

### 4.10 Power Operator (`)
**HolyC:**
```holyc
x = 2`8;  // 2^8 = 256
```

**Translation:**
```c
x = holyc_pow(2, 8);
```

Where `holyc_pow()` is provided in runtime:
```c
double holyc_pow(double base, double exp) {
    return pow(base, exp);
}
```

### 4.11 Operator Precedence
HolyC has different precedence than C. Parser must handle:
```
, >> << / % &  ^  |  +  -  <  >  <=  >=  ==  !=  &&  ^^  ||  =  <<=  >>=  /=  &=  |=  ^=  +=  -=
```

**Strategy:** Build proper precedence table in parser, then emit C with explicit parentheses.

### 4.12 Try/Catch/Throw
**HolyC:**
```holyc
try {
    throw('ERRO');
} catch {
    if (Fs->except_ch == 'ERRO')
        "Caught error\n";
}
```

**Translation Strategy:**
Use setjmp/longjmp:
```c
typedef struct {
    jmp_buf jmp;
    uint64_t except_ch;
    int catch_except;
} holyc_exception_ctx_t;

holyc_exception_ctx_t *holyc_ex_ctx;

void holyc_throw(uint64_t ch) {
    holyc_ex_ctx->except_ch = ch;
    longjmp(holyc_ex_ctx->jmp, 1);
}

// Usage:
holyc_exception_ctx_t ex_ctx;
holyc_exception_ctx_t *old_ctx = holyc_ex_ctx;
holyc_ex_ctx = &ex_ctx;
if (setjmp(ex_ctx.jmp) == 0) {
    // try block
    holyc_throw(0x4F525245ULL);
} else {
    // catch block
    if (holyc_ex_ctx->except_ch == 0x4F525245ULL)
        holyc_print("Caught error\n");
}
holyc_ex_ctx = old_ctx;
```

### 4.13 Classes (Structs)
**HolyC:**
```holyc
class MyClass {
    I64 x;
    U8 name[32];
};
```

**Translation:**
```c
typedef struct MyClass {
    int64_t x;
    uint8_t name[32];
} MyClass;
```

### 4.14 Union with Type Prefix
**HolyC:**
```holyc
I64i union MyUnion {
    I8i i8[8];
    U8i u8[8];
};
```

**Translation:**
```c
typedef union MyUnion {
    int8_t i8[8];
    uint8_t u8[8];
} MyUnion;

// "I64i" prefix means can be used as I64
```

### 4.15 lastclass Keyword
**HolyC:**
```holyc
U0 Process(MyClass *obj, lastclass type) {
    // type is set to "MyClass"
}
```

**Translation Strategy:**
Generate type parameter:
```c
void Process(MyClass *obj, const char *type) {
    // type = "MyClass"
}
// Call: Process(&obj, "MyClass");
```

### 4.16 Meta Data for Classes
**HolyC:**
```holyc
class Person {
    U8 name[32] format "Name: %s";
    I64 age format "Age: %d";
};
```

**Translation Strategy:**
Generate metadata tables:
```c
typedef struct Person {
    uint8_t name[32];
    int64_t age;
} Person;

static const char *Person_name_format = "Name: %s";
static const char *Person_age_format = "Age: %d";
```

### 4.17 No continue Statement
**HolyC:** Use `goto` instead

**Translation:** Leave as-is, C supports both goto and continue.

### 4.18 Lock Blocks
**HolyC:**
```holyc
lock {
    counter++;
}
```

**Translation:**
```c
// Simplified - use atomic operations or mutexes
__atomic_fetch_add(&counter, 1, __ATOMIC_SEQ_CST);
```

### 4.19 Preprocessor Directives
Most directives translate directly:
- `#include` → `#include`
- `#define` → `#define`
- `#if/#ifdef/#ifndef/#else/#endif` → same

**Special Cases:**
- `#exe{}` - Limited support, evaluate at transpile time where possible
- `#ifaot/#ifjit` - Treat as `#if 1` or `#if 0` based on mode

### 4.20 External Function Declarations (FFI)
HolyC provides several keywords for interfacing with external C libraries:

**extern**: Bind to existing symbol in symbol table (JIT) or import at load time (AOT)
```holyc
extern I64 MyFunc(I64 x);
```

**import**: Import symbol from another module at load time
```holyc
import U0 ExternalFunc(U8 *str);
```

**_extern**: Bind to existing symbol with different name (C to asm binding)
```holyc
_extern MY_C_FUNCTION U0 MyCFunc(I64 x);
```

**_import**: Import symbol with different name from another module
```holyc
_import EXTERNAL_NAME U0 MyWrapper(I64 x);
```

**Translation Strategy:**
Generate proper C declarations with external linkage:
```c
// extern I64 MyFunc(I64 x);
extern int64_t MyFunc(int64_t x);

// _extern MY_C_FUNCTION U0 MyCFunc(I64 x);
extern void MyCFunc(int64_t x);  // Actual symbol: MY_C_FUNCTION

// Link mappings tracked in symbol table
```

For `_extern` and `_import`, generate linker aliases or wrapper functions:
```c
// Option 1: Linker alias (if supported)
extern void MY_C_FUNCTION(int64_t) __attribute__((alias("MyCFunc")));

// Option 2: Wrapper function
extern void MY_C_FUNCTION(int64_t x);
void MyCFunc(int64_t x) {
    MY_C_FUNCTION(x);
}
```

### 4.21 Dynamic Memory Management
HolyC provides heap allocation with tracking:

**Core Functions:**
```holyc
U8 *ptr = MAlloc(1024);        // Allocate 1KB
Free(ptr);                      // Free memory
I64 size = MSize(ptr);          // Query allocation size
```

**Translation:**
```c
uint8_t *ptr = holyc_malloc(1024);
holyc_free(ptr);
int64_t size = holyc_msize(ptr);
```

**Runtime Implementation:**
```c
// holyc_runtime.h
typedef struct {
    size_t size;
    uint8_t data[];
} holyc_alloc_header_t;

static inline void* holyc_malloc(size_t size) {
    holyc_alloc_header_t *hdr = malloc(sizeof(holyc_alloc_header_t) + size);
    if (!hdr) return NULL;
    hdr->size = size;
    return hdr->data;
}

static inline void holyc_free(void *ptr) {
    if (!ptr) return;
    holyc_alloc_header_t *hdr = (holyc_alloc_header_t*)((char*)ptr - offsetof(holyc_alloc_header_t, data));
    free(hdr);
}

static inline size_t holyc_msize(void *ptr) {
    if (!ptr) return 0;
    holyc_alloc_header_t *hdr = (holyc_alloc_header_t*)((char*)ptr - offsetof(holyc_alloc_header_t, data));
    return hdr->size;
}
```

**Variants:**
```holyc
MAllocIdent(size, task);        // Alloc from specific task heap
CAlloc(size);                   // Zero-initialized allocation
StrNew(str);                    // Duplicate string
```

### 4.22 Pointers and Pointer Arithmetic
HolyC supports full pointer operations:

**Pointer Declaration:**
```holyc
I64 *ptr;
U8 **ptr_to_ptr;
```

**Pointer Arithmetic:**
```holyc
ptr++;                  // Advance by sizeof(I64)
ptr += 5;               // Advance by 5 * sizeof(I64)
I64 diff = ptr2 - ptr1; // Difference in elements
```

**Translation:** Direct C equivalent with proper types:
```c
int64_t *ptr;
uint8_t **ptr_to_ptr;
ptr++;
ptr += 5;
int64_t diff = ptr2 - ptr1;
```

**Dereferencing:**
```holyc
I64 val = *ptr;
*ptr = 42;
```

**Address-of:**
```holyc
I64 x = 10;
I64 *ptr = &x;
```

### 4.23 Function Pointers and Callbacks
HolyC uses `&` prefix for function addresses:

**Function Pointer Declaration:**
```holyc
U0 (*callback)(I64 x);
```

**Assignment:**
```holyc
callback = &MyFunction;
```

**Invocation:**
```holyc
callback(42);
```

**Translation:**
```c
void (*callback)(int64_t x);
callback = MyFunction;  // & optional in C
callback(42);
```

**Example - Callback System:**
```holyc
U0 ProcessArray(I64 *arr, I64 size, U0 (*fn)(I64)) {
    I64 i;
    for (i = 0; i < size; i++)
        fn(arr[i]);
}

U0 PrintValue(I64 x) {
    "%d\n", x;
}

// Usage
ProcessArray(data, 100, &PrintValue);
```

**Translation:**
```c
void ProcessArray(int64_t *arr, int64_t size, void (*fn)(int64_t)) {
    int64_t i;
    for (i = 0; i < size; i++)
        fn(arr[i]);
}

void PrintValue(int64_t x) {
    holyc_print("%d\n", x);
}

// Usage
ProcessArray(data, 100, PrintValue);
```

### 4.24 Classes with Methods
HolyC classes support member functions:

**Class Definition with Methods:**
```holyc
class CVector {
    F64 x, y, z;
};

U0 CVector->Init(F64 _x, F64 _y, F64 _z) {
    this->x = _x;
    this->y = _y;
    this->z = _z;
}

F64 CVector->Length() {
    return Sqrt(this->x * this->x + this->y * this->y + this->z * this->z);
}

U0 CVector->Add(CVector *other) {
    this->x += other->x;
    this->y += other->y;
    this->z += other->z;
}
```

**Translation Strategy:**
Convert methods to functions with explicit `this` parameter:
```c
typedef struct CVector {
    double x, y, z;
} CVector;

void CVector_Init(CVector *this, double _x, double _y, double _z) {
    this->x = _x;
    this->y = _y;
    this->z = _z;
}

double CVector_Length(CVector *this) {
    return sqrt(this->x * this->x + this->y * this->y + this->z * this->z);
}

void CVector_Add(CVector *this, CVector *other) {
    this->x += other->x;
    this->y += other->y;
    this->z += other->z;
}
```

**Method Invocation:**
```holyc
CVector *v = MAlloc(sizeof(CVector));
v->Init(1.0, 2.0, 3.0);
F64 len = v->Length();
```

**Translation:**
```c
CVector *v = holyc_malloc(sizeof(CVector));
CVector_Init(v, 1.0, 2.0, 3.0);
double len = CVector_Length(v);
```

**Implementation Notes:**
- Track method-to-function mapping in symbol table
- Generate function names as `ClassName_MethodName`
- Transform `obj->Method(args)` to `ClassName_Method(obj, args)`
- `this` keyword becomes first parameter

### 4.25 Class Inheritance
HolyC supports single inheritance:

**Base Class:**
```holyc
class CShape {
    I64 x, y;
};

U0 CShape->Draw() {
    "Drawing shape\n";
}

class CCircle : CShape {
    F64 radius;
};

U0 CCircle->Draw() {
    "Drawing circle\n";
}

F64 CCircle->Area() {
    return 3.14159 * this->radius * this->radius;
}
```

**Translation Strategy:**
Embed base class as first member:
```c
typedef struct CShape {
    int64_t x, y;
} CShape;

void CShape_Draw(CShape *this) {
    holyc_print("Drawing shape\n");
}

typedef struct CCircle {
    CShape base;  // Base class embedded
    double radius;
} CCircle;

void CCircle_Draw(CCircle *this) {
    holyc_print("Drawing circle\n");
}

double CCircle_Area(CCircle *this) {
    return 3.14159 * this->radius * this->radius;
}

// Access base members:
// circle->base.x, circle->base.y
```

**Method Resolution:**
```holyc
CCircle *c = MAlloc(sizeof(CCircle));
c->x = 10;           // Access base member
c->radius = 5.0;     // Access derived member
c->Draw();           // Calls CCircle->Draw
```

**Translation:**
```c
CCircle *c = holyc_malloc(sizeof(CCircle));
c->base.x = 10;
c->radius = 5.0;
CCircle_Draw(c);
```

**Note:** HolyC does not have virtual functions/dynamic dispatch. All method calls are statically resolved at compile time.

### 4.26 Arrays and Array Operations
HolyC supports both static and dynamic arrays:

**Static Arrays:**
```holyc
I64 arr[10];
I64 matrix[3][4];
```

**Dynamic Arrays:**
```holyc
I64 *arr = MAlloc(10 * sizeof(I64));
```

**Array Access:**
```holyc
arr[5] = 42;
I64 val = arr[5];
```

**Multi-dimensional:**
```holyc
matrix[2][3] = 99;
```

**Translation:**
```c
int64_t arr[10];
int64_t matrix[3][4];
int64_t *arr = holyc_malloc(10 * sizeof(int64_t));
arr[5] = 42;
int64_t val = arr[5];
matrix[2][3] = 99;
```

**Array Pointer Equivalence:**
```holyc
I64 *ptr = arr;     // Array decays to pointer
ptr[3] = 100;       // Equivalent to *(ptr + 3) = 100
```

### 4.27 Opaque Pointers and Handle Types
For interfacing with external libraries that use opaque types:

**HolyC Pattern:**
```holyc
class CDeviceHandle {
    U64 handle;  // Opaque handle from external library
};

_extern cuda_malloc U8* CudaMalloc(I64 size);
_extern cuda_free U0 CudaFree(U8 *ptr);
_extern cuda_memcpy U0 CudaMemcpy(U8 *dst, U8 *src, I64 size, I64 kind);

class CTensor {
    U8 *data;        // GPU pointer
    I64 shape[4];
    I64 ndim;
};

U0 CTensor->Init(I64 *dims, I64 n) {
    I64 i, size = 1;
    this->ndim = n;
    for (i = 0; i < n; i++) {
        this->shape[i] = dims[i];
        size *= dims[i];
    }
    this->data = CudaMalloc(size * sizeof(F64));
}

U0 CTensor->Free() {
    if (this->data)
        CudaFree(this->data);
}
```

**Translation:**
```c
typedef struct CDeviceHandle {
    uint64_t handle;
} CDeviceHandle;

extern uint8_t* cuda_malloc(int64_t size);
extern void cuda_free(uint8_t *ptr);
extern void cuda_memcpy(uint8_t *dst, uint8_t *src, int64_t size, int64_t kind);

typedef struct CTensor {
    uint8_t *data;
    int64_t shape[4];
    int64_t ndim;
} CTensor;

void CTensor_Init(CTensor *this, int64_t *dims, int64_t n) {
    int64_t i, size = 1;
    this->ndim = n;
    for (i = 0; i < n; i++) {
        this->shape[i] = dims[i];
        size *= dims[i];
    }
    this->data = cuda_malloc(size * sizeof(double));
}

void CTensor_Free(CTensor *this) {
    if (this->data)
        cuda_free(this->data);
}
```

### 4.28 Function Attributes
HolyC supports function flags for special behaviors:

**interrupt**: Interrupt handler (x86-specific)
```holyc
interrupt U0 MyIRQHandler() {
    // Handler code
}
```

**haserrcode**: Exception frame has error code
```holyc
interrupt haserrcode U0 PageFaultHandler() {
    // Handler with error code
}
```

**public**: Export symbol for external use
```holyc
public U0 ExportedFunction(I64 x) {
    // Visible to other modules
}
```

**argpop/noargpop**: Control argument cleanup
```holyc
argpop U0 CallerCleans(I64 x, I64 y) {
    // Arguments popped by caller
}
```

**Translation:**
Most attributes map to C calling conventions or are ignored:
```c
// public → regular function (default in C)
void ExportedFunction(int64_t x) { }

// interrupt → depends on platform, may need inline asm
__attribute__((interrupt)) void MyIRQHandler(void) { }
```

### 4.29 Register Variables
HolyC allows explicit register allocation:

**Register Specification:**
```holyc
U0 FastFunc() {
    I64 reg R15 counter = 0;
    I64 noreg temp = 100;
    // counter prefers R15, temp forced to stack
}
```

**Translation:**
```c
void FastFunc(void) {
    register int64_t counter __asm__("r15") = 0;
    int64_t temp = 100;
    // Register hints may be ignored by C compiler
}
```

**Note:** C compilers typically ignore register hints, treating them as suggestions.

## 5. Abstract Syntax Tree (AST)

### 5.1 Core Node Types
```python
class ASTNode:
    pass

class Program(ASTNode):
    declarations: List[Declaration]
    
class Declaration(ASTNode):
    pass

class FunctionDecl(Declaration):
    return_type: Type
    name: str
    parameters: List[Parameter]
    body: Block
    
class VarDecl(Declaration):
    type: Type
    name: str
    init: Optional[Expression]
    is_global: bool
    
class ClassDecl(Declaration):
    name: str
    members: List[VarDecl]
    base_class: Optional[str]
    methods: List[FunctionDecl]

class MethodDecl(FunctionDecl):
    class_name: str
    is_constructor: bool
    
class ExternDecl(Declaration):
    return_type: Type
    name: str
    parameters: List[Parameter]
    external_name: Optional[str]  # For _extern
    is_import: bool  # extern vs import
    
class Statement(ASTNode):
    pass

class Block(Statement):
    statements: List[Statement]
    
class IfStmt(Statement):
    condition: Expression
    then_block: Block
    else_block: Optional[Block]
    
class WhileStmt(Statement):
    condition: Expression
    body: Block
    
class ForStmt(Statement):
    init: Optional[Statement]
    condition: Optional[Expression]
    increment: Optional[Expression]
    body: Block
    
class SwitchStmt(Statement):
    expression: Expression
    cases: List[CaseStmt]
    is_unchecked: bool
    
class CaseStmt(ASTNode):
    values: List[int]  # Can be range
    is_range: bool
    is_auto: bool  # No explicit value
    statements: List[Statement]
    is_subswitch: bool
    subswitch_prefix: List[Statement]
    subswitch_suffix: List[Statement]
    
class ReturnStmt(Statement):
    value: Optional[Expression]
    
class TryCatchStmt(Statement):
    try_block: Block
    catch_block: Block
    
class ThrowStmt(Statement):
    value: Expression
    
class ExpressionStmt(Statement):
    expression: Expression
    
class Expression(ASTNode):
    pass

class BinaryOp(Expression):
    op: str
    left: Expression
    right: Expression
    
class UnaryOp(Expression):
    op: str
    operand: Expression
    
class CallExpr(Expression):
    function: Expression
    arguments: List[Expression]
    
class MemberAccess(Expression):
    object: Expression
    member: str
    is_method_call: bool

class MethodCall(Expression):
    object: Expression
    method: str
    arguments: List[Expression]
    
class ArrayAccess(Expression):
    array: Expression
    index: Expression

class PointerDeref(Expression):
    operand: Expression
    
class AddressOf(Expression):
    operand: Expression
    
class Literal(Expression):
    value: Any
    type: Type
    
class Identifier(Expression):
    name: str

class ThisExpr(Expression):
    pass  # 'this' keyword in methods
```

## 6. Implementation Phases

### Phase 1: Foundation (Week 1-2)
- [ ] Lexer with all HolyC tokens
- [ ] Basic type system
- [ ] Simple parser for variable declarations and assignments
- [ ] Basic code generator
- [ ] Runtime library header generation
- [ ] CLI tool

### Phase 2: Control Flow (Week 3)
- [ ] If/while/for statements
- [ ] Basic switch statements
- [ ] Function declarations and calls
- [ ] Return statements

### Phase 3: HolyC-Specific Features (Week 4-5)
- [ ] String/char literal sugar
- [ ] Multi-char literals
- [ ] Chained comparisons
- [ ] Power operator
- [ ] Default arguments
- [ ] Top-level code collection

### Phase 4: Advanced Switch (Week 6)
- [ ] Range cases
- [ ] Auto-increment cases
- [ ] Sub-switches
- [ ] Unchecked switches

### Phase 5: Object System (Week 7)
- [ ] Classes (structs)
- [ ] Class methods
- [ ] Method invocation (obj->Method())
- [ ] this keyword
- [ ] Single inheritance
- [ ] Unions
- [ ] Member access
- [ ] Sub-integer access
- [ ] Class metadata

### Phase 6: Advanced Features (Week 8)
- [ ] Try/catch/throw
- [ ] Variadic functions (argc/argv)
- [ ] Function pointers and callbacks
- [ ] Dynamic memory (MAlloc/Free/MSize)
- [ ] Pointer arithmetic
- [ ] lastclass keyword
- [ ] offset() function
- [ ] Lock blocks

### Phase 7: External Interfacing (Week 9)
- [ ] extern/import declarations
- [ ] _extern/_import with name binding
- [ ] External function calls
- [ ] Opaque pointer types
- [ ] C library interfacing
- [ ] Function attributes (public, interrupt, etc.)
- [ ] Register variable hints

### Phase 8: Preprocessor (Week 10)
- [ ] Basic directives
- [ ] #exe{} limited support
- [ ] Conditional compilation

### Phase 9: Testing & Polish (Week 11-12)
- [ ] Comprehensive test suite
- [ ] Error messages
- [ ] Code formatting options
- [ ] Documentation

## 7. Runtime Library

The transpiler will generate a `holyc_runtime.h` header that must be included:

```c
#ifndef HOLYC_RUNTIME_H
#define HOLYC_RUNTIME_H

#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdarg.h>
#include <setjmp.h>
#include <math.h>

// Type definitions
typedef void U0;
// ... (all type mappings)

// Integer unions for sub-access
typedef union { /* ... */ } holyc_i64_t;
typedef union { /* ... */ } holyc_u64_t;
// ... (similar for other sizes)

// Exception handling
typedef struct {
    jmp_buf jmp;
    uint64_t except_ch;
    int catch_except;
} holyc_exception_ctx_t;

extern holyc_exception_ctx_t *holyc_ex_ctx;

void holyc_throw(uint64_t ch);

// Variadic argument support
typedef struct {
    int64_t count;
    int64_t *args;
} holyc_varargs_t;

## 7. Runtime Library

The transpiler will generate a `holyc_runtime.h` header that must be included:

```c
#ifndef HOLYC_RUNTIME_H
#define HOLYC_RUNTIME_H

#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdarg.h>
#include <setjmp.h>
#include <math.h>

// Type definitions
typedef void U0;
typedef int8_t I8;
typedef uint8_t U8;
typedef int16_t I16;
typedef uint16_t U16;
typedef int32_t I32;
typedef uint32_t U32;
typedef int64_t I64;
typedef uint64_t U64;
typedef double F64;

// Integer unions for sub-access
typedef union {
    int64_t value;
    struct {
        uint8_t u8[8];
        int8_t i8[8];
        uint16_t u16[4];
        int16_t i16[4];
        uint32_t u32[2];
        int32_t i32[2];
    };
} holyc_i64_t;

typedef union {
    uint64_t value;
    struct {
        uint8_t u8[8];
        uint16_t u16[4];
        uint32_t u32[2];
    };
} holyc_u64_t;

// Similar for I32, U32, I16, U16

// Exception handling
typedef struct {
    jmp_buf jmp;
    uint64_t except_ch;
    int catch_except;
} holyc_exception_ctx_t;

extern holyc_exception_ctx_t *holyc_ex_ctx;

void holyc_throw(uint64_t ch);

// Variadic argument support
typedef struct {
    int64_t count;
    int64_t *args;
} holyc_varargs_t;

// Runtime functions
void holyc_print(const char *fmt, ...);
void holyc_putchars(uint64_t chars);
int64_t ToI64(double x);
double ToF64(int64_t x);
int ToBool(int64_t x);
double holyc_pow(double base, double exp);

// Memory management
void* holyc_malloc(size_t size);
void holyc_free(void *ptr);
void* holyc_calloc(size_t size);
size_t holyc_msize(void *ptr);
char* holyc_strdup(const char *str);

// Pointer utilities
void holyc_memcpy(void *dst, const void *src, size_t n);
void holyc_memset(void *ptr, int value, size_t n);
int holyc_memcmp(const void *a, const void *b, size_t n);

// TempleOS compatibility stubs
// ... (Dir, various system functions)

#endif
```

## 8. Code Generation Strategy

### 8.1 General Principles
1. **Readability First**: Generate clean, formatted C code
2. **Comments**: Preserve HolyC comments, add transpiler hints
3. **Naming**: Prefix generated symbols with `_holyc_` or `holyc_`
4. **Indentation**: Maintain 4-space indentation
5. **Line Mapping**: Emit `#line` directives to map back to HolyC source

### 8.2 Output Structure
```c
// Generated by HolyC transpiler from: source.HC
#include "holyc_runtime.h"

// Forward declarations
// ...

// Global variables
// ...

// Function definitions
// ...

// Top-level initialization
void _holyc_init(void) {
    // Top-level statements
}

int main(int argc, char **argv) {
    _holyc_init();
    return 0;
}
```

### 8.3 Pretty Printing
- Use an indentation tracker
- Break long lines intelligently
- Align similar declarations
- Group related code with blank lines

## 9. Error Handling

### 9.1 Lexer Errors
- Unterminated strings
- Invalid characters
- Malformed numbers

### 9.2 Parser Errors
- Syntax errors with context
- Show line and column
- Suggest corrections where possible

### 9.3 Semantic Errors
- Undefined symbols
- Type mismatches (where checkable)
- Invalid member access

### 9.4 Error Message Format
```
Error: [file.HC:line:col] Message
    5 | I64 x = "string";
        |         ^^^^^^^^ Cannot assign string to I64
```

## 10. Testing Strategy

### 10.1 Unit Tests
- Lexer: Token generation for all constructs
- Parser: AST construction for each language feature
- Code Gen: Output verification for each pattern

### 10.2 Integration Tests
Test complete HolyC programs:
- Hello World variations
- Mathematical calculations
- Control flow
- Data structures
- Error handling
- External library interfacing
- Class hierarchies with inheritance
- Callback systems

### 10.3 Practical Example Programs

#### 10.3.1 Vector Math Library with External FFI
```holyc
// Interface to external math library
_extern sqrt F64 Sqrt(F64 x);
_extern sin F64 Sin(F64 x);
_extern cos F64 Cos(F64 x);

class CVec3 {
    F64 x, y, z;
};

U0 CVec3->Init(F64 _x, F64 _y, F64 _z) {
    this->x = _x;
    this->y = _y;
    this->z = _z;
}

F64 CVec3->Length() {
    return Sqrt(this->x * this->x + this->y * this->y + this->z * this->z);
}

U0 CVec3->Normalize() {
    F64 len = this->Length();
    if (len > 0.0) {
        this->x /= len;
        this->y /= len;
        this->z /= len;
    }
}

CVec3* CVec3->Cross(CVec3 *other) {
    CVec3 *result = MAlloc(sizeof(CVec3));
    result->x = this->y * other->z - this->z * other->y;
    result->y = this->z * other->x - this->x * other->z;
    result->z = this->x * other->y - this->y * other->x;
    return result;
}

// Usage
CVec3 *v1 = MAlloc(sizeof(CVec3));
CVec3 *v2 = MAlloc(sizeof(CVec3));
v1->Init(1.0, 0.0, 0.0);
v2->Init(0.0, 1.0, 0.0);
CVec3 *v3 = v1->Cross(v2);
"Cross product: (%f, %f, %f)\n", v3->x, v3->y, v3->z;
```

#### 10.3.2 Callback-Based Event System
```holyc
class CEvent {
    U8 *name;
    I64 data;
};

U0 (*event_handler)(CEvent *evt);

U0 RegisterHandler(U0 (*handler)(CEvent *)) {
    event_handler = handler;
}

U0 TriggerEvent(U8 *name, I64 data) {
    CEvent *evt = MAlloc(sizeof(CEvent));
    evt->name = name;
    evt->data = data;
    if (event_handler)
        event_handler(evt);
    Free(evt);
}

U0 MyHandler(CEvent *evt) {
    "Event: %s, Data: %d\n", evt->name, evt->data;
}

// Usage
RegisterHandler(&MyHandler);
TriggerEvent("ButtonClick", 42);
```

#### 10.3.3 Device Driver Interface Pattern
```holyc
// External device driver interface
_extern device_init I64 DeviceInit(U8 *name);
_extern device_write U0 DeviceWrite(I64 handle, U8 *data, I64 size);
_extern device_read I64 DeviceRead(I64 handle, U8 *buffer, I64 size);
_extern device_close U0 DeviceClose(I64 handle);

class CDevice {
    I64 handle;
    U8 *name;
    I64 is_open;
};

U0 CDevice->Open(U8 *device_name) {
    this->name = device_name;
    this->handle = DeviceInit(device_name);
    this->is_open = (this->handle >= 0);
}

U0 CDevice->Write(U8 *data, I64 size) {
    if (this->is_open)
        DeviceWrite(this->handle, data, size);
}

I64 CDevice->Read(U8 *buffer, I64 size) {
    if (this->is_open)
        return DeviceRead(this->handle, buffer, size);
    return -1;
}

U0 CDevice->Close() {
    if (this->is_open) {
        DeviceClose(this->handle);
        this->is_open = 0;
    }
}

// Usage
CDevice *dev = MAlloc(sizeof(CDevice));
dev->Open("/dev/mydevice");
U8 buffer[256];
I64 bytes = dev->Read(buffer, 256);
dev->Close();
```

#### 10.3.4 Memory Pool Allocator
```holyc
class CMemPool {
    U8 *pool;
    I64 size;
    I64 used;
    I64 *free_list;
};

U0 CMemPool->Init(I64 pool_size) {
    this->size = pool_size;
    this->pool = MAlloc(pool_size);
    this->used = 0;
    this->free_list = NULL;
}

U8* CMemPool->Alloc(I64 size) {
    if (this->used + size > this->size)
        return NULL;
    U8 *ptr = this->pool + this->used;
    this->used += size;
    return ptr;
}

U0 CMemPool->Reset() {
    this->used = 0;
}

U0 CMemPool->Destroy() {
    Free(this->pool);
}
```

#### 10.3.5 Array Container with Dynamic Growth
```holyc
class CArray {
    I64 *data;
    I64 size;
    I64 capacity;
};

U0 CArray->Init(I64 initial_capacity) {
    this->capacity = initial_capacity;
    this->size = 0;
    this->data = MAlloc(initial_capacity * sizeof(I64));
}

U0 CArray->Push(I64 value) {
    if (this->size >= this->capacity) {
        // Grow array
        this->capacity *= 2;
        I64 *new_data = MAlloc(this->capacity * sizeof(I64));
        I64 i;
        for (i = 0; i < this->size; i++)
            new_data[i] = this->data[i];
        Free(this->data);
        this->data = new_data;
    }
    this->data[this->size] = value;
    this->size++;
}

I64 CArray->Get(I64 index) {
    if (index >= 0 && index < this->size)
        return this->data[index];
    return 0;
}

U0 CArray->Destroy() {
    Free(this->data);
}
```

### 10.4 Test Organization
```
tests/
├── unit/
│   ├── test_parser.py
│   └── ...
└── integration/
    ├── hello_world.hc
    └── ...
```

## 11. CLI Interface

```bash
# Basic usage
holyc-transpile input.HC -o output.c

# With runtime header generation
holyc-transpile input.HC -o output.c --generate-runtime

# Multiple files
holyc-transpile file1.HC file2.HC -o combined.c

# Pretty print options
holyc-transpile input.HC -o output.c --indent=4 --max-line-length=80

# Debug output
holyc-transpile input.HC --dump-tokens
holyc-transpile input.HC --dump-ast
holyc-transpile input.HC --verbose
```

## 12. Future Enhancements

### 12.1 Optimization
- Dead code elimination
- Constant folding
- Inline small functions

### 12.2 Assembly Support
- Parse basic asm blocks
- Convert to GCC inline assembly

### 12.3 Documentation Generation
- Extract DolDoc comments
- Generate Markdown/HTML docs

### 12.4 IDE Integration
- Language server protocol
- VS Code extension
- Syntax highlighting

## 13. Dependencies

### 13.1 Python Standard Library Only
- `re` - Regular expressions for lexer
- `argparse` - CLI argument parsing
- `dataclasses` - AST node definitions
- `typing` - Type hints
- `pathlib` - File operations
- `sys`, `os` - System operations

### 13.2 Optional Dependencies
- `pytest` - Testing (dev only)
- `black` - Code formatting (dev only)
- `mypy` - Type checking (dev only)

## 14. Documentation

### 14.1 User Documentation
- README with quick start
- Installation guide
- Feature compatibility matrix
- Examples gallery
- Troubleshooting guide

### 14.2 Developer Documentation
- Architecture overview
- Adding new features
- Testing guidelines
- Code style guide

## 15. Success Criteria

The transpiler is considered successful when it can:

1. ✅ Transpile all example programs from holyc_spec.md
2. ✅ Generate compilable C code (gcc/clang with -std=c11)
3. ✅ Produce executables with identical behavior to HolyC
4. ✅ Generate readable, well-formatted C code
5. ✅ Provide helpful error messages
6. ✅ Handle all key HolyC language features
7. ✅ Support class methods and single inheritance
8. ✅ Interface with external C libraries via extern/_extern
9. ✅ Support function pointers and callbacks
10. ✅ Handle dynamic memory allocation (MAlloc/Free)
11. ✅ Process realistic HolyC programs (>500 lines)
12. ✅ Support systems programming patterns (device drivers, pools, containers)
13. ✅ Maintain <1 second transpile time for typical files
14. ✅ Have >90% test coverage
15. ✅ Include comprehensive documentation

## 16. Limitations & Trade-offs

### 16.1 Accepted Limitations
- No TempleOS-specific system calls (provide stubs)
- Limited #exe{} support (static evaluation only)
- No JIT compilation features
- No inline assembly (initially)
- No direct memory access (can be added)

### 16.2 Design Trade-offs
- **Simplicity vs Performance**: Prioritize simple, correct translation over optimal C
- **Compatibility vs Purity**: Generate idiomatic C even if verbose
- **Features vs Timeline**: Core features first, advanced features later
- **Error Detection**: Some errors caught at C compile time rather than transpile time

## 17. Conclusion

This design provides a clear path to building a faithful HolyC to C transpiler that:
- Respects the unique features of HolyC
- Generates clean, readable C code
- Maintains simplicity in implementation
- Can be built incrementally
- Is fully testable
- Supports advanced systems programming patterns
- Enables seamless C library interfacing
- Provides complete object-oriented programming support
- Handles complex memory management scenarios

The phased approach allows for steady progress while delivering working features at each stage. The focus on simplicity and readability ensures the transpiler remains maintainable and the generated code is debuggable.

### 17.1 Advanced Use Cases Enabled

This transpiler design supports sophisticated applications including:

**Systems Programming**: Device drivers, kernel modules, embedded systems
**Scientific Computing**: High-performance numerical libraries with external BLAS/LAPACK
**Graphics Programming**: OpenGL/Vulkan wrappers, game engines
**Hardware Acceleration**: CUDA/OpenCL interfaces, GPU computing
**Real-time Systems**: Callback-based event loops, interrupt handlers
**Data Structures**: Custom allocators, containers, trees, graphs
**Network Programming**: Socket wrappers, protocol implementations

The comprehensive FFI support, class system with methods, and pointer operations make HolyC suitable for any task requiring low-level control while maintaining the clean, concise syntax that makes HolyC unique.
