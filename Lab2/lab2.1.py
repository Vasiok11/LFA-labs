from graphviz import Digraph

def convert_to_regular_grammar(ndfa):
    productions = {}
    for state in ndfa['states']:
        productions[state] = []
        if state in ndfa['final_states']:
            productions[state].append('ε')
        if state in ndfa['transitions']:
            for symbol, next_states in ndfa['transitions'][state].items():
                for next_state in next_states:
                    productions[state].append(f"{symbol}{next_state}")
    return productions

def is_deterministic(ndfa):
    for state, trans in ndfa['transitions'].items():
        for symbol in trans:
            if len(trans[symbol]) > 1:
                return False
    return True

def convert_ndfa_to_dfa(ndfa):
    initial = frozenset({ndfa['initial_state']})
    dfa_states = {initial}
    queue = [initial]
    transitions = {}
    final_states = set()

    while queue:
        current = queue.pop(0)
        if any(s in ndfa['final_states'] for s in current):
            final_states.add(current)
        transitions[current] = {}
        for symbol in ndfa['alphabet']:
            next_states = set()
            for state in current:
                next_states.update(ndfa['transitions'].get(state, {}).get(symbol, set()))
            next_fs = frozenset(next_states)
            if next_fs not in dfa_states and next_fs:
                dfa_states.add(next_fs)
                queue.append(next_fs)
            transitions[current][symbol] = next_fs

    state_names = {}
    for i, state in enumerate(dfa_states):
        state_names[state] = f'q{"".join(sorted(state))}' if state else 'dead'

    dfa = {
        'states': [state_names[s] for s in dfa_states],
        'alphabet': list(ndfa['alphabet']),
        'initial_state': state_names[initial],
        'final_states': [state_names[s] for s in final_states],
        'transitions': {}
    }
    for state in transitions:
        dfa['transitions'][state_names[state]] = {
            sym: state_names.get(next_state, 'dead')
            for sym, next_state in transitions[state].items()
        }
    return dfa

def draw_fa(fa, filename, title):
    dot = Digraph(comment=title)
    dot.attr(rankdir='LR')

    for state in fa['states']:
        if state in fa['final_states']:
            dot.node(state, shape='doublecircle')
        else:
            dot.node(state, shape='circle')

    for state, transitions in fa['transitions'].items():
        for symbol, next_state in transitions.items():
            if isinstance(next_state, set):
                for ns in next_state:
                    dot.edge(state, ns, label=symbol)
            else:
                dot.edge(state, next_state, label=symbol)

    dot.node('start', shape='point')
    dot.edge('start', fa['initial_state'])

    dot.render(filename, format='png', cleanup=True)
    print(f"{title} graph saved as '{filename}.png'")

def main():
    ndfa = {
        'states': {'q0', 'q1', 'q2'},
        'alphabet': {'a', 'b'},
        'initial_state': 'q0',
        'final_states': {'q2'},
        'transitions': {
            'q0': {'a': {'q0', 'q1'}, 'b': {'q0'}},
            'q1': {'a': {'q0'}, 'b': {'q2'}},
            'q2': {'b': {'q2'}}
        }
    }

    grammar = convert_to_regular_grammar(ndfa)
    print("Regular Grammar Productions:")
    for nt in sorted(grammar.keys()):
        print(f"{nt} → {' | '.join(grammar[nt])}")

    print("\nIs Deterministic?", is_deterministic(ndfa))

    dfa = convert_ndfa_to_dfa(ndfa)
    print("\nDFA:")
    print("States:", dfa['states'])
    print("Alphabet:", dfa['alphabet'])
    print("Initial State:", dfa['initial_state'])
    print("Final States:", dfa['final_states'])
    print("Transitions:")
    for state in dfa['transitions']:
        for sym, next_state in dfa['transitions'][state].items():
            print(f"{state} --{sym}--> {next_state}")

    draw_fa(ndfa, 'ndfa_graph', 'NDFA')
    draw_fa(dfa, 'dfa_graph', 'DFA')

if __name__ == "__main__":
    main()