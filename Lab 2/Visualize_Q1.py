from automathon import DFA
import string
import re

all_chars = set(string.ascii_letters + string.digits + string.punctuation + " ")
q = {'q0', 'q1', 'q2'}
sigma = all_chars

delta = {
    'q0': {ch: 'q1' for ch in string.ascii_lowercase},  
    'q2': {ch: 'q2' for ch in all_chars} 
}

delta['q1'] = {}
for ch in all_chars:
    if ch in string.ascii_lowercase:
        delta['q1'][ch] = 'q1'  
    else:
        delta['q1'][ch] = 'q2'  

initial_state = 'q0'
f = {'q1'}

def sanitize_transitions(delta):
    sanitized_delta = {}
    for state, transitions in delta.items():
        sanitized_delta[state] = {}
        for char, target_state in transitions.items():
            sanitized_char = re.escape(char)  
            sanitized_delta[state][sanitized_char] = target_state
    return sanitized_delta

delta = sanitize_transitions(delta)
automata = DFA(q, sigma, delta, initial_state, f)

test_string = input("Enter string: ")
print("Accepted" if automata.accept(test_string) else "Not Accepted")

automata.view("visual_q1")