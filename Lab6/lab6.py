import re
from enum import Enum, auto


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


class Token:
    def __init__(self, type, value, line=1, column=1):
        self.type = type
        self.value = value
        self.line = line
        self.column = column

    def __repr__(self):
        return f"Token({self.type.name}, '{self.value}', line={self.line}, col={self.column})"


token_specs = [
    (TokenType.MOVE_NUM, r'\d+\.'),
    (TokenType.CASTLE, r'O-O(?:-O)?'),
    (TokenType.PROMOTION, r'[a-h][18]=[NBRQ]'),
    (TokenType.PAWN_CAPTURE, r'[a-h]x[a-h][1-8]'),
    (TokenType.PIECE_CAPTURE, r'[NBRQK][a-h]?[1-8]?x[a-h][1-8]'),
    (TokenType.PIECE_MOVE, r'[NBRQK][a-h]?[1-8]?[a-h][1-8]'),
    (TokenType.PIECE, r'[NBRQK]'),
    (TokenType.PAWN_MOVE, r'[a-h][1-8]'),
    (TokenType.CAPTURE, r'x'),
    (TokenType.CHECK, r'\+'),
    (TokenType.CHECKMATE, r'#'),
    (TokenType.SEPARATOR, r'\s+'),
    (TokenType.MISMATCH, r'.'),
]

tok_regex = '|'.join(f'(?P<{name.name}>{pattern})' for name, pattern in token_specs)
pattern = re.compile(tok_regex)


def lex(input_str):
    tokens = []
    line_num = 1
    line_start = 0

    pos = 0
    while pos < len(input_str):
        match = pattern.match(input_str, pos)
        if not match:
            raise ValueError(f'No match found at position {pos}')

        token_type_name = match.lastgroup
        token_value = match.group(token_type_name)
        token_type = TokenType[token_type_name]

        line_num += input_str[pos:match.start()].count('\n')
        if '\n' in input_str[pos:match.start()]:
            line_start = input_str.rfind('\n', pos, match.start()) + 1
        column = match.start() - line_start + 1

        if token_type == TokenType.SEPARATOR:
            pass
        elif token_type == TokenType.MISMATCH:
            raise ValueError(f'Incorrect character {token_value!r} at line {line_num}, column {column}')
        else:
            tokens.append(Token(token_type, token_value, line_num, column))

        pos = match.end()

    return tokens


class ASTNode:
    pass


class Game(ASTNode):
    def __init__(self):
        self.moves = []

    def __repr__(self):
        return f"Game({len(self.moves)} moves)"


class Move(ASTNode):
    def __init__(self, number=None):
        self.number = number
        self.white_move = None
        self.black_move = None

    def __repr__(self):
        return f"Move({self.number}, white={self.white_move}, black={self.black_move})"


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

    def __repr__(self):
        origin = ""
        if self.origin_file:
            origin += self.origin_file
        if self.origin_rank:
            origin += self.origin_rank

        check = "+" if self.is_check else ""
        checkmate = "#" if self.is_checkmate else ""

        return f"PieceMove({self.piece}{origin}->{self.destination}{check}{checkmate})"


class PawnMove(MoveAction):
    def __init__(self, destination, promotion_piece=None):
        self.destination = destination
        self.promotion_piece = promotion_piece
        self.is_check = False
        self.is_checkmate = False

    def __repr__(self):
        promotion = f"={self.promotion_piece}" if self.promotion_piece else ""
        check = "+" if self.is_check else ""
        checkmate = "#" if self.is_checkmate else ""

        return f"PawnMove({self.destination}{promotion}{check}{checkmate})"


class Capture(MoveAction):
    def __init__(self, piece, origin_file=None, origin_rank=None, destination=None):
        self.piece = piece
        self.origin_file = origin_file
        self.origin_rank = origin_rank
        self.destination = destination
        self.is_check = False
        self.is_checkmate = False

    def __repr__(self):
        origin = ""
        if self.origin_file:
            origin += self.origin_file
        if self.origin_rank:
            origin += self.origin_rank

        check = "+" if self.is_check else ""
        checkmate = "#" if self.is_checkmate else ""

        return f"Capture({self.piece}{origin}x{self.destination}{check}{checkmate})"


