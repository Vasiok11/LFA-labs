
# Intro to formal languages. Regular grammars. Finite Automata.

### Course: Formal Languages & Finite Automata
### Author: Pascari Vasile
### Variant: 23

----

## Theory
A formal language consists of an alphabet, a vocabulary, and a grammar.
The grammar defines the rules for constructing valid words in the language, and the automaton defines a mechanism for recognizing strings belonging to the language.
This project explores the relationship between regular grammars and finite automata by converting a given grammar into a finite automaton and checking if a string belongs to the language defined by the grammar.
A finite automaton (FA) is a state machine with a finite number of states that processes input strings one symbol at a time, transitioning between states based on predefined rules.


## Objectives:

* Implement a Grammar class to represent a given grammar.
* Implement a Finite Automaton (FA) class to convert the grammar to an automaton.
* Implement a method to generate valid strings from the grammar.
* Implement functionality to check if a string belongs to the language accepted by the automaton.


## Implementation description

* The "Grammar" class has predefined sets of non-terminals, terminals, rules and the start symbol based on my given variant.

```
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
```

* The "generate_string" method generates valid strings with the help of recursion and depth to prevent infinite derivations
* It has a "derive" function that tracks the generated string and the derivation steps shown in the output

```
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
```

* "generate_strings" is used to generate multiple strings and their derivations, and it returns a list containing each string and derivation steps.

```
    def generate_strings(self, count, max_depth=10):
        results = []
        for _ in range(count):
            derived_string, derivation = self.generate_string(max_depth)
            results.append((derived_string, derivation.strip()))
        return results
```

* The method "to_finite_automaton" has the purpose of converting the grammar to Finite Automaton, and has states and transitions used to recognize the same language as the grammar.

```
        def to_finite_automaton(self):
        states = {'qS', 'qB', 'qC', 'qF'}
        transitions = {
            'qS': {'a': {'qB'}},
            'qB': {'b': {'qB', 'qC'}},
            'qC': {'c': {'qF'}}
        }
        return FiniteAutomaton(states, self.VT, transitions, 'qS', {'qF'})
```

* "FiniteAutomaton" class implements the strings check, and the method "accepts" tracks the possible states and transitions.

```
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
        
```        
## Results
* Here is an example of an output. The program generates strings based on the given rules and it displays the derivations. The finite automaton check also works : "abc" string is correct, because it ends in "c". "abb" is wrong, because it doesn't end with c, which means that it isn't a finite automaton, and "ac" is wrong simply because it doesn't follow the grammar rules.
```
The generated strings:
String: abbaabc, Derivation: S→aB B→bB B→bC C→aS S→aB B→bC C→c
String: abc, Derivation: S→aB B→bC C→c
String: abbaabbaab, Derivation: S→aB B→bB B→bC C→aS S→aB B→bB B→bC C→aS S→aB B→bC C→c
String: abbbbc, Derivation: S→aB B→bB B→bB B→bB B→bC C→c
String: abbbbbaaba, Derivation: S→aB B→bC C→bB B→bB B→bB B→bC C→aS S→aB B→bC C→aS S→aB
 
Testing strings:
String abc is correct 
String abbc is correct 
String abbbc is correct 
String ac is wrong 
String abb is wrong 
```
## Conclusion

The code succesfully implements the generation of grammar based on a given set of rules, and it also implements the conversion of grammar into a finite automaton.
I used 2 main classes for that: Grammar and FiniteAutomaton. The Grammar class is responsible for generating strings with their derivation steps, while the FiniteAutomaton class checks whether a string belons to the language.
So for example, the string "abbbc" is accepted because it follows valid transitions (S - aB- abC - abbC -abbbc), while "abb" is incorrect because it doesn't end with "c" so it doesn't reach the final state.

## References

_Formal Languages and Finite Automata, Guide for practical lessons_ by COJUHARI Irina, DUCA Ludmila, FIODOROV Ion.
