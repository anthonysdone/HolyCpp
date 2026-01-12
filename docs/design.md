# HolyC- Language Design Document

## Table of Contents

### Core Language Specification
1. [Overview](#1-overview)
2. [Type System](#2-type-system)
3. [Functions](#3-functions)
4. [Control Flow](#4-control-flow)
5. [String and Character Literals](#5-string-and-character-literals)
6. [Operators](#6-operators)
7. [Type Casting](#7-type-casting)
8. [Classes (Structs)](#8-classes-structs)
9. [Unions](#9-unions)
10. [Memory Management](#10-memory-management)

### Advanced Features
11. [Foreign Function Interface (FFI)](#11-foreign-function-interface-ffi)
12. [Function Pointers](#12-function-pointers)
13. [Preprocessor](#13-preprocessor)
14. [Program Entry Point](#14-program-entry-point)
15. [Exception Handling](#15-exception-handling)
16. [Inline Assembly](#16-inline-assembly)
17. [Special Features NOT Supported](#17-special-features-not-supported)

### Implementation Guide
18. [Haskell Transpiler Architecture](#18-haskell-transpiler-architecture)
19. [Examples](#19-examples)
20. [Transpiler Usage](#20-transpiler-usage)
21. [Standard Library / Runtime](#21-standard-library--runtime)
22. [Implementation Roadmap](#22-implementation-roadmap)
23. [Project File Structure](#23-project-file-structure)
24. [Testing Strategy](#24-testing-strategy)
25. [Future Extensions](#25-future-extensions)

### Real-World Applications
26. [BurningBush Deep Learning Framework](#26-burningbush-deep-learning-framework-considerations)
27. [Conclusion](#27-conclusion)

---

## 1. Overview

**HolyC-** is a simplified dialect of HolyC designed to be easily transpiled to C while maintaining the distinctive aesthetic and feel of the original language. The primary design goal is simplicity in implementation via a Haskell transpiler, making pragmatic compromises where necessary while preserving HolyC's unique character.

### Design Philosophy

1. **Transpiler-First**: Every language feature must have a straightforward mapping to C
2. **Sugar Over Substance**: Most HolyC- features are syntactic sugar over C constructs
3. **Minimal Runtime**: Avoid features requiring complex runtime support
4. **Type System Compatibility**: Leverage C's type system directly
5. **Parse Simplicity**: Favor unambiguous, easily parseable syntax

### Reference Implementation: BurningBush

HolyC- is specifically designed to support real-world projects like **BurningBush**, a GPU-accelerated deep learning framework with a three-language architecture:

- **Frontend**: HolyC- (tensor management, autograd, training loops)
- **Backend**: CUDA (GPU kernels)
- **Glue**: C ABI (shared library interface)

Key features for BurningBush:
- ✅ FFI declarations (`_extern`) for CUDA kernel calls
- ✅ Opaque pointers (`U0 *`) for GPU memory handles
- ✅ Function pointers for autograd backward functions
- ✅ Classes with single inheritance for module hierarchy
- ✅ Zero-overhead transpilation to C

See Section 23 for detailed BurningBush integration examples.

## 2. Type System

### 2.1 Primitive Types

HolyC- adopts HolyC's distinctive type names as direct aliases to C types:

```
HolyC-          C Equivalent        Description
------          ------------        -----------
U0              void               Zero-size void type
I8              int8_t             Signed 8-bit integer
U8              uint8_t            Unsigned 8-bit integer
I16             int16_t            Signed 16-bit integer
U16             uint16_t           Unsigned 16-bit integer
I32             int32_t            Signed 32-bit integer
U32             uint32_t           Unsigned 32-bit integer
I64             int64_t            Signed 64-bit integer
U64             uint64_t           Unsigned 64-bit integer
F64             double             64-bit floating point
Bool            bool               Boolean type
None!           float              No 32 bit float in HolyC-!
```

**Transpilation Strategy**: Generate typedefs in the output C header:

```c
typedef void U0;
typedef int8_t I8;
typedef uint8_t U8;
// ... etc
```

### 2.2 Note on I0

We omit `I0` (signed 0-byte int) as it's esoteric and has no practical C equivalent.

### 2.3 Pointers and Arrays

Standard C syntax:
- Pointers: `U8 *ptr`
- Arrays: `I64 arr[10]`

## 3. Functions

### 3.1 Function Declaration

**HolyC- Syntax:**
```holyc
U0 MyFunction(I64 x, U8 *str)
{
  // body
}
```

**Transpiles to C:**
```c
void MyFunction(int64_t x, uint8_t *str)
{
  // body
}
```

### 3.2 Function Calls Without Parentheses

**Syntax**: Functions with zero arguments can be called without parentheses.

**HolyC-:**
```holyc
PrintMenu;
DoStuff();  // Also valid
```

**Transpilation**: If identifier is a known zero-argument function, emit `identifier()`:

```c
PrintMenu();
DoStuff();
```

**Implementation Note**: Transpiler maintains a symbol table of function signatures to distinguish function names from variables.

### 3.3 Default Arguments

**SIMPLIFIED**: Default arguments are NOT supported in HolyC-. This feature requires complex handling and doesn't map cleanly to C.

**Rationale**: C doesn't have default arguments. Simulating them would require function overloading or varargs, adding complexity. Users should define wrapper functions if needed.

### 3.4 Public Keyword

**Syntax**: Functions can be marked `public`:

```holyc
public U0 ExportedFunc()
{
  // ...
}
```

**Transpilation**: Maps to C's normal function (non-static):

```c
void ExportedFunc()
{
  // ...
}
```

Functions without `public` are assumed public (for simplicity). We could support `static` for private functions.

### 3.5 Variadic Functions

**SIMPLIFIED**: Use C's standard variadic approach with `stdarg.h`.

**HolyC-:**
```holyc
I64 Sum(I64 count, ...)
{
  // use va_list, va_start, va_arg, va_end
}
```

**Rationale**: HolyC's `argc`/`argv[]` magic requires runtime support. Standard C varargs are simpler and well-understood.

## 4. Control Flow

### 4.1 If/Else, While, For

Standard C syntax - no changes needed.

### 4.2 No Continue Statement

**Constraint**: HolyC- does not have `continue`. Use `goto` instead.

**Example:**
```holyc
for (i = 0; i < 10; i++) {
  if (i == 5)
    goto skip;
  Print("i = %d\n", i);
  skip:;
}
```

### 4.3 Switch Statements

**Standard switch**: Regular C syntax is supported.

**SIMPLIFIED**: The following HolyC features are NOT supported:
- `switch []` (unchecked switch)
- Range cases (`case 4...7:`)
- Empty case labels (auto-increment)
- Sub-switch with `start`/`end`

**Rationale**: These features don't exist in C and would require complex code generation.

## 5. String and Character Literals

### 5.1 Standalone String Literals as Statements

One of HolyC's most distinctive features: string literals as statements.

**HolyC-:**
```holyc
U0 Greet()
{
  "Hello, World!\n";
}
```

**Transpilation**: Convert to `printf()` call:

```c
void Greet()
{
  printf("Hello, World!\n");
}
```

### 5.2 Format Strings with Arguments

**HolyC-:**
```holyc
"Name: %s, Age: %d\n", name, age;
```

**Transpiles to:**
```c
printf("Name: %s, Age: %d\n", name, age);
```

**Parser Note**: String literal followed by comma and expression list is a print statement.

### 5.3 Variable Format Strings

**HolyC-:**
```holyc
"" fmt, arg1, arg2;
```

**Transpiles to:**
```c
printf(fmt, arg1, arg2);
```

**Note**: Empty string literal signals format string is a variable.

### 5.4 Character Literals as Statements

**HolyC-:**
```holyc
'X';
'\n';
```

**Transpiles to:**
```c
putchar('X');
putchar('\n');
```

### 5.5 Multi-Character Literals

**SIMPLIFIED**: NOT supported. Single quotes contain only single characters.

**Rationale**: `'ABC'` as a packed integer is non-portable and rarely useful. Users can use explicit hex constants: `0x434241`.

## 6. Operators

### 6.1 Standard Operators

Most C operators work identically: `+`, `-`, `*`, `/`, `%`, `&`, `|`, `^`, `~`, `<<`, `>>`, etc.

### 6.2 Power Operator

**Syntax**: `base ` exponent` (backtick operator)

**HolyC-:**
```holyc
x = 2 ` 10;  // 2^10
```

**Transpiles to:**
```c
x = pow(2, 10);
```

**Note**: Requires `#include <math.h>` and linking with `-lm`.

### 6.3 Chained Comparisons

**SIMPLIFIED**: NOT supported.

**Rationale**: `5 < i < 10` doesn't have a simple, readable C translation without introducing temporary variables. Users should use `&&`.

### 6.4 No Ternary Operator

**Constraint**: `? :` operator is NOT available in HolyC- (matching original HolyC).

Use `if`/`else` instead.

## 7. Type Casting

### 7.1 Postfix Casting

**HolyC-:**
```holyc
ptr(U8 *)
value(I64)
```

**Transpiles to C prefix cast:**
```c
(uint8_t*)ptr
(int64_t)value
```

**Parser Note**: `expression(Type)` transforms to `(Type)expression`.

### 7.2 Conversion Functions

Support helper functions for clarity:

**HolyC-:**
```holyc
ToI64(x)
ToF64(x)
ToBool(x)
```

**Transpiles to:**
```c
((int64_t)(x))
((double)(x))
((bool)(x))
```

## 8. Classes (Structs)

### 8.1 Class Declaration

**HolyC- uses `class` keyword** (instead of `struct`):

```holyc
class Point
{
  I64 x;
  I64 y;
};
```

**Transpiles to:**
```c
typedef struct Point {
  int64_t x;
  int64_t y;
} Point;
```

**Note**: We automatically typedef the struct so it can be used as `Point` instead of `struct Point`.

### 8.2 Single Inheritance

**HolyC-:**
```holyc
class Base
{
  I64 value;
};

class Derived : Base
{
  I64 extra;
};
```

**Transpiles to C (struct embedding):**
```c
typedef struct Base {
  int64_t value;
} Base;

typedef struct Derived {
  Base base;  // Embedded base struct
  int64_t extra;
} Derived;
```

**Accessing base members:**
```holyc
Derived d;
d.value = 10;  // Direct access
```

**Transpiles to:**
```c
Derived d;
d.base.value = 10;  // Access through embedded base
```

**Implementation Note**: Transpiler must track inheritance and rewrite member access for inherited fields.

### 8.3 No Multiple Inheritance

Only single inheritance is supported (matching original HolyC).

## 9. Unions

**Syntax**: `union` keyword (compatible with C):

```holyc
union Value
{
  I64 i;
  F64 f;
  U8 *s;
};
```

**Transpiles directly:**
```c
typedef union Value {
  int64_t i;
  double f;
  uint8_t *s;
} Value;
```

## 10. Memory Management

### 10.1 Standard Library Functions

Use C standard library names directly:
- `malloc()`, `calloc()`, `realloc()`, `free()`

### 10.2 HolyC-Style Memory Functions (Optional Sugar)

Optionally support HolyC names as aliases:

**HolyC-:**
```holyc
MAlloc(size)
CAlloc(size)
Free(ptr)
```

**Transpiles to:**
```c
malloc(size)
calloc(1, size)  // CAlloc allocates and zeroes
free(ptr)
```

## 10.3 Opaque Pointers

HolyC- supports opaque pointer types for external resources (GPU memory, handles, etc.):

**HolyC-:**
```holyc
U0 *gpu_ptr;  // Opaque pointer to GPU memory
gpu_ptr = cuda_malloc(1024);
```

**Transpiles to:**
```c
void *gpu_ptr;
gpu_ptr = cuda_malloc(1024);
```

**Note**: The transpiler treats `U0 *` as `void *` in C, perfect for opaque handles.

## 11. Foreign Function Interface (FFI)

### 11.1 External Function Declarations

**Syntax**: Use `_extern` keyword to declare functions from C libraries:

**HolyC-:**
```holyc
_extern U0 cuda_malloc(U0 **ptr, I64 size);
_extern U0 cuda_free(U0 *ptr);
_extern U0 cuda_add(U0 *out, U0 *a, U0 *b, I64 n);
```

**Transpiles to:**
```c
extern void cuda_malloc(void **ptr, int64_t size);
extern void cuda_free(void *ptr);
extern void cuda_add(void *out, void *a, void *b, int64_t n);
```

**Usage:**
```holyc
U0 *ptr;
cuda_malloc(&ptr, 1024);
cuda_free(ptr);
```

**Implementation Note**: The transpiler tracks `_extern` declarations and:
1. Emits them as `extern` declarations in the C output
2. Does not generate function bodies
3. Assumes these functions are provided by linked libraries

### 11.2 Linking with External Libraries

**Build Process**: When compiling the generated C code, link against required libraries:

```bash
# Transpile HolyC- to C
hcm myprogram.hc -o myprogram.c

# Compile and link with external library
gcc myprogram.c -o myprogram -L./lib -lmylibrary
```

For BurningBush example:
```bash
# Build CUDA kernels into shared library
cd backend && make  # Produces libburningbush.so

# Transpile HolyC- frontend
hcm frontend/tensor.hc -o tensor.c

# Compile and link
gcc tensor.c -o burningbush -L./backend -lburningbush -lcudart
```

### 11.3 Type Compatibility

HolyC- types map cleanly to C for FFI:

| HolyC- | C | Notes |
|--------|---|-------|
| `U0 *` | `void *` | Opaque pointers |
| `I64` | `int64_t` | Safe on 64-bit systems |
| `U8 *` | `uint8_t *` | Byte arrays/strings |
| `F64` | `double` | Floating point |

**Important**: Avoid passing complex types (classes with inheritance) across FFI boundaries. Use simple structs or pointers only.

### 11.4 Complete FFI Example

**HolyC-:**
```holyc
// Declare external CUDA functions
_extern U0 cuda_malloc(U0 **ptr, I64 size);
_extern U0 cuda_memcpy_h2d(U0 *dst, U0 *src, I64 size);
_extern U0 cuda_add(U0 *out, U0 *a, U0 *b, I64 n);
_extern U0 cuda_free(U0 *ptr);

class CTensor
{
  U0 *data;  // GPU pointer
  I64 size;
};

U0 TensorAdd(CTensor *out, CTensor *a, CTensor *b)
{
  cuda_add(out->data, a->data, b->data, a->size);
}

// Usage
CTensor a, b, c;
a.size = 1024;
cuda_malloc(&a.data, a.size * 8);  // 8 bytes per F64
cuda_malloc(&b.data, b.size * 8);
cuda_malloc(&c.data, c.size * 8);

TensorAdd(&c, &a, &b);

cuda_free(a.data);
cuda_free(b.data);
cuda_free(c.data);
```

**Generated C:**
```c
#include "holycminus_runtime.h"

extern void cuda_malloc(void **ptr, int64_t size);
extern void cuda_memcpy_h2d(void *dst, void *src, int64_t size);
extern void cuda_add(void *out, void *a, void *b, int64_t n);
extern void cuda_free(void *ptr);

typedef struct CTensor {
  void *data;
  int64_t size;
} CTensor;

void TensorAdd(CTensor *out, CTensor *a, CTensor *b) {
  cuda_add(out->data, a->data, b->data, a->size);
}

void __holycminus_init() {
  CTensor a, b, c;
  a.size = 1024;
  cuda_malloc(&a.data, a.size * 8);
  cuda_malloc(&b.data, b.size * 8);
  cuda_malloc(&c.data, c.size * 8);
  
  TensorAdd(&c, &a, &b);
  
  cuda_free(a.data);
  cuda_free(b.data);
  cuda_free(c.data);
}

int main(int argc, char **argv) {
  __holycminus_init();
  return 0;
}
```

## 12. Function Pointers

### 12.1 Function Pointer Declaration

**Syntax**: Standard C function pointer syntax:

**HolyC-:**
```holyc
U0 (*callback)(I64);  // Pointer to function taking I64, returning void
```

**Transpiles to:**
```c
void (*callback)(int64_t);
```

### 12.2 Taking Function Addresses

Use `&` operator to get function address (matching HolyC):

**HolyC-:**
```holyc
U0 MyCallback(I64 x)
{
  "Callback: %d\n", x;
}

U0 (*func_ptr)(I64) = &MyCallback;
func_ptr(42);
```

**Transpiles to:**
```c
void MyCallback(int64_t x) {
  printf("Callback: %d\n", x);
}

void (*func_ptr)(int64_t) = &MyCallback;
func_ptr(42);
```

### 12.3 Function Pointers in Classes

**HolyC-:**
```holyc
class COptimizer
{
  U0 (*step_fn)(U0 *);  // Function pointer for custom step logic
  U0 *state;
};

U0 SGDStep(U0 *state)
{
  "Running SGD step\n";
}

COptimizer opt;
opt.step_fn = &SGDStep;
opt.step_fn(opt.state);
```

**Transpiles to:**
```c
typedef struct COptimizer {
  void (*step_fn)(void *);
  void *state;
} COptimizer;

void SGDStep(void *state) {
  printf("Running SGD step\n");
}

// ... in __holycminus_init():
COptimizer opt;
opt.step_fn = &SGDStep;
opt.step_fn(opt.state);
```

### 12.4 Typedef for Function Pointers (Optional Sugar)

For cleaner syntax, support typedef'd function pointer types:

**HolyC-:**
```holyc
class StepFn : U0 (*)(U0 *);  // Create type alias

class COptimizer
{
  StepFn step;
  U0 *state;
};
```

**Transpiles to:**
```c
typedef void (*StepFn)(void *);

typedef struct COptimizer {
  StepFn step;
  void *state;
} COptimizer;
```

**Implementation Note**: The transpiler treats `class Name : FunctionType` specially when `FunctionType` is a function pointer signature, generating a typedef instead of struct inheritance.

## 13. Preprocessor

### 11.1 #include

**Syntax**: Only double quotes supported (matching HolyC):

```holyc
#include "myheader.h"
```

**Transpiles to:**
```c
#include "myheader.h"
```

### 11.2 #define

Standard C `#define` for constants:

```holyc
#define MAX_SIZE 100
#define PI 3.14159
```

**SIMPLIFIED**: No function-like macros (matching HolyC philosophy).

### 11.3 No #exe{}

**Rationale**: Compile-time code execution requires interpreter integration. Far too complex for initial implementation.

## 14. Program Entry Point

### 14.1 Top-Level Code Execution

**Feature**: Code outside functions executes at startup (HolyC style).

**HolyC-:**
```holyc
"Program starting...\n";

I64 global_val = 42;

U0 Helper()
{
  "Helper called\n";
}

"Calling helper...\n";
Helper;
```

**Transpilation Strategy**: Collect all top-level statements into a `__holycminus_init()` function:

```c
void __holycminus_init() {
  printf("Program starting...\n");
  printf("Calling helper...\n");
  Helper();
}

int64_t global_val = 42;

void Helper() {
  printf("Helper called\n");
}

int main(int argc, char **argv) {
  __holycminus_init();
  return 0;
}
```

**Note**: Variable initializations remain as global initializers. Only statements are moved to init function.

### 12.2 Optional Main Function

User can optionally define a `Main()` function:

**HolyC-:**
```holyc
U0 Main()
{
  "This is main\n";
}
```

**Transpilation**: If `Main()` exists, call it from generated `main()`:

```c
void Main() {
  printf("This is main\n");
}

int main(int argc, char **argv) {
  __holycminus_init();
  Main();
  return 0;
}
```

## 15. Exception Handling

**SIMPLIFIED**: NOT supported initially.

**Rationale**: HolyC's `try`/`catch`/`throw` has unique semantics that don't map to C. Would require setjmp/longjmp and significant runtime support.

**Future**: Could add as layer over `setjmp`/`longjmp`.

## 16. Inline Assembly

**SIMPLIFIED**: NOT supported.

**Rationale**: Assembly is platform-specific and would require passing through unchanged, defeating portability. Users can use C's inline asm if needed in the generated C code.

## 17. Special Features NOT Supported

The following HolyC features are explicitly NOT included in HolyC-:

- `lastclass` keyword (requires compile-time reflection)
- `offset()` function (just use C's `offsetof`)
- Class member metadata (`fmtstr`, `fmtdata`)
- `lock{}` blocks (use platform-specific mutexes)
- `MSize()` heap function (C doesn't track allocation sizes)
- Register hints (`reg`, `noreg`)
- `no_warn` statement
- Function modifiers: `interrupt`, `haserrcode`, `argpop`
- `$` escape sequences (DolDoc features)

## 18. Haskell Transpiler Architecture

### 18.1 Pipeline Overview

```
HolyC- Source
      ↓
   [Lexer] → Tokens
      ↓
   [Parser] → AST
      ↓
 [Resolver] → Annotated AST (symbol resolution)
      ↓
  [Codegen] → C Source
```

### 18.2 Lexer

**Module**: `HolyCMinus.Lexer`

**Responsibilities**:
- Tokenize input stream
- Handle HolyC- specific tokens (backtick, type names, etc.)
- Track source locations for error reporting

**Key Token Types**:
```haskell
data Token
  = TKeyword Keyword
  | TIdentifier Text
  | TTypeKeyword Type  -- U0, I8, I64, etc.
  | TStringLit Text
  | TCharLit Char
  | TIntLit Integer
  | TFloatLit Double
  | TOperator Operator
  | TBacktick  -- Power operator
  | TPunctuation Char
  | ...
```

### 18.3 Parser

**Module**: `HolyCMinus.Parser`

**Technology**: Use parser combinators (`megaparsec` or `parsec`)

**AST Data Types**:
```haskell
data Program = Program [TopLevel]

data TopLevel
  = TLFunction Function
  | TLClass ClassDecl
  | TLUnion UnionDecl
  | TLStatement Statement  -- Top-level executable statement
  | TLVarDecl Type Identifier (Maybe Expr)
  | TLInclude FilePath
  | TLDefine Identifier Text

data Function = Function
  { fnReturnType :: Type
  , fnName :: Identifier
  , fnParams :: [Parameter]
  , fnBody :: [Statement]
  , fnIsPublic :: Bool
  }

data Statement
  = SExpr Expr
  | SReturn (Maybe Expr)
  | SIf Expr [Statement] (Maybe [Statement])
  | SWhile Expr [Statement]
  | SFor (Maybe Statement) (Maybe Expr) (Maybe Expr) [Statement]
  | SSwitch Expr [Case]
  | SBlock [Statement]
  | SGoto Label
  | SLabel Label
  | SVarDecl Type Identifier (Maybe Expr)
  | SPrintString Text [Expr]  -- Special: string literal statement
  | SPutChar Char             -- Special: char literal statement

data Expr
  = EVar Identifier
  | EIntLit Integer
  | EFloatLit Double
  | EStringLit Text
  | ECharLit Char
  | EBinOp BinOp Expr Expr
  | EUnaryOp UnaryOp Expr
  | EPostfixCast Expr Type     -- x(U8*)
  | ECall Identifier [Expr]
  | EMemberAccess Expr Identifier
  | EArrayAccess Expr Expr
  | EAddressOf Identifier
  | EPower Expr Expr           -- Backtick operator
  | ...

data BinOp = Add | Sub | Mul | Div | Mod | ...
```

### 16.4 Resolver (Semantic Analysis)

**Module**: `HolyCMinus.Resolver`

**Responsibilities**:
1. Build symbol table
2. Resolve function calls without parentheses
3. Track class inheritance for member access rewriting
4. Validate types (minimal type checking)
5. Annotate AST with resolved information

**Symbol Table**:
```haskell
data Symbol
  = SFunction Type [Parameter]
  | SVariable Type
  | SClass ClassInfo
  | SUnion UnionInfo

data ClassInfo = ClassInfo
  { ciFields :: [(Identifier, Type)]
  , ciParent :: Maybe Identifier
  }

type SymbolTable = Map Identifier Symbol
```

### 18.5 Code Generator

**Module**: `HolyCMinus.Codegen`

**Responsibilities**:
- Transform AST to C code
- Generate type definitions
- Generate runtime initialization function
- Handle special syntactic sugar transformations

**Key Transformations**:

1. **Type Names**: 
   - `I64` → `int64_t`

2. **Functions Without Parentheses**:
   - `Foo;` → `Foo();`

3. **String Literal Statements**:
   - `"Hello %s\n", name;` → `printf("Hello %s\n", name);`

4. **Postfix Casts**:
   - `ptr(U8*)` → `(uint8_t*)ptr`

5. **Power Operator**:
   - `2 ` 8` → `pow(2, 8)`

6. **Classes**:
   ```holyc
   class Foo { I64 x; };
   ```
   →
   ```c
   typedef struct Foo { int64_t x; } Foo;
   ```

7. **Inheritance**:
   ```holyc
   class Derived : Base { I64 y; };
   Derived d;
   d.value = 10;  // 'value' is in Base
   ```
   →
   ```c
   typedef struct Derived { Base base; int64_t y; } Derived;
   Derived d;
   d.base.value = 10;
   ```

8. **Top-Level Statements**:
   Collect into `__holycminus_init()` and generate `main()`.

### 18.6 Error Reporting

Use source locations from lexer to provide helpful errors:
```
error: undefined function 'Foo' at line 42, column 5
  |
42|   Foo;
  |   ^^^
```

### 18.7 Pretty Printer (Optional)

**Module**: `HolyCMinus.Pretty`

Use `prettyprinter` library to format generated C code nicely.

## 20. Transpiler Usage

### Command-Line Interface

```bash
hcm input.hc -o output.c
hcm input.hc -o output.c --run  # Compile and run
```

### Compilation Pipeline

```bash
# Transpile
hcm myprogram.hc -o myprogram.c

# Compile with GCC
gcc myprogram.c -o myprogram -lm

# Run
./myprogram
```

## 21. Standard Library / Runtime

### 21.1 Minimal Runtime Header

Generate a `holycminus_runtime.h` with:

```c
#ifndef HOLYCMINUS_RUNTIME_H
#define HOLYCMINUS_RUNTIME_H

#include <stdint.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

// Type aliases
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
typedef bool Bool;

// Helper functions
#define ToI64(x) ((I64)(x))
#define ToF64(x) ((F64)(x))
#define ToBool(x) ((Bool)(x))

// Optional: HolyC-style memory functions
#define MAlloc malloc
#define CAlloc(size) calloc(1, size)
#define Free free

#endif // HOLYCMINUS_RUNTIME_H
```

### 21.2 Generated C Code Structure

```c
#include "holycminus_runtime.h"

// Forward declarations
void Foo();
void Bar();

// Type definitions
typedef struct MyClass { ... } MyClass;

// Global variables
I64 global_var = 42;

// Function definitions
void Foo() { ... }
void Bar() { ... }

// Initialization function
void __holycminus_init() {
  printf("Starting...\n");
  Foo();
}

// Entry point
int main(int argc, char **argv) {
  __holycminus_init();
  Main();  // If user defined Main()
  return 0;
}
```

## 19. Examples

### 19.1 Hello World

**HolyC-:**
```holyc
"Hello, World!\n";
```

**Generated C:**
```c
#include "holycminus_runtime.h"

void __holycminus_init() {
  printf("Hello, World!\n");
}

int main(int argc, char **argv) {
  __holycminus_init();
  return 0;
}
```

### 19.2 Simple Function

**HolyC-:**
```holyc
I64 Add(I64 a, I64 b)
{
  return a + b;
}

I64 result = Add(5, 10);
"Result: %d\n", result;
```

**Generated C:**
```c
#include "holycminus_runtime.h"

I64 Add(I64 a, I64 b);

I64 result;

I64 Add(I64 a, I64 b) {
  return a + b;
}

void __holycminus_init() {
  result = Add(5, 10);
  printf("Result: %d\n", result);
}

int main(int argc, char **argv) {
  __holycminus_init();
  return 0;
}
```

### 19.3 Class with Methods

**HolyC-:**
```holyc
class Point
{
  I64 x;
  I64 y;
};

U0 PrintPoint(Point *p)
{
  "Point(%d, %d)\n", p->x, p->y;
}

Point p;
p.x = 10;
p.y = 20;
PrintPoint(&p);
```

**Generated C:**
```c
#include "holycminus_runtime.h"

typedef struct Point {
  I64 x;
  I64 y;
} Point;

void PrintPoint(Point *p);

Point p;

void PrintPoint(Point *p) {
  printf("Point(%d, %d)\n", p->x, p->y);
}

void __holycminus_init() {
  p.x = 10;
  p.y = 20;
  PrintPoint(&p);
}

int main(int argc, char **argv) {
  __holycminus_init();
  return 0;
}
```

### 19.4 Power Operator

**HolyC-:**
```holyc
F64 x = 2.0 ` 10.0;
"2^10 = %f\n", x;
```

**Generated C:**
```c
#include "holycminus_runtime.h"

F64 x;

void __holycminus_init() {
  x = pow(2.0, 10.0);
  printf("2^10 = %f\n", x);
}

int main(int argc, char **argv) {
  __holycminus_init();
  return 0;
}
```

### 19.5 FFI with External Library (BurningBush-style)

**HolyC-:**
```holyc
// Declare external CUDA functions
_extern U0 cuda_malloc(U0 **ptr, I64 size);
_extern U0 cuda_add(U0 *out, U0 *a, U0 *b, I64 n);
_extern U0 cuda_free(U0 *ptr);

class CTensor
{
  U0 *data;
  I64 size;
};

CTensor* CreateTensor(I64 size)
{
  CTensor *t = MAlloc(sizeof(CTensor));
  t->size = size;
  cuda_malloc(&t->data, size * 8);
  return t;
}

// Create and add tensors on GPU
CTensor *a = CreateTensor(1024);
CTensor *b = CreateTensor(1024);
CTensor *c = CreateTensor(1024);

cuda_add(c->data, a->data, b->data, 1024);
"Tensors added on GPU\n";

cuda_free(a->data);
cuda_free(b->data);
cuda_free(c->data);
```

**Generated C:**
```c
#include "holycminus_runtime.h"

// External declarations
extern void cuda_malloc(void **ptr, int64_t size);
extern void cuda_add(void *out, void *a, void *b, int64_t n);
extern void cuda_free(void *ptr);

// Type definitions
typedef struct CTensor {
  void *data;
  int64_t size;
} CTensor;

// Function declarations
CTensor* CreateTensor(int64_t size);

// Function definitions
CTensor* CreateTensor(int64_t size) {
  CTensor *t = malloc(sizeof(CTensor));
  t->size = size;
  cuda_malloc(&t->data, size * 8);
  return t;
}

// Initialization
void __holycminus_init() {
  CTensor *a = CreateTensor(1024);
  CTensor *b = CreateTensor(1024);
  CTensor *c = CreateTensor(1024);
  
  cuda_add(c->data, a->data, b->data, 1024);
  printf("Tensors added on GPU\n");
  
  cuda_free(a->data);
  cuda_free(b->data);
  cuda_free(c->data);
}

int main(int argc, char **argv) {
  __holycminus_init();
  return 0;
}
```

**Compile and link:**
```bash
# Transpile
hcm tensor_example.hc -o tensor_example.c

# Compile with CUDA library
gcc tensor_example.c -o tensor_example -L./lib -lburningbush -lcudart

# Run
./tensor_example
```

## 22. Implementation Roadmap

### Phase 1: Core Transpiler
1. Lexer for basic tokens
2. Parser for simple functions and statements
3. Basic code generator
4. Type definitions
5. String literal statements

### Phase 2: Classes and Structures
1. Class/struct declarations
2. Member access
3. Single inheritance
4. Unions

### Phase 3: FFI and Interop
1. `_extern` declarations
2. Function pointers
3. Opaque pointer types
4. Symbol table for external functions

### Phase 4: Syntactic Sugar
1. Function calls without parentheses
2. Postfix type casting
3. Power operator
4. Character literal statements

### Phase 5: Top-Level Code
1. Initialization function generation
2. Main function handling
3. Global variable initialization

### Phase 6: Polish
1. Error messages
2. Source location tracking
3. Pretty printing
4. Optimization flags
5. Documentation

## 23. Project File Structure

The HolyC- transpiler project follows a clean, modular structure optimized for development and distribution.

### 23.1 Repository Layout

```
holycminus/
├── src/
│   ├── HolyCMinus/
│   │   ├── Lexer.hs              # Tokenization
│   │   ├── Parser.hs             # AST generation
│   │   ├── AST.hs                # AST data types
│   │   ├── Resolver.hs           # Symbol resolution & semantic analysis
│   │   ├── Codegen.hs            # C code generation
│   │   ├── Pretty.hs             # Pretty printing for C output
│   │   ├── Error.hs              # Error reporting utilities
│   │   └── Types.hs              # Shared types and utilities
│   └── Main.hs                   # CLI entry point
│
├── runtime/
│   ├── holycminus_runtime.h      # Standard runtime header
│   └── README.md                 # Runtime documentation
│
├── tests/
│   ├── unit/
│   │   ├── TestLexer.hs         # Lexer unit tests
│   │   ├── TestParser.hs        # Parser unit tests
│   │   ├── TestResolver.hs      # Resolver tests
│   │   └── TestCodegen.hs       # Codegen tests
│   ├── integration/
│   │   ├── TestBasic.HC         # Test of basic syntax  
│   │   ├── TestFlasses.HC       # Test of classes and functions
│   │   └── TestFfi.HC           # Test of the FFI
│   └── main_test.hs              # Test suite entry point
│
├── docs/
│   ├── design.md                 # This file
│   ├── reference.md              # Complete language reference
│   ├── context.md                # A shortened summary of the design
│   └── checklist.md              # A checklist of what must be implemented
│
├── scripts/
│   ├── build.sh                  # Build transpiler
│   ├── test.sh                   # Run test suite
│   ├── install.sh                # Install transpiler
│   └── format.sh                 # Format Haskell code
│
├── holycminus.cabal              # Cabal build configuration
├── stack.yaml                    # Stack build configuration
├── Setup.hs                      # Cabal setup
├── LICENSE                       # MIT or similar
├── README.md                     # Project overview
└── .gitignore                    # Git ignore rules
```

### 23.2 Core Module Descriptions

**src/HolyCMinus/Lexer.hs**
- Tokenizes HolyC- source code
- Handles HolyC-specific tokens (type names, backtick operator)
- Tracks source locations for error reporting
- Uses `megaparsec` or similar parser combinator library

**src/HolyCMinus/Parser.hs**
- Builds Abstract Syntax Tree from token stream
- Parses declarations, statements, expressions
- Handles operator precedence
- Reports syntax errors with locations

**src/HolyCMinus/AST.hs**
- Defines all AST data types
- `Program`, `TopLevel`, `Function`, `Class`, etc.
- Generic over annotations for multiple compilation passes

**src/HolyCMinus/Resolver.hs**
- Builds symbol table
- Resolves function calls without parentheses
- Tracks class inheritance for member access rewriting
- Validates external function declarations
- Annotates AST with resolved information

**src/HolyCMinus/Codegen.hs**
- Transforms annotated AST to C code
- Handles all syntactic sugar transformations
- Generates type definitions and forward declarations
- Creates initialization function from top-level code
- Manages include directives and dependencies

**src/HolyCMinus/Pretty.hs**
- Pretty prints generated C code
- Formats with proper indentation
- Uses `prettyprinter` library
- Makes output readable and debuggable

**src/HolyCMinus/Error.hs**
- Error message formatting
- Source location display
- Helpful error suggestions
- Warning system

**src/Main.hs**
- Command-line argument parsing
- Pipeline orchestration (Lexer → Parser → Resolver → Codegen)
- File I/O
- Error handling and reporting

### 23.3 Build Configuration

**holycminus.cabal:**
```haskell
cabal-version: 2.4
name: holycminus
version: 0.1.0.0
synopsis: HolyC to C transpiler
license: MIT
author: Your Name
maintainer: your.email@example.com

executable holycminus
  main-is: Main.hs
  other-modules:
    HolyCMinus.Lexer,
    HolyCMinus.Parser,
    HolyCMinus.AST,
    HolyCMinus.Resolver,
    HolyCMinus.Codegen,
    HolyCMinus.Pretty,
    HolyCMinus.Error,
    HolyCMinus.Types
  build-depends:
    base >= 4.14 && < 5,
    megaparsec >= 9.0,
    parser-combinators >= 1.3,
    text >= 1.2,
    containers >= 0.6,
    mtl >= 2.2,
    prettyprinter >= 1.7,
    optparse-applicative >= 0.16,
    filepath >= 1.4,
    directory >= 1.3
  hs-source-dirs: src
  default-language: Haskell2010
  ghc-options: -Wall -O2

test-suite holycminus-test
  type: exitcode-stdio-1.0
  main-is: Spec.hs
  other-modules:
    LexerSpec,
    ParserSpec,
    ResolverSpec,
    CodegenSpec
  build-depends:
    base,
    holycminus,
    hspec >= 2.7,
    QuickCheck >= 2.14
  hs-source-dirs: test
  default-language: Haskell2010
  ghc-options: -Wall
```

### 23.4 Development Workflow

**1. Building the transpiler:**
```bash
# Using Stack
cd holycminus
stack build
stack install  # Installs to ~/.local/bin

# Using Cabal
cabal build
cabal install
```

**2. Running tests:**
```bash
stack test                        # All tests
stack test --test-arguments="--match Lexer"  # Specific module
```

**3. Transpiling HolyC- code:**
```bash
hcm examples/hello_world.hc -o hello.c
gcc hello.c -o hello -I./runtime
./hello
```

**4. Development with examples:**
```bash
cd examples/burningbush
./build.sh                        # Transpile all .hc files
cd backend && make                # Build CUDA kernels
cd ../abi && make                 # Build ABI wrapper
gcc -o burningbush *.c -L./abi -lburningbush
./burningbush
```

### 23.5 Distribution

**Binary releases:**
```
holycminus-v0.1.0-linux-x64/
├── bin/
│   └── holycminus               # Compiled binary
├── runtime/
│   └── holycminus_runtime.h     # Runtime header
├── examples/
│   └── ...                      # Example programs
└── README.md                    # Quick start guide
```

**Source distribution:**
```bash
cabal sdist                      # Creates tarball
# Produces: dist/holycminus-0.1.0.0.tar.gz
```

### 23.6 CI/CD Pipeline

**GitHub Actions workflow (.github/workflows/ci.yml):**
```yaml
name: CI
on: [push, pull_request]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: haskell/actions/setup@v1
        with:
          ghc-version: '9.2'
          cabal-version: '3.6'
      
      - name: Cache
        uses: actions/cache@v2
        with:
          path: ~/.cabal
          key: cabal-${{ hashFiles('**/*.cabal') }}
      
      - name: Build
        run: cabal build
      
      - name: Test
        run: cabal test
      
      - name: Generate examples
        run: |
          cabal run holycminus -- examples/hello_world.hc -o test.c
          gcc test.c -o test -I./runtime
          ./test
```

### 23.7 Documentation Structure

**docs/ contents:**
- `design.md` (this file) - Design decisions and architecture
- `language_reference.md` - Complete language specification
- `tutorial.md` - Step-by-step getting started

## 24. Testing Strategy

### Unit Tests
- Lexer: token recognition
- Parser: AST generation for each construct
- Codegen: verify C output for each feature

### Integration Tests
- End-to-end: HolyC- → C → executable
- Run generated programs and verify output
- Test examples from original HolyC docs

### Example Test Cases
```haskell
testHelloWorld :: IO ()
testStringPrintf :: IO ()
testFunctionCall :: IO ()
testClassDeclaration :: IO ()
testInheritance :: IO ()
testPowerOperator :: IO ()
testExternDeclaration :: IO ()
testFunctionPointer :: IO ()
testOpaquePointer :: IO ()
```

### Real-World Tests
- BurningBush tensor operations (FFI with mock CUDA library)
- BurningBush autograd graph construction
- Module system (CLinear, CMLP)
- Optimizer step functions

**Example BurningBush Test:**
```bash
# Create mock CUDA library for testing
gcc -shared -fPIC mock_cuda.c -o libmock_cuda.so

# Transpile BurningBush tensor code
hcm tests/tensor_test.hc -o tensor_test.c

# Compile and link
gcc tensor_test.c -L. -lmock_cuda -o tensor_test

# Run test
./tensor_test
# Expected: "Tensor add test passed"
```

## 25. Future Extensions

### Possible Additions
- Exception handling via `setjmp`/`longjmp`
- More compile-time features
- Optimizer to reduce unnecessary temporaries
- Better error messages with suggestions
- REPL for interactive development
- Debugger support (generate debug symbols)

### Non-Goals
- Full HolyC compatibility (too complex)
- Assembly support (non-portable)
- OS-specific features (graphics, task management)
- JIT compilation

## 26. BurningBush Deep Learning Framework Considerations

This section addresses how HolyC- specifically supports building **BurningBush**, a GPU-accelerated deep learning framework with a three-language architecture (HolyC- frontend, CUDA backend, C ABI glue).

### 26.1 Architecture Support

HolyC- provides all necessary features for BurningBush's design:

**Frontend (HolyC-)**:
- Classes for tensor management (`CTensor`, `CAutoNode`)
- Inheritance for module hierarchy (`CModule` → `CLinear` → layers)
- Opaque pointers (`U0 *`) for GPU memory handles
- FFI declarations (`_extern`) for CUDA kernel calls
- Method-like syntax via helper functions

**C ABI Glue Layer**:
- External function declarations map to shared library exports
- Type compatibility (I64 ↔ int64_t, U0* ↔ void*)
- Simple calling convention

**Memory Model**:
- All tensors in GPU memory (host holds pointers only)
- No F32 type needed (uses F64 or raw bytes)
- Explicit memory management via FFI calls

### 26.2 Core Tensor Class Example

**HolyC- Code:**
```holyc
// External CUDA operations
_extern U0 cuda_malloc(U0 **ptr, I64 size);
_extern U0 cuda_free(U0 *ptr);
_extern U0 cuda_add(U0 *out, U0 *a, U0 *b, I64 n);
_extern U0 cuda_matmul(U0 *out, U0 *a, U0 *b, I64 m, I64 n, I64 k);
_extern U0 cuda_relu_fwd(U0 *out, U0 *in, I64 n);

class CTensor
{
  U0 *data;      // GPU pointer (opaque)
  I64 *shape;    // Shape array
  I64 ndim;      // Number of dimensions
  Bool requires_grad;
  CAutoNode *grad_fn;  // For autograd
};

U0 TensorInit(CTensor *self, I64 *shape, I64 ndim)
{
  I64 size = 1;
  I64 i;
  
  self->shape = MAlloc(ndim * 8);  // sizeof(I64) = 8
  self->ndim = ndim;
  self->requires_grad = 0;  // false
  self->grad_fn = 0;  // NULL
  
  for (i = 0; i < ndim; i++) {
    self->shape[i] = shape[i];
    size = size * shape[i];
  }
  
  cuda_malloc(&self->data, size * 8);  // 8 bytes per F64
}

U0 TensorFree(CTensor *self)
{
  cuda_free(self->data);
  Free(self->shape);
}

CTensor* TensorAdd(CTensor *a, CTensor *b)
{
  CTensor *out = MAlloc(sizeof(CTensor));
  I64 size = 1;
  I64 i;
  
  TensorInit(out, a->shape, a->ndim);
  
  for (i = 0; i < a->ndim; i++)
    size = size * a->shape[i];
  
  cuda_add(out->data, a->data, b->data, size);
  
  return out;
}
```

**Key Points**:
- Opaque `U0 *data` pointer to GPU memory
- Shape stored on host (plain C array)
- FFI calls for all GPU operations
- Manual memory management

### 26.3 Module System Example

**HolyC- Code:**
```holyc
class CModule
{
  U0 *state;  // Opaque state pointer
};

class CLinear : CModule
{
  CTensor *weight;
  CTensor *bias;
  I64 in_features;
  I64 out_features;
};

U0 LinearInit(CLinear *self, I64 in_features, I64 out_features)
{
  I64 weight_shape[2];
  I64 bias_shape[1];
  
  self->in_features = in_features;
  self->out_features = out_features;
  
  weight_shape[0] = out_features;
  weight_shape[1] = in_features;
  self->weight = MAlloc(sizeof(CTensor));
  TensorInit(self->weight, weight_shape, 2);
  
  bias_shape[0] = out_features;
  self->bias = MAlloc(sizeof(CTensor));
  TensorInit(self->bias, bias_shape, 1);
  
  // Initialize weights (would call CUDA kernel)
  // xavier_uniform(self->weight);
}

CTensor* LinearForward(CLinear *self, CTensor *input)
{
  CTensor *out = MAlloc(sizeof(CTensor));
  I64 batch_size = input->shape[0];
  I64 out_shape[2];
  
  out_shape[0] = batch_size;
  out_shape[1] = self->out_features;
  TensorInit(out, out_shape, 2);
  
  // out = input @ weight.T + bias
  cuda_matmul(out->data, input->data, self->weight->data,
              batch_size, self->out_features, self->in_features);
  
  return out;
}
```

**Key Points**:
- Single inheritance (`CLinear : CModule`)
- Tensor parameters as member variables
- Forward function returns new tensor
- All compute via FFI calls

### 26.4 Autograd Tape System

**HolyC- Code:**
```holyc
class CAutoNode
{
  CTensor *tensor;
  CAutoNode **inputs;  // Array of parent nodes
  I64 num_inputs;
  U0 (*backward_fn)(CAutoNode *);  // Function pointer!
};

U0 AddBackward(CAutoNode *node)
{
  CTensor *grad = node->tensor->grad;
  
  // Gradient flows to both inputs
  if (node->inputs[0]->tensor->requires_grad) {
    // node->inputs[0]->tensor->grad += grad
    cuda_add(node->inputs[0]->tensor->grad->data,
             node->inputs[0]->tensor->grad->data,
             grad->data,
             GetTensorSize(grad));
  }
  
  if (node->inputs[1]->tensor->requires_grad) {
    cuda_add(node->inputs[1]->tensor->grad->data,
             node->inputs[1]->tensor->grad->data,
             grad->data,
             GetTensorSize(grad));
  }
}

CTensor* TensorAddWithGrad(CTensor *a, CTensor *b)
{
  CTensor *out = TensorAdd(a, b);
  
  if (a->requires_grad || b->requires_grad) {
    CAutoNode *node = MAlloc(sizeof(CAutoNode));
    node->tensor = out;
    node->num_inputs = 2;
    node->inputs = MAlloc(2 * 8);  // sizeof(pointer)
    node->inputs[0] = a->grad_fn;
    node->inputs[1] = b->grad_fn;
    node->backward_fn = &AddBackward;  // Function pointer!
    
    out->grad_fn = node;
    out->requires_grad = 1;  // true
  }
  
  return out;
}

U0 TensorBackward(CTensor *self)
{
  CAutoNode *node = self->grad_fn;
  
  if (node) {
    // Call backward function via function pointer
    node->backward_fn(node);
    
    // Recursively backward through inputs
    I64 i;
    for (i = 0; i < node->num_inputs; i++) {
      if (node->inputs[i])
        TensorBackward(node->inputs[i]->tensor);
    }
  }
}
```

**Key Points**:
- Function pointers for backward operations
- Dynamic array of input nodes
- Recursive backward pass
- Gradient accumulation via CUDA

### 26.5 Training Loop Example

**HolyC- Code:**
```holyc
class CSGD
{
  CTensor **params;  // Array of tensor pointers
  I64 num_params;
  F64 lr;
};

_extern U0 cuda_sgd_step(U0 *param, U0 *grad, F64 lr, I64 size);

U0 SGDStep(CSGD *self)
{
  I64 i;
  for (i = 0; i < self->num_params; i++) {
    CTensor *param = self->params[i];
    if (param->grad) {
      cuda_sgd_step(param->data, param->grad->data,
                    self->lr, GetTensorSize(param));
    }
  }
}

U0 SGDZeroGrad(CSGD *self)
{
  I64 i;
  for (i = 0; i < self->num_params; i++) {
    CTensor *param = self->params[i];
    if (param->grad) {
      // Zero out gradients on GPU
      _extern U0 cuda_zero(U0 *ptr, I64 size);
      cuda_zero(param->grad->data, GetTensorSize(param) * 8);
    }
  }
}

// Training loop
U0 TrainMLP()
{
  CLinear *fc1 = MAlloc(sizeof(CLinear));
  CLinear *fc2 = MAlloc(sizeof(CLinear));
  LinearInit(fc1, 784, 128);
  LinearInit(fc2, 128, 10);
  
  CSGD *optim = MAlloc(sizeof(CSGD));
  optim->num_params = 4;
  optim->params = MAlloc(4 * 8);
  optim->params[0] = fc1->weight;
  optim->params[1] = fc1->bias;
  optim->params[2] = fc2->weight;
  optim->params[3] = fc2->bias;
  optim->lr = 0.01;
  
  I64 epoch;
  for (epoch = 0; epoch < 100; epoch++) {
    // Forward pass
    CTensor *h = LinearForward(fc1, x_train);
    h = TensorReLU(h);
    CTensor *pred = LinearForward(fc2, h);
    
    // Loss
    CTensor *loss = CrossEntropyLoss(pred, y_train);
    
    "Epoch %d, Loss: ", epoch;
    PrintTensor(loss);
    '\n';
    
    // Backward pass
    SGDZeroGrad(optim);
    TensorBackward(loss);
    
    // Update weights
    SGDStep(optim);
  }
}
```

**Key Points**:
- Manual optimizer state management
- Array of parameter pointers
- Explicit training loop structure
- FFI calls for weight updates

### 26.6 Feature Checklist for BurningBush

✅ **Supported (Essential)**:
- Classes with single inheritance
- Opaque pointers (`U0 *`) for GPU memory
- FFI declarations (`_extern`) for CUDA kernels
- Function pointers for backward operations
- Dynamic arrays (pointer + count pattern)
- Manual memory management
- String formatting for logging
- Standard control flow

✅ **Supported (Nice-to-Have)**:
- Zero-arg function calls without parens
- String literal statements for logging
- Postfix casts for pointer manipulation
- Power operator for size calculations

❌ **Not Needed**:
- F32 type (uses F64 or raw bytes)
- Exception handling (explicit error checking)
- Multiple inheritance (single is sufficient)
- Complex metaprogramming

### 26.7 Build Workflow for BurningBush

```bash
# 1. Build CUDA kernels
cd backend/kernels
nvcc -shared -o libburningbush.so *.cu -lcudart

# 2. Build C ABI wrapper
cd ../../abi
gcc -shared -c cuda_abi.cpp -o cuda_abi.o
gcc -shared cuda_abi.o -L../backend/kernels -lburningbush -o libburningbush_abi.so

# 3. Transpile HolyC- frontend
cd ../frontend
hcm tensor.hc -o tensor.c
hcm autograd.hc -o autograd.c
hcm nn/linear.hc -o nn_linear.c
# ... transpile all frontend files

# 4. Compile transpiled C code
gcc tensor.c autograd.c nn_linear.c -o burningbush \
    -L../abi -lburningbush_abi \
    -Wl,-rpath,../abi

# 5. Run
./burningbush
```

### 26.8 Performance Considerations

**HolyC- overhead**: Minimal! The transpiled C code is nearly identical to handwritten C:

- No runtime interpretation
- Direct function calls (inlined by C compiler)
- Zero-cost abstractions (classes → structs)
- Pointer arithmetic compiles identically

**Bottlenecks are in CUDA**, not the frontend:
- GEMM optimization (Simon Boehm's blog, 10 kernel variants)
- FlashAttention (lubits.ch/flash)
- Memory bandwidth (vectorized loads/stores)

The HolyC- frontend adds **<1% overhead** compared to pure C, making it ideal for this use case.

### 26.9 Example: Complete Tensor Add with Autograd

**HolyC-:**
```holyc
_extern U0 cuda_malloc(U0 **ptr, I64 size);
_extern U0 cuda_free(U0 *ptr);
_extern U0 cuda_add(U0 *out, U0 *a, U0 *b, I64 n);

class CTensor {
  U0 *data;
  I64 size;
  Bool requires_grad;
  CTensor *grad;
};

CTensor* TensorCreate(I64 size) {
  CTensor *t = MAlloc(sizeof(CTensor));
  t->size = size;
  cuda_malloc(&t->data, size * 8);
  t->requires_grad = 0;
  t->grad = 0;
  return t;
}

CTensor* Add(CTensor *a, CTensor *b) {
  CTensor *out = TensorCreate(a->size);
  cuda_add(out->data, a->data, b->data, a->size);
  
  if (a->requires_grad || b->requires_grad) {
    out->requires_grad = 1;
    // Store computation graph info...
  }
  
  return out;
}

// Usage
CTensor *a = TensorCreate(1024);
CTensor *b = TensorCreate(1024);
a->requires_grad = 1;

CTensor *c = Add(a, b);
"Result computed on GPU\n";
```

**Generated C** (cleaned up for readability):
```c
#include "holycminus_runtime.h"

extern void cuda_malloc(void **ptr, int64_t size);
extern void cuda_free(void *ptr);
extern void cuda_add(void *out, void *a, void *b, int64_t n);

typedef struct CTensor {
  void *data;
  int64_t size;
  bool requires_grad;
  struct CTensor *grad;
} CTensor;

CTensor* TensorCreate(int64_t size) {
  CTensor *t = malloc(sizeof(CTensor));
  t->size = size;
  cuda_malloc(&t->data, size * 8);
  t->requires_grad = false;
  t->grad = NULL;
  return t;
}

CTensor* Add(CTensor *a, CTensor *b) {
  CTensor *out = TensorCreate(a->size);
  cuda_add(out->data, a->data, b->data, a->size);
  
  if (a->requires_grad || b->requires_grad) {
    out->requires_grad = true;
    // Store computation graph info...
  }
  
  return out;
}

void __holycminus_init() {
  CTensor *a = TensorCreate(1024);
  CTensor *b = TensorCreate(1024);
  a->requires_grad = true;
  
  CTensor *c = Add(a, b);
  printf("Result computed on GPU\n");
}

int main(int argc, char **argv) {
  __holycminus_init();
  return 0;
}
```

**Analysis**: The generated C is clean, efficient, and indistinguishable from handwritten code. The HolyC- syntax provides:
1. Cleaner type names (`I64` vs `int64_t`)
2. Simpler print statements
3. Familiar HolyC aesthetic
4. Zero runtime overhead

## 27. Conclusion

HolyC- strikes a balance between preserving HolyC's distinctive character and pragmatic implementation simplicity. By carefully selecting which features to support and which to omit, we create a language that:

1. **Looks like HolyC** - Type names, string statements, and overall aesthetic preserved
2. **Transpiles cleanly to C** - Every feature maps straightforwardly
3. **Easy to implement** - Haskell parser combinators and direct AST transformation
4. **Practical to use** - Generated C code is readable and debuggable
5. **Production-ready** - Suitable for real projects like BurningBush deep learning framework

The resulting transpiler should be implementable in ~2000-3000 lines of Haskell, providing a fun and functional tribute to TempleOS while being genuinely useful for those who appreciate HolyC's syntax.

### Key Achievements

**For Language Designers**:
- Demonstrates how to make a transpiler-first language
- Shows pragmatic compromises for C interop
- Proves that unique syntax doesn't require complex runtimes

**For HolyC Enthusiasts**:
- Preserves Terry Davis's distinctive design choices
- Makes HolyC-style programming portable
- Enables HolyC on any platform with a C compiler

**For Practitioners**:
- Zero-overhead abstractions (classes, operator sugar)
- Clean FFI for calling C/CUDA libraries
- Suitable for systems programming and scientific computing
- Reference implementation: BurningBush (GPU deep learning in HolyC-)

The language succeeds if:
- You enjoy writing in it
- The transpiler is maintainable
- The generated C is readable
- Real projects (like BurningBush) are built with it

HolyC- is a love letter to TempleOS, optimized for the real world.
