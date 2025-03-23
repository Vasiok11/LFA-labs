# Lexer & Scanner
### Course: Formal Languages & Finite Automata
### Author: Pascari Vasile

----

## Theory

### Lexical Analysis and Lexers

A **lexer**  is a fundamental component of many programming language processors, such as compilers and interpreters. Its primary role is to break down an input string (often source code or text) into smaller, meaningful units called **tokens**. Tokens are the building blocks of a language and represent its basic syntax, such as keywords, identifiers, operators, and literals.

The lexer works by scanning the input character by character and grouping them into tokens based on predefined rules, typically expressed as **regular expressions**. For example, in a general-purpose programming language, a lexer might recognize tokens like `if`, `else`, `+`, or `123`. In the context of this program, the lexer is designed to recognize chess move notations, such as `e4`, `O-O`, or `Qxf7#`.

Lexers are often paired with **parsers**, which analyze the structure of the token stream to ensure it conforms to the language's grammar. Together, lexers and parsers form the core of many language-processing tools.
### Domain-Specific Languages (DSLs)

A **domain-specific language (DSL)** is a programming or notation language tailored to a specific application domain. Unlike general-purpose languages like Python or Java, DSLs are designed to solve problems within a narrow context, making them more expressive and easier to use for their intended purpose. Examples of DSLs include SQL for database queries, regular expressions for pattern matching, and LaTeX for document formatting.

Chess move notations, as processed by this program, can be considered a form of DSL. They have a specific syntax and semantics tailored to the domain of chess. For instance, `e4` represents moving a pawn to the e4 square, while `O-O` represents castling on the kingside. The lexer in this program is designed to recognize and tokenize these domain-specific notations, enabling further processing or analysis.

### How Lexers and DSLs Relate

In this program, the lexer is designed to process a DSL for chess move notations. The `token_specs` list defines the syntax of this DSL using regular expressions, specifying patterns for move numbers, piece movements, captures, promotions, and other chess-specific elements. The lexer scans the input string, matches these patterns, and produces a stream of tokens that represent the moves in a structured way.

For example, the input string `1. e4 c5 2. Nf3` is broken down into tokens like `[('MOVE_NUM', '1.'), ('PIECE_MOVE', 'e4'), ('PIECE_MOVE', 'c5'), ('MOVE_NUM', '2.'), ('PIECE_MOVE', 'Nf3')]`. This tokenized representation can then be used for further processing, such as validating the moves, generating a chessboard visualization, or analyzing the game.


## Objectives

The primary objectives of this lab are to:

1. **Understand Lexical Analysis in the Context of a DSL:**
   - Gain a deep understanding of how lexical analysis converts raw text into a structured sequence of tokens.
   - Recognize the importance of lexers in the process of compiling or interpreting domain-specific languages, such as the Chess notations language.

2. **Design and Implement a Lexer for the Chess DSL:**
   - Develop a lexer that can process input scripts.
   - Define token types for keywords, identifiers, string literals, numeric values, and operators.

## Implementation description

In this section, i will talk about the implementation of the Chess Notation DSL lexer and explain each part of the code separately.


### token_specs list

This list defines the different types of tokens (patterns) that the lexer will recognize in the input string. Each token is represented as a tuple with two elements:

```
token_specs = [
    # move numbers
    ('MOVE_NUM', r'\d+\.'),
    # queen/king castling
    ('CASTLE', r'O-O(?:-O)?'),
    # promotion of pawn
    ('PROMOTION', r'[a-h][18]=[NBRQ]'),
    # pawn capture
    ('PAWN_CAPTURE', r'[a-h]x[a-h][1-8]'),
    # piece capture
    ('PIECE_CAPTURE', r'[NBRQK][a-h]?[1-8]?x[a-h][1-8]'),
    # piece moves
    ('PIECE_MOVE', r'[NBRQK][a-h]?[1-8]?[a-h][1-8]'),
    # piece notation
    ('PIECE', r'[NBRQK]'),
    # squares
    ('SQUARE', r'[a-h][1-8]'),
    # capture
    ('CAPTURE', r'x'),
    # check and checkmate
    ('CHECK', r'\+'),
    ('CHECKMATE', r'#'),
    # move separator
    ('SEPARATOR', r'\s+'),
    # unmatched character
    ('MISMATCH', r'.'),
]
```

