# dfa for accepting strings
# starts with lowercase letter and followed by 1 or more lowercase letters
# only 2 states: start and accept
import re

seq = r'[a-z]'

# now i will just make 2 groups, 1st is seq and then seq*
final_seq = r'([a-z])([a-z]*)'

word = input("Enter a string: ")
if re.fullmatch(final_seq, word):
    print("Accepted")
else:
    print("Not Accepted")