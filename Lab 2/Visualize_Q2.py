import graphviz

def create_complete_fst():
    dot = graphviz.Digraph('NounMorphologyFST', format='svg')
    # States
    dot.node('0', '0', shape='point', width='0.1')
    dot.node('1', '1')
    dot.node('2', '2') 
    dot.node('3', '3')
    dot.node('4', '4', shape='doublecircle')
    dot.node('5', '5', shape='doublecircle')
    
    # Transitions with input:output format
    # State 0 -> State 1: Read any valid noun
    dot.edge('0', '1', 'noun:noun')
    
    # State 1 -> States 2,3,4 based on ending
    dot.edge('1', '2', '[s,z,x,ch,sh]:[s,z,x,ch,sh]')  # E-insertion cases
    dot.edge('1', '3', '[consonant+y]:[consonant+y]')    # Y-replacement cases  
    dot.edge('1', '4', 'other:other')                    # Regular S-addition
    
    # For invalid words
    dot.edge('1', '5', 'invalid:Invalid Word')
    
    # State 2 -> State 4: Apply E-insertion rule
    dot.edge('2', '4', 'ε:es')
    
    # State 3 -> State 4: Apply Y-replacement rule  
    dot.edge('3', '4', 'y:ies')
    
    # Self-loops for generating morphological features
    dot.edge('4', '4', 'ε:+N+SG')  # Add singular features
    dot.edge('4', '4', 'ε:+N+PL')  # Add plural features
    
    return dot

fst = create_complete_fst()
fst.render('q2_visual', format='svg', cleanup=True)