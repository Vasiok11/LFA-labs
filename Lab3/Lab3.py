import re

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

tok_regex = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in token_specs)
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


# test cases
test_cases = [
    # King's pawn to sicilian defense opening test
    "1. e4 c5 2. Nf3 d6 3. d4 cxd4 4. Nxd4 Nf6 5. Nc3",

    # castling sequence test
    "1. e4 e5 2. Nf3 Nc6 3. Bc4 Bc5 4. O-O Nf6 5. d3 O-O",

    # checks and checkmate test
    "1. e4 e5 2. Qh5 Nc6 3. Bc4 Nf6 4. Qxf7#",
]

for i, input_moves in enumerate(test_cases):
    print(f"\nTest Case {i + 1}: {input_moves}")
    try:
        tokens = lex(input_moves)
        print("Tokens:")
        for token in tokens:
            print(f"[{token[0]}, {token[1]}]")
    except ValueError as e:
        print(f"Error: {e}")