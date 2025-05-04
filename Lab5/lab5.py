import itertools
from collections import OrderedDict


class ChomskyNormalizer:
    def __init__(self, Vn, Vt, P, S):
        self.Vn = Vn.copy()
        self.Vt = Vt.copy()
        self.P = self._parse_productions(P)
        self.S = S
        self.terminal_map = {}
        self.pair_map = OrderedDict()
        self.new_nonterm_counter = 0
        self.original_S = S

    def _parse_productions(self, P):
        productions = {}
        for rule in P.split(','):
            rule = rule.strip()
            if not rule:
                continue
            left, right = rule.split('->')
            left = left.strip()
            alternatives = [alt.strip() for alt in right.split('|')]
            productions[left] = alternatives
        return productions

    def _get_new_nonterminal(self, prefix='N'):
        new_nonterm = f"{prefix}{self.new_nonterm_counter}"
        self.new_nonterm_counter += 1
        return new_nonterm

    def eliminate_epsilons(self):
        nullable = set()
        changed = True
        while changed:
            changed = False
            for left, rights in self.P.items():
                if left in nullable:
                    continue

                for rule in rights:
                    if rule == 'ε' or (rule and all(sym in nullable for sym in rule.split())):
                        nullable.add(left)
                        changed = True
                        break

        has_empty_string = self.S in nullable

        new_P = {}
        for left, rights in self.P.items():
            new_rules = set()
            for rule in rights:
                if rule == 'ε':
                    continue

                symbols = rule.split()
                nullable_indices = [i for i, sym in enumerate(symbols) if sym in nullable]

                for r in range(len(nullable_indices) + 1):
                    for indices_to_remove in itertools.combinations(nullable_indices, r):
                        new_rule = [sym for i, sym in enumerate(symbols) if i not in indices_to_remove]
                        if new_rule:
                            new_rules.add(' '.join(new_rule))

            if new_rules:
                new_P[left] = list(new_rules)

        if has_empty_string:
            new_S = self._get_new_nonterminal('S')
            self.Vn.append(new_S)
            new_P[new_S] = [self.S]
            if 'ε' not in new_P.get(self.S, []):
                new_P.setdefault(self.S, []).append('ε')
            self.original_S = self.S
            self.S = new_S

        self.P = new_P

    def eliminate_unit_rules(self):
        unit_pairs = {}

        for left, rights in self.P.items():
            unit_pairs[left] = {left}
            for rule in rights:
                if rule in self.Vn:
                    unit_pairs[left].add(rule)

        changed = True
        while changed:
            changed = False
            for A in self.Vn:
                current_set = unit_pairs.get(A, set())
                new_set = current_set.copy()

                for B in current_set:
                    new_set.update(unit_pairs.get(B, set()))

                if len(new_set) > len(current_set):
                    unit_pairs[A] = new_set
                    changed = True

        new_P = {}
        for A in self.Vn:
            new_rules = []
            for B in unit_pairs.get(A, set()):
                for rule in self.P.get(B, []):
                    if rule not in self.Vn and rule != 'ε':
                        new_rules.append(rule)

            if new_rules:
                new_P[A] = new_rules

        self.P = new_P

    def eliminate_inaccessible_symbols(self):
        accessible = set()
        queue = [self.S]

        while queue:
            current = queue.pop(0)
            if current not in accessible:
                accessible.add(current)
                for rule in self.P.get(current, []):
                    for sym in rule.split():
                        if sym in self.Vn and sym not in accessible:
                            queue.append(sym)

        self.Vn = [nt for nt in self.Vn if nt in accessible]

        self.P = {k: v for k, v in self.P.items() if k in accessible}

    def eliminate_nonproductive_symbols(self):
        productive = set()

        for left, rights in self.P.items():
            for rule in rights:
                if rule == 'ε' or all(sym in self.Vt for sym in rule.split()):
                    productive.add(left)
                    break

        changed = True
        while changed:
            changed = False
            for left, rights in self.P.items():
                if left in productive:
                    continue

                for rule in rights:
                    if all(sym in self.Vt or sym in productive for sym in rule.split()):
                        productive.add(left)
                        changed = True
                        break

        if self.S not in productive:
            raise ValueError("Grammar does not generate any strings (start symbol is not productive)")

        self.Vn = [nt for nt in self.Vn if nt in productive]

        new_P = {}
        for left in self.Vn:
            new_rules = []
            for rule in self.P.get(left, []):
                symbols = rule.split()
                if rule == 'ε' or all(sym in self.Vt or sym in productive for sym in symbols):
                    new_rules.append(rule)
            if new_rules:
                new_P[left] = new_rules

        self.P = new_P

    def _ensure_terminal_rules(self):
        for term in self.Vt:
            new_nonterm = self._get_new_nonterminal('T')
            self.terminal_map[term] = new_nonterm
            self.Vn.append(new_nonterm)
            self.P[new_nonterm] = [term]

        for left in list(self.P.keys()):
            new_rules = []
            for rule in self.P[left]:
                symbols = rule.split()
                if len(symbols) == 1 and symbols[0] in self.Vt:
                    new_rules.append(rule)
                else:
                    new_rule = []
                    for sym in symbols:
                        if sym in self.Vt:
                            new_rule.append(self.terminal_map[sym])
                        else:
                            new_rule.append(sym)
                    new_rules.append(' '.join(new_rule))
            self.P[left] = new_rules

    def _split_long_rules(self):
        for left in list(self.P.keys()):
            new_rules = []
            for rule in self.P[left]:
                symbols = rule.split()
                if len(symbols) <= 2:
                    new_rules.append(rule)
                elif len(symbols) > 2:
                    current_symbols = symbols
                    while len(current_symbols) > 2:
                        first_two = ' '.join(current_symbols[:2])
                        if first_two not in self.pair_map:
                            new_nonterm = self._get_new_nonterminal('N')
                            self.pair_map[first_two] = new_nonterm
                            self.Vn.append(new_nonterm)
                            self.P[new_nonterm] = [first_two]

                        current_symbols = [self.pair_map[first_two]] + current_symbols[2:]

                    new_rules.append(' '.join(current_symbols))

            self.P[left] = new_rules

    def convert_to_cnf(self):
        if any(self.S in rule.split() for rules in self.P.values() for rule in rules):
            new_S = self._get_new_nonterminal('S')
            self.Vn.append(new_S)

            self.P[new_S] = self.P[self.S].copy()
            self.S = new_S

        for rule in self.P.get(self.S, []):
            if rule == 'ε':
                self.P[self.S].remove('ε')
                if not self.P[self.S]:
                    placeholder = self._get_new_nonterminal('X')
                    self.Vn.append(placeholder)
                    self.P[placeholder] = ['ε']
                    self.P[self.S] = [placeholder]
                break

        self._ensure_terminal_rules()
        self._split_long_rules()

        self.eliminate_unit_rules()

    def normalize(self):
        print("initial grammar:")
        print(self)

        self.eliminate_epsilons()
        print("\nε-elimination:")
        print(self)

        self.eliminate_unit_rules()
        print("\nunit rule elimination:")
        print(self)

        self.eliminate_inaccessible_symbols()
        print("\nremoving inaccessible symbols:")
        print(self)

        self.eliminate_nonproductive_symbols()
        print("\nremoving non-productive symbols:")
        print(self)

        self.convert_to_cnf()
        print("\nFinal CNF:")
        print(self)

        return self

    def __str__(self):
        lines = []
        for left in sorted(self.P.keys()):
            if not self.P[left]:
                continue
            rhs = ' | '.join(self.P[left])
            lines.append(f"{left} -> {rhs}")
        return '\n'.join(lines)


def test_variant_23():
    print("Variant 23:")
    Vn = ["S", "A", "B", "C", "E"]
    Vt = ["a", "b"]
    P = "S -> b A C | B, A -> a | a S | b C a C b, B -> A C | b S | a A a, C -> ε | A B, E -> B A"
    S = "S"

    normalizer = ChomskyNormalizer(Vn, Vt, P, S)
    normalizer.normalize()


def test_variant_10():
    print("\n\n" + "="*50 + "\n")
    print("Testing Variant 10:")
    Vn = ["S", "A", "B", "D"]
    Vt = ["a", "b", "d"]
    P = "S -> d B | S A B, A -> d | d S | a A a A b | ε, B -> a | a S | B A, D -> A b a"
    S = "S"

    normalizer = ChomskyNormalizer(Vn, Vt, P, S)
    normalizer.normalize()


if __name__ == "__main__":
    test_variant_23()
    test_variant_10()