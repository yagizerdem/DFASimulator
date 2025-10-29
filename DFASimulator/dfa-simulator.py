import os
import json


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


root_path = os.getcwd()
tuple_dir = os.path.join(root_path, "tuples")
if not os.path.exists(tuple_dir):
    raise Exception("Tuples not found to create DFA {Q, S, q0, F, delta}")
tuple_names = os.listdir(tuple_dir)

input_dir = os.path.join(root_path, "inputs")
if not os.path.exists(input_dir):
    raise Exception("Input path not found")

input_names = os.listdir(input_dir)

# dfa, input, dfa file name, input file name
dfa_input_list: list[(DFA, list[str], str, str)] = []
dfa_list: list[(str, DFA)] = []  # map file name and dfa
input_list: list[(str, list[str])] = []  # map file name and input


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

for file_name in input_names:
    input_absolute_path = os.path.join(input_dir, file_name)
    file = open(input_absolute_path, "r")
    serialized = file.read()
    file.close()
    input = list(filter(lambda x: len(x) > 0, map(
        lambda x: x.strip(), serialized.split("\n"))))
    input_list.append((file_name, input))


# map dfa and input files by matchinf file names first segment
for dfa in dfa_list:
    dfa_file_name: str = dfa[0]
    for input in input_list:
        input_file_name: str = input[0]

        if dfa_file_name.startswith(input_file_name.split(".").pop(0)):
            dfa_input_list.append((dfa[1], input[1], dfa[0], input[0]))

# validate dfa


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


for dfa_input in dfa_input_list:
    dfa = dfa_input[0]
    input_list = dfa_input[1]
    dfa_file_name = dfa_input[2]
    input_file_name = dfa_input[3]
    validateTransitionCounts(dfa, dfa_file_name)
    validateCharSet(dfa, dfa_file_name)


# simulates dfa


def isMatch(dfa: DFA, input: list[str]) -> bool:
    cur_state = dfa.StartState
    for token in input:
        transition = next((t for t in dfa.Transitions if t.FromState ==
                          cur_state and t.Consume == token), None)
        cur_state = transition.ToState
    return cur_state in dfa.AcceptStates


for dfa_input in dfa_input_list:
    dfa = dfa_input[0]
    input_list = dfa_input[1]
    dfa_file_name = dfa_input[2]
    input_file_name = dfa_input[3]
    print("-" * 50)
    print(f"DFA {dfa_file_name}, input {input_file_name} test results :")
    print("\n")

    for input in input_list:
        flag = isMatch(dfa,  input)
        if flag:
            print(
                f"{dfa_file_name} match with input {input} [ACCEPTED]")
        else:
            print(f"{dfa_file_name} not match with input {input} [REJECTED]")
