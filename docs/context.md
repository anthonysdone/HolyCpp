# HolyC- Project Context

**Quick Reference for AI Assistants**

## Project Overview

HolyC- is a simplified dialect of HolyC (from TempleOS) that transpiles to C. The goal is a clean, maintainable Haskell transpiler that preserves HolyC's distinctive aesthetic while mapping straightforwardly to C.

**Core Philosophy**: Transpiler-first design where every feature has a simple C mapping. No complex runtime, no VM, just clean syntactic sugar over C.

## Key Language Features

### Type System
```
HolyC-    C Type      
U0        void        
I8/U8     int8_t/uint8_t
I16/U16   int16_t/uint16_t
I32/U32   int32_t/uint32_t
I64/U64   int64_t/uint64_t
F64       double      
Bool      bool       
DNE!      float 
```

### Distinctive Syntax
1. **String literals as statements**: `"Hello\n";` → `printf("Hello\n");`
2. **Char literals as statements**: `'X';` → `putchar('X');`
3. **Zero-arg function calls without parens**: `DoStuff;` → `DoStuff();`
4. **Postfix casting**: `ptr(U8*)` → `(uint8_t*)ptr`
5. **Power operator**: `2 ` 10` → `pow(2, 10)` (backtick)
6. **Class keyword for structs**: `class Foo { ... };` → `typedef struct Foo { ... } Foo;`

### Advanced Features
- **Single inheritance**: Embedded struct pattern (`Derived` contains `Base base` member)
- **FFI via _extern**: `_extern U0 cuda_malloc(...);` → `extern void cuda_malloc(...);`
- **Function pointers**: Standard C syntax supported
- **Top-level code**: Collected into `__holycminus_init()` function
- **Opaque pointers**: `U0*` for GPU memory handles, etc.

### NOT Supported
- Multiple inheritance
- Default arguments
- Continue statement (use goto)
- Ternary operator
- Exception handling
- Inline assembly
- Chained comparisons
- Multi-character literals

## Project Structure

```
holycminus/
├── src/HolyCMinus/
│   ├── Types.hs      # Core types (Identifier, Type, SourceLoc)
│   ├── AST.hs        # AST definitions
│   ├── Lexer.hs      # Tokenization
│   ├── Parser.hs     # AST generation
│   ├── Resolver.hs   # Symbol resolution & semantic analysis
│   ├── Codegen.hs    # C code generation
│   ├── Pretty.hs     # C code pretty printing
│   └── Error.hs      # Error reporting
├── src/Main.hs       # CLI entry point
├── runtime/
│   └── holycminus_runtime.h  # Type aliases, runtime macros
├── tests/
│   ├── unit/         # Unit tests for each module
│   └── integration/  # End-to-end .HC test files
└── scripts/          # Build, test, install scripts
```

## Compilation Pipeline

```
HolyC- Source → [Lexer] → Tokens → [Parser] → AST → [Resolver] → Annotated AST → [Codegen] → C Source
```

### Lexer (`Lexer.hs`)
- Tokenize HolyC- keywords, operators, literals
- Handle backtick operator specially
- Track source locations for errors
- Support single-line `//` and multi-line `/* */` comments

### Parser (`Parser.hs`)
- Parse using megaparsec combinators
- Build untyped AST
- Handle operator precedence
- Special cases: string/char literal statements, zero-arg function calls
- Error recovery at statement boundaries

### Resolver (`Resolver.hs`)
- Build symbol table (functions, classes, variables)
- Resolve inheritance hierarchies
- Annotate function calls (distinguish zero-arg functions from variables)
- Track which class fields are inherited (for member access rewriting)
- Minimal type checking

### Codegen (`Codegen.hs`)
- Transform AST to C
- Rewrite inherited member access: `derived.base_field` → `derived.base.base_field`
- Collect top-level statements into `__holycminus_init()`
- Generate forward declarations for functions
- Emit `holycminus_runtime.h` include

### Pretty Printer (`Pretty.hs`)
- Format generated C code cleanly
- Proper indentation and line breaks
- Uses `prettyprinter` library

## Key Implementation Details

