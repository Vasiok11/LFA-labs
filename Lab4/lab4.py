import random
import re


class CombinationGenerator:
    def __init__(self, max_repetitions=5):
        self.max_repetitions = max_repetitions
        self.steps = []

    def tokenize(self, regex_str):
        self.steps.append(f"1. Tokenizing: '{regex_str}'")

        patterns = [
            (r'\([^()]+\)(?:\*|\+|\?|\d+)?', 'group'),
            (r'[A-Za-z0-9]\*', 'zero_or_more'),
            (r'[A-Za-z0-9]\+', 'one_or_more'),
            (r'[A-Za-z0-9]\?', 'optional'),
            (r'[A-Za-z0-9]\d+', 'repeat'),
            (r'[A-Za-z0-9]', 'literal')
        ]

        tokens = []
        i = 0
        while i < len(regex_str):
            matched = False
            for pattern, token_type in patterns:
                match = re.match(pattern, regex_str[i:])
                if match:
                    token_text = match.group(0)
                    tokens.append((token_text, token_type))
                    i += len(token_text)
                    matched = True
                    break

            if not matched:
                if regex_str[i].isspace():
                    i += 1
                else:
                    tokens.append((regex_str[i], 'literal'))
                    i += 1

        token_summary = ", ".join([f"'{t[0]}'" for t in tokens])
        self.steps.append(f"2. Tokens identified: {token_summary}")
        return tokens

    def parse_group(self, group_token):
        match = re.match(r'\(([^()]+)\)(?:([*+?])|(\d+))?', group_token)
        if not match:
            return [group_token], [1]

        content, operator, repeat_count = match.groups()
        alternatives = [alt.strip() for alt in content.split('|')]

        if operator == '*':
            possible_counts = range(self.max_repetitions + 1)
            rep_type = "zero or more (0-5)"
        elif operator == '+':
            possible_counts = range(1, self.max_repetitions + 1)
            rep_type = "one or more (1-5)"
        elif operator == '?':
            possible_counts = range(2)
            rep_type = "optional (0-1)"
        elif repeat_count:
            count = int(repeat_count)
            possible_counts = [count]
            rep_type = f"exactly {count}"
        else:
            possible_counts = [1]
            rep_type = "exactly 1"

        self.steps.append(f"- Group '{group_token}': alternatives={alternatives}, repetition={rep_type}")
        return alternatives, possible_counts

    def generate_combinations(self, regex_str, count=10, seed=None):
        if seed is not None:
            random.seed(seed)

        self.steps = []
        self.steps.append(f"Processing regex: '{regex_str}'")

        normalized_regex = regex_str
        for i in range(2, 10):
            if i == 2:
                normalized_regex = normalized_regex.replace('²', '2')
            elif i == 3:
                normalized_regex = normalized_regex.replace('³', '3')
            else:
                normalized_regex = normalized_regex.replace(f'^{i}', str(i))

        tokens = self.tokenize(normalized_regex)
        combinations = []

        for i in range(count):
            combination = []
            self.steps.append(f"\ncombination #{i + 1}:")

            for token, token_type in tokens:
                if token_type == 'literal':
                    combination.append(token)
                    self.steps.append(f"- Literal '{token}': added")

                elif token_type == 'zero_or_more':
                    char = token[0]
                    rep_count = random.randint(0, self.max_repetitions)
                    combination.append(char * rep_count)
                    self.steps.append(f"- '{char}*': using {rep_count} occurrences (repetition = zero or more)")

                elif token_type == 'one_or_more':
                    char = token[0]
                    rep_count = random.randint(1, self.max_repetitions)
                    combination.append(char * rep_count)
                    self.steps.append(f"- '{char}+': using {rep_count} occurrences")

                elif token_type == 'optional':
                    char = token[0]
                    rep_count = random.randint(0, 1)
                    if rep_count == 1:
                        combination.append(char)
                        self.steps.append(f"- '{char}?': included")
                    else:
                        self.steps.append(f"- '{char}?': omitted")

                elif token_type == 'repeat':
                    match = re.match(r'([A-Za-z0-9])(\d+)', token)
                    if match:
                        char, count = match.groups()
                        count = int(count)
                        combination.append(char * count)
                        self.steps.append(f"- '{char}{count}': repeated {count} times")
                    else:
                        self.steps.append(f"- Failed to parse repeat token: '{token}'")
                        combination.append(token)

                elif token_type == 'group':
                    alternatives, possible_counts = self.parse_group(token)

                    repeat_count = random.choice(possible_counts)

                    if repeat_count > 0:
                        chosen_alternative = random.choice(alternatives)
                        group_value = chosen_alternative * repeat_count
                        self.steps.append(
                            f"- Group '{token}': selected '{chosen_alternative}' repeated {repeat_count} times")
                    else:
                        group_value = ""
                        self.steps.append(f"- Group '{token}': selected 0 repetitions")

                    combination.append(group_value)

            result = ''.join(combination)
            combinations.append(result)
            self.steps.append(f"- Result: '{result}'")

        return combinations

    def get_processing_steps(self):
        return self.steps


def main():
    generator = CombinationGenerator(max_repetitions=5)

    example_regexes = [
        "O(P|Q|R)+ 2(3|4)",
        "A*B(C|D|E)F(G|H|I)²",
        "J+K(L|M|N)*O?(P|Q)³"
    ]

    for regex in example_regexes:
        print(f"\nGenerating combinations for: {regex}")
        combinations = generator.generate_combinations(regex, count=5)
        print("Sample combinations:")
        for combo in combinations:
            print(f"  - {combo}")

        print("\nProcessing steps:")
        for step in generator.get_processing_steps():
            print(f"  {step}")


if __name__ == "__main__":
    main()