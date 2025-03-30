# Regular expressions
### Course: Formal Languages & Finite Automata
### Author: Pascari Vasile
### Variant: 3

----

## Theory

### What are regular expressions?

Regular expressions (regex or regexp) are specialized text patterns that describe search criteria. They act as a powerful query language for text, allowing you to specify complex patterns to match, extract, or manipulate strings. Developed in the 1950s by mathematician Stephen Cole Kleene as a notation for regular languages, they've become an indispensable tool in computing, text processing, and data analysis.
At their core, regex patterns define rules for matching character sequences, enabling precise text operations that would be cumbersome or impossible with simple string methods. Their compact syntax packs remarkable expressive power, making them both challenging to master and incredibly valuable once understood.

### What Are Regular Expressions Used For?

Regular expressions are essential tools for text processing across many domains. Developers use them for validating user input like email addresses or phone numbers. Data analysts employ regex for searching through large datasets to find specific patterns or extracting particular information from unstructured text.

They excel at tasks such as:
- **Validation** of formatted strings like postal codes or credit card numbers
- **Search and replace** operations in text editors and word processors
- **Data extraction** from logs, documents, or web pages

### Basic Regex Components

The pattern `^\d{3}-\d{2}-\d{4}$` would match a U.S. Social Security Number format (123-45-6789) by combining several fundamental building blocks:

Literal characters match exactly as written, while metacharacters like the period (.) match any single character. Quantifiers such as asterisk (*), plus (+), and curly braces ({n}) control how many times a pattern should match. Character classes defined with square brackets [abc] match any character from the specified set.

This syntax follows formal language theory principles, making patterns both precise and computationally efficient. Despite their cryptic appearance, they represent a formal grammar that can be processed by finite state machines. This theoretical foundation enables regex engines to perform complex pattern matching with remarkable efficiency.

These patterns are implemented in virtually all programming languages, text editors, and many command-line tools, making them a universal skill for anyone working with text data.

## Objectives

The primary objectives of this lab are to:

1. Write and cover what regular expressions are, what they are used for;
2. Write a code that will generate valid combinations of symbols conform given regular expressions by giving a set of regexes as input and get valid word as an output
3. Write a function that will show sequence of processing regular expression
## Implementation description

In this section, i will talk about the implementation of the Regular expression combinations generator and explain each part of the code separately.


### tokenize method

The ```tokenize``` method has the purpose of breaking down regex patterns into understandable patterns for the code:

```
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
```

The way it works is that it starts by logging the tokenization step, and then defines the pattern matches for different regex elements, those elements being:
* Groups with quantifiers ```(abc)*```
* Zero-or-more ```a*```
* One-or-more ```b*```
* Optionals ```c?```
* Literal repetitions 
* Simple literals

The method has multiple layers of processing. As previously mentioned, it begins by logging the input string. After that, it defines a priority-ordered list of pattern matches, with groups being highest priority and applies patterns sequentially until all tokens are identified.

### parse_group method

This method handles the regex structures through patterns analysis, and returns both the alternatives and repetition counts, providing everything necessary for the subsequent  random generation

```
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
```
The key aspects of this method are:
* Structural parsing through the usage of a regex in order to decompose groups into content and quantifiers
* It splits group content by ```|``` to identify all valid options
* Distinguishes between ```*```, ```+```, ```?``` and exact counts
* And handles bare groups without quantifiers



### The generate_combinations method

This is the core generation method which combines all the components. It has a multi-stage process, which starts by iterating through the tokens to build outputs, and then makes probabilistic choices for alternatives and repetitions. Each token type has its own custom handling:
* Literals are included as they are
* Quantifiers  generate appropriate character repetitions
* Groups trigger recursive  alternative selection
* Special cases such as exponents are getting normalized before being processed
```
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
```

Besides that, it has step logging and provides step by step display of every decision taken by the code so that the logic of the generation behaviour becomes clearer, by mentioning each taken decision ```Literal 'K' added``` , occurrences ```'J+': using 4 occurences``` and repetitions ```repetition= zero or more```
### The main function



```
def main():
    generator = RegexCombinationGenerator(max_repetitions=5)

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
```
The purpose of the ```main``` function is simply to demonstrage the usage of the code. The way it works is that it:
* Creates a generator instance
* Processes  the sample regex patterns
* Displays both the results and the step-by-step proccesing logic.




## Results
```
Generating combinations for: O(P|Q|R)+ 2(3|4)
Sample combinations:
  - OQQ23
  - OPP23
  - ORRR23
  - OPPPPP23
  - OR23

Processing steps:
  Processing regex: 'O(P|Q|R)+ 2(3|4)'
  1. Tokenizing: 'O(P|Q|R)+ 2(3|4)'
  2. Tokens identified: 'O', '(P|Q|R)+', '2', '(3|4)'
  
combination #1:
  - Literal 'O': added
  - Group '(P|Q|R)+': alternatives=['P', 'Q', 'R'], repetition=one or more (1-5)
  - Group '(P|Q|R)+': selected 'Q' repeated 2 times
  - Literal '2': added
  - Group '(3|4)': alternatives=['3', '4'], repetition=exactly 1
  - Group '(3|4)': selected '3' repeated 1 times
  - Result: 'OQQ23'
  
combination #2:
  - Literal 'O': added
  - Group '(P|Q|R)+': alternatives=['P', 'Q', 'R'], repetition=one or more (1-5)
  - Group '(P|Q|R)+': selected 'P' repeated 2 times
  - Literal '2': added
  - Group '(3|4)': alternatives=['3', '4'], repetition=exactly 1
  - Group '(3|4)': selected '3' repeated 1 times
  - Result: 'OPP23'
  
combination #3:
  - Literal 'O': added
  - Group '(P|Q|R)+': alternatives=['P', 'Q', 'R'], repetition=one or more (1-5)
  - Group '(P|Q|R)+': selected 'R' repeated 3 times
  - Literal '2': added
  - Group '(3|4)': alternatives=['3', '4'], repetition=exactly 1
  - Group '(3|4)': selected '3' repeated 1 times
  - Result: 'ORRR23'
  
combination #4:
  - Literal 'O': added
  - Group '(P|Q|R)+': alternatives=['P', 'Q', 'R'], repetition=one or more (1-5)
  - Group '(P|Q|R)+': selected 'P' repeated 5 times
  - Literal '2': added
  - Group '(3|4)': alternatives=['3', '4'], repetition=exactly 1
  - Group '(3|4)': selected '3' repeated 1 times
  - Result: 'OPPPPP23'
  
combination #5:
  - Literal 'O': added
  - Group '(P|Q|R)+': alternatives=['P', 'Q', 'R'], repetition=one or more (1-5)
  - Group '(P|Q|R)+': selected 'R' repeated 1 times
  - Literal '2': added
  - Group '(3|4)': alternatives=['3', '4'], repetition=exactly 1
  - Group '(3|4)': selected '3' repeated 1 times
  - Result: 'OR23'

Generating combinations for: A*B(C|D|E)F(G|H|I)²
Sample combinations:
  - ABDFHH
  - AAAABCFGG
  - AAAAABDFII
  - AAAABEFGG
  - AAAAABDFII

Processing steps:
  Processing regex: 'A*B(C|D|E)F(G|H|I)²'
  1. Tokenizing: 'A*B(C|D|E)F(G|H|I)2'
  2. Tokens identified: 'A*', 'B', '(C|D|E)', 'F', '(G|H|I)2'
  
combination #1:
  - 'A*': using 1 occurrences (repetition = zero or more)
  - Literal 'B': added
  - Group '(C|D|E)': alternatives=['C', 'D', 'E'], repetition=exactly 1
  - Group '(C|D|E)': selected 'D' repeated 1 times
  - Literal 'F': added
  - Group '(G|H|I)2': alternatives=['G', 'H', 'I'], repetition=exactly 2
  - Group '(G|H|I)2': selected 'H' repeated 2 times
  - Result: 'ABDFHH'
  
combination #2:
  - 'A*': using 4 occurrences (repetition = zero or more)
  - Literal 'B': added
  - Group '(C|D|E)': alternatives=['C', 'D', 'E'], repetition=exactly 1
  - Group '(C|D|E)': selected 'C' repeated 1 times
  - Literal 'F': added
  - Group '(G|H|I)2': alternatives=['G', 'H', 'I'], repetition=exactly 2
  - Group '(G|H|I)2': selected 'G' repeated 2 times
  - Result: 'AAAABCFGG'
  
combination #3:
  - 'A*': using 5 occurrences (repetition = zero or more)
  - Literal 'B': added
  - Group '(C|D|E)': alternatives=['C', 'D', 'E'], repetition=exactly 1
  - Group '(C|D|E)': selected 'D' repeated 1 times
  - Literal 'F': added
  - Group '(G|H|I)2': alternatives=['G', 'H', 'I'], repetition=exactly 2
  - Group '(G|H|I)2': selected 'I' repeated 2 times
  - Result: 'AAAAABDFII'
  
combination #4:
  - 'A*': using 4 occurrences (repetition = zero or more)
  - Literal 'B': added
  - Group '(C|D|E)': alternatives=['C', 'D', 'E'], repetition=exactly 1
  - Group '(C|D|E)': selected 'E' repeated 1 times
  - Literal 'F': added
  - Group '(G|H|I)2': alternatives=['G', 'H', 'I'], repetition=exactly 2
  - Group '(G|H|I)2': selected 'G' repeated 2 times
  - Result: 'AAAABEFGG'
  
combination #5:
  - 'A*': using 5 occurrences (repetition = zero or more)
  - Literal 'B': added
  - Group '(C|D|E)': alternatives=['C', 'D', 'E'], repetition=exactly 1
  - Group '(C|D|E)': selected 'D' repeated 1 times
  - Literal 'F': added
  - Group '(G|H|I)2': alternatives=['G', 'H', 'I'], repetition=exactly 2
  - Group '(G|H|I)2': selected 'I' repeated 2 times
  - Result: 'AAAAABDFII'

Generating combinations for: J+K(L|M|N)*O?(P|Q)³
Sample combinations:
  - JJJKNNPPP
  - JJJJKMMMQQQ
  - JJJJJKNNOQQQ
  - JJJKMMMMMQQQ
  - JJJJKLOQQQ

Processing steps:
  Processing regex: 'J+K(L|M|N)*O?(P|Q)³'
  1. Tokenizing: 'J+K(L|M|N)*O?(P|Q)3'
  2. Tokens identified: 'J+', 'K', '(L|M|N)*', 'O?', '(P|Q)3'
  
combination #1:
  - 'J+': using 3 occurrences
  - Literal 'K': added
  - Group '(L|M|N)*': alternatives=['L', 'M', 'N'], repetition=zero or more (0-5)
  - Group '(L|M|N)*': selected 'N' repeated 2 times
  - 'O?': omitted
  - Group '(P|Q)3': alternatives=['P', 'Q'], repetition=exactly 3
  - Group '(P|Q)3': selected 'P' repeated 3 times
  - Result: 'JJJKNNPPP'
  
combination #2:
  - 'J+': using 4 occurrences
  - Literal 'K': added
  - Group '(L|M|N)*': alternatives=['L', 'M', 'N'], repetition=zero or more (0-5)
  - Group '(L|M|N)*': selected 'M' repeated 3 times
  - 'O?': omitted
  - Group '(P|Q)3': alternatives=['P', 'Q'], repetition=exactly 3
  - Group '(P|Q)3': selected 'Q' repeated 3 times
  - Result: 'JJJJKMMMQQQ'
  
combination #3:
  - 'J+': using 5 occurrences
  - Literal 'K': added
  - Group '(L|M|N)*': alternatives=['L', 'M', 'N'], repetition=zero or more (0-5)
  - Group '(L|M|N)*': selected 'N' repeated 2 times
  - 'O?': included
  - Group '(P|Q)3': alternatives=['P', 'Q'], repetition=exactly 3
  - Group '(P|Q)3': selected 'Q' repeated 3 times
  - Result: 'JJJJJKNNOQQQ'
  
combination #4:
  - 'J+': using 3 occurrences
  - Literal 'K': added
  - Group '(L|M|N)*': alternatives=['L', 'M', 'N'], repetition=zero or more (0-5)
  - Group '(L|M|N)*': selected 'M' repeated 5 times
  - 'O?': omitted
  - Group '(P|Q)3': alternatives=['P', 'Q'], repetition=exactly 3
  - Group '(P|Q)3': selected 'Q' repeated 3 times
  - Result: 'JJJKMMMMMQQQ'
  
combination #5:
  - 'J+': using 4 occurrences
  - Literal 'K': added
  - Group '(L|M|N)*': alternatives=['L', 'M', 'N'], repetition=zero or more (0-5)
  - Group '(L|M|N)*': selected 'L' repeated 1 times
  - 'O?': included
  - Group '(P|Q)3': alternatives=['P', 'Q'], repetition=exactly 3
  - Group '(P|Q)3': selected 'Q' repeated 3 times
  - Result: 'JJJJKLOQQQ'
```

## Conclusion

In this lab, we explored the fundamentals of regular expressions, their practical applications, and their connection to formal language theory. We developed a regex-based word generator that can parse, tokenize, and process regex patterns to generate valid string combinations. The implementation effectively decomposes regex patterns into recognizable components, handles quantifiers and groups, and constructs randomized yet conforming outputs.

Through systematic tokenization, parsing, and generation steps, we demonstrated how regex can be programmatically interpreted to produce structured outputs. The logging mechanism provides a clear view of how each pattern is processed, making the approach both transparent and debuggable.

Overall, this project illustrates the computational power of regular expressions and their role in automating text processing tasks. The developed solution not only reinforces the theoretical understanding of finite automata and formal languages but also has practical applications in fields like data validation, lexical analysis, and pattern recognition.


## References

[1] [A sample of a regular expression implementation](https://llvm.org/docs/tutorial/MyFirstLanguageFrontend/LangImpl01.html)

[2] [Regular expressions](https://en.wikipedia.org/wiki/Lexical_analysis)

[3] [Formal Languages and Finite Automata, Guide for practical lessons](https://else.fcim.utm.md/pluginfile.php/110458/mod_resource/content/0/LFPC_Guide.pdf)