### Inheritance Handling
```holyc
class Base { I64 x; };
class Derived : Base { I64 y; };
```
Generates:
```c
typedef struct Base { int64_t x; } Base;
typedef struct Derived { Base base; int64_t y; } Derived;
```
Member access `d.x` must be rewritten to `d.base.x` by codegen.

### Top-Level Code
All statements outside functions go into `__holycminus_init()`:
```c
void __holycminus_init() {
  // Top-level statements here
}
int main(int argc, char **argv) {
  __holycminus_init();
  return 0;
}
```

### FFI Pattern (for BurningBush-style usage)
```holyc
_extern U0 cuda_malloc(U0 **ptr, I64 size);
U0 *gpu_ptr;
cuda_malloc(&gpu_ptr, 1024);
```
→
```c
extern void cuda_malloc(void **ptr, int64_t size);
void *gpu_ptr;
cuda_malloc(&gpu_ptr, 1024);
```

### Function Pointers in Classes
```holyc
class COptimizer {
  U0 (*step_fn)(U0 *);
  U0 *state;
};
```
→
```c
typedef struct COptimizer {
  void (*step_fn)(void *);
  void *state;
} COptimizer;
```

## Common Patterns

### AST Design
- Generic over annotations: `data Expr a = ...`
- Allows multiple passes (unresolved → resolved)
- `SourceLoc` embedded in all nodes for error reporting

### Symbol Table
```haskell
data Symbol
  = SFunction Type [Type]
  | SVariable Type
  | SClass ClassInfo
  | SExternal Type [Type]
```
Scoped symbol table with inheritance tracking.

### Error Reporting
- Display source location with caret
- Show surrounding context lines
- Collect multiple errors before failing
- Helpful suggestions when possible

## Testing Strategy

### Unit Tests
- `TestLexer.hs`: Token recognition
- `TestParser.hs`: AST generation
- `TestResolver.hs`: Symbol resolution
- `TestCodegen.hs`: C code generation

### Integration Tests (.HC files)
- `TestBasic.HC`: Core language features
- `TestFlasses.HC`: Classes and functions
- `TestFfi.HC`: External functions, FFI

Each integration test transpiles → compiles with gcc → runs.

## Development Guidelines

1. **Type safety first**: Use Haskell's type system to prevent invalid ASTs
2. **Preserve source locations**: Always track where code came from for errors
3. **Fail early with clear errors**: Better to reject than generate wrong C
4. **Keep C output readable**: Generated code should look hand-written
5. **Test incrementally**: Unit tests for each feature, integration tests for combinations

## Common Gotchas

- **Zero-arg function calls**: Must maintain symbol table to distinguish `Foo;` (function call) from `foo;` (variable reference)
- **Inherited field access**: Requires rewriting member access in codegen
- **String literal statements**: Parser must distinguish `"text";` (print) from `x = "text";` (string literal expression)
- **Power operator precedence**: Backtick has specific precedence level
- **External functions**: Don't generate bodies, just `extern` declarations

## Example Transpilation

**Input (HolyC-):**
```holyc
class Point { I64 x; I64 y; };

U0 PrintPoint(Point *p) {
  "Point(%d, %d)\n", p->x, p->y;
}

Point p;
p.x = 10;
p.y = 20;
PrintPoint(&p);
```

**Output (C):**
```c
#include "holycminus_runtime.h"

typedef struct Point { int64_t x; int64_t y; } Point;
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

## Quick Reference: Transpilation Rules

| HolyC- | C |
|--------|---|
| `"text\n";` | `printf("text\n");` |
| `'X';` | `putchar('X');` |
| `Foo;` (0-arg fn) | `Foo();` |
| `x(I64)` | `(int64_t)x` |
| `2 ` 10` | `pow(2, 10)` |
| `class X { ... };` | `typedef struct X { ... } X;` |
| `class Y : X { ... };` | `typedef struct Y { X base; ... } Y;` |
| `_extern U0 f();` | `extern void f();` |
| Top-level code | Inside `__holycminus_init()` |

## References

- Full design: `docs/design.md`
- Implementation checklist: `docs/checklist.md`
- Runtime header: `runtime/holycminus_runtime.h`
