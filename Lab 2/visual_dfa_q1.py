import string
from automata.fa.dfa import DFA

from visual_automata.fa.dfa import VisualDFA
all_chars = set(string.printable)

dfa = VisualDFA(
    states={"q0", "q1", "q2"},
    input_symbols={string.ascii_lowercase},
    transitions={
        "q0": {letter: "q1" if letter in "ab" else "q2" for letter in string.ascii_lowercase},
        "q1": {},
        "q2": {letter: "q2" for letter in all_chars},
    },
    
    initial_state="q0",
    final_states={"q1"},
)
for ch in all_chars:
    if ch in string.ascii_lowercase:
        transitions['q1'][ch] = 'q1' 
    else:
        transitions['q1'][ch] = 'q2' 

dfa = VisualDFA(dfa)
dfa.show_diagram("visual_q1")