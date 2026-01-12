# HolyC- Implementation Checklist

This checklist organizes all implementation tasks by file/module, derived from the design document. Each section lists what needs to be implemented without including actual code.

---

## Project Setup

### Repository Structure
- [ ] Create directory structure: `src/`, `runtime/`, `tests/`, `docs/`, `scripts/`
- [ ] Set up Haskell project with Cabal or Stack
- [ ] Create `.gitignore` for Haskell projects
- [ ] Initialize LICENSE file (MIT or similar)
- [ ] Create basic README.md with project overview

### Build Configuration Files

#### `holycminus.cabal`
- [ ] Define package metadata (name, version, license, author)
- [ ] Configure executable target with main module
- [ ] List all module dependencies (megaparsec, text, containers, mtl, prettyprinter, optparse-applicative, etc.)
- [ ] Set up test suite target
- [ ] Configure compiler flags (-Wall, -O2)
- [ ] Specify source directories

#### `stack.yaml` (if using Stack)
- [ ] Specify resolver/GHC version
- [ ] List project packages
- [ ] Configure extra dependencies if needed

---

## Core Data Types

### `src/HolyCMinus/Types.hs`
- [ ] Define `Identifier` type (Text-based)
- [ ] Define `Label` type for goto labels
- [ ] Define primitive type enumeration (`U0`, `I8`, `U8`, `I16`, `U16`, `I32`, `U32`, `I64`, `U64`, `F64`, `Bool`)
- [ ] Define pointer and array type representations
- [ ] Define function pointer type representation
- [ ] Create type equality and comparison functions
- [ ] Implement pretty printing for types
- [ ] Define source location tracking type (file, line, column)
- [ ] Create utility functions for type manipulation

### `src/HolyCMinus/AST.hs`
- [ ] Define `Program` type (list of top-level declarations)
- [ ] Define `TopLevel` sum type:
  - Function declarations
  - Class declarations
  - Union declarations
  - External function declarations (`_extern`)
  - Global variable declarations
  - Include directives
  - Define directives
  - Top-level statements
- [ ] Define `Function` record type:
  - Return type
  - Name
  - Parameters (list of name-type pairs)
  - Body (list of statements)
  - Public flag
- [ ] Define `ClassDecl` record type:
  - Name
  - Optional parent class (for inheritance)
  - Field list (name-type pairs)
- [ ] Define `UnionDecl` record type:
  - Name
  - Field list
- [ ] Define `Statement` sum type:
  - Expression statement
  - Return statement (optional expression)
  - Variable declaration with optional initialization
  - If/else statement
  - While loop
  - For loop (init, condition, increment, body)
  - Switch statement with cases
  - Block statement (list of statements)
  - Goto statement
  - Label definition
  - Print string statement (special: string literal + args)
  - Put char statement (special: char literal)
- [ ] Define `Expr` sum type:
  - Variable reference
  - Integer literal
  - Float literal
  - String literal
  - Character literal
  - Binary operations
  - Unary operations
  - Postfix type cast
  - Function call
  - Member access (struct/class field)
  - Array indexing
  - Address-of operator
  - Power operator (backtick)
  - Dereference
  - Sizeof
- [ ] Define `BinOp` enumeration (all binary operators)
- [ ] Define `UnaryOp` enumeration (all unary operators)
- [ ] Define `Case` type for switch cases
- [ ] Make AST types generic over annotations (for multi-pass compilation)

---

## Lexer

