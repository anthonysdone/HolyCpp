# HolyC to C Transpiler - Implementation Checklist

## Project Setup

- [x] **Task 0.1**: Initialize Python project structure
  - Create `holyc_transpiler/` directory
  - Create `tests/` directory structure
  - Create `__init__.py` files
  - Setup `pyproject.toml` or `setup.py`
  - Create `.gitignore` for Python

- [x] **Task 0.2**: Setup development environment
  - Create virtual environment
  - Install development dependencies (pytest, black, mypy)
  - Create `requirements.txt`

---

## Phase 1: Core Types and AST Nodes

### 1. Type System (`types.py`) - ~200 LoC

- [x] **Task 1.1**: Implement `holyc_transpiler/types.py` (~200 LoC)
  - Define `Type` base class
  - Implement primitive types: `U0`, `I8`, `U8`, `I16`, `U16`, `I32`, `U32`, `I64`, `U64`, `F64`
  - Implement `PointerType` class (supports multiple levels: `I64*`, `I64**`)
  - Implement `ArrayType` class (with dimensions)
  - Implement `ClassType` class (with name only - no inheritance in HolyC)
  - Implement `UnionType` class
  - Implement `FunctionType` class (return type + parameter types)
  - Add type equivalence checking (`__eq__`)
  - Add type string representation for C generation
  - Add helper functions: `is_integer()`, `is_float()`, `is_pointer()`, `is_void()`
  - Map HolyC type names to Type instances

- [ ] **Task 1.2**: Create `tests/test_types.py` (<100 LoC)
  - Test primitive type creation and properties
  - Test pointer type creation (single and multi-level)
  - Test array type creation and dimension handling
  - Test class type creation (no inheritance)
  - Test type equivalence
  - Test C type string generation
  - Test type helper functions

### 2. AST Node Definitions (`ast_nodes.py`) - ~400 LoC

- [ ] **Task 2.1**: Implement `holyc_transpiler/ast_nodes.py` (~400 LoC)
  - Define `ASTNode` base class with source location tracking
  - **Declaration nodes:**
    - `Program` (list of declarations)
    - `FunctionDecl` (return type, name, params, body, attributes)
    - `MethodDecl` (extends FunctionDecl with class_name)
    - `VarDecl` (type, name, initializer, is_global, is_static)
    - `ClassDecl` (name, members, methods, base_class)
    - `UnionDecl` (name, members, type_prefix)
    - `ExternDecl` (return_type, name, params, external_name, is_import)
  - **Statement nodes:**
    - `Block` (list of statements)
    - `ExpressionStmt` (expression)
    - `IfStmt` (condition, then_block, else_block)
    - `WhileStmt` (condition, body)
    - `ForStmt` (init, condition, increment, body)
    - `SwitchStmt` (expression, cases, is_unchecked)
    - `CaseStmt` (values, is_range, is_auto, statements, subswitch data)
    - `ReturnStmt` (value)
    - `TryCatchStmt` (try_block, catch_block)
    - `ThrowStmt` (value)
    - `GotoStmt` (label)
    - `LabelStmt` (label)
    - `LockStmt` (body)
  - **Expression nodes:**
    - `BinaryOp` (op, left, right)
    - `UnaryOp` (op, operand)
    - `CallExpr` (function, arguments)
    - `MethodCall` (object, method, arguments)
    - `MemberAccess` (object, member)
    - `ArrayAccess` (array, index)
    - `PointerDeref` (operand)
    - `AddressOf` (operand)
    - `Literal` (value, type)
    - `Identifier` (name)
    - `ThisExpr` (for methods)
    - `SizeofExpr` (type)
    - `OffsetExpr` (class_name, member)
  - Add `__repr__` methods for debugging
  - Add visitor pattern support (optional but recommended)

- [ ] **Task 2.2**: Create `tests/unit/test_ast_nodes.py` (<100 LoC)
  - Test AST node creation
  - Test node property access
  - Test source location tracking
  - Test node equality (if implemented)
  - Test AST tree construction
  - Test visitor pattern (if implemented)

---

## Phase 2: Lexer

### 3. Lexical Analysis (`lexer.py`) - ~600 LoC