class Castle(MoveAction):
    def __init__(self, is_kingside):
        self.is_kingside = is_kingside
        self.is_check = False
        self.is_checkmate = False

    def __repr__(self):
        castle_type = "Kingside" if self.is_kingside else "Queenside"
        check = "+" if self.is_check else ""
        checkmate = "#" if self.is_checkmate else ""

        return f"Castle({castle_type}{check}{checkmate})"


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
        if self.check(TokenType.MOVE_NUM):
            move_token = self.advance()
            move_number = move_token.value
            move = Move(move_number)

            white_move = self.move_action()
            if white_move:
                move.white_move = white_move

            if not self.is_at_end() and not self.check(TokenType.MOVE_NUM):
                black_move = self.move_action()
                if black_move:
                    move.black_move = black_move

            return move

        return None

    def move_action(self):
        if self.check(TokenType.CASTLE):
            token = self.advance()
            is_kingside = token.value == "O-O"
            castle = Castle(is_kingside)

            self.check_for_check_or_checkmate(castle)

            return castle

        elif self.check(TokenType.PROMOTION):
            token = self.advance()
            destination = token.value[:2]
            promotion_piece = token.value[3]

            pawn_move = PawnMove(destination, promotion_piece)
            self.check_for_check_or_checkmate(pawn_move)

            return pawn_move

        elif self.check(TokenType.PAWN_CAPTURE):
            token = self.advance()
            origin_file = token.value[0]
            destination = token.value[2:]

            capture = Capture("P", origin_file, None, destination)
            self.check_for_check_or_checkmate(capture)

            return capture

        elif self.check(TokenType.PIECE_CAPTURE):
            token = self.advance()
            value = token.value
            piece = value[0]

            x_pos = value.find('x')

            origin = value[1:x_pos]
            origin_file = None
            origin_rank = None

            if len(origin) == 1:
                if origin.isalpha():
                    origin_file = origin
                else:
                    origin_rank = origin
            elif len(origin) == 2:
                origin_file = origin[0]
                origin_rank = origin[1]

            destination = value[x_pos + 1:]

            capture = Capture(piece, origin_file, origin_rank, destination)
            self.check_for_check_or_checkmate(capture)

            return capture

        elif self.check(TokenType.PIECE_MOVE):
            token = self.advance()
            value = token.value
            piece = value[0]

            rest = value[1:]
            destination = rest[-2:]

            origin = rest[:-2]
            origin_file = None
            origin_rank = None

            if len(origin) == 1:
                if origin.isalpha():
                    origin_file = origin
                else:
                    origin_rank = origin
            elif len(origin) == 2:
                origin_file = origin[0]
                origin_rank = origin[1]

            piece_move = PieceMove(piece, origin_file, origin_rank, destination)
            self.check_for_check_or_checkmate(piece_move)

            return piece_move

        elif self.check(TokenType.PAWN_MOVE):
            token = self.advance()
            destination = token.value

            pawn_move = PawnMove(destination)
            self.check_for_check_or_checkmate(pawn_move)

            return pawn_move

        return None

    def check_for_check_or_checkmate(self, move_action):
        if self.check(TokenType.CHECK):
            self.advance()
            move_action.is_check = True
        elif self.check(TokenType.CHECKMATE):
            self.advance()
            move_action.is_checkmate = True

    def check(self, type):
        if self.is_at_end():
            return False
        return self.peek().type == type

    def advance(self):
        if not self.is_at_end():
            self.current += 1
        return self.tokens[self.current - 1]

    def peek(self):
        return self.tokens[self.current]

    def is_at_end(self):
        return self.current >= len(self.tokens)


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


test_cases = [
    # King's pawn to sicilian defense opening test
    "1. e4 c5 2. Nf3 d6 3. d4 cxd4 4. Nxd4 Nf6 5. Nc3",

    # castling sequence test
    "1. e4 e5 2. Nf3 Nc6 3. Bc4 Bc5 4. O-O Nf6 5. d3 O-O",

    # checks and checkmate test
    "1. e4 e5 2. Qh5 Nc6 3. Bc4 Nf6 4. Qxf7#",

    # Additional test cases
    "1. e4 e5 2. Nf3 Nc6 3. Bb5 a6 4. Ba4 Nf6 5. O-O Be7 6. Re1 b5 7. Bb3 d6 8. c3 O-O",  # Ruy Lopez
    "1. d4 Nf6 2. c4 e6 3. Nc3 Bb4",  # Nimzo-Indian Defense
]


def main():
    for i, input_moves in enumerate(test_cases):
        print(f"\n=== Test Case {i + 1} ===")
        print(f"Input: {input_moves}")

        try:
            tokens = lex(input_moves)
            print("\nTokens:")
            for j, token in enumerate(tokens):
                print(f"  {j}: {token}")

            parser = ChessParser(tokens)
            ast = parser.parse()

            print("\nAST Visualization (Tree Structure):")
            print(visualize_ast(ast))

        except ValueError as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()