The way it works is that it has a structure, where each token is represented as a tuple that consists of a name and pattern(name, pattern)
* **name** is a descriptive name for the token
* **pattern** is the regex pattern that matches the token

For example, **MOVE_NUM** is used to match move numbers like "1.", "2."; **PROMOTION** matches pawn promotions such as "a8=Q" (promotes to a queen on a8); **MISMATCH** is used for error handling , and so on.

### Regex pattern compilation

The purpose of this code snippet is to compile all the token patterns into a single regex and compiles the regex for token matching.

```
tok_regex = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in token_specs)
pattern = re.compile(tok_regex)
```

**tok_regex** is the one that takes care of joining all the token patterns into the regex using the "|" operator, and each pattern is wrapped in a named group using **(?P<{name}>{pattern})**.


The **pattern** variable compiles the combined regex for faster token matching.

### The lex method

This method has the role of tokenizing the input string into a list of tokens
```
def lex(input_str):
    tokens = []
    line_num = 1
    line_start = 0

    pos = 0
    while pos < len(input_str):
        match = pattern.match(input_str, pos)
        if not match:
            raise ValueError(f'No match found at position {pos}')

        token_type = match.lastgroup
        token_value = match.group(token_type)

        line_num += input_str[pos:match.start()].count('\n')
        if '\n' in input_str[pos:match.start()]:
            line_start = input_str.rfind('\n', pos, match.start()) + 1
        column = match.start() - line_start + 1

        if token_type == 'SEPARATOR':
            pass
        elif token_type == 'MISMATCH':
            raise ValueError(f'Incorrect character{token_value!r} at line {line_num}, column {column}')
        else:
            tokens.append((token_type, token_value))

        pos = match.end()

    return tokens
```

In order to do that, it goes through multiple steps as follows:
1. **Initialization**
    * For the initialization, it stores the list of recognized tokens into **tokens** array. The method also has three variables used for tracking the current line number, start position, and current position in the input string, the variables themselves being **line_num**, **line_start**, and **pos**. 
2. **Loop through input**
    * The while loop has the purpose of iterating through the input string in order to match the regex pattern at the current **pos**. If there's no match, a **ValueError** is raised.
3. **Token extraction**
    * **token_type** is used to extract the name of the matched token, while **token_value** extracts the actual text that matched the pattern.
4. **Line and column tracking**
    * The **line_num** and **line_start** variables will be updated if newlines are encountered, and it calculates the column number for error reporting
5. **Token handling**
    * If the token is a **SEPARATOR**, it is ignored
    * If the token is a **MISMATCH**,  an error is raised with details about the incorrect character.
    * Otherwise, the token is added to the **tokens** list.
6. **Update position**
   * **pos** is updated to the end of the current match.
7. **The function returns the list of tokens**
### Test cases list

This list has a set of different cases used to check the lexer' s functionality

```
test_cases = [
    # King's pawn to sicilian defense opening test
    "1. e4 c5 2. Nf3 d6 3. d4 cxd4 4. Nxd4 Nf6 5. Nc3",

    # castling sequence test
    "1. e4 e5 2. Nf3 Nc6 3. Bc4 Bc5 4. O-O Nf6 5. d3 O-O",

    # checks and checkmate test
    "1. e4 e5 2. Qh5 Nc6 3. Bc4 Nf6 4. Qxf7#",
]
```

### Running the test cases

This for loop is used to test the lexer and input the results.

