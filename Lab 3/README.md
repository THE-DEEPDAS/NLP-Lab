score = node's count , cnt ni value
so it is no. of words in corpus passing that trie node

score(doublt) mate find child with max score
fraction = 1 - (max_child_count / node_count)
score = fraction * branching

this is a heuristic that interprets distribution balance as low fraction = low score so good distribution

to check which trie is better it calculates which has produced max successfull splits

support = n -> cnt