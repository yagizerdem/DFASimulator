import os
import json

if  not os.path.exists("./nfa"):
    raise Exception("nfa not exist")



class Transition:
    def __init__(self, _from: str, to: str, consume: str):
        self._from = _from
        self.to = to
        self.consume = consume

    def __str__(self):
        return f"{self._from} --{self.consume}--> {self.to}"

    def to_dict(self):
        return {
            "from": self._from,
            "to": self.to,
            "symbol": self.consume
        }


class Nfa:
      def __init__(self, symbols: list[str], states: list[str], startState: str, finalStates: list[str], file_name):
            self.symbols = symbols
            self.states = states
            self.startState = startState
            self.finalStates = finalStates
            self.transitions: list[Transition] = []
            self.file_name =file_name

      def add_transition(self, _from: str, to: str, consume: str):
            self.transitions.append(Transition(_from, to, consume))

      def epsClosure(self, state):
            closure  = []

            if state not in self.states:
                 return closure

            closure = [state]
            stack = [state]

            while len(stack) > 0:
                  new_stack = []
                  state = stack.pop()

                  for transition in self.transitions:
                        if transition._from == state and \
                                transition.consume == "eps"\
                                    and transition.to not in new_stack \
                                            and transition.to not in closure:
                             new_stack.append(transition.to)

                  closure.extend(new_stack)
                  stack.extend(new_stack)

            return closure
   

      def __str__(self):
            transitions_str = "\n  ".join(str(t) for t in self.transitions)
            return (
                f"NFA:\n"
                f"  Symbols: {self.symbols}\n"
                f"  States: {self.states}\n"
                f"  Start State: {self.startState}\n"
                f"  Final States: {self.finalStates}\n"
                f"  Transitions:\n  {transitions_str}"
            )


class Dfa:
    def __init__(self, symbols: list[str], states: list[str], startState: str, finalStates: list[str], file_name: str):
        self.symbols = symbols
        self.states = states
        self.startState = startState
        self.finalStates = finalStates
        self.transitions: list[Transition] = []
        self.file_name = file_name

    def add_transition(self, _from: str, to: str, consume: str):
        self.transitions.append(Transition(_from, to, consume))

    def to_dict(self):
        return {
            "symbols": self.symbols,
            "states": self.states,
            "startState": self.startState,
            "finalStates": self.finalStates,
            "transitions": [t.to_dict() for t in self.transitions]
        }

    def __str__(self):
        transitions_str = "\n  ".join(str(t) for t in self.transitions)
        return (
            f"DFA:\n"
            f"  Symbols: {self.symbols}\n"
            f"  States: {self.states}\n"
            f"  Start State: {self.startState}\n"
            f"  Final States: {self.finalStates}\n"
            f"  Transitions:\n  {transitions_str}"
        )



serialized_nfas = []
nfas : list[Nfa] = []

nfa_file_names = os.listdir("./nfa")




for file_name in nfa_file_names:
      realative_path = os.path.join("./nfa", file_name)
      with open(realative_path, 'r') as f:
            serialized_nfa_graph = ''.join(c for c in f.read().strip()).replace("\n" , "").replace("\t", "").replace(" ",  "")
            json_obj = json.loads(serialized_nfa_graph)
            nfa  = Nfa(json_obj["symbols"], json_obj["states"], json_obj["startState"], json_obj["finalStates"], file_name)

            # add transitions
            for t in json_obj["transitions"]:
                  transition = Transition(t["from"], t["to"], t["consume"])            
                  nfa.transitions.append(transition)

            nfas.append(nfa)



dfa_table_nfa_map = []

for nfa in nfas:
      table = {}
      look_ahead_states = []

      eps_closure_of_start_state = nfa.epsClosure(nfa.startState)
      eps_closure_of_start_state.sort()
      merged = ",".join(eps_closure_of_start_state)
      look_ahead_states.append(merged)

      for state in look_ahead_states:
            if state in table:
                  continue
            table[state] = {}

            for symbol in [symbol for symbol in nfa.symbols if symbol != "eps"]:
                  reached_states = set()
                  for transition in nfa.transitions:
                       for split_state in state.split(","):
                              if transition._from == split_state and transition.consume == symbol:
                                      reached_states.add(transition.to)

                  eps_transition = set()
                  for reacehd_state in reached_states:
                        closure = nfa.epsClosure(reacehd_state)
                        for c in closure:
                              eps_transition.add(c)

                  eps_transition = list(eps_transition)
                  eps_transition.sort()
                  merged = ",".join(eps_transition)
                  table[state][symbol] = merged if len(merged) > 0 else "-"
                  if merged not in table.keys():
                        look_ahead_states.append(merged)


      dfa_table_nfa_map.append((table, nfa))



for item in dfa_table_nfa_map:
      table : dict = item[0]
      nfa :Nfa = item[1]

      if len(table.keys()) == 0:
          continue

      start_state = list(table.keys())[0]
      final_states = set()
      for state in list(table.keys()):
            splitted = set(state.split(","))
            if len(set(nfa.finalStates).intersection(splitted)) > 0:
                 final_states.add(state)
      
      
      file_name = f"dfa_{nfa.file_name.split(".")[0]}.json"

      dfa = Dfa([s for s in nfa.symbols if len(s.strip()) > 0 and s.strip() != "eps"],  [state for state in list(table.keys()) if len(state.strip()) > 0], start_state, list(final_states), file_name)
      
      dfa.states.append("q_dead")
      for symbol in [s for s in nfa.symbols if s != "eps"]:
           dfa.transitions.append(Transition("q_dead", "q_dead", symbol))
      
      # add transitions
      for i, (_from, symbol_to_map )in enumerate(table.items()):
            for j , (consume, to) in enumerate(symbol_to_map.items()):
                 if _from.strip() == "" or to.strip() == "" :
                      continue 
                 dfa.transitions.append(Transition(_from, to, consume))



      serialized = json.dumps(dfa.to_dict(), indent=2)
      
      with open(f"./dfa/{dfa.file_name}", "w", encoding="utf-8") as f:
           f.write(serialized)