```
for i, input_moves in enumerate(test_cases):
    print(f"\nTest Case {i + 1}: {input_moves}")
    try:
        tokens = lex(input_moves)
        print("Tokens:")
        for token in tokens:
            print(f"[{token[0]}, {token[1]}]")
    except ValueError as e:
        print(f"Error: {e}")
```

The way it works, is that it iterates through the **test_cases** list, calls the **lex** method to tokenize the input, and prints the tokens themselves.

## Results
```
Test Case 1: 1. e4 c5 2. Nf3 d6 3. d4 cxd4 4. Nxd4 Nf6 5. Nc3
Tokens:
[MOVE_NUM, 1.]
[SQUARE, e4]
[SQUARE, c5]
[MOVE_NUM, 2.]
[PIECE_MOVE, Nf3]
[SQUARE, d6]
[MOVE_NUM, 3.]
[SQUARE, d4]
[PAWN_CAPTURE, cxd4]
[MOVE_NUM, 4.]
[PIECE_CAPTURE, Nxd4]
[PIECE_MOVE, Nf6]
[MOVE_NUM, 5.]
[PIECE_MOVE, Nc3]

Test Case 2: 1. e4 e5 2. Nf3 Nc6 3. Bc4 Bc5 4. O-O Nf6 5. d3 O-O
Tokens:
[MOVE_NUM, 1.]
[SQUARE, e4]
[SQUARE, e5]
[MOVE_NUM, 2.]
[PIECE_MOVE, Nf3]
[PIECE_MOVE, Nc6]
[MOVE_NUM, 3.]
[PIECE_MOVE, Bc4]
[PIECE_MOVE, Bc5]
[MOVE_NUM, 4.]
[CASTLE, O-O]
[PIECE_MOVE, Nf6]
[MOVE_NUM, 5.]
[SQUARE, d3]
[CASTLE, O-O]

Test Case 3: 1. e4 e5 2. Qh5 Nc6 3. Bc4 Nf6 4. Qxf7#
Tokens:
[MOVE_NUM, 1.]
[SQUARE, e4]
[SQUARE, e5]
[MOVE_NUM, 2.]
[PIECE_MOVE, Qh5]
[PIECE_MOVE, Nc6]
[MOVE_NUM, 3.]
[PIECE_MOVE, Bc4]
[PIECE_MOVE, Nf6]
[MOVE_NUM, 4.]
[PIECE_CAPTURE, Qxf7]
[CHECKMATE, #]

Process finished with exit code 0
```

## Conclusion

This program implements a lexical analyzer (lexer) designed to tokenize chess move notations into meaningful components. It uses regular expressions to define and match patterns for various chess moves, such as piece moves, captures, castling, promotions, and other elements like checks and checkmates. The lexer processes an input string, identifies valid tokens, and handles errors for invalid characters or moves. 

The key components of the program include the token_specs list, which defines token names and their corresponding regex patterns, the tok_regex variable, which combines these patterns into a single regex string, and the pattern variable, which compiles the regex for efficient matching. The lex function serves as the core of the program, iterating through the input string, extracting tokens, and tracking line and column numbers for error reporting. 

A set of test cases is provided to validate the lexer's functionality, covering valid move sequences, edge cases, and invalid inputs. While the program is functional and achieves its goal, it could be improved for readability, maintainability, and scalability by separating concerns, using a class-based structure, adding documentation, and implementing custom exceptions. 

Overall, this lexer provides a solid foundation for parsing chess move notations and can be extended or refactored to handle more complex requirements in the future.


## References

[1] [A sample of a lexer implementation](https://llvm.org/docs/tutorial/MyFirstLanguageFrontend/LangImpl01.html)

[2] [Lexical analysis](https://en.wikipedia.org/wiki/Lexical_analysis)

[3] [Formal Languages and Finite Automata, Guide for practical lessons](https://else.fcim.utm.md/pluginfile.php/110458/mod_resource/content/0/LFPC_Guide.pdf)