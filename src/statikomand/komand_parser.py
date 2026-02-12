from typing import Callable
import shlex
from dataclasses import dataclass


@dataclass
class ParsedKomandArgs:
    """
    Empty class that is used to store parsed arguments.
    """

    def __init__(self):
        pass


class KomandArg:
    """
    Generic class that is subclassed to define both positional
    arguments and flags.
    """

    def __init__(
        self,
        label: str,
        completer: Callable | None = None,
        help: str | None = None,
    ):
        self.label = label
        self.help = help
        self.completer = completer

    def do_complete(self, code: str) -> list[str]:
        """
        Similar to jupyter kernels do_complete method, proposes
        completions for the value of the argument.
        """
        if self.completer is None:
            return []
        return self.completer(code)


class PositionalKomandArg(KomandArg):
    """
    Positional argument of a command. All of them are
    mandatory for each command call.
    """

    def __init__(
        self,
        name: str,
        completer: Callable | None = None,
        label: str | None = None,
        help: str | None = None,
    ):
        if label is None:
            label = name
        self.name = name
        if self.name[0] == "-":
            raise ValueError(
                f"A positional argument must not start with '-' : {self.label}"
            )
        super().__init__(completer=completer, label=label, help=help)


class OptionalKomandArg(KomandArg):
    """
    Optional argument of a command (flag).
    """

    def __init__(
        self,
        flags: list[str],
        completer: Callable | None = None,
        label: str | None = None,
        help: str | None = None,
    ):
        if label is None:
            label = flags[0].strip("--")
        for each_name_or_flag in flags:
            if each_name_or_flag[0] != "-":
                raise ValueError(
                    f"Heterogenous name or flags among : {flags}. The value {each_name_or_flag} does not start with '-'."
                )
        self.flags = flags
        super().__init__(completer=completer, label=label, help=help)