- [ ] **Task 3.1**: Implement `holyc_transpiler/lexer.py` (~600 LoC)
  - Define `TokenType` enum (all HolyC tokens)
  - Define `Token` class (type, value, line, column)
  - Implement `Lexer` class:
    - Initialize with source text
    - Track current position, line, column
    - `peek()` - look ahead without consuming
    - `advance()` - consume and move forward
    - `skip_whitespace()`
    - `skip_line_comment()` (// comments)
    - `skip_block_comment()` (/* */ comments)
    - `read_number()` - integers, hex (0x), floats
    - `read_string()` - string literals with escape sequences
    - `read_char()` - char literals (including multi-char like 'ABC')
    - `read_identifier()` - identifiers and keywords
    - `next_token()` - main tokenization function
    - `tokenize()` - return all tokens
  - **Handle operators:**
    - Single: `+ - * / % & | ^ ~ ! < > =`
    - Double: `++ -- << >> <= >= == != && || ^^ += -= *= /= %= &= |= ^= <<= >>=`
    - Backtick: `` ` `` (power operator)
    - Arrow: `->`, `...` (note :: for methods is replaced by ->)
  - **Handle keywords:**
    - Types: `U0 I8 U8 I16 U16 I32 U32 I64 U64 F64`
    - Control: `if else while for switch case default break goto return try catch throw`
    - Class: `class union public extern import _extern _import`
    - Other: `sizeof offset static noreg reg this start end lock lastclass`
  - Handle string literals as statement (syntax sugar)
  - Pack multi-char literals into uint64_t
  - Proper error reporting with line/column

- [ ] **Task 3.2**: Create `tests/unit/test_lexer.py` (<100 LoC)
  - Test single tokens (operators, punctuation)
  - Test keywords vs identifiers
  - Test number literals (decimal, hex, float)
  - Test string literals (with escapes)
  - Test single-char and multi-char literals
  - Test character literal packing ('ABC' → 0x434241)
  - Test comments (line and block)
  - Test whitespace handling
  - Test error cases (unterminated strings, invalid chars)
  - Test complete tokenization of sample programs

---

## Phase 3: Parser

### 4. Syntax Analysis (`parser.py`) - ~1800 LoC

- [ ] **Task 4.1**: Implement `holyc_transpiler/parser.py` - Part 1 (Core Parser) (~200 LoC)
  - Define `Parser` class:
    - Initialize with token list
    - Track current position
    - `peek()` - look at current token
    - `peek_ahead(n)` - look ahead n tokens
    - `advance()` - consume token
    - `expect(token_type)` - consume and verify
    - `match(*token_types)` - check if current matches any
    - `error(message)` - report parse error with context
  - Implement operator precedence table for HolyC
  - Implement helper methods:
    - `is_type()` - check if token is a type
    - `is_declaration_start()` - check if starting a declaration
    - `synchronize()` - error recovery

- [ ] **Task 4.2**: Implement `holyc_transpiler/parser.py` - Part 2 (Expressions) (~600 LoC)
  - Implement expression parsing with precedence climbing:
    - `parse_expression()` - entry point
    - `parse_assignment()` - assignment operators
    - `parse_logical_or()` - `||` operator
    - `parse_logical_xor()` - `^^` operator
    - `parse_logical_and()` - `&&` operator
    - `parse_bitwise_or()` - `|` operator
    - `parse_bitwise_xor()` - `^` operator
    - `parse_bitwise_and()` - `&` operator
    - `parse_equality()` - `==`, `!=`
    - `parse_comparison()` - `<`, `>`, `<=`, `>=` (handle chaining!)
    - `parse_shift()` - `<<`, `>>`
    - `parse_additive()` - `+`, `-`
    - `parse_multiplicative()` - `*`, `/`, `%`
    - `parse_power()` - `` ` `` operator
    - `parse_unary()` - `!`, `~`, `-`, `++`, `--`, `*`, `&`
    - `parse_postfix()` - `[]`, `->`, `.`, `()`, `++`, `--`
    - `parse_primary()` - literals, identifiers, `(expr)`, `this`, `sizeof`, `offset`
  - **Special handling:**
    - Chained comparisons: `5 < i < j < 20` → `5 < i && i < j && j < 20`
    - Function calls without parens (bare identifier as statement)
    - String/char literals as statements (calls Print/PutChars)
  - Return proper AST nodes

- [ ] **Task 4.3**: Implement `holyc_transpiler/parser.py` - Part 3 (Statements) (~500 LoC)
  - Implement statement parsing:
    - `parse_statement()` - dispatch to specific parsers
    - `parse_block()` - `{ statements }`
    - `parse_if()` - `if (cond) block [else block]`
    - `parse_while()` - `while (cond) block`
    - `parse_for()` - `for (init; cond; incr) block`
    - `parse_switch()` - handle `switch` and `switch []`
    - `parse_case()` - handle ranges, auto-increment, sub-switches
    - `parse_return()` - `return [expr];`
    - `parse_try_catch()` - `try block catch block`
    - `parse_throw()` - `throw(expr);`
    - `parse_goto()` - `goto label;`
    - `parse_label()` - `label:`
    - `parse_lock()` - `lock { statements }`
    - `parse_expression_stmt()` - expression as statement
  - Handle statement-level string/char literals

- [ ] **Task 4.4**: Implement `holyc_transpiler/parser.py` - Part 4 (Declarations) (~500 LoC)
  - Implement declaration parsing:
    - `parse_program()` - top-level entry point
    - `parse_declaration()` - dispatch to specific parsers
    - `parse_function()` - function with default args, attributes
    - `parse_method()` - method declaration (Class->Method)
    - `parse_variable()` - global/local variables with initializers
    - `parse_class()` - class with members and methods
    - `parse_union()` - union with optional type prefix
    - `parse_extern()` - extern/import/_extern/_import declarations
    - `parse_parameters()` - function parameters with defaults
    - `parse_type()` - type specifications (with pointers, arrays)
  - Handle function attributes: `public`, `interrupt`, `haserrcode`, `argpop`, etc.
  - Handle variable attributes: `static`, `reg`, `noreg`
  - Collect top-level statements (not in functions) for `_holyc_init()`

- [ ] **Task 4.5**: Create `tests/unit/test_parser.py` (<300 LoC)
  - **Expression tests:**
    - Test operator precedence
    - Test chained comparisons
    - Test power operator
    - Test function calls (with and without parens)
    - Test member access and array indexing
    - Test pointer operations
    - Test sizeof and offset
  - **Statement tests:**
    - Test control flow (if, while, for)
    - Test switch with all variants (range, auto, sub-switch)
    - Test try/catch/throw
    - Test goto/label
    - Test lock blocks
  - **Declaration tests:**
    - Test function declarations (with defaults, attributes)
    - Test variable declarations (global, static)
    - Test class declarations (with methods, inheritance)
    - Test extern declarations (all variants)
  - **Integration tests:**
    - Parse complete small programs
    - Test error recovery
    - Test source location tracking

---

## Phase 4: Semantic Analysis

### 5. Symbol Table and Type Checking (`semantic.py`) - ~800 LoC

- [ ] **Task 5.1**: Implement `holyc_transpiler/semantic.py` (~800 LoC)
  - Define `Symbol` class (name, type, declaration node, scope)
  - Define `Scope` class (parent scope, symbol table, scope type)
  - Define `SymbolTable` class:
    - `enter_scope(scope_type)` - push new scope
    - `exit_scope()` - pop scope
    - `declare(name, type, node)` - add symbol to current scope
    - `lookup(name)` - search current and parent scopes
    - `lookup_current(name)` - search only current scope
  - Define `SemanticAnalyzer` class:
    - Initialize with AST
    - `analyze()` - main entry point
    - **Visit methods for each AST node type:**
      - `visit_Program()`
      - `visit_FunctionDecl()` - check return type, params
      - `visit_MethodDecl()` - bind to class, handle `this`
      - `visit_VarDecl()` - check type, initializer
      - `visit_ClassDecl()` - check inheritance, members, methods
      - `visit_ExternDecl()` - register external symbols
      - `visit_IfStmt()`, `visit_WhileStmt()`, `visit_ForStmt()`
      - `visit_SwitchStmt()` - check case values, detect duplicates
      - `visit_TryCatchStmt()`, `visit_ThrowStmt()`
      - `visit_BinaryOp()` - check operand types
      - `visit_UnaryOp()` - check operand type
      - `visit_CallExpr()` - check function exists, arg count/types
      - `visit_MethodCall()` - check method exists on class
      - `visit_MemberAccess()` - check member exists
      - `visit_ArrayAccess()` - check array type, index type
      - `visit_Identifier()` - check symbol exists
  - **Type checking:**
    - Implicit integer conversions (widen to I64)
    - Check pointer arithmetic validity
    - Check assignment compatibility
    - Handle lastclass type inference
  - **Error reporting:**
    - Undefined symbols
    - Type mismatches
    - Duplicate declarations
    - Invalid member access
  - Track method-to-class mappings
  - Track top-level statements for `_holyc_init()`

- [ ] **Task 5.2**: Create `tests/unit/test_semantic.py` (~400 LoC)
  - Test symbol declaration and lookup
  - Test scope management (nested scopes)
  - Test function declaration and calls
  - Test class member access
  - Test method resolution
  - Test inheritance (base class member access)
  - Test error detection:
    - Undefined variables
    - Duplicate declarations
    - Type mismatches
    - Invalid member access
  - Test type inference and checking

---

## Phase 5: Code Generation

### 6. Runtime Library Generator (`runtime.py`) - ~500 LoC

- [ ] **Task 6.1**: Implement `holyc_transpiler/runtime.py` (~300 LoC + 200 LoC generated)
  - Define `RuntimeGenerator` class
  - `generate_header()` - create complete holyc_runtime.h:
    - Standard includes
    - Type definitions (U0, I8, U8, ..., F64)
    - Integer union types (holyc_i64_t, holyc_u64_t, etc.)
    - Exception context structure
    - Varargs structure
    - Function declarations:
      - `holyc_print(fmt, ...)`
      - `holyc_putchars(uint64_t chars)`
      - `ToI64(double)`, `ToF64(int64_t)`, `ToBool(int64_t)`
      - `holyc_pow(double, double)`
      - `holyc_malloc(size_t)`, `holyc_free(void*)`, `holyc_msize(void*)`
      - `holyc_calloc(size_t)`, `holyc_strdup(const char*)`
      - `holyc_throw(uint64_t)`
  - `generate_implementation()` - create holyc_runtime.c:
    - Implement all runtime functions
    - Exception handling with setjmp/longjmp
    - Memory allocation with header tracking
    - Print function with variadic args
    - PutChars to unpack multi-char literals
    - Type conversion functions
  - Handle optional features (minimal vs full runtime)

- [ ] **Task 6.2**: Create `tests/unit/test_runtime.py` (~200 LoC)
  - Test header generation (check all declarations present)
  - Test implementation generation
  - Test that generated C code compiles
  - Test runtime functions (if compiled):
    - Memory allocation/deallocation
    - MSize correctness
    - Print formatting
    - Type conversions
    - Multi-char literal unpacking

### 7. C Code Generator (`codegen.py`) - ~2000 LoC

- [ ] **Task 7.1**: Implement `holyc_transpiler/codegen.py` - Part 1 (Core Generator) (~200 LoC)
  - Define `CodeGenerator` class:
    - Initialize with AST, symbol table
    - Track indentation level
    - Track generated code sections (includes, declarations, definitions)
    - `generate()` - main entry point
    - `indent()` - increase indentation
    - `dedent()` - decrease indentation
    - `emit(code)` - add code at current indentation
    - `emit_line(code)` - add line with newline
  - Generate file header and includes
  - Generate forward declarations
  - Track external function bindings (_extern, _import)

- [ ] **Task 7.2**: Implement `holyc_transpiler/codegen.py` - Part 2 (Declarations) (~400 LoC)
  - Implement declaration code generation:
    - `gen_program()` - generate complete C file
    - `gen_function()` - generate function definition
    - `gen_method()` - generate method as function (ClassName_MethodName)
    - `gen_variable()` - generate global/local variables
    - `gen_class()` - generate typedef struct
    - `gen_union()` - generate typedef union
    - `gen_extern()` - generate extern declaration or wrapper
    - `gen_parameters()` - generate parameter list
    - `gen_type()` - generate C type string
  - Handle function with default arguments:
    - Generate wrapper functions for different arg patterns
    - Use sentinel values or explicit wrappers
  - Handle class inheritance (embed base as first member)
  - Generate metadata for class members (if format specified)

- [ ] **Task 7.3**: Implement `holyc_transpiler/codegen.py` - Part 3 (Statements) (~500 LoC)
  - Implement statement code generation:
    - `gen_block()` - generate `{ statements }`
    - `gen_if()` - generate if/else
    - `gen_while()` - generate while loop
    - `gen_for()` - generate for loop
    - `gen_switch()` - handle all switch variants
    - `gen_case()` - handle range, auto-increment, sub-switch
    - `gen_return()` - generate return statement
    - `gen_try_catch()` - generate setjmp/longjmp exception handling
    - `gen_throw()` - generate throw call
    - `gen_goto()` - generate goto
    - `gen_label()` - generate label
    - `gen_lock()` - generate atomic operation or mutex
    - `gen_expression_stmt()` - generate expression statement
  - Handle special statement contexts:
    - String literal as statement → holyc_print()
    - Char literal as statement → holyc_putchars()

- [ ] **Task 7.4**: Implement `holyc_transpiler/codegen.py` - Part 4 (Expressions) (~600 LoC)
  - Implement expression code generation:
    - `gen_expression()` - dispatch to specific generators
    - `gen_binary_op()` - generate binary operations
      - Handle power operator (`` ` `` → holyc_pow)
      - Add parentheses for precedence
    - `gen_unary_op()` - generate unary operations
    - `gen_call()` - generate function call
      - Handle varargs (wrap in struct)
      - Handle calls without parens
    - `gen_method_call()` - generate ClassName_MethodName(obj, args)
    - `gen_member_access()` - generate obj.member or obj->member
      - Handle base class access (obj.base.member)
      - Handle sub-integer access (convert to union)
    - `gen_array_access()` - generate array[index]
    - `gen_pointer_deref()` - generate *ptr
    - `gen_address_of()` - generate &var
    - `gen_literal()` - generate literal values
      - Pack multi-char literals
    - `gen_identifier()` - generate variable reference
    - `gen_this()` - generate this parameter reference
    - `gen_sizeof()` - generate sizeof(type)
    - `gen_offset()` - generate offsetof(struct, member)
  - Handle chained comparisons (expand to &&)
  - Handle lastclass (substitute class name)

- [ ] **Task 7.5**: Implement `holyc_transpiler/codegen.py` - Part 5 (Special Features) (~300 LoC)
  - Generate `_holyc_init()` function from top-level statements
  - Generate `main()` function that calls `_holyc_init()`
  - Generate wrapper functions for default arguments
  - Generate method dispatch (ClassName_MethodName transformation)
  - Generate exception handling setup
  - Handle extern symbol bindings:
    - Generate wrapper for _extern with different name
    - Generate proper linkage
  - Add `#line` directives for source mapping (optional)
  - Format output code (indentation, spacing)

- [ ] **Task 7.6**: Create `tests/unit/test_codegen.py` (<300 LoC)
  - **Declaration tests:**
    - Test function code generation
    - Test method code generation (name transformation)
    - Test class code generation (struct + methods)
    - Test class inheritance (base embedding)
    - Test extern declarations
  - **Statement tests:**
    - Test control flow code generation
    - Test switch variants (range, auto, sub-switch)
    - Test try/catch (setjmp/longjmp)
  - **Expression tests:**
    - Test operator code generation
    - Test function calls (with/without parens)
    - Test method calls
    - Test member access
    - Test chained comparisons
    - Test power operator
  - **Feature tests:**
    - Test default arguments (wrapper generation)
    - Test top-level code collection
    - Test string/char statement syntax
    - Test lastclass substitution
  - **Output tests:**
    - Test indentation correctness
    - Test compilability (gcc -c generated.c)

---

## Phase 6: CLI and Integration

### 8. Command-Line Interface (`main.py`) - ~200 LoC

- [ ] **Task 8.1**: Implement `holyc_transpiler/main.py` (~200 LoC)
  - Implement `main()` function:
    - Parse command-line arguments using argparse
    - **Arguments:**
      - Input file(s) (positional)
      - `-o, --output` - output file (default: stdout or input.c)
      - `--generate-runtime` - generate holyc_runtime.h/c
      - `--runtime-path` - where to place runtime files
      - `--indent` - indentation size (default: 4)
      - `--max-line-length` - max line length (default: 80)
      - `--dump-tokens` - print tokens and exit
      - `--dump-ast` - print AST and exit
      - `--verbose, -v` - verbose output
      - `--no-compile` - skip compilation check
    - Read input file(s)
    - Run lexer
    - Run parser
    - Run semantic analyzer
    - Run code generator
    - Write output file(s)
    - Optionally generate runtime library
    - Handle errors gracefully with useful messages
    - Exit with appropriate status code
  - Optional: Compile check (call gcc -c on output)

- [ ] **Task 8.2**: Create `tests/unit/test_main.py` (~150 LoC)
  - Test CLI argument parsing
  - Test input file reading
  - Test output file writing
  - Test pipeline execution (lexer → parser → semantic → codegen)
  - Test error handling
  - Test dump options (--dump-tokens, --dump-ast)
  - Test runtime generation option

---

## Phase 7: Integration Tests

### 9. End-to-End Integration Tests

- [ ] **Task 9.1**: Create `tests/integration/test_hello_world.py` (~100 LoC)
  - Test all "Hello World" variations from holyc_spec.md
  - Verify transpiled code compiles
  - Verify output matches expected

- [ ] **Task 9.2**: Create `tests/integration/test_basic_ops.py` (~150 LoC)
  - Test arithmetic operations
  - Test comparison operations (including chained)
  - Test logical operations
  - Test power operator

- [ ] **Task 9.3**: Create `tests/integration/test_control_flow.py` (~200 LoC)
  - Test if/else statements
  - Test while loops
  - Test for loops
  - Test switch statements (all variants)
  - Test goto/label

- [ ] **Task 9.4**: Create `tests/integration/test_functions.py` (~200 LoC)
  - Test function declarations
  - Test function calls (with/without parens)
  - Test default arguments
  - Test variadic functions (argc/argv)
  - Test return values

- [ ] **Task 9.5**: Create `tests/integration/test_classes.py` (~250 LoC)
  - Test class declarations
  - Test class methods
  - Test method calls
  - Test class inheritance
  - Test member access
  - Test sub-integer access

- [ ] **Task 9.6**: Create `tests/integration/test_pointers.py` (~150 LoC)
  - Test pointer declarations
  - Test pointer arithmetic
  - Test pointer dereferencing
  - Test address-of operator
  - Test arrays and array access

- [ ] **Task 9.7**: Create `tests/integration/test_external_ffi.py` (~200 LoC)
  - Test extern declarations
  - Test _extern with name binding
  - Test function pointer callbacks
  - Test opaque handle pattern

- [ ] **Task 9.8**: Create `tests/integration/test_memory.py` (~150 LoC)
  - Test MAlloc/Free
  - Test MSize
  - Test CAlloc
  - Test dynamic arrays
  - Test memory pools

- [ ] **Task 9.9**: Create `tests/integration/test_exceptions.py` (~100 LoC)
  - Test try/catch/throw
  - Test exception propagation
  - Test exception values

- [ ] **Task 9.10**: Create `tests/integration/test_advanced.py` (~400 LoC)
  - Test complete programs from holyc_spec.md
  - Test vector math library example
  - Test callback event system example
  - Test device driver pattern example
  - Test memory pool allocator example
  - Test dynamic array container example

- [ ] **Task 9.11**: Create `tests/integration/test_compilation.py` (~100 LoC)
  - For each integration test, compile with gcc
  - Verify no compilation errors
  - Optionally run and verify output

## Summary Statistics

**Total Tasks**: ~50 implementation tasks + ~15 test tasks + ~12 integration tests + ~12 polish tasks = **~89 tasks**

**Total Estimated LoC**: ~9,650 LoC
- Implementation: ~6,700 LoC
- Tests: ~4,950 LoC

**Critical Path**:
1. Types & AST (~800 LoC)
2. Lexer (~1,000 LoC)
3. Parser (~2,600 LoC)
4. Semantic Analysis (~1,200 LoC)
5. Code Generation (~3,300 LoC)
6. Integration & Testing (~2,000 LoC)
7. Documentation & Polish

**Success Criteria** (from design.md):
- ✅ All holyc_spec.md examples transpile and compile
- ✅ Generated C code is readable and well-formatted
- ✅ All key HolyC features implemented
- ✅ >90% test coverage
- ✅ <1 second transpile time for typical files
- ✅ Comprehensive documentation