### `src/HolyCMinus/Lexer.hs`
- [ ] Import megaparsec or parsec libraries
- [ ] Define `Token` sum type:
  - Keywords (if, else, while, for, return, class, union, public, _extern, etc.)
  - Type keywords (U0, I8, U8, I16, U16, I32, U32, I64, U64, F64, Bool)
  - Identifiers
  - String literals (track content)
  - Character literals
  - Integer literals
  - Float literals
  - Operators (+, -, *, /, %, &, |, ^, ~, <<, >>, &&, ||, !, ==, !=, <, >, <=, >=, =, etc.)
  - Backtick (power operator)
  - Punctuation (parentheses, braces, brackets, semicolon, comma, dot, arrow, colon)
  - Preprocessor directives (#include, #define)
- [ ] Implement whitespace skipper (spaces, tabs, newlines)
- [ ] Implement single-line comment parser (`//`)
- [ ] Implement multi-line comment parser (`/* */`)
- [ ] Implement identifier lexer (alphanumeric + underscore, not starting with digit)
- [ ] Implement keyword recognition (check identifier against keyword list)
- [ ] Implement type keyword recognition
- [ ] Implement string literal lexer:
  - Handle escape sequences (\n, \t, \", \\, etc.)
  - Track empty string literals specially (for variable format strings)
- [ ] Implement character literal lexer
- [ ] Implement integer literal lexer (decimal, hexadecimal, octal, binary)
- [ ] Implement float literal lexer
- [ ] Implement operator lexers (handle multi-character operators correctly)
- [ ] Implement preprocessor directive lexer
- [ ] Implement source location tracking for each token
- [ ] Create main tokenization function that returns list of located tokens
- [ ] Add error reporting for lexical errors (unterminated strings, invalid characters, etc.)

---

## Parser

### `src/HolyCMinus/Parser.hs`
- [ ] Import parser combinator libraries and lexer
- [ ] Define parser monad type (with state for symbol tracking)
- [ ] Implement token consumption primitives:
  - Match specific token
  - Match token by type
  - Peek at next token
  - Expect token or fail with error
- [ ] Implement operator precedence table
- [ ] Implement expression parser:
  - Primary expressions (literals, identifiers, parenthesized)
  - Postfix expressions (function calls, array access, member access, postfix casts)
  - Unary expressions
  - Binary expressions (using precedence climbing or shunting yard)
  - Power operator (backtick) at correct precedence
  - Handle special case: function calls without parentheses (zero-arg functions)
- [ ] Implement statement parsers:
  - Expression statements
  - Variable declarations with optional initialization
  - Return statements
  - If/else statements
  - While loops
  - For loops (handle all three parts as optional)
  - Switch statements with case clauses
  - Blocks (statement sequences in braces)
  - Goto statements
  - Label definitions
  - Special: string literal statements (detect and parse as print statements)
  - Special: character literal statements (parse as putchar)
- [ ] Implement type parser:
  - Base type keywords
  - Pointer types (with arbitrary levels)
  - Array types (with size expressions)
  - Function pointer types
- [ ] Implement function declaration parser:
  - Parse optional `public` keyword
  - Parse return type
  - Parse function name
  - Parse parameter list (name-type pairs)
  - Parse function body (block statement)
  - Handle variadic functions (ellipsis in parameters)
- [ ] Implement external function declaration parser (`_extern`):
  - Parse `_extern` keyword
  - Parse function signature (same as regular function but no body)
- [ ] Implement class declaration parser:
  - Parse `class` keyword
  - Parse class name
  - Parse optional inheritance (`: ParentClass`)
  - Parse field declarations in braces
  - Handle special case: function pointer typedef (`class Name : FunctionType`)
- [ ] Implement union declaration parser:
  - Similar to class but with `union` keyword
- [ ] Implement preprocessor directive parsers:
  - `#include "file"` (only double quotes)
  - `#define NAME value`
- [ ] Implement top-level parser:
  - Try each top-level construct in order
  - Collect top-level statements (not inside functions)
  - Build complete `Program` AST
- [ ] Implement error recovery:
  - Synchronize on statement boundaries after errors
  - Report helpful error messages with source locations
  - Suggest fixes for common mistakes
- [ ] Create main parse function that takes token list and returns AST

---

## Resolver (Semantic Analysis)

### `src/HolyCMinus/Resolver.hs`
- [ ] Define `Symbol` sum type:
  - Function symbol (return type, parameter types)
  - Variable symbol (type)
  - Class symbol (field info, parent class)
  - Union symbol (field info)
  - External function symbol
- [ ] Define `SymbolTable` type (map from identifier to symbol)
- [ ] Define `ClassInfo` record:
  - Field list with types
  - Parent class name (if any)
  - Complete field list including inherited fields
- [ ] Implement symbol table operations:
  - Insert symbol
  - Lookup symbol
  - Enter new scope
  - Exit scope
  - Check for redefinition errors
- [ ] Implement first pass: collect all declarations
  - Collect all function signatures
  - Collect all class definitions
  - Collect all union definitions
  - Collect all external declarations
  - Collect all global variables
  - Build inheritance hierarchy for classes
- [ ] Implement class inheritance resolution:
  - For each class, resolve parent class
  - Compute complete field list (parent fields + own fields)
  - Check for circular inheritance
  - Validate parent class exists
- [ ] Implement second pass: resolve all references
  - Annotate function calls with resolved function info
  - Resolve zero-argument function calls without parentheses
  - Distinguish between function names and variable names
  - Annotate variable references with type info
- [ ] Implement member access resolution:
  - For class member access, determine if field is inherited
  - Track whether field comes from base class (for rewriting)
  - Annotate member access nodes with resolved info
- [ ] Implement type checking (minimal):
  - Check function call argument count matches
  - Check return type matches
  - Check assignment compatibility
  - Report type mismatch errors
- [ ] Implement validation:
  - Check for undefined symbols
  - Check for multiple definitions
  - Check goto labels are defined
  - Check switch cases for duplicates
- [ ] Create annotated AST type (AST with resolved symbol info)
- [ ] Implement main resolution function that takes AST and returns annotated AST

---

## Code Generator

### `src/HolyCMinus/Codegen.hs`
- [ ] Define code generation state:
  - Track required includes
  - Track generated typedefs
  - Track forward declarations needed
  - Track initialization function statements
  - Track whether `Main()` function exists
  - Track inheritance info for member access rewriting
- [ ] Implement type name translation:
  - Map HolyC- type names to C type names (I64 → int64_t, etc.)
  - Handle pointer types
  - Handle array types
  - Handle function pointer types
- [ ] Implement expression code generation:
  - Variable references (direct translation)
  - Literals (direct translation)
  - Binary operators (translate to C operators)
  - Unary operators (translate to C operators)
  - Power operator (backtick → `pow()` function call, track need for math.h)
  - Function calls (emit with parentheses always)
  - Postfix casts (rewrite as prefix C-style casts)
  - Member access (rewrite for inheritance: `derived.base_field` → `derived.base.base_field`)
  - Array indexing (direct translation)
  - Address-of operator (direct translation)
  - Sizeof (direct translation)
- [ ] Implement statement code generation:
  - Expression statements (direct translation)
  - Return statements (direct translation)
  - Variable declarations (translate types, handle initialization)
  - If/else statements (direct translation)
  - While loops (direct translation)
  - For loops (direct translation)
  - Switch statements (direct translation)
  - Blocks (direct translation)
  - Goto/labels (direct translation)
  - Print string statements (translate to `printf()` calls)
  - Print char statements (translate to `putchar()` calls)
- [ ] Implement function code generation:
  - Generate function signature with translated types
  - Generate function body
  - Handle `public` keyword (emit as regular function)
  - Handle external functions (emit `extern` declaration, no body)
- [ ] Implement class code generation:
  - Generate `typedef struct` with translated field types
  - For derived classes, embed base struct as first field named `base`
  - Handle function pointer typedef special case
- [ ] Implement union code generation:
  - Generate `typedef union` similar to struct
- [ ] Implement top-level code organization:
  - Collect all top-level statements (not in functions)
  - Generate `__holycminus_init()` function containing these statements
  - Track all global variable declarations (emit at top level)
  - Separate variable initializations from declarations
- [ ] Implement main function generation:
  - Always generate `main(int argc, char **argv)` function
  - Call `__holycminus_init()` first
  - If user defined `Main()`, call it after init
  - Return 0
- [ ] Implement include/define handling:
  - Emit `#include` directives at top of output
  - Emit `#define` directives after includes
  - Always include "holycminus_runtime.h"
- [ ] Implement forward declaration generation:
  - Analyze which functions are called before defined
  - Generate forward declarations for all functions
  - Handle mutual recursion
- [ ] Implement complete C file generation pipeline:
  - Emit includes (runtime header + user includes)
  - Emit defines
  - Emit typedefs (classes, unions)
  - Emit forward declarations
  - Emit global variable declarations
  - Emit external function declarations
  - Emit function definitions
  - Emit initialization function
  - Emit main function
- [ ] Implement helper utilities:
  - Indent tracking for pretty output
  - Line breaking for long statements
  - Comment generation for debugging

---

## Pretty Printer

### `src/HolyCMinus/Pretty.hs`
- [ ] Import prettyprinter library
- [ ] Implement pretty printing for types
- [ ] Implement pretty printing for expressions (C syntax)
- [ ] Implement pretty printing for statements (C syntax with proper indentation)
- [ ] Implement pretty printing for function definitions
- [ ] Implement pretty printing for struct/union definitions
- [ ] Implement indentation management
- [ ] Implement line breaking for long expressions
- [ ] Create main pretty printing function that takes generated C AST and produces text
- [ ] Optionally add color coding for terminals

---

## Error Reporting

### `src/HolyCMinus/Error.hs`
- [ ] Define error types:
  - Lexical errors (invalid character, unterminated string, etc.)
  - Syntax errors (unexpected token, missing semicolon, etc.)
  - Semantic errors (undefined symbol, type mismatch, etc.)
  - Multiple errors (collect and report all)
- [ ] Implement source location formatting:
  - Display file:line:column
  - Show relevant source line
  - Highlight error position with caret (^)
  - Show surrounding context lines
- [ ] Implement error message formatting:
  - Error level (error, warning, note)
  - Clear description of problem
  - Suggestion for fix (if applicable)
  - Related locations (for redefinition errors, etc.)
- [ ] Implement error collection:
  - Continue parsing after errors when possible
  - Collect multiple errors to show all at once
- [ ] Implement warning system:
  - Unused variables
  - Implicit type conversions
  - Unreachable code
  - Missing return statements
- [ ] Create pretty error printer with colors (optional)

---

## CLI Entry Point

### `src/Main.hs`
- [ ] Import optparse-applicative for command-line parsing
- [ ] Define command-line options:
  - Input file path (positional argument)
  - Output file path (-o flag)
  - Run after compilation (--run flag)
  - Verbose mode (-v flag)
  - Output intermediate representations (--dump-tokens, --dump-ast, etc.)
  - Include paths (-I flag)
  - Library paths (-L flag)
  - Libraries to link (-l flag)
- [ ] Implement option parsing
- [ ] Implement file reading
- [ ] Implement compilation pipeline:
  - Call lexer
  - Call parser
  - Call resolver
  - Call code generator
  - Call pretty printer
  - Write output to file
- [ ] Implement error handling and reporting
- [ ] Implement verbose output (show each compilation stage)
- [ ] Implement optional compilation of generated C code:
  - Call gcc/clang with appropriate flags
  - Link with math library if power operator used
  - Link with user-specified libraries
  - Report compilation errors
- [ ] Implement optional execution of compiled binary (--run flag)
- [ ] Implement version and help text

---

## Runtime Support

### `runtime/holycminus_runtime.h`
- [ ] Add header guard
- [ ] Include standard C headers:
  - stdint.h (for fixed-width integer types)
  - stdbool.h (for bool type)
  - stdio.h (for printf, putchar)
  - stdlib.h (for malloc, free)
  - string.h (for string operations)
  - math.h (for pow function)
  - stdarg.h (for variadic functions)
- [ ] Define type aliases:
  - U0 → void
  - I8 → int8_t
  - U8 → uint8_t
  - I16 → int16_t
  - U16 → uint16_t
  - I32 → int32_t
  - U32 → uint32_t
  - I64 → int64_t
  - U64 → uint64_t
  - F64 → double
  - Bool → bool
- [ ] Define conversion macros/functions:
  - ToI64(x) → ((int64_t)(x))
  - ToF64(x) → ((double)(x))
  - ToBool(x) → ((bool)(x))
- [ ] Define optional HolyC-style memory function aliases:
  - MAlloc → malloc
  - CAlloc → calloc(1, ...)
  - Free → free
- [ ] Add documentation comments explaining each typedef

### `runtime/README.md`
- [ ] Explain purpose of runtime header
- [ ] Document type mappings
- [ ] Explain how to use in generated C code
- [ ] Provide examples
- [ ] Explain linking requirements (math library for power operator)

---

## Testing

### Test Infrastructure

#### `tests/unit/TestLexer.hs`
- [ ] Test tokenization of keywords
- [ ] Test tokenization of type keywords
- [ ] Test tokenization of identifiers
- [ ] Test tokenization of literals (int, float, string, char)
- [ ] Test tokenization of operators
- [ ] Test tokenization of backtick operator
- [ ] Test tokenization of comments (single-line and multi-line)
- [ ] Test string escape sequences
- [ ] Test error cases (unterminated strings, invalid characters)
- [ ] Test source location tracking

#### `tests/unit/TestParser.hs`
- [ ] Test parsing of simple expressions
- [ ] Test parsing of binary operators with correct precedence
- [ ] Test parsing of postfix casts
- [ ] Test parsing of function calls (with and without parentheses)
- [ ] Test parsing of power operator
- [ ] Test parsing of statements (if, while, for, switch, return, etc.)
- [ ] Test parsing of function declarations
- [ ] Test parsing of class declarations
- [ ] Test parsing of class inheritance
- [ ] Test parsing of union declarations
- [ ] Test parsing of external declarations
- [ ] Test parsing of preprocessor directives
- [ ] Test parsing of string literal statements
- [ ] Test parsing of character literal statements
- [ ] Test parsing of top-level statements
- [ ] Test error recovery and reporting

#### `tests/unit/TestResolver.hs`
- [ ] Test symbol table operations
- [ ] Test function resolution
- [ ] Test variable resolution
- [ ] Test class field resolution
- [ ] Test inheritance resolution
- [ ] Test member access resolution (with inherited fields)
- [ ] Test zero-argument function call resolution
- [ ] Test undefined symbol detection
- [ ] Test redefinition detection
- [ ] Test type checking (basic)
- [ ] Test circular inheritance detection

#### `tests/unit/TestCodegen.hs`
- [ ] Test type name translation
- [ ] Test expression code generation
- [ ] Test statement code generation
- [ ] Test function code generation
- [ ] Test class code generation (with and without inheritance)
- [ ] Test union code generation
- [ ] Test external function declaration generation
- [ ] Test initialization function generation
- [ ] Test main function generation
- [ ] Test power operator translation to pow()
- [ ] Test string literal statement translation to printf()
- [ ] Test postfix cast translation
- [ ] Test member access rewriting for inheritance
- [ ] Test forward declaration generation
- [ ] Test include/define handling

### Integration Tests

#### `tests/integration/TestBasic.HC`
- [ ] Create test: Hello World (simple string literal statement)
- [ ] Create test: Variable declarations and arithmetic
- [ ] Create test: Function definition and call
- [ ] Create test: If/else statement
- [ ] Create test: While loop
- [ ] Create test: For loop
- [ ] Create test: Switch statement
- [ ] Create test: Power operator usage
- [ ] Create test: Postfix casting
- [ ] Create test: Character literal statements
- [ ] Verify transpilation, compilation, and execution

#### `tests/integration/TestFlasses.HC` (Classes + Functions)
- [ ] Create test: Simple class declaration and usage
- [ ] Create test: Class with multiple fields
- [ ] Create test: Class inheritance (single level)
- [ ] Create test: Multi-level inheritance
- [ ] Create test: Member access on base class fields
- [ ] Create test: Union declaration and usage
- [ ] Create test: Function pointers in classes
- [ ] Verify correct struct embedding for inheritance
- [ ] Verify member access rewriting works correctly

#### `tests/integration/TestFfi.HC`
- [ ] Create test: External function declaration (_extern)
- [ ] Create test: Calling external function
- [ ] Create test: Function pointers
- [ ] Create test: Opaque pointers (U0 *)
- [ ] Create test: FFI with mock library (BurningBush-style)
- [ ] Create mock C library for testing
- [ ] Verify correct extern declarations in output
- [ ] Verify linking with external library works

### Test Runner

#### `tests/main_test.hs`
- [ ] Set up test framework (hspec or tasty)
- [ ] Import all unit test modules
- [ ] Coordinate integration test execution
- [ ] Configure test output formatting
- [ ] Add test summary reporting

---

## Build Scripts

### `scripts/build.sh`
- [ ] Implement build script using stack or cabal
- [ ] Add option to build in release mode
- [ ] Add option to clean build artifacts
- [ ] Display build progress

### `scripts/test.sh`
- [ ] Implement test running script
- [ ] Run unit tests
- [ ] Run integration tests
- [ ] Compile integration test outputs with gcc
- [ ] Execute compiled tests and verify output
- [ ] Generate test report

### `scripts/install.sh`
- [ ] Implement installation script
- [ ] Copy binary to installation directory (e.g., ~/.local/bin)
- [ ] Copy runtime header to appropriate location
- [ ] Set up PATH if needed
- [ ] Display installation success message

### `scripts/format.sh`
- [ ] Implement code formatting script using stylish-haskell or ormolu
- [ ] Format all Haskell source files
- [ ] Check formatting in CI mode (--check flag)

---

## Documentation

### `README.md`
- [ ] Write project overview
- [ ] Explain what HolyC- is
- [ ] List key features
- [ ] Provide installation instructions
- [ ] Provide quick start guide
- [ ] Show basic usage examples
- [ ] Link to detailed documentation
- [ ] Provide build instructions for development
- [ ] List dependencies
- [ ] Add license information

### `docs/reference.md`
- [ ] Document complete language syntax
- [ ] Document all type keywords
- [ ] Document operators and precedence
- [ ] Document control flow constructs
- [ ] Document class/union syntax
- [ ] Document FFI usage
- [ ] Document preprocessor directives
- [ ] Provide comprehensive examples for each feature
- [ ] Document transpilation behavior
- [ ] Explain differences from original HolyC

---

## CI/CD

### `.github/workflows/ci.yml`
- [ ] Set up GitHub Actions workflow
- [ ] Configure Haskell environment (ghc, cabal/stack)
- [ ] Configure caching for dependencies
- [ ] Add build step
- [ ] Add unit test step
- [ ] Add integration test step (transpile and compile test files)
- [ ] Add format checking step (optional)
- [ ] Configure test reporting
- [ ] Set up artifact uploads (compiled binary)
- [ ] Configure workflow triggers (push, pull request)

---

## Distribution

### Binary Release Packaging
- [ ] Create release script
- [ ] Package compiled binary
- [ ] Package runtime header
- [ ] Create README for release
- [ ] Create archive (tar.gz or zip)
- [ ] Generate checksums

### Source Distribution
- [ ] Configure cabal sdist
- [ ] Test source distribution build
- [ ] Verify all files are included

---

## Future Enhancements (Phase 2)

### Optional Features
- [ ] REPL implementation for interactive development
- [ ] Better error messages with suggestions
- [ ] Debugger support (generate debug symbols)
- [ ] Optimization passes (dead code elimination, etc.)
- [ ] Language server protocol (LSP) implementation for IDE support
- [ ] Syntax highlighting for editors (VSCode, Vim, Emacs)
- [ ] Standard library extensions (common utilities)
- [ ] Exception handling via setjmp/longjmp
- [ ] Package manager for HolyC- libraries

---

## Implementation Order Recommendation

Based on dependencies and complexity, implement in this order:

1. **Phase 1: Foundation**
   - Project setup (cabal, directory structure)
   - Types.hs (core data types)
   - AST.hs (AST definitions)
   - Lexer.hs (tokenization)
   - Basic unit tests for lexer

2. **Phase 2: Parsing**
   - Parser.hs (expression parsing first, then statements, then top-level)
   - Error.hs (error reporting)
   - Unit tests for parser

3. **Phase 3: Semantic Analysis**
   - Resolver.hs (symbol table, basic resolution)
   - Unit tests for resolver

4. **Phase 4: Code Generation**
   - Codegen.hs (basic code generation)
   - Pretty.hs (C code formatting)
   - runtime/holycminus_runtime.h
   - Unit tests for codegen

5. **Phase 5: CLI & Integration**
   - Main.hs (CLI interface)
   - Integration tests (basic examples)
   - Build scripts

6. **Phase 6: Advanced Features**
   - Inheritance support in resolver and codegen
   - FFI support
   - Function pointers
   - Advanced integration tests (TestFfi.HC)

7. **Phase 7: Polish**
   - Documentation (README, reference)
   - CI/CD setup (optional)
   - Release preparation

---

## Success Criteria

The implementation is complete when:
- [ ] All core language features transpile correctly
- [ ] All unit tests pass
- [ ] All integration tests (TestBasic.HC, TestFlasses.HC, TestFfi.HC) transpile, compile, and run successfully
- [ ] Generated C code is readable and idiomatic
- [ ] Error messages are helpful and clear
- [ ] Core documentation is complete (README, design, reference, checklist)
- [ ] FFI usage works correctly with external libraries
- [ ] CI/CD pipeline passes (if implemented)
- [ ] Binary can be built and installed
