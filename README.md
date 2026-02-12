# Statikomand

Python static command parser.

> Like argparse, but without connection to CLI.

All CLI parsers interacts with user terminal in order to parse a command (python argparse calls sys.argv for example).

This python module provides tools for doing the same job, without any interaction with the user terminal. It just parses a raw string into a structured object.

It also provides a way to declare completion of arguments names and parameters.

## Getting Started

```bash
pip install statikomand
```

### Command parser

```python
from statikomand.komand_parser import KomandParser

parser = KomandParser()

parser.add_argument("-f", "--flag1", label="flag")
parser.add_argument("-d", "--delete", label="del")
parser.add_argument("POS1", label="pos1")
parser.add_argument("POS2")

code = "param1 param2 -f 'flag1 parameter' -d delete_param"
args = parser.parse(code)

print(args.pos1)  # value for POS1 positional argument : 'param1'
print(args.POS2)  # value for POS2 positional argument : 'param2'
```

### Command completion

> Each argument can have a completer method, which is a function that take one string argument, and returns a list of strings (proposition of completions)

The 'do_complete' method of the parser tries to complete the flag names, and calls the do_complete method of positional and / or flag arguments; according to the position of the last caracter.

Here is an example :

```python
from statikomand.komand_parser import KomandParser
def completer_1(code: str):
    return ["completion1", "completion2"]


def completer_2(code: str):
    return [code + code + code]


parser = KomandParser()

parser.add_argument("-f", "--flag1", label="flag", completer=completer_1)
parser.add_argument("-d", "--delete", label="del", completer=completer_2)
parser.add_argument("POS1", completer=completer_1)
parser.add_argument("POS2", completer=completer_2)

# completes positional parameter 1 with completer_1
code = "this-code-will-be-replaced-by-completer-1"
res = parser.do_complete(code)
print(res)  # proposition of completions for code : ['completion1', 'completion2']


# completes flag's name
code2 = "param1 param2 --fl"
res2 = parser.do_complete(code2)
print(res2)  # proposition of completions for code : ['--flag1']

# completes flag1 parameter with flag1 completer
code3 = "param1 param2 --flag1 blabla"
res3 = parser.do_complete(code3)
print(res3)  # proposition of completions for code : ['completion1', 'completion1']
```
