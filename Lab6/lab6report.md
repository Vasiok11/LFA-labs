# Parser & Building an Abstract Syntax Tree
### Course: Formal Languages & Finite Automata
### Author: Pascari Vasile

----

## Theory

### Parsing and Abstract Syntax Trees

A **parser** is a software component that analyzes input data (typically text) and builds a data structure according to a formal grammar. Parsing is a crucial step that follows lexical analysis in language processing systems. While a lexer breaks input into tokens, a parser determines the syntactic structure of those tokens, checking if they conform to the grammar rules of the language.

An **Abstract Syntax Tree (AST)** is a hierarchical tree representation of the abstract syntactic structure of source code. Each node in the tree represents a construct in the source code. The tree is "abstract" because it does not represent every detail of the real syntax, but rather just the structural elements relevant for processing.

In the context of our chess notation language:
- The **lexer** identifies individual tokens like "e4", "Nf3", or "O-O"
- The **parser** combines these tokens into a structured representation of a chess game
- The **AST** shows the hierarchical relationships between moves, capturing the structure of the game

### Parsing Techniques

There are several common parsing techniques:

1. **Recursive Descent Parsing**: A top-down parsing technique where the parser has a function for each non-terminal symbol in the grammar. These functions call each other recursively to parse the input according to the grammar rules.

2. **LL Parsing**: A table-driven top-down parser that processes input from left to right and constructs a leftmost derivation.

3. **LR Parsing**: A bottom-up parser that reads input from left to right and constructs a rightmost derivation in reverse.

4. **Parser Generators**: Tools like YACC, Bison, or ANTLR that automatically generate parsers from grammar specifications.

For our chess notation parser, we've implemented a **recursive descent parser**, which is intuitive and straightforward for this domain-specific language.

## Objectives

The primary objectives of this lab work are to:

1. **Implement a TokenType Enum**: Create a structured way to categorize tokens identified by the lexer.

2. **Design an AST Structure**: Define node classes that can represent the hierarchical structure of chess games.

3. **Build a Parser**: Implement a parser that constructs an AST from the token stream.

4. **Visualize the AST**: Create a text-based visualization that clearly shows the structure of the AST.

## Implementation Description

### TokenType Enum

The `TokenType` enum provides a structured way to categorize tokens:

```python
class TokenType(Enum):
    MOVE_NUM = auto()        
    CASTLE = auto()          
    PROMOTION = auto()       
    PAWN_CAPTURE = auto()    
    PIECE_CAPTURE = auto()   
    PIECE_MOVE = auto()      
    PIECE = auto()           
    SQUARE = auto()          
    CAPTURE = auto()         
    CHECK = auto()           
    CHECKMATE = auto()       
    SEPARATOR = auto()       
    MISMATCH = auto()        
    PAWN_MOVE = auto()       
```

Each token type corresponds to a specific pattern in chess notation. The lexer uses regular expressions to identify these patterns and categorize the tokens accordingly.

### Token Class

The `Token` class encapsulates information about each identified token:

```python
class Token:
    def __init__(self, type, value, line=1, column=1):
        self.type = type
        self.value = value
        self.line = line
        self.column = column
    
    def __repr__(self):
        return f"Token({self.type.name}, '{self.value}', line={self.line}, col={self.column})"
```

This class stores not only the token type and value but also the line and column position, which is useful for error reporting.

### AST Node Classes

The AST is structured as a hierarchy of node classes that represent different elements of chess notation:

```python
class ASTNode:
    pass

class Game(ASTNode):
    def __init__(self):
        self.moves = []  # List of Move nodes

class Move(ASTNode):
    def __init__(self, number=None):
        self.number = number  # Move number (e.g., "1.")
        self.white_move = None  # MoveAction for white
        self.black_move = None  # MoveAction for black

class MoveAction(ASTNode):
    pass

class PieceMove(MoveAction):
    def __init__(self, piece, origin_file=None, origin_rank=None, destination=None):
        self.piece = piece
        self.origin_file = origin_file
        self.origin_rank = origin_rank
        self.destination = destination
        self.is_check = False
        self.is_checkmate = False

class PawnMove(MoveAction):
    def __init__(self, destination, promotion_piece=None):
        self.destination = destination
        self.promotion_piece = promotion_piece
        self.is_check = False
        self.is_checkmate = False

class Capture(MoveAction):
    def __init__(self, piece, origin_file=None, origin_rank=None, destination=None):
        self.piece = piece
        self.origin_file = origin_file
        self.origin_rank = origin_rank
        self.destination = destination
        self.is_check = False
        self.is_checkmate = False

class Castle(MoveAction):
    def __init__(self, is_kingside):
        self.is_kingside = is_kingside
        self.is_check = False
        self.is_checkmate = False
```

