import os
import json

"""
 Make a variable Ri for each state qi of the DFA.
 Add the rule Ri → aRj to the CFG if δ(qi,a)=qj is a transition in the DFA.
 Add the rule Ri → ε if qi is an accept state of the DFA.
 Make R0 the start variable of the grammar, where q0 is the start state of the machine.
"""


"""
A GFG (or just a grammar) G is a tuple G = (V, T, P, S) where

V is the (finite) set of variables (or non terminals or syntactic categories). Each variable represents a language, i.e., a set of strings
T is a finite set of terminals, i.e., the symbols that form the strings of the language being defined
P is a set of production rules that represent the recursive definition of the language.
S is the start symbol that represents the language being defined. Other variables represent auxiliary classes of strings that are used to define the language of the start symbol.

"""


class Transition:
    def __init__(self, FromState, ToState, Consume):
        self.FromState = FromState
        self.ToState = ToState
        self.Consume = Consume

    def __str__(self):
        return f"{self.FromState} --{self.Consume}--> {self.ToState}"


class DFA:
    def __init__(self):
        self.Symbols: list = []
        self.States: list[str] = []
        self.AcceptStates: list[str] = []
        self.Transitions: list[Transition] = []
        self.StartState: str = None

    def __str__(self):
        transitions_str = "\n  ".join(str(t) for t in self.Transitions)
        return (
            f"DFA:\n"
            f"  Symbols: {self.Symbols}\n"
            f"  States: {self.States}\n"
            f"  StartState: {self.StartState}\n"
            f"  AcceptStates: {self.AcceptStates}\n"
            f"  Transitions:\n  {transitions_str}"
        )


class CFG:
    def __init__(self):
        self.terminals = []
        self.nonterminals = []
        self.productionrules = []
        self.startSymbol = None

    def to_dict(self):
        return {
            'terminals': self.terminals,
            'nonterminals': self.nonterminals,
            'productionrules': self.productionrules,
            'startSymbol': self.startSymbol
        }


root_path = os.getcwd()
tuple_dir = os.path.join(root_path, "dfa-graph")
if not os.path.exists(tuple_dir):
    raise Exception("Tuples not found to create DFA {Q, S, q0, F, delta}")
tuple_names = os.listdir(tuple_dir)

dfa_list: list[(str, DFA)] = []  # map file name and dfa

for file_name in tuple_names:
    tuple_absolute_path = os.path.join(tuple_dir, file_name)
    file = open(tuple_absolute_path, "r")
    serialized = file.read()
    file.close()
    data = json.loads(serialized)

    dfa: DFA = DFA()
    dfa.Symbols = data["Symbols"]
    dfa.States = data["States"]
    dfa.AcceptStates = data["AcceptStates"]
    dfa.StartState = data["StartState"]

    transitions = data["Transitions"]
    for transition in transitions:
        dfa.Transitions.append(Transition(
            transition["FromState"], transition["ToState"], transition["Consume"]))

    dfa_list.append((file_name, dfa))


def validateTransitionCounts(dfa: DFA, dfa_file_name):
    for state in dfa.States:
        for symbol in dfa.Symbols:
            transtion_count = [transition for transition in dfa.Transitions if transition.Consume ==
                               symbol and transition.FromState == state]
            if len(transtion_count) > 1:
                raise Exception(
                    f"{dfa_file_name} contains ambigious transitions from state {state} that consumes {symbol}")

            if len(transtion_count) == 0:
                raise Exception(
                    f"{dfa_file_name} contains no transitions from state {state} that consumes {symbol}")


def validateCharSet(dfa: DFA, dfa_file_name: str):
    consumed_chars = list(set(t.Consume for t in dfa.Transitions))

    if set(consumed_chars) != set(dfa.Symbols):
        missing = set(dfa.Symbols) - set(consumed_chars)
        extra = set(consumed_chars) - set(dfa.Symbols)

        msg = f"[{dfa_file_name}] Invalid DFA alphabet definition:\n"
        if missing:
            msg += f"Missing symbols (defined but not used in transitions): {', '.join(missing)}\n"
        if extra:
            msg += f"Extra symbols (used in transitions but not defined in Symbols): {', '.join(extra)}"
        raise Exception(msg)


# handle validations
for f_name_dfa in dfa_list:
    validateTransitionCounts(f_name_dfa[1], f_name_dfa[1])
    validateCharSet(f_name_dfa[1], f_name_dfa[1])

cfg_list: list[(str, CFG)] = []

for f_name_dfa in dfa_list:
    dfa = f_name_dfa[1]
    dfa_f_name = f_name_dfa[0]
    cfg_file_name = f"CFG_{dfa_f_name.split('.')[0]}.json"

    cfg = CFG()
    cfg.startSymbol = dfa.StartState
    cfg.nonterminals = dfa.States
    cfg.terminals = dfa.Symbols

    for R in cfg.nonterminals:
        dfa_transitions = [t for t in dfa.Transitions if t.FromState == R]
        production_rule = f"{R} -> "
        for transition in dfa_transitions:
            production_rule += f"{transition.Consume}{transition.ToState} |"

        production_rule = production_rule[:len(production_rule) - 1]

        if R in dfa.AcceptStates:
            production_rule += f"| EPS"

        cfg.productionrules.append(production_rule)

    cfg_list.append((cfg_file_name, cfg))


for f_name_cfg in cfg_list:
    f_name = f_name_cfg[0]
    cfg = f_name_cfg[1]

    serialized_cfg = json.dumps(cfg.to_dict())

    root_path = os.getcwd()
    cfg_out_path = os.path.join(root_path, "cfg-graph")
    if not os.path.exists(cfg_out_path):
        os.mkdir(cfg_out_path)

    f_absolute_path = f"{os.path.join(cfg_out_path, f_name)}"

    with open(f_absolute_path, 'w') as f:
        f.write(serialized_cfg)
