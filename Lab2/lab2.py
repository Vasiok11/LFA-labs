import random


class Grammar:
    def __init__(self):
        self.VN = {'S', 'B', 'C'}
        self.VT = {'a', 'b', 'c'}
        self.P = {
            'S': ['aB'],
            'B': ['bC', 'bB'],
            'C': ['bB', 'c', 'aS']
        }
        self.start = 'S'

    def generate_string(self, max_depth=10):
        def derive(symbol, depth, derivation):
            if depth > max_depth:
                return '', derivation
            if symbol in self.VT:
                return symbol, derivation
            production = random.choice(self.P[symbol])
            derived_string = ''

            new_derivation = derivation + f"{symbol}→{production} "
            for s in production:
                result, new_derivation = derive(s, depth + 1, new_derivation)
                derived_string += result
            return derived_string, new_derivation

        return derive(self.start, 0, "")

    def generate_strings(self, count, max_depth=10):
        results = []
        for _ in range(count):
            derived_string, derivation = self.generate_string(max_depth)
            results.append((derived_string, derivation.strip()))
        return results

    def to_finite_automaton(self):
        states = {'qS', 'qB', 'qC', 'qF'}
        transitions = {
            'qS': {'a': {'qB'}},
            'qB': {'b': {'qB', 'qC'}},
            'qC': {'c': {'qF'}}
        }
        return FiniteAutomaton(states, self.VT, transitions, 'qS', {'qF'})

    def classify_grammar(self):
        is_regular = True
        is_context_free = True
        is_context_sensitive = True

        for lhs, rhs_list in self.P.items():
            for rhs in rhs_list:
                if len(rhs) > 2:
                    is_regular = False
                elif len(rhs) == 2:
                    if not (rhs[0] in self.VT and rhs[1] in self.VN):
                        is_regular = False
                elif len(rhs) == 1:
                    if not (rhs[0] in self.VT or rhs[0] in self.VN):
                        is_regular = False

                if len(lhs) != 1 or lhs not in self.VN:
                    is_context_free = False

                if len(rhs) < len(lhs):
                    is_context_sensitive = False

        if is_regular:
            return "Type 3 (Regular)"
        elif is_context_free:
            return "Type 2 (Context-Free)"
        elif is_context_sensitive:
            return "Type 1 (Context-Sensitive)"
        else:
            return "Type 0 (Unrestricted)"


class FiniteAutomaton:
    def __init__(self, states, alphabet, transitions, start_state, accept_states):
        self.states = states
        self.alphabet = alphabet
        self.transitions = transitions
        self.start_state = start_state
        self.accept_states = accept_states

    def accepts(self, input_string):
        current_states = {self.start_state}

        for symbol in input_string:
            next_states = set()
            for state in current_states:
                if state in self.transitions and symbol in self.transitions[state]:
                    next_states.update(self.transitions[state][symbol])
            if not next_states:
                return False
            current_states = next_states

        return bool(current_states & self.accept_states)


if __name__ == "__main__":
    grammar = Grammar()
    generated_strings = grammar.generate_strings(5, max_depth=10)
    print("The generated strings:")
    for string, derivation in generated_strings:
        print(f"String: {string}, Derivation: {derivation}")

    fa = grammar.to_finite_automaton()
    test_strings = [
        "abc",
        "abbc",
        "abbbc",
        "ac",
        "abb"
    ]

    print("\nTesting strings:")
    for s in test_strings:
        print(f"String {s} is {'correct' if fa.accepts(s) else 'wrong'} ")

    print("\nGrammar Classification:")
    print(grammar.classify_grammar())