class KomandParser:
    def __init__(
        self,
        description: str | None = None,
    ):
        self.description: str = description if description is not None else ""
        self.all_names_and_flags = []
        self.flags: list[OptionalKomandArg] = []
        self.positionals: list[PositionalKomandArg] = []

    def add_argument(
        self,
        *name_or_flags: str,
        completer: Callable | None = None,
        label: str | None = None,
        # action=None,
        # nargs=None,
        # const=None,
        # default=None,
        # type=None,
        # choices=None,
        # required=None,
        # help=None,
        # metavar=None,
        # dest=None,
        # deprecated=None,
    ):
        """
        Parameters :
        ---
            - name or flags - Either a name or a list of option strings, e.g. 'foo' or '-f', '--foo'.
            - action - The basic type of action to be taken when this argument is encountered at the command line.
            - nargs - The number of command-line arguments that should be consumed.
            - const - A constant value required by some action and nargs selections.
            - default - The value produced if the argument is absent from the command line and if it is absent from the namespace object.
            - type - The type to which the command-line argument should be converted.
            - choices - A sequence of the allowable values for the argument.
            - required - Whether or not the command-line option may be omitted (optionals only).
            - help - A brief description of what the argument does.
            - metavar - A name for the argument in usage messages.
            - dest - The name of the attribute to be added to the object returned by parse_args().
            - deprecated - Whether or not use of the argument is deprecated.
        """
        name_or_flags_list = list(name_or_flags)
        for k, each_arg in enumerate(name_or_flags_list):
            if len(each_arg) == 0:
                raise ValueError(f"Empty string for name_or_flags value number {k}")

        for each_name_or_flag in name_or_flags_list:
            if each_name_or_flag in self.all_names_and_flags:
                raise ValueError(
                    f"The name or flag {each_name_or_flag} is already defined in an argument. Please change name."
                )

        first_name_or_flag = name_or_flags_list[0]
        added_name_or_flags = []
        if first_name_or_flag[0] == "-":
            self.flags.append(
                OptionalKomandArg(name_or_flags_list, completer=completer, label=label)
            )
            added_name_or_flags += name_or_flags_list
        else:
            if len(name_or_flags_list) > 1:
                raise ValueError(
                    f"For positional arguments, only one name must be given. Received {name_or_flags_list}."
                )
            self.positionals.append(
                PositionalKomandArg(
                    name_or_flags_list[0], completer=completer, label=label
                )
            )
            added_name_or_flags.append(name_or_flags_list[0])

        self.all_names_and_flags += added_name_or_flags

    def do_complete_flag_name(self, word: str) -> list[str]:
        """
        Finds all flags whose name start with 'word'.

        Parameters :
        ---
            - word (str) : beginning of flag's name (e.g. --f)

        Returns :
        ---
            The list of matching flag names, e.g. ['--force', '--flag'].
        """
        all_matches = []
        for each_name in self.all_names_and_flags:
            if each_name[0] != "-":
                continue
            if len(each_name) < len(word):
                continue
            if each_name[: len(word)] == word:
                all_matches.append(each_name)
        return all_matches

    def try_complete_flag_value(self, flag_name: str, word: str) -> list[str] | None:
        """
        Try to find a flag with the given name, and calls the 'do_complete'
        method of this flag, with the given word.

        Parameters :
        ---
            - flag_name (str) : name of the flag
            - word (str) : word to be completed

        Returns :
        ---
            Either None if no match was found, or the list of matches
        """
        if flag_name not in self.all_names_and_flags:
            return
        for each_flag in self.flags:
            if flag_name not in each_flag.flags:
                continue
            return each_flag.do_complete(word)

    def do_complete(self, code: str) -> list[str]:
        """
        Proposes completion for the code, after the last token only.

        Parameters :
        ---
            - code (str) : the code that will be completed

        Examples :
        ---
            - 'POS1 --flag1 Tru' : the 'do_complete' method calls
                'do_complete' method of --flag1 argument, and
                returns the proposed list of matches,
            - 'POS1 --fl' :  the 'do_complete' method return all flags
                starting with 'fl',
            - 'POS1 PO' : returns the 'do_complete' method of the second
                positional argument.

        Returns :
        ---
            The end of the code string, given the rules stated above.
        """
        splitted_code = shlex.split(code)
        last_word = splitted_code[-1]
        last_word_rank = len(splitted_code) - 1
        if last_word[0] == "-" and code[-1] != " ":
            return self.do_complete_flag_name(last_word)
        for k in range(last_word_rank):
            this_token = splitted_code[last_word_rank - k]
            if this_token[0] == "-":
                potential_matches = self.try_complete_flag_value(this_token, last_word)
                if potential_matches is not None:
                    return potential_matches

        if last_word_rank >= len(self.positionals):
            return []
        guessed_positional = self.positionals[last_word_rank]
        return guessed_positional.do_complete(last_word)

    def find_flag_with_name(self, flag_name: str):
        if flag_name[0] != "-":
            raise ValueError(f"Unexpected name for flag {flag_name}.")
        if flag_name not in self.all_names_and_flags:
            raise ValueError(f"Unknwon name for flag {flag_name}.")
        for each_flag in self.flags:
            if flag_name in each_flag.flags:
                return each_flag
        raise ValueError(f"Unknwon name for flag {flag_name}.")

    def parse(self, code: str) -> ParsedKomandArgs:
        """
        Parses the code into structured arguments : a ParsedKomandArgs
        with attributes set to positionals and flags labels.

        By default, all flags are set to None. An error
        is raised when not enough.

        Parameters :
        ---
            - code (str): the command line which will be parsed

        Returns :
        ---
            a ParsedKomandArgs object, with attributes set to each positional
            and flag label
        """
        components = shlex.split(code)

        # Create an empty parsed argument object
        arg_obj = ParsedKomandArgs()
        for each_flag in self.flags:
            arg_obj.__setattr__(each_flag.label, None)

        # Handle positional values, starting from first token
        positional_idx = 0
        for component in components:
            if component.startswith("-"):
                if positional_idx < len(self.positionals):
                    raise ValueError(
                        f"Not enough positional values were unpacked. Expected {len(self.positionals)}, got {positional_idx}"
                    )
                break
            if positional_idx >= len(self.positionals):
                raise ValueError(
                    f"Too much values were unpacked for positionals arguments. Expected {len(self.positionals)}, got {positional_idx+1}"
                )
            pos_label = self.positionals[positional_idx].label
            arg_obj.__setattr__(pos_label, component)
            positional_idx += 1

        # Handle flags, starting from token number positional_idx
        for k in range(positional_idx, len(components) - 1, 2):
            flag_name, flag_param = components[k], components[k + 1]
            flag = self.find_flag_with_name(flag_name)
            arg_obj.__setattr__(flag.label, flag_param)

        return arg_obj