This structure allows us to represent:
- A complete chess game as a sequence of moves
- Each move number with its corresponding white and black actions
- Different types of move actions (piece moves, pawn moves, captures, castling)
- Special indicators like check and checkmate

### Parser Implementation

The `ChessParser` class implements a recursive descent parser for chess notation:

```python
class ChessParser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current = 0
    
    def parse(self):
        game = Game()
        
        while not self.is_at_end():
            move = self.move()
            if move:
                game.moves.append(move)
        
        return game
    
    def move(self):
        # parses a single move

    def move_action(self):
        # parses different types of move actions

    # Helper methods
    def check_for_check_or_checkmate(self, move_action):
        # check/checkmate checker
    
    def check(self, type):
        # ...
    
    def advance(self):
        # ...
    
    def peek(self):
        # ...
    
    def is_at_end(self):
        # ...
```

The parser processes tokens sequentially, building the AST as it goes. It uses a set of methods, each responsible for parsing a specific part of the chess notation:

- `parse()`: Builds the complete game tree
- `move()`: Parses a single move (move number, white's move, black's move)
- `move_action()`: Parses individual move actions (castling, pawn moves, piece moves, captures)

The parser uses helper methods like `check()`, `advance()`, `peek()`, and `is_at_end()` to manage token consumption and lookahead.

### AST Visualization

To visualize the AST, we implemented a text-based visualization function that uses ASCII characters to represent the tree structure:

```python
def visualize_ast(ast):
    result = []

    def _visualize_node(node, prefix="", is_last=True, is_root=True):
        branch = "└── " if is_last else "├── "

        if not is_root:
            result.append(f"{prefix}{branch}{_node_str(node)}")
        else:
            result.append(_node_str(node))

        child_prefix = prefix
        if not is_root:
            child_prefix += "    " if is_last else "│   "

        if isinstance(node, Game):
            for i, move in enumerate(node.moves):
                _visualize_node(move, child_prefix, i == len(node.moves) - 1, False)
        elif isinstance(node, Move):
            white_prefix = child_prefix

            if node.white_move and node.black_move:
                result.append(f"{child_prefix}├── White: ")
                _visualize_node(node.white_move, child_prefix + "│   ", False, False)

                result.append(f"{child_prefix}└── Black: ")
                _visualize_node(node.black_move, child_prefix + "    ", True, False)
            elif node.white_move:
                result.append(f"{child_prefix}└── White: ")
                _visualize_node(node.white_move, child_prefix + "    ", True, False)
            elif node.black_move:
                result.append(f"{child_prefix}└── Black: ")
                _visualize_node(node.black_move, child_prefix + "    ", True, False)

    def _node_str(node):
        if isinstance(node, Game):
            return f"Game ({len(node.moves)} moves)"
        elif isinstance(node, Move):
            return f"Move {node.number}"
        elif isinstance(node, PieceMove):
            origin = ""
            if node.origin_file:
                origin += node.origin_file
            if node.origin_rank:
                origin += node.origin_rank

            check = "+" if node.is_check else ""
            checkmate = "#" if node.is_checkmate else ""

            return f"PieceMove: {node.piece}{origin}->{node.destination}{check}{checkmate}"
        elif isinstance(node, PawnMove):
            promotion = f"={node.promotion_piece}" if node.promotion_piece else ""
            check = "+" if node.is_check else ""
            checkmate = "#" if node.is_checkmate else ""

            return f"PawnMove: ->{node.destination}{promotion}{check}{checkmate}"
        elif isinstance(node, Capture):
            origin = ""
            if node.origin_file:
                origin += node.origin_file
            if node.origin_rank:
                origin += node.origin_rank

            piece_name = "Pawn" if node.piece == "P" else node.piece
            check = "+" if node.is_check else ""
            checkmate = "#" if node.is_checkmate else ""

            return f"Capture: {piece_name}{origin}x{node.destination}{check}{checkmate}"
        elif isinstance(node, Castle):
            castle_type = "Kingside" if node.is_kingside else "Queenside"
            check = "+" if node.is_check else ""
            checkmate = "#" if node.is_checkmate else ""

            return f"Castle: {castle_type}{check}{checkmate}"
        else:
            return str(node)

    _visualize_node(ast)

    return '\n'.join(result)
```

This function recursively traverses the AST, generating a  representation with proper indentation and branch connections:

```
Game (3 moves)
├── Move 1.
│   ├── White: 
│   │   └── PawnMove: ->e4
│   └── Black: 
│       └── PieceMove: N->f6
├── Move 2.
│   ├── White: 
│   │   └── PawnMove: ->c4
│   └── Black: 
│       └── PawnMove: ->e6
└── Move 3.
    ├── White: 
    │   └── PieceMove: N->c3
    └── Black: 
        └── PieceMove: B->b4
```

The visualization uses:
- "└──" for the last child in a branch
- "├──" for non-last children
- "│" for vertical lines connecting nodes
- Proper indentation to show parent-child relationships

## Results

### Example: Sicilian Defense Opening

Input: `1. e4 c5 2. Nf3 d6 3. d4 cxd4 4. Nxd4 Nf6 5. Nc3`
```
=== Test Case 1 ===
Input: 1. e4 c5 2. Nf3 d6 3. d4 cxd4 4. Nxd4 Nf6 5. Nc3

Tokens:
  0: Token(MOVE_NUM, '1.', line=1, col=1)
  1: Token(PAWN_MOVE, 'e4', line=1, col=4)
  2: Token(PAWN_MOVE, 'c5', line=1, col=7)
  3: Token(MOVE_NUM, '2.', line=1, col=10)
  4: Token(PIECE_MOVE, 'Nf3', line=1, col=13)
  5: Token(PAWN_MOVE, 'd6', line=1, col=17)
  6: Token(MOVE_NUM, '3.', line=1, col=20)
  7: Token(PAWN_MOVE, 'd4', line=1, col=23)
  8: Token(PAWN_CAPTURE, 'cxd4', line=1, col=26)
  9: Token(MOVE_NUM, '4.', line=1, col=31)
  10: Token(PIECE_CAPTURE, 'Nxd4', line=1, col=34)
  11: Token(PIECE_MOVE, 'Nf6', line=1, col=39)
  12: Token(MOVE_NUM, '5.', line=1, col=43)
  13: Token(PIECE_MOVE, 'Nc3', line=1, col=46)

AST Visualization (Tree Structure):
Game (5 moves)
├── Move 1.
│   ├── White: 
│   │   ├── PawnMove: ->e4
│   └── Black: 
│       └── PawnMove: ->c5
├── Move 2.
│   ├── White: 
│   │   ├── PieceMove: N->f3
│   └── Black: 
│       └── PawnMove: ->d6
├── Move 3.
│   ├── White: 
│   │   ├── PawnMove: ->d4
│   └── Black: 
│       └── Capture: Pawncxd4
├── Move 4.
│   ├── White: 
│   │   ├── Capture: Nxd4
│   └── Black: 
│       └── PieceMove: N->f6
└── Move 5.
    └── White: 
        └── PieceMove: N->c3
```

This AST correctly represents the structure of the Sicilian Defense opening.



## Conclusion

In this lab work, we successfully implemented a parser and AST for chess notation, building upon the lexer from the previous lab. The implementation demonstrates the key concepts of parsing and abstract syntax trees:

1. **Token Type Enumeration**: We created a structured way to categorize tokens, enhancing the lexer from the previous lab.

2. **AST Design**: We designed a hierarchical structure that effectively represents the syntax and semantics of chess notation.

3. **Recursive Descent Parsing**: We implemented a parser that constructs an AST from a sequence of tokens, using a clear and intuitive recursive descent approach.

4. **AST Visualization**: We created a text-based visualization that clearly shows the structure of the AST, using ASCII characters to represent the tree hierarchy.

The parser and AST form a solid foundation for further development of chess-related applications, such as game analysis, visualization, or computer opponents. By processing chess notation into a structured representation, they enable more sophisticated processing and analysis of chess games.

This lab work has demonstrated the power of parsing and abstract syntax trees in the context of domain-specific languages. These techniques are widely applicable in compiler construction, programming language design, and various text-processing applications, making them valuable tools in the field of formal languages and automata.

## References

[1] Alfred V. Aho, Monica S. Lam, Ravi Sethi, and Jeffrey D. Ullman. (2006). "Compilers: Principles, Techniques, and Tools (2nd Edition)". Addison Wesley.

[2] Robert Nystrom. (2021). "Crafting Interpreters". Genever Benning.

[3] Terence Parr. (2010). "Language Implementation Patterns: Create Your Own Domain-Specific and General Programming Languages". Pragmatic Bookshelf.

[4] Formal Languages and Finite Automata, Guide for practical lessons. Retrieved from https://else.fcim.utm.md/pluginfile.php/110458/mod_resource/content/0/LFPC_Guide